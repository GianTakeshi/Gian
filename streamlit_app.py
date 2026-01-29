import streamlit as st
import pandas as pd
import re

# --- 1. UI 配置与全局样式 ---
st.set_page_config(page_title="GianTakeshi | Matrix Hub", page_icon="🚀", layout="wide")

GITHUB_USERNAME = "GianTakeshi"

st.markdown(f"""
    <style>
    .stApp {{ background: #020617; color: #ffffff; }}
    header {{ visibility: hidden; }}

    /* 固定悬浮头像回归 */
    .user-profile {{
        position: fixed; top: 20px; left: 20px; display: flex; align-items: center; gap: 12px; z-index: 1000000; 
        background: rgba(255, 255, 255, 0.05); padding: 5px 15px 5px 5px; border-radius: 50px;
        border: 1px solid rgba(56, 189, 248, 0.3); backdrop-filter: blur(15px);
    }}
    .avatar {{ width: 35px; height: 35px; border-radius: 50%; border: 2px solid #38bdf8; object-fit: cover; }}
    .user-name {{ font-weight: 700; font-size: 0.85rem; color: #ffffff; }}

    /* 九宫格单元样式 */
    .grid-unit {{
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        transition: all 0.2s ease;
        margin-bottom: 10px;
        height: 130px; 
    }}
    .grid-unit:hover {{ border-color: #38bdf8; background: rgba(56, 189, 248, 0.05); transform: translateY(-3px); }}

    .unit-header {{ background: rgba(56, 189, 248, 0.2); color: #38bdf8; font-size: 0.7rem; font-weight: 800; padding: 5px; text-align: center; }}
    .unit-body {{ padding: 10px; text-align: center; flex-grow: 1; display: flex; align-items: center; justify-content: center; }}
    .unit-color {{ font-size: 0.9rem; font-weight: 700; color: #ffffff; }}
    .unit-footer {{ padding: 5px; background: rgba(255, 255, 255, 0.02); display: flex; flex-wrap: wrap; gap: 4px; justify-content: center; border-top: 1px solid rgba(255, 255, 255, 0.05); }}
    
    .size-tag {{ font-size: 0.65rem; color: #94a3b8; background: rgba(255,255,255,0.06); padding: 1px 5px; border-radius: 4px; }}
    .size-tag b {{ color: #38bdf8; }}
    </style>

    <div class="user-profile">
        <img src="https://avatars.githubusercontent.com/{GITHUB_USERNAME}" class="avatar">
        <div class="user-name">{GITHUB_USERNAME}</div>
    </div>
""", unsafe_allow_html=True)

# --- 2. 核心逻辑：严格的数据分流 ---
def process_sku_logic(uploaded_file):
    COLOR_REG = r'(?i)Color[:：\s]*([a-zA-Z0-9\-_/]+)'
    SIZE_REG = r'(?i)Size[:：\s]*([a-zA-Z0-9\-\s/]+?)(?=\s*(?:Color|Size|$|[,;，；]))'
    SIZE_MAP = {'HIGH ANKLE SOCKS': 'L', 'KNEE-HIGH SOCKS': 'M'}
    
    df = pd.read_excel(uploaded_file, engine='openpyxl')
    col_a, col_c, col_g, col_i = df.columns[0], df.columns[2], df.columns[6], df.columns[8]
    
    correct_data = [] # 存放正确的数据
    error_rows = []   # 存放异常的数据
    
    for index, row in df.iterrows():
        c_raw = str(row[col_c]).strip()
        if not c_raw or c_raw == 'nan': continue
        
        # 拦截：复合品类（包含分号）
        if ';' in c_raw or '；' in c_raw:
            error_rows.append({'行号': index+2, '订单编号': row[col_a], '原因': '复合品类拦截', '内容': c_raw})
            continue

        cat = c_raw.split(' ')[0].upper()
        if cat.startswith('WZ'): cat = 'WZ'
        
        g_text = str(row[col_g])
        i_val = str(row[col_i])
        i_qty = int(re.findall(r'\d+', i_val)[0]) if re.findall(r'\d+', i_val) else 0
        
        chunks = [c.strip() for c in re.split(r'[;；]', g_text) if c.strip()]
        data_pairs = []
        for chunk in chunks:
            c_match = re.search(COLOR_REG, chunk)
            s_match = re.search(SIZE_REG, chunk)
            if c_match:
                color_val = c_match.group(1).strip().upper()
                raw_size = s_match.group(1).strip().upper() if s_match else ""
                data_pairs.append((color_val, SIZE_MAP.get(raw_size, raw_size)))
        
        # 严格校验：解析出的对数必须等于订单声明的数量
        if len(data_pairs) == i_qty and i_qty > 0:
            for c_val, s_val in data_pairs:
                correct_data.append({'Category': cat, 'Color': c_val, 'Size': s_val})
        else:
            error_rows.append({
                '行号': index+2, 
                '订单编号': row[col_a], 
                '原因': f'数量不符(解析{len(data_pairs)}/应有{i_qty})',
                '原始属性': g_text
            })
            
    return pd.DataFrame(correct_data), pd.DataFrame(error_rows)

# --- 3. 界面展示 ---
st.markdown("<h2 style='text-align:center; margin-top:50px;'>🚀 数据矩阵看板</h2>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("", type=["xlsx"])

if uploaded_file:
    final_df, error_df = process_sku_logic(uploaded_file)
    tab1, tab2 = st.tabs(["💎 正确数据汇总", "📡 异常拦截报告"])

    with tab1:
        if not final_df.empty:
            final_df = final_df.sort_values(by=['Category', 'Color'])
            groups = list(final_df.groupby(['Category', 'Color']))
            
            # 每行 6 列渲染
            cols_per_row = 6
            for i in range(0, len(groups), cols_per_row):
                row_items = groups[i : i + cols_per_row]
                cols = st.columns(cols_per_row)
                
                for idx, ((cat, clr), group) in enumerate(row_items):
                    size_counts = group['Size'].value_counts()
                    size_html = "".join([f'<div class="size-tag">{s if s!="" else "FREE"} <b>×{q}</b></div>' for s, q in size_counts.items()])
                    
                    cols[idx].markdown(f"""
                        <div class="grid-unit">
                            <div class="unit-header">{cat}</div>
                            <div class="unit-body"><div class="unit-color">{clr}</div></div>
                            <div class="unit-footer">{size_html}</div>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("暂无有效汇总数据")

    with tab2:
        if not error_df.empty:
            st.warning(f"发现 {len(error_df)} 条异常数据，已自动从汇总中剔除：")
            st.dataframe(error_df, use_container_width=True)
        else:
            st.success("数据校验完美，无异常！")

    if st.button("↺ 重新上传数据"):
        st.rerun()
