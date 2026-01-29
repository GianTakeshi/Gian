import streamlit as st
import pandas as pd
import re
import time

# --- 1. UI 增强 (全屏磨砂玻璃质感) ---
st.set_page_config(page_title="GianTakeshi 专属工作台", page_icon="🚀", layout="wide")

GITHUB_USERNAME = "GianTakeshi" 

st.markdown(f"""
    <style>
    .stApp {{ background: radial-gradient(circle at 50% 50%, #1e293b, #010409); color: #ffffff; }}
    header {{visibility: hidden;}}

    /* 结果面板 */
    .result-card {{
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 20px;
    }}
    .category-title {{ color: #38bdf8; font-size: 1.5rem; font-weight: 800; border-left: 5px solid #38bdf8; padding-left: 15px; margin-bottom: 15px; }}
    
    /* 异常卡片样式 */
    .error-item {{
        background: rgba(245, 158, 11, 0.08);
        border: 1px solid rgba(245, 158, 11, 0.3);
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
    }}
    .error-label {{ color: #f59e0b; font-weight: bold; font-size: 0.8rem; text-transform: uppercase; }}

    /* 左上角头像面板 - 已更新版本文字 */
    .user-profile {{
        position: fixed; top: 25px; left: 25px; display: flex; align-items: center; gap: 12px; z-index: 9999;
        background: rgba(255, 255, 255, 0.05); padding: 6px 16px 6px 6px; border-radius: 50px;
        border: 1px solid rgba(56, 189, 248, 0.3); backdrop-filter: blur(10px);
    }}
    .avatar {{ width: 38px; height: 38px; border-radius: 50%; border: 2px solid #38bdf8; object-fit: cover; }}
    .version-tag {{ font-size: 0.65rem; color: #38bdf8; font-weight: bold; letter-spacing: 0.5px; }}
    </style>
    
    <div class="user-profile">
        <img src="https://avatars.githubusercontent.com/{GITHUB_USERNAME}" class="avatar">
        <div style="display: flex; flex-direction: column;">
            <span style="font-weight:700; font-size:0.9rem; color: #ffffff;">{GITHUB_USERNAME}</span>
            <span class="version-tag">● 测试版 V0.3</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 2. 核心逻辑 (与源代码严格对齐) ---
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
            all_error_rows.append({'行号': index + 2, '订单编号': row[col_a], '品名': c_raw, '原因': "多个商品", '原始属性': str(row[col_g])})
            continue

        category_name = c_raw.split(' ')[0].upper()
        if category_name.startswith('WZ'): category_name = 'WZ'

        g_text = str(row[col_g])
        i_qty = int(re.findall(r'\d+', str(row[col_i]))[0]) if re.findall(r'\d+', str(row[col_i])) else 0

        chunks = re.split(r'[;；]', g_text)
        data_pairs = []
        for chunk in chunks:
            chunk = chunk.strip()
            if not chunk: continue
            c_match = re.search(COLOR_REG, chunk)
            s_match = re.search(SIZE_REG, chunk)
            if c_match:
                color_val = c_match.group(1).strip().upper()
                raw_size = s_match.group(1).strip().upper() if s_match else ""
                data_pairs.append((color_val, SIZE_MAP.get(raw_size, raw_size)))

        if len(data_pairs) == i_qty and i_qty > 0:
            for c_val, s_val in data_pairs:
                all_normal_data.append({'Category': category_name, 'Color': c_val, 'Size': s_val})
        else:
            all_error_rows.append({
                '行号': index + 2, 
                '订单编号': row[col_a], 
                '品名': category_name, 
                '原因': f"解析数({len(data_pairs)})≠购买数({i_qty})", 
                '原始属性': g_text
            })

    return pd.DataFrame(all_normal_data), pd.DataFrame(all_error_rows)

# --- 3. 页面渲染 ---
st.markdown("<div style='text-align:center; padding-top:30px;'><h1 style='color:#38bdf8; font-size:3rem; font-weight:800;'>智能数据看版 🚀</h1></div>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("", type=["xlsx"])

if uploaded_file:
    with st.spinner('正在使用 V0.3 引擎解析数据...'):
        final_df, error_df = process_sku_logic(uploaded_file)
    
    tab1, tab2 = st.tabs(["✨ 汇总预览", "🚩 异常工作台"])

    with tab1:
        if not final_df.empty:
            categories = sorted(final_df['Category'].unique())
            for cat in categories:
                st.markdown(f'<div class="category-title">{cat}</div>', unsafe_allow_html=True)
                cat_data = final_df[final_df['Category'] == cat]
                color_groups = cat_data.groupby('Color')
                for clr, group in color_groups:
                    size_counts = group['Size'].value_counts()
                    tags = " ".join([f'<span style="background:rgba(56,189,248,0.2); color:#38bdf8; padding:2px 8px; border-radius:5px; margin-right:5px;">{s if s!="" else "无尺码"} *{q}</span>' for s, q in size_counts.items()])
                    st.markdown(f"**Color {clr}** : {tags}", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.info("未识别到汇总数据")

    with tab2:
        if not error_df.empty:
            st.markdown(f"<p style='color:#f59e0b;'>发现 {len(error_df)} 条异常，请及时处理：</p>", unsafe_allow_html=True)
            for _, err in error_df.iterrows():
                st.markdown(f"""
                <div class="error-item">
                    <div style="display:flex; justify-content:space-between;">
                        <span class="error-label">行号: {err['行号']}</span>
                        <span style="color:#f59e0b; font-weight:bold;">{err['原因']}</span>
                    </div>
                    <div style="margin-top:5px; font-size:0.9rem;">
                        <b>订单编号:</b> {err['订单编号']} <br>
                        <b>商品名称:</b> {err['品名']} <br>
                        <b>原始 SKU 属性:</b> <span style="color:#94a3b8; font-family:monospace;">{err['原始属性']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("太棒了！测试版 V0.3 未发现任何解析异常。")

st.markdown("<div style='text-align:center; margin-top:50px; color:rgba(148,163,184,0.3);'>GianTakeshi LIVE VIEW | TEST VERSION 0.3</div>", unsafe_allow_html=True)
