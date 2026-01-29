import streamlit as st
import pandas as pd
import re

# --- 1. UI 配置 ---
st.set_page_config(page_title="GianTakeshi | Matrix", page_icon="🚀", layout="wide")

st.markdown(f"""
    <style>
    .stApp {{ background: #020617; color: #ffffff; }}
    header {{visibility: hidden;}}

    /* 标题区域 */
    .hero-container {{ padding: 20px 0; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 25px; }}
    .grand-title {{ font-size: 1.8rem !important; font-weight: 800; color: #38bdf8; }}
    
    /* --- 关键：强制并排的容器 --- */
    .matrix-wrapper {{
        display: flex !important;
        flex-wrap: wrap !important; /* 核心：允许换行 */
        gap: 12px !important;      /* 单元格间距 */
        width: 100% !important;
        justify-content: flex-start !important;
        align-items: stretch !important;
    }}

    /* 单个九宫格单元 */
    .grid-unit {{
        flex: 0 0 160px; /* 固定宽度，不收缩 */
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        transition: all 0.2s ease;
    }}
    
    .grid-unit:hover {{
        border-color: #38bdf8;
        background: rgba(56, 189, 248, 0.05);
        transform: translateY(-3px);
    }}

    .unit-header {{
        background: rgba(56, 189, 248, 0.2);
        color: #38bdf8;
        font-size: 0.7rem;
        font-weight: 800;
        padding: 5px;
        text-align: center;
        border-bottom: 1px solid rgba(56, 189, 248, 0.1);
    }}

    .unit-body {{
        padding: 12px 8px;
        text-align: center;
        flex-grow: 1;
    }}
    
    .unit-color {{
        font-size: 0.95rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 8px;
    }}

    .unit-footer {{
        padding: 6px;
        background: rgba(255, 255, 255, 0.02);
        display: flex;
        flex-wrap: wrap;
        gap: 4px;
        justify-content: center;
    }}
    
    .size-tag {{
        font-size: 0.7rem;
        color: #94a3b8;
        background: rgba(255,255,255,0.06);
        padding: 1px 6px;
        border-radius: 4px;
    }}
    .size-tag b {{ color: #38bdf8; }}
    </style>
    
    <div class="hero-container">
        <h1 class="grand-title">数据矩阵看板</h1>
    </div>
    """, unsafe_allow_html=True)

# --- 2. 解析逻辑 (稳定版) ---
def process_sku_logic(uploaded_file):
    COLOR_REG = r'(?i)Color[:：\s]*([a-zA-Z0-9\-_/]+)'
    SIZE_REG = r'(?i)Size[:：\s]*([a-zA-Z0-9\-\s/]+?)(?=\s*(?:Color|Size|$|[,;，；]))'
    SIZE_MAP = {'HIGH ANKLE SOCKS': 'L', 'KNEE-HIGH SOCKS': 'M'}
    df = pd.read_excel(uploaded_file, engine='openpyxl')
    col_a, col_c, col_g, col_i = df.columns[0], df.columns[2], df.columns[6], df.columns[8]
    all_normal_data, all_error_rows = [], []
    for index, row in df.iterrows():
        c_raw = str(row[col_c]).strip()
        if not c_raw or c_raw == 'nan': continue
        if ';' in c_raw or '；' in c_raw:
            all_error_rows.append({'行号': index+2, '订单编号': row[col_a], '原因': "复合品类"})
            continue
        cat = c_raw.split(' ')[0].upper()
        if cat.startswith('WZ'): cat = 'WZ'
        g_text, i_val = str(row[col_g]), str(row[col_i])
        i_qty = int(re.findall(r'\d+', i_val)[0]) if re.findall(r'\d+', i_val) else 0
        chunks = re.split(r'[;；]', g_text)
        data_pairs = []
        for chunk in chunks:
            chunk = chunk.strip()
            if not chunk: continue
            c_match, s_match = re.search(COLOR_REG, chunk), re.search(SIZE_REG, chunk)
            if c_match:
                color_val = c_match.group(1).strip().upper()
                raw_size = s_match.group(1).strip().upper() if s_match else ""
                data_pairs.append((color_val, SIZE_MAP.get(raw_size, raw_size)))
        if len(data_pairs) == i_qty and i_qty > 0:
            for c_val, s_val in data_pairs: all_normal_data.append({'Category': cat, 'Color': c_val, 'Size': s_val})
        else:
            all_error_rows.append({'行号': index+2, '订单编号': row[col_a], '原因': f"不匹配({len(data_pairs)}/{i_qty})"})
    return pd.DataFrame(all_normal_data), pd.DataFrame(all_error_rows)

# --- 3. 渲染 ---
uploaded_file = st.file_uploader("", type=["xlsx"])

if uploaded_file:
    final_df, error_df = process_sku_logic(uploaded_file)
    tab1, tab2 = st.tabs(["💎 汇总矩阵", "📡 异常监控"])

    with tab1:
        if not final_df.empty:
            final_df = final_df.sort_values(by=['Category', 'Color'])
            groups = final_df.groupby(['Category', 'Color'])
            
            # --- 关键改动：先拼接完整 HTML 再一次性输出 ---
            matrix_html = '<div class="matrix-wrapper">'
            
            for (cat, clr), group in groups:
                size_counts = group['Size'].value_counts()
                size_html = "".join([f'<div class="size-tag">{s if s!="" else "FREE"} <b>×{q}</b></div>' for s, q in size_counts.items()])
                
                matrix_html += f"""
                    <div class="grid-unit">
                        <div class="unit-header">{cat}</div>
                        <div class="unit-body">
                            <div class="unit-color">{clr}</div>
                        </div>
                        <div class="unit-footer">
                            {size_html}
                        </div>
                    </div>
                """
            
            matrix_html += '</div>'
            st.markdown(matrix_html, unsafe_allow_html=True)
        
        st.button("↺ 刷新数据")

    with tab2:
        if not error_df.empty:
            st.table(error_df)
        else:
            st.success("无异常")
