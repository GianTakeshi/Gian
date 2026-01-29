import streamlit as st
import pandas as pd
import re
import time

# --- 1. 极致大气 UI 设计 ---
st.set_page_config(page_title="GianTakeshi | Data Engine", page_icon="🚀", layout="wide")

GITHUB_USERNAME = "GianTakeshi" 

st.markdown(f"""
    <style>
    .stApp {{ background: radial-gradient(circle at 50% 50%, #1e293b, #010409); color: #ffffff; }}
    header {{visibility: hidden;}}

    /* --- 顶级大气标题样式 --- */
    .hero-container {{
        text-align: center;
        padding: 60px 0 40px 0;
        background: transparent;
    }}
    .grand-title {{
        font-family: 'Inter', 'Segoe UI', sans-serif;
        font-size: 5.5rem !important; /* 超大字号 */
        font-weight: 900;
        letter-spacing: 15px; /* 极宽间距，大气感来源 */
        margin: 0;
        background: linear-gradient(to bottom, #ffffff 30%, #38bdf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 10px 20px rgba(56, 189, 248, 0.3));
        text-transform: uppercase;
    }}
    .grand-subtitle {{
        font-size: 1.2rem;
        letter-spacing: 8px;
        color: rgba(148, 163, 184, 0.8);
        margin-top: -10px;
        font-weight: 300;
    }}

    /* 结果面板 */
    .result-card {{
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 24px;
        padding: 25px;
    }}
    .category-title {{ 
        color: #38bdf8; font-size: 1.6rem; font-weight: 800; 
        border-left: 6px solid #38bdf8; padding-left: 20px; margin-bottom: 20px; 
    }}
    
    /* 异常卡片样式 */
    .error-item {{
        background: rgba(245, 158, 11, 0.05);
        border: 1px solid rgba(245, 158, 11, 0.2);
        border-radius: 15px;
        padding: 18px;
        margin-bottom: 12px;
    }}

    /* 左上角头像面板 */
    .user-profile {{
        position: fixed; top: 25px; left: 25px; display: flex; align-items: center; gap: 12px; z-index: 9999;
        background: rgba(255, 255, 255, 0.05); padding: 8px 18px 8px 8px; border-radius: 50px;
        border: 1px solid rgba(56, 189, 248, 0.3); backdrop-filter: blur(10px);
    }}
    .avatar {{ width: 42px; height: 42px; border-radius: 50%; border: 2px solid #38bdf8; object-fit: cover; }}
    .version-tag {{ font-size: 0.7rem; color: #38bdf8; font-weight: bold; letter-spacing: 1px; }}
    </style>
    
    <div class="user-profile">
        <img src="https://avatars.githubusercontent.com/{GITHUB_USERNAME}" class="avatar">
        <div style="display: flex; flex-direction: column;">
            <span style="font-weight:800; font-size:1rem; color: #ffffff;">{GITHUB_USERNAME}</span>
            <span class="version-tag">● 测试版 V0.3</span>
        </div>
    </div>

    <div class="hero-container">
        <h1 class="grand-title">智能数据看板</h1>
        <p class="grand-subtitle">INTELLIGENT DATA ENGINE</p>
    </div>
    """, unsafe_allow_html=True)

# --- 2. 核心逻辑 (保持不变) ---
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
            all_error_rows.append({'行号': index + 2, '订单编号': row[col_a], '品名': cat, '原因': f"解析({len(data_pairs)})≠购买({i_qty})", '原始属性': g_text})
    return pd.DataFrame(all_normal_data), pd.DataFrame(all_error_rows)

# --- 3. 页面渲染 ---
uploaded_file = st.file_uploader("", type=["xlsx"])

if uploaded_file:
    with st.spinner('ENGINE STARTING...'):
        final_df, error_df = process_sku_logic(uploaded_file)
    
    tab1, tab2 = st.tabs(["✨ 核心汇总结果", "🚩 异常实时监控"])

    with tab1:
        if not final_df.empty:
            categories = sorted(final_df['Category'].unique())
            for cat in categories:
                st.markdown(f'<div class="category-title">{cat}</div>', unsafe_allow_html=True)
                cat_data = final_df[final_df['Category'] == cat]
                color_groups = cat_data.groupby('Color')
                for clr, group in color_groups:
                    size_counts = group['Size'].value_counts()
                    tags = " ".join([f'<span style="background:rgba(56,189,248,0.15); border:1px solid rgba(56,189,248,0.3); color:#38bdf8; padding:3px 12px; border-radius:8px; margin-right:8px; font-weight:bold;">{s if s!="" else "FREE"} *{q}</span>' for s, q in size_counts.items()])
                    st.markdown(f"<div style='margin-bottom:12px;'><b style='color:#ffffff; font-size:1.1rem; margin-right:15px;'>{clr}</b> {tags}</div>", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

    with tab2:
        if not error_df.empty:
            for _, err in error_df.iterrows():
                st.markdown(f"""
                <div class="error-item">
                    <span class="error-label">ENTRY LINE: {err['行号']}</span>
                    <span style="color:#f59e0b; font-weight:bold; float:right;">{err['原因']}</span>
                    <div style="margin-top:10px; font-size:0.95rem; color:rgba(255,255,255,0.7);">
                        <b>ID:</b> {err['订单编号']} | <b>RAW:</b> <span style="font-family:monospace; color:#94a3b8;">{err['原始属性']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("SYSTEM SECURE: NO ANOMALIES DETECTED.")

st.markdown("<div style='text-align:center; margin-top:60px; color:rgba(148,163,184,0.2); letter-spacing:5px; font-size:0.7rem;'>GIAN TAKESHI SYSTEM CORE | PREMIUM EDITION</div>", unsafe_allow_html=True)
