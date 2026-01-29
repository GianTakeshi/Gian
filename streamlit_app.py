import streamlit as st
import pandas as pd
import re
import html

# --- 1. UI 视觉配置 ---
st.set_page_config(page_title="GianTakeshi | Matrix Hub", page_icon="💎", layout="wide")

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

    /* 大格子：品类属性框 */
    .cat-box {{
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        margin-bottom: 15px;
        min-height: 160px; /* 保证高度对齐 */
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }}

    /* 品类名称加大 */
    .cat-name {{
        background: rgba(56, 189, 248, 0.2);
        color: #38bdf8;
        font-size: 1.1rem; 
        font-weight: 900;
        padding: 8px;
        text-align: center;
        border-bottom: 1px solid rgba(56, 189, 248, 0.1);
    }}

    /* 内部胶囊容器 */
    .capsule-area {{
        padding: 10px;
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        justify-content: center;
    }}

    /* 嵌套的小格子 */
    .inner-cap {{
        display: inline-flex;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 4px;
        font-size: 11px;
        background: rgba(255, 255, 255, 0.02);
    }}
    .c-clr {{ background: rgba(56, 189, 248, 0.1); padding: 2px 6px; color: #fff; font-weight: bold; border-right: 1px solid rgba(255,255,255,0.1); }}
    .c-sze {{ padding: 2px 6px; color: #ccc; }}
    .c-sze b {{ color: #38bdf8; }}
    </style>
    
    <div class="user-profile">
        <img src="https://avatars.githubusercontent.com/GianTakeshi" style="width:35px;height:35px;border-radius:50%;">
        <div style="font-weight:700; font-size:0.85rem; color:white;">GianTakeshi</div>
    </div>
""", unsafe_allow_html=True)

# --- 2. 逻辑层 (保持稳健) ---
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
                c_m, s_m = re.search(COLOR_REG, chunk), re.search(SIZE_REG, chunk)
                if c_m:
                    clr = c_m.group(1).strip().upper()
                    sze = s_m.group(1).strip().upper() if s_m else "FREE"
                    parsed.append({'Category': cat, 'Color': clr, 'Size': SIZE_MAP.get(sze, sze)})
            if len(parsed) == target_qty: valid.extend(parsed)
            else: error.append({'行': idx+2, '原因': f'数量不符({len(parsed)}/{target_qty})'})
        except: continue
    return pd.DataFrame(valid), pd.DataFrame(error)

# --- 3. 渲染层 (恢复一排六个大格子) ---
st.markdown("<h2 style='text-align:center; padding-top:50px;'>🚀 属性矩阵看板</h2>", unsafe_allow_html=True)
file = st.file_uploader("", type=["xlsx"])

if file:
    v_df, e_df = process_data(file)
    t1, t2 = st.tabs(["✅ 汇总矩阵", "❌ 异常报告"])
    
    with t1:
        if not v_df.empty:
            v_df = v_df.sort_values(['Category', 'Color'])
            cat_groups = list(v_df.groupby('Category'))
            
            # --- 关键：恢复一排 6 个 ---
            cols_per_row = 6
            for i in range(0, len(cat_groups), cols_per_row):
                batch = cat_groups[i : i + cols_per_row]
                cols = st.columns(cols_per_row)
                
                for idx, (cat, group) in enumerate(batch):
                    # 统计该品类下所有 Color+Size 组合
                    sub_stats = group.groupby(['Color', 'Size']).size().reset_index(name='count')
                    
                    # 极简 HTML 构建胶囊，防止乱码
                    inner_html = ""
                    for _, r in sub_stats.iterrows():
                        safe_clr = html.escape(str(r['Color']))
                        inner_html += f'<div class="inner-cap"><span class="c-clr">{safe_clr}</span><span class="c-sze">{r["Size"]} <b>×{r["count"]}</b></span></div>'
                    
                    # 在对应的列渲染大盒子
                    cols[idx].markdown(f"""
                    <div class="cat-box">
                        <div class="cat-name">{cat}</div>
                        <div class="capsule-area">{inner_html}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("数据解析后为空")
            
    with t2:
        st.dataframe(e_df, use_container_width=True)
