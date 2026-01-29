import streamlit as st
import pandas as pd
import re
import html

# --- 1. UI 配置与样式 ---
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

    /* 清单行样式 */
    .color-row {{
        display: flex;
        flex-direction: column; /* 竖向排列颜色块 */
        background: rgba(255, 255, 255, 0.03);
        margin: 6px 0;
        padding: 8px 12px;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }}
    
    .clr-label {{
        font-size: 0.9rem;
        font-weight: 800;
        color: #38bdf8;
        margin-bottom: 4px;
        border-bottom: 1px solid rgba(255,255,255,0.05);
        padding-bottom: 2px;
    }}

    .size-chips {{
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
    }}

    .size-chip {{
        font-size: 0.75rem;
        color: #cbd5e1;
        background: rgba(255,255,255,0.05);
        padding: 1px 6px;
        border-radius: 4px;
    }}
    .size-chip b {{
        color: #38bdf8;
        margin-left: 2px;
    }}
    </style>
    
    <div class="user-profile">
        <img src="https://avatars.githubusercontent.com/GianTakeshi" style="width:35px;height:35px;border-radius:50%;">
        <div style="font-weight:700; font-size:0.85rem; color:white;">GianTakeshi</div>
    </div>
""", unsafe_allow_html=True)

# --- 2. 逻辑层 (增加颜色聚合逻辑) ---
def process_data(uploaded_file):
    COLOR_REG, SIZE_REG = r'(?i)Color[:：\s]*([a-zA-Z0-9\-_/]+)', r'(?i)Size[:：\s]*([a-zA-Z0-9\-\s/]+?)(?=\s*(?:Color|Size|$|[,;，；]))'
    SIZE_MAP = {'HIGH ANKLE SOCKS': 'L', 'KNEE-HIGH SOCKS': 'M'}
    df = pd.read_excel(uploaded_file, engine='openpyxl')
    valid, error = [], []
    for idx, row in df.iterrows():
        try:
            name, attr, qty = str(row[df.columns[2]]), str(row[df.columns[6]]), str(row[df.columns[8]])
            if ';' in name or '；' in name:
                error.append({'行': idx+2, '原因': '复合品类'})
                continue
            cat = name.split(' ')[0].upper()
            if cat.startswith('WZ'): cat = 'WZ'
            target_qty = int(re.findall(r'\d+', qty)[0]) if re.findall(r'\d+', qty) else 0
            chunks = [c.strip() for c in re.split(r'[;；]', attr) if c.strip()]
            parsed = []
            for chunk in chunks:
                c_m, s_m = re.search(COLOR_REG, chunk)
                s_m = re.search(SIZE_REG, chunk)
                if c_m:
                    clr = c_m.group(1).strip().upper()
                    sze = s_m.group(1).strip().upper() if s_m else "FREE"
                    parsed.append({'Category': cat, 'Color': clr, 'Size': SIZE_MAP.get(sze, sze)})
            if len(parsed) == target_qty: valid.extend(parsed)
            else: error.append({'行': idx+2, '原因': f'数量不符({len(parsed)}/{target_qty})'})
        except: continue
    return pd.DataFrame(valid), pd.DataFrame(error)

# --- 3. 渲染层 ---
st.markdown("<h2 style='text-align:center; padding-top:50px;'>📊 颜色聚合看板</h2>", unsafe_allow_html=True)
file = st.file_uploader("", type=["xlsx"])

if file:
    v_df, e_df = process_data(file)
    t1, t2 = st.tabs(["✅ 汇总矩阵", "❌ 异常拦截"])
    
    with t1:
        if not v_df.empty:
            v_df = v_df.sort_values(['Category', 'Color'])
            cat_groups = list(v_df.groupby('Category'))
            
            # 每行 6 个大盒子
            cols_per_row = 6
            for i in range(0, len(cat_groups), cols_per_row):
                batch = cat_groups[i : i + cols_per_row]
                cols = st.columns(cols_per_row)
                
                for idx, (cat, group) in enumerate(batch):
                    with cols[idx].container(border=True):
                        # 大盒子头部
                        st.markdown(f"""<div style="text-align:center; color:#38bdf8; font-weight:900; font-size:1.1rem; border-bottom:1px solid rgba(56,189,248,0.2); padding-bottom:5px;">{cat}</div>""", unsafe_allow_html=True)
                        st.markdown(f"""<div style="text-align:center; color:#94a3b8; font-size:0.7rem; margin-bottom:8px;">TOTAL: {len(group)} PCS</div>""", unsafe_allow_html=True)
                        
                        # 颜色聚合逻辑：按颜色分组
                        color_groups = group.groupby('Color')
                        for clr, clr_data in color_groups:
                            # 统计该颜色下的所有尺码数量
                            size_stats = clr_data['Size'].value_counts().sort_index()
                            
                            # 构建尺码小标签 HTML
                            size_html = "".join([f'<span class="size-chip">{s}<b>×{q}</b></span>' for s, q in size_stats.items()])
                            
                            # 渲染颜色行
                            st.markdown(f"""
                            <div class="color-row">
                                <div class="clr-label">{html.escape(str(clr))}</div>
                                <div class="size-chips">
                                    {size_html}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
        else:
            st.info("解析结果为空")
            
    with t2:
        st.dataframe(e_df, use_container_width=True)
