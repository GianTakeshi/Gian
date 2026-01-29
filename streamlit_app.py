import streamlit as st
import pandas as pd
import re

# --- 1. UI 配置 ---
st.set_page_config(page_title="GianTakeshi | Data Hub", page_icon="🚀", layout="wide")

GITHUB_USERNAME = "GianTakeshi" 
BASE_URL = "https://inflyway.com/kamelnet/#/kn/fly-link/orders/detail?id="

st.markdown(f"""
    <style>
    .stApp {{ background: #020617; color: #ffffff; }}
    header {{visibility: hidden;}}

    /* 标题区域 */
    .hero-container {{ text-align: left; padding: 30px 0 10px 0; border-bottom: 1px solid rgba(255,255,255,0.05); margin-bottom: 20px; }}
    .grand-title {{ font-size: 2rem !important; font-weight: 900; color: #ffffff; }}
    
    /* 核心样式：让外层容器支持 inline 显示 */
    div[data-testid="stVerticalBlock"] > div:has(div.glass-tag) {{
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: wrap !important;
        gap: 0px !important;
    }}

    .glass-tag {{
        display: inline-flex;
        align-items: center;
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 6px;
        margin: 0 8px 8px 0; /* 紧凑间距 */
        overflow: hidden;
        transition: all 0.2s ease;
        white-space: nowrap;
    }}
    
    .glass-tag:hover {{ border-color: #38bdf8; background: rgba(56, 189, 248, 0.1); }}

    .tag-cat {{ background: rgba(56, 189, 248, 0.2); color: #38bdf8; font-size: 0.65rem; font-weight: 800; padding: 3px 8px; border-right: 1px solid rgba(56, 189, 248, 0.2); }}
    .tag-color {{ font-size: 0.8rem; font-weight: 700; color: #f8fafc; padding: 3px 10px; }}
    .tag-sizes {{ display: flex; gap: 4px; padding-right: 8px; font-size: 0.75rem; color: #94a3b8; }}
    .tag-sizes b {{ color: #38bdf8; }}

    .sn-button {{
        display: inline-block; padding: 2px 10px; background: rgba(56, 189, 248, 0.1);
        color: #38bdf8 !important; border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 10px; text-decoration: none !important; font-size: 0.75rem;
    }}
    </style>
    
    <div class="hero-container">
        <h1 class="grand-title">核心属性解析</h1>
    </div>
    """, unsafe_allow_html=True)

# --- 2. 逻辑层 (保持稳健) ---
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
            all_error_rows.append({'行号': index + 2, '订单编号': row[col_a], '原因': "复合品类"})
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
            all_error_rows.append({'行号': index + 2, '订单编号': row[col_a], '原因': f"数量错({len(data_pairs)}/{i_qty})"})
    return pd.DataFrame(all_normal_data), pd.DataFrame(all_error_rows)

# --- 3. 渲染层 ---
uploaded_file = st.file_uploader("", type=["xlsx"])

if uploaded_file:
    final_df, error_df = process_sku_logic(uploaded_file)
    tab1, tab2 = st.tabs(["💎 汇总数据", "📡 异常监控"])

    with tab1:
        if not final_df.empty:
            final_df = final_df.sort_values(by=['Category', 'Color'])
            groups = final_df.groupby(['Category', 'Color'])
            
            # 使用 container 包装，避免 st.markdown 内部解析限制
            container = st.container()
            with container:
                # 遍历显示每一个标签
                for (cat, clr), group in groups:
                    size_counts = group['Size'].value_counts()
                    size_html = " ".join([f'<span>{s if s!="" else "FREE"}<b>×{q}</b></span>' for s, q in size_counts.items()])
                    
                    st.markdown(f"""
                        <div class="glass-tag">
                            <div class="tag-cat">{cat}</div>
                            <div class="tag-color">{clr}</div>
                            <div class="tag-sizes">{size_html}</div>
                        </div>
                    """, unsafe_allow_html=True)
        
        st.button("↺ 重新解析", on_click=lambda: st.rerun())

    with tab2:
        if not error_df.empty:
            for _, err in error_df.iterrows():
                full_link = f"{BASE_URL}{err['订单编号']}"
                st.markdown(f"🚩 行 {err['行号']} | {err['原因']} | <a href='{full_link}' target='_blank' class='sn-button'>单据 {err['订单编号']}</a>", unsafe_allow_html=True)
        else:
            st.success("无异常")
