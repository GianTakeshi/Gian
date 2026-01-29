import streamlit as st
import pandas as pd
import re
import time

# --- 1. UI 重塑：真正的不随滚动条移动的悬浮面板 ---
st.set_page_config(page_title="GianTakeshi | Data Engine", page_icon="🚀", layout="wide")

GITHUB_USERNAME = "GianTakeshi" 

st.markdown(f"""
    <style>
    /* 全局背景 */
    .stApp {{ background: radial-gradient(circle at 50% 50%, #1e293b, #010409); color: #ffffff; }}
    header {{visibility: hidden;}}

    /* --- 核心：真正悬浮在最顶层的面板 --- */
    .floating-user-panel {{
        position: fixed; 
        top: 30px; 
        left: 30px; 
        z-index: 1000000; /* 极高层级，确保永远在最上方 */
        display: flex; 
        align-items: center; 
        gap: 15px;
        background: rgba(15, 23, 42, 0.6); 
        padding: 10px 20px; 
        border-radius: 60px;
        border: 1px solid rgba(56, 189, 248, 0.4); 
        backdrop-filter: blur(15px);
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
    }}
    
    /* 呼吸灯圆环代替照片 */
    .status-ring {{
        width: 12px;
        height: 12px;
        background-color: #10b981;
        border-radius: 50%;
        box-shadow: 0 0 10px #10b981, 0 0 20px #10b981;
        animation: pulse 2s infinite;
    }}
    
    @keyframes pulse {{
        0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }}
        70% {{ transform: scale(1); box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }}
        100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }}
    }}

    .user-info-text {{ display: flex; flex-direction: column; }}
    .user-name {{ font-weight: 800; font-size: 1rem; color: #ffffff; letter-spacing: 0.5px; }}
    .version-tag {{ font-size: 0.65rem; color: #38bdf8; font-weight: bold; opacity: 0.8; }}

    /* 大气标题 */
    .hero-container {{ text-align: center; padding: 100px 0 60px 0; }}
    .grand-title {{
        font-family: 'Inter', sans-serif;
        font-size: 5rem !important;
        font-weight: 900;
        letter-spacing: 12px;
        background: linear-gradient(to bottom, #ffffff 40%, #38bdf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }}
    .grand-subtitle {{ font-size: 1rem; letter-spacing: 6px; color: rgba(148, 163, 184, 0.6); }}

    /* 选项卡间距优化 */
    .stTabs {{ margin-top: 20px; }}
    </style>
    
    <div class="floating-user-panel">
        <div class="status-ring"></div>
        <div class="user-info-text">
            <div class="user-name">{GITHUB_USERNAME}</div>
            <div class="version-tag">测试版 V0.3</div>
        </div>
    </div>

    <div class="hero-container">
        <h1 class="grand-title">属性解析中枢</h1>
        <p class="grand-subtitle">CORE PROPERTY PARSING HUB</p>
    </div>
    """, unsafe_allow_html=True)

# --- 2. 核心逻辑 (保持你的源代码提取方案) ---
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
            all_error_rows.append({'行号': index + 2, '订单编号': row[col_a], '品名': c_raw, '原因': "复合品类阻断", '原始属性': str(row[col_g])})
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
            all_error_rows.append({'行号': index + 2, '订单编号': row[col_a], '品名': cat, '原因': f"校验不匹配({len(data_pairs)}/{i_qty})", '原始属性': g_text})
    return pd.DataFrame(all_normal_data), pd.DataFrame(all_error_rows)

# --- 3. 渲染 ---
uploaded_file = st.file_uploader("", type=["xlsx"])

if uploaded_file:
    with st.spinner('重构逻辑矩阵中...'):
        final_df, error_df = process_sku_logic(uploaded_file)
    
    tab1, tab2 = st.tabs(["💎 结构化属性汇总", "📡 实时异常捕获"])

    with tab1:
        if not final_df.empty:
            categories = sorted(final_df['Category'].unique())
            for cat in categories:
                st.markdown(f'<div style="color:#38bdf8; font-size:1.4rem; font-weight:800; margin:30px 0 15px 0;">◈ {cat} ◈</div>', unsafe_allow_html=True)
                cat_data = final_df[final_df['Category'] == cat]
                color_groups = cat_data.groupby('Color')
                for clr, group in color_groups:
                    size_counts = group['Size'].value_counts()
                    tags = " ".join([f'<span style="background:rgba(56,189,248,0.1); border:1px solid rgba(56,189,248,0.2); color:#ffffff; padding:4px 12px; border-radius:4px; margin-right:8px; font-family: sans-serif;">{s if s!="" else "FREE"} <b style="color:#38bdf8;">× {q}</b></span>' for s, q in size_counts.items()])
                    st.markdown(f"<div style='margin-bottom:12px; background:rgba(255,255,255,0.02); padding:12px; border-radius:12px;'><span style='color:#94a3b8; margin-right:20px; font-family:monospace; font-size:1.1rem;'>{clr}</span> {tags}</div>", unsafe_allow_html=True)
        else:
            st.info("数据链路空载。")

    with tab2:
        if not error_df.empty:
            for _, err in error_df.iterrows():
                st.markdown(f"""
                <div style="background:rgba(245,158,11,0.03); border:1px solid rgba(245,158,11,0.2); border-radius:10px; padding:15px; margin-bottom:10px;">
                    <span style="color:#f59e0b; font-weight:bold; font-size:0.8rem;">LINE: {err['行号']}</span>
                    <span style="color:#ffffff; margin-left:15px; font-weight:600;">{err['原因']}</span>
                    <div style="margin-top:8px; font-size:0.85rem; color:#64748b;">
                        <b>SN:</b> {err['订单编号']} | <b>LOG:</b> {err['原始属性']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

st.markdown("<div style='height:100px;'></div>", unsafe_allow_html=True) # 底部留白
