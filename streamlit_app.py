import streamlit as st
import pandas as pd
import re
import html

# --- 1. UI 视觉配置 (加入等高控制) ---
st.set_page_config(page_title="GianTakeshi | Matrix Hub", page_icon="📊", layout="wide")

st.markdown(f"""
    <style>
    .stApp {{ background: #020617; color: #ffffff; }}
    header {{ visibility: hidden; }}

    /* 悬浮头像 */
    .user-profile {{
        position: fixed; top: 20px; left: 20px; display: flex; align-items: center; gap: 12px; z-index: 99999; 
        background: rgba(255, 255, 255, 0.05); padding: 5px 15px 5px 5px; border-radius: 50px;
        border: 1px solid rgba(56, 189, 248, 0.3); backdrop-filter: blur(10px);
    }}

    /* 统一大盒子容器：强制等高并处理溢出 */
    .stElementContainer div[data-testid="stVerticalBlockBorderWrapper"] {{
        height: 320px !important; /* 你可以根据需求调整这个像素值 */
        overflow-y: auto;
        overflow-x: hidden;
        background: rgba(255, 255, 255, 0.02);
        border-radius: 12px;
        scrollbar-width: thin; /* Firefox 滚动条 */
        scrollbar-color: rgba(56, 189, 248, 0.3) transparent;
    }}

    /* Chrome 滚动条美化 */
    div[data-testid="stVerticalBlockBorderWrapper"]::-webkit-scrollbar {{
        width: 4px;
    }}
    div[data-testid="stVerticalBlockBorderWrapper"]::-webkit-scrollbar-thumb {{
        background: rgba(56, 189, 248, 0.3);
        border-radius: 10px;
    }}

    .item-row {{
        display: flex; align-items: center; flex-wrap: wrap; gap: 6px;
        background: rgba(255, 255, 255, 0.04); margin: 4px 0; padding: 6px 10px;
        border-radius: 6px; border: 1px solid rgba(255, 255, 255, 0.05);
    }}

    .clr-tag {{
        font-size: 0.85rem; font-weight: 800; color: #38bdf8;
        padding-right: 8px; border-right: 1px solid rgba(255, 255, 255, 0.1); white-space: nowrap;
    }}

    .sze-badge {{
        font-size: 0.75rem; color: #cbd5e1; background: rgba(56, 189, 248, 0.15);
        padding: 2px 8px; border-radius: 4px; white-space: nowrap; display: flex; align-items: center;
    }}
    .sze-badge b {{ color: #ffffff; font-family: monospace; font-size: 0.85rem; }}
    .qty-only {{ color: #38bdf8; font-weight: bold; margin-right: 2px; }}
    </style>
    
    <div class="user-profile">
        <img src="https://avatars.githubusercontent.com/GianTakeshi" style="width:35px;height:35px;border-radius:50%;">
        <div style="font-weight:700; font-size:0.85rem; color:white;">GianTakeshi</div>
    </div>
""", unsafe_allow_html=True)

# --- 2. 逻辑层 ---
def process_data(uploaded_file):
    COLOR_REG = r'(?i)Color[:：\s]*([a-zA-Z0-9\-_/]+)'
    SIZE_REG = r'(?i)Size[:：\s]*([a-zA-Z0-9\-\s/]+?)(?=\s*(?:Color|Size|$|[,;，；]))'
    SIZE_MAP = {'HIGH ANKLE SOCKS': 'L', 'KNEE-HIGH SOCKS': 'M'}
    df = pd.read_excel(uploaded_file, engine='openpyxl')
    valid = []
    for idx, row in df.iterrows():
        try:
            name, attr = str(row.iloc[2]).strip(), str(row.iloc[6]).strip()
            if ';' in name or '；' in name: continue
            cat = name.split(' ')[0].upper()
            if cat.startswith('WZ'): cat = 'WZ'
            chunks = [c.strip() for c in re.split(r'[;；]', attr) if c.strip()]
            for chunk in chunks:
                c_m, s_m = re.search(COLOR_REG, chunk), re.search(SIZE_REG, chunk)
                if c_m:
                    clr = c_m.group(1).strip().upper()
                    sze_raw = s_m.group(1).strip().upper() if s_m else "FREE"
                    valid.append({'Category': cat, 'Color': clr, 'Size': SIZE_MAP.get(sze_raw, sze_raw)})
        except: continue
    return pd.DataFrame(valid)

# --- 3. 渲染层 ---
st.markdown("<h2 style='text-align:center; padding-top:50px;'>📋 等高整齐矩阵看板</h2>", unsafe_allow_html=True)
file = st.file_uploader("", type=["xlsx"])

if file:
    v_df = process_data(file)
    if not v_df.empty:
        v_df = v_df.sort_values(['Category', 'Color'])
        cat_groups = list(v_df.groupby('Category'))
        
        cols_per_row = 6
        for i in range(0, len(cat_groups), cols_per_row):
            batch = cat_groups[i : i + cols_per_row]
            cols = st.columns(cols_per_row)
            for idx, (cat, group) in enumerate(batch):
                # 利用 border=True 配合 CSS height 锁定大小
                with cols[idx].container(border=True):
                    st.markdown(f'<div style="text-align:center; color:#38bdf8; font-weight:900; font-size:1.1rem; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:5px; margin-bottom:10px;">{cat}</div>', unsafe_allow_html=True)
                    
                    color_groups = group.groupby('Color')
                    for clr, clr_data in color_groups:
                        size_stats = clr_data['Size'].value_counts().sort_index()
                        size_html = ""
                        for s, q in size_stats.items():
                            if s == "FREE":
                                size_html += f'<span class="sze-badge"><span class="qty-only">×</span><b>{q}</b></span>'
                            else:
                                size_html += f'<span class="sze-badge">{s}<b>×{q}</b></span>'
                        
                        st.markdown(f"""
                        <div class="item-row">
                            <span class="clr-tag">{html.escape(str(clr))}</span>
                            {size_html}
                        </div>
                        """, unsafe_allow_html=True)
    else:
        st.info("暂无数据。")
