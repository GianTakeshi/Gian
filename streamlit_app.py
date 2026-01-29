import streamlit as st
import pandas as pd
import re

# --- 1. UI 配置与全局样式 ---
st.set_page_config(page_title="GianTakeshi | Matrix Hub", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    .stApp { background: #020617; color: #ffffff; }
    header { visibility: hidden; }

    /* 单个九宫格单元的样式 */
    .grid-unit {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        transition: all 0.2s ease;
        margin-bottom: 15px; /* 行间距 */
        height: 140px; /* 固定高度确保整齐 */
    }
    
    .grid-unit:hover {
        border-color: #38bdf8;
        background: rgba(56, 189, 248, 0.05);
        transform: translateY(-3px);
    }

    .unit-header {
        background: rgba(56, 189, 248, 0.2);
        color: #38bdf8;
        font-size: 0.7rem;
        font-weight: 800;
        padding: 6px;
        text-align: center;
        text-transform: uppercase;
    }

    .unit-body {
        padding: 10px;
        text-align: center;
        flex-grow: 1;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .unit-color {
        font-size: 0.9rem;
        font-weight: 700;
        color: #ffffff;
    }

    .unit-footer {
        padding: 6px;
        background: rgba(255, 255, 255, 0.02);
        display: flex;
        flex-wrap: wrap;
        gap: 4px;
        justify-content: center;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .size-tag {
        font-size: 0.65rem;
        color: #94a3b8;
        background: rgba(255,255,255,0.06);
        padding: 1px 5px;
        border-radius: 4px;
    }
    .size-tag b { color: #38bdf8; }
    </style>
""", unsafe_allow_html=True)

# --- 2. 核心逻辑 ---
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
            for c_val, s_val in data_pairs:
                all_normal_data.append({'Category': cat, 'Color': c_val, 'Size': s_val})
        else:
            all_error_rows.append({'行号': index+2, '订单编号': row[col_a], '原因': '校验失败'})
            
    return pd.DataFrame(all_normal_data), pd.DataFrame(all_error_rows)

# --- 3. 界面展示 ---
st.title("🚀 数据矩阵中心")
uploaded_file = st.file_uploader("上传您的数据源", type=["xlsx"])

if uploaded_file:
    final_df, error_df = process_sku_logic(uploaded_file)
    
    tab1, tab2 = st.tabs(["💎 汇总矩阵", "📡 异常监控"])

    with tab1:
        if not final_df.empty:
            final_df = final_df.sort_values(by=['Category', 'Color'])
            groups = final_df.groupby(['Category', 'Color'])
            group_list = list(groups)
            
            # --- 关键渲染：每行固定 6 列 ---
            cols_per_row = 6
            for i in range(0, len(group_list), cols_per_row):
                row_items = group_list[i : i + cols_per_row]
                cols = st.columns(cols_per_row) # 创建 6 个并排的列
                
                for idx, ((cat, clr), group) in enumerate(row_items):
                    size_counts = group['Size'].value_counts()
                    size_html = "".join([f'<div class="size-tag">{s if s!="" else "FREE"} <b>×{q}</b></div>' for s, q in size_counts.items()])
                    
                    # 在对应的列中渲染卡片
                    cols[idx].markdown(f"""
                        <div class="grid-unit">
                            <div class="unit-header">{cat}</div>
                            <div class="unit-body">
                                <div class="unit-color">{clr}</div>
                            </div>
                            <div class="unit-footer">
                                {size_html}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("解析结果为空")

    with tab2:
        st.dataframe(error_df, use_container_width=True)
