import streamlit as st
import pandas as pd
import re
import html

# --- 1. UI 视觉配置 (固定高度 + 美化) ---
st.set_page_config(page_title="GianTakeshi | Matrix Hub", page_icon="💎", layout="wide")

st.markdown(f"""
    <style>
    .stApp {{ background: #020617; color: #ffffff; }}
    header {{ visibility: hidden; }}
    
    /* 核心：强制所有原生 container 等高并支持滚动 */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        height: 380px !important; 
        overflow-y: auto !important;
        background: rgba(255, 255, 255, 0.02);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        scrollbar-width: thin;
        scrollbar-color: rgba(56, 189, 248, 0.3) transparent;
    }}
    
    div[data-testid="stVerticalBlockBorderWrapper"]::-webkit-scrollbar {{ width: 4px; }}
    div[data-testid="stVerticalBlockBorderWrapper"]::-webkit-scrollbar-thumb {{
        background: rgba(56, 189, 248, 0.3); border-radius: 10px;
    }}

    .user-profile {{
        position: fixed; top: 20px; left: 20px; display: flex; align-items: center; gap: 12px; z-index: 99999; 
        background: rgba(255, 255, 255, 0.05); padding: 5px 15px 5px 5px; border-radius: 50px;
        border: 1px solid rgba(56, 189, 248, 0.3); backdrop-filter: blur(10px);
    }}
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
    valid, error = [], []
    for idx, row in df.iterrows():
        try:
            name, attr, qty = str(row.iloc[2]), str(row.iloc[6]), str(row.iloc[8])
            if ';' in name or '；' in name:
                error.append({'行': idx+2, '原因': '复合品类'})
                continue
            cat = name.split(' ')[0].upper()
            if cat.startswith('WZ'): cat = 'WZ'
            target_qty = int(re.findall(r'\d+', qty)[0]) if re.findall(r'\d+', qty) else 0
            chunks = [c.strip() for c in re.split(r'[;；]', attr) if c.strip()]
            parsed = []
            for chunk in chunks:
                c_m, s_m = re.search(COLOR_REG, chunk), re.search(SIZE_REG, chunk)
                if c_m:
                    clr = c_m.group(1).strip().upper()
                    sze_raw = s_m.group(1).strip().upper() if s_m else "FREE"
                    parsed.append({'Category': cat, 'Color': clr, 'Size': SIZE_MAP.get(sze_raw, sze_raw)})
            if len(parsed) == target_qty: valid.extend(parsed)
            else: error.append({'行': idx+2, '原因': f'数量不符({len(parsed)}/{target_qty})'})
        except: continue
    return pd.DataFrame(valid), pd.DataFrame(error)

# --- 3. 渲染层 ---
st.markdown("<h2 style='text-align:center; padding-top:50px;'>📊 统一聚合看板</h2>", unsafe_allow_html=True)
file = st.file_uploader("", type=["xlsx"])

if file:
    v_df, e_df = process_data(file)
    t1, t2 = st.tabs(["✅ 汇总矩阵", "❌ 异常报告"])
    
    with t1:
        if not v_df.empty:
            v_df = v_df.sort_values(['Category', 'Color'])
            cat_groups = list(v_df.groupby('Category'))
            
            cols_per_row = 6
            for i in range(0, len(cat_groups), cols_per_row):
                batch = cat_groups[i : i + cols_per_row]
                cols = st.columns(cols_per_row)
                
                for idx, (cat, group) in enumerate(batch):
                    with cols[idx].container(border=True):
                        # 吸顶头部
                        st.markdown(f"""
                            <div style="background:rgba(56, 189, 248, 0.2); margin:-1rem -1rem 10px -1rem; padding:10px; text-align:center; color:#38bdf8; font-weight:900; font-size:1.1rem; border-bottom:1px solid rgba(56,189,248,0.1); position:sticky; top:-1rem; z-index:10;">
                                {cat}
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # --- 核心改动：按 Color 聚合 ---
                        color_groups = group.groupby('Color')
                        for clr, clr_data in color_groups:
                            # 统计该颜色下的所有尺码
                            size_stats = clr_data['Size'].value_counts().sort_index()
                            
                            # 生成尺码胶囊：FREE 隐藏，其他显示
                            size_html = ""
                            for s, q in size_stats.items():
                                if s == "FREE":
                                    size_html += f'<span style="background:rgba(56,189,248,0.1); padding:2px 6px; border-radius:4px; margin-left:4px; color:#fff;">×{q}</span>'
                                else:
                                    size_html += f'<span style="background:rgba(56,189,248,0.1); padding:2px 6px; border-radius:4px; margin-left:4px; color:#ccc;">{s}<b style="color:#38bdf8; margin-left:2px;">×{q}</b></span>'
                            
                            # 渲染颜色聚合行
                            st.markdown(f"""
                                <div style="display:flex; align-items:center; background:rgba(255,255,255,0.05); margin-bottom:6px; padding:6px 10px; border-radius:6px; font-size:11px; border:1px solid rgba(255,255,255,0.05); flex-wrap:wrap;">
                                    <span style="color:#38bdf8; font-weight:bold; border-right:1px solid rgba(255,255,255,0.1); padding-right:8px; min-width:45px; white-space:nowrap;">{html.escape(str(clr))}</span>
                                    <div style="display:flex; flex-wrap:wrap; gap:4px;">{size_html}</div>
                                </div>
                            """, unsafe_allow_html=True)
        else:
            st.info("数据解析后为空")
            
    with t2:
        st.dataframe(e_df, use_container_width=True)
