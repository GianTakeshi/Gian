import streamlit as st
import pandas as pd
import re
import html

# --- 1. UI 视觉配置 ---
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

    /* 每一行的容器：颜色和尺码并排 */
    .item-row {{
        display: flex;
        align-items: center; /* 垂直居中对齐 */
        flex-wrap: wrap;    /* 尺码多了自动换行 */
        gap: 8px;
        background: rgba(255, 255, 255, 0.04);
        margin: 4px 0;
        padding: 6px 10px;
        border-radius: 6px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }}

    /* 颜色标签：紧凑样式 */
    .clr-tag {{
        font-size: 0.85rem;
        font-weight: 800;
        color: #38bdf8;
        padding-right: 8px;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
        white-space: nowrap;
    }}

    /* 尺码小标签 */
    .sze-badge {{
        font-size: 0.75rem;
        color: #cbd5e1;
        background: rgba(56, 189, 248, 0.1);
        padding: 1px 6px;
        border-radius: 4px;
        white-space: nowrap;
    }}
    .sze-badge b {{
        color: #ffffff;
        margin-left: 2px;
    }}
    </style>
    
    <div class="user-profile">
        <img src="https://avatars.githubusercontent.com/GianTakeshi" style="width:35px;height:35px;border-radius:50%;">
        <div style="font-weight:700; font-size:0.85rem; color:white;">GianTakeshi</div>
    </div>
""", unsafe_allow_html=True)

# --- 2. 逻辑层 (继续使用 iloc 物理对齐) ---
def process_data(uploaded_file):
    COLOR_REG = r'(?i)Color[:：\s]*([a-zA-Z0-9\-_/]+)'
    SIZE_REG = r'(?i)Size[:：\s]*([a-zA-Z0-9\-\s/]+?)(?=\s*(?:Color|Size|$|[,;，；]))'
    SIZE_MAP = {'HIGH ANKLE SOCKS': 'L', 'KNEE-HIGH SOCKS': 'M'}
    
    df = pd.read_excel(uploaded_file, engine='openpyxl')
    valid, error = [], []
    
    for idx, row in df.iterrows():
        try:
            # 物理列定位：2=品类, 6=属性, 8=数量
            name = str(row.iloc[2]).strip()
            attr = str(row.iloc[6]).strip()
            qty_raw = str(row.iloc[8]).strip()
            
            if ';' in name or '；' in name:
                error.append({'行': idx+2, '原因': '复合品类'})
                continue

            cat = name.split(' ')[0].upper()
            if cat.startswith('WZ'): cat = 'WZ'
            
            chunks = [c.strip() for c in re.split(r'[;；]', attr) if c.strip()]
            parsed_items = []
            for chunk in chunks:
                c_m = re.search(COLOR_REG, chunk)
                s_m = re.search(SIZE_REG, chunk)
                if c_m:
                    clr = c_m.group(1).strip().upper()
                    sze_raw = s_m.group(1).strip().upper() if s_m else "FREE"
                    parsed_items.append({'Category': cat, 'Color': clr, 'Size': SIZE_MAP.get(sze_raw, sze_raw)})
            
            if parsed_items:
                valid.extend(parsed_items)
            else:
                error.append({'行': idx+2, '原因': '未识别出Color属性'})
        except Exception as e:
            error.append({'行': idx+2, '原因': f'报错: {str(e)}'})
            
    return pd.DataFrame(valid), pd.DataFrame(error)

# --- 3. 渲染层 ---
st.markdown("<h2 style='text-align:center; padding-top:50px;'>📋 紧凑属性看板</h2>", unsafe_allow_html=True)
file = st.file_uploader("", type=["xlsx"])

if file:
    v_df, e_df = process_data(file)
    t1, t2 = st.tabs(["✅ 矩阵汇总", "❌ 解析异常"])
    
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
                        # 大框标题
                        st.markdown(f'<div style="text-align:center; color:#38bdf8; font-weight:900; font-size:1.1rem; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:5px; margin-bottom:10px;">{cat}</div>', unsafe_allow_html=True)
                        
                        # 颜色聚合
                        color_groups = group.groupby('Color')
                        for clr, clr_data in color_groups:
                            size_stats = clr_data['Size'].value_counts().sort_index()
                            # 生成尺码小标
                            size_html = "".join([f'<span class="sze-badge">{s}<b>×{q}</b></span>' for s, q in size_stats.items()])
                            
                            # 渲染核心：Color 在左，Size 在右，同一行
                            st.markdown(f"""
                            <div class="item-row">
                                <span class="clr-tag">{html.escape(str(clr))}</span>
                                {size_html}
                            </div>
                            """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ 没抓到数据，快去 Tab 2 看看解析日志！")
            
    with t2:
        st.dataframe(e_df, use_container_width=True)
