import streamlit as st
import pandas as pd
import re
import io
from openpyxl.styles import PatternFill, Alignment, Border, Side

# --- 1. 页面配置 ---
st.set_page_config(page_title="SKU汇总工具", page_icon="🚀", layout="centered")

## ----------------- GitHub 用户名设置 ----------------- ##
GITHUB_USERNAME = "gian-code" # <-- 宝宝，这里填入你的 GitHub 用户名
## --------------------------------------------------- ##

st.markdown(f"""
    <style>
    /* 全局背景 */
    .stApp {{
        background: radial-gradient(circle at 50% 50%, #1e293b, #020617);
        color: #ffffff;
    }}
    header {{visibility: hidden;}}

    /* --- 左上角头像样式 --- */
    .user-profile {{
        position: fixed;
        top: 20px;
        left: 20px;
        display: flex;
        align-items: center;
        gap: 12px;
        z-index: 999;
        background: rgba(255, 255, 255, 0.05);
        padding: 8px 15px;
        border-radius: 50px;
        border: 1px solid rgba(56, 189, 248, 0.2);
        backdrop-filter: blur(10px);
    }}
    .avatar {{
        width: 35px;
        height: 35px;
        border-radius: 50%;
        border: 2px solid #38bdf8;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.5);
    }}
    .user-name {{
        font-weight: 600;
        font-size: 0.9rem;
        color: #e2e8f0;
    }}

    /* 标题部分 */
    .hero-section {{
        text-align: center;
        padding-top: 60px;
        margin-bottom: 40px;
    }}
    .hero-title {{
        font-size: 4rem !important;
        font-weight: 800;
        background: linear-gradient(to bottom, #ffffff, #94a3b8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    .hero-subtitle {{
        font-size: 2.5rem !important;
        font-weight: 700;
        color: #38bdf8;
        margin-top: -10px;
    }}

    /* --- 终极汉化方案 --- */
    [data-testid="stFileUploadDropzone"] > div {{ color: transparent !important; }}
    [data-testid="stFileUploadDropzone"] button {{
        color: transparent !important;
        background-color: #38bdf8 !important;
        border: none !important;
        position: relative;
        width: 140px;
        height: 45px;
    }}
    [data-testid="stFileUploadDropzone"]::before {{
        content: "请将 Excel 文件拖拽至此处";
        position: absolute; top: 40%; left: 50%; transform: translate(-50%, -50%);
        color: #ffffff !important; font-size: 1.3rem; font-weight: bold; z-index: 1;
    }}
    [data-testid="stFileUploadDropzone"]::after {{
        content: "支持 XLSX 格式 | 最大 200MB";
        position: absolute; top: 55%; left: 50%; transform: translate(-50%, -50%);
        color: #94a3b8 !important; font-size: 0.9rem; z-index: 1;
    }}
    [data-testid="stFileUploadDropzone"] button::after {{
        content: "选择文件";
        position: absolute; left: 0; top: 0; width: 100%; height: 100%;
        display: flex; align-items: center; justify-content: center;
        color: #000000 !important; font-weight: bold; visibility: visible;
    }}
    .stFileUploader section {{
        background: rgba(255, 255, 255, 0.05) !important;
        border: 2px dashed #38bdf8 !important;
        border-radius: 24px !important;
        min-height: 250px;
        display: flex; justify-content: center; align-items: center;
    }}

    .footer {{
        text-align: center;
        margin-top: 100px;
        color: rgba(71, 85, 105, 0.6);
        font-size: 0.8rem;
    }}
    </style>
    
    <div class="user-profile">
        <img src="https://github.com/{GITHUB_USERNAME}.png" class="avatar" alt="Avatar">
        <span class="user-name">{GITHUB_USERNAME}</span>
    </div>
    """, unsafe_allow_html=True)

# --- 2. 逻辑函数 ---
def process_sku_data(uploaded_file):
    COLOR_REG = r'(?i)Color[:：\s]*([a-zA-Z0-9\-_/]+)'
    SIZE_REG = r'(?i)Size[:：\s]*([a-zA-Z0-9\-\s/]+?)(?=\s*(?:Color|Size|$|[,，;；]))'
    SIZE_MAP = {'HIGH ANKLE SOCKS': 'L', 'KNEE-HIGH SOCKS': 'M'}
    df = pd.read_excel(uploaded_file, engine='openpyxl')
    all_normal_data = []
    for _, row in df.iterrows():
        c_raw = str(row[df.columns[2]]).strip()
        if not c_raw or c_raw == 'nan': continue
        cat = c_raw.split(' ')[0].upper()
        if cat.startswith('WZ'): cat = 'WZ'
        qty_match = re.findall(r'\d+', str(row[df.columns[8]]))
        qty = int(qty_match[0]) if qty_match else 0
        chunks = re.split(r'[;；,，\n]', str(row[df.columns[6]]))
        pairs = []
        for chunk in chunks:
            c_m = re.search(COLOR_REG, chunk)
            s_m = re.search(SIZE_REG, chunk)
            if c_m:
                cv = c_m.group(1).strip().upper()
                sv = s_m.group(1).strip().upper() if s_m else ""
                pairs.append((cv, SIZE_MAP.get(sv, sv)))
        if len(pairs) == qty and qty > 0:
            for cv, sv in pairs:
                all_normal_data.append({'Category': cat, 'Color': cv, 'Size': sv})
    return pd.DataFrame(all_normal_data)

# --- 3. 布局 ---
st.markdown("<div class='hero-section'>", unsafe_allow_html=True)
st.markdown("<h1 class='hero-title'>智能商品</h1>", unsafe_allow_html=True)
st.markdown("<h1 class='hero-subtitle'>属性汇总大师 🚀</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #94a3b8; font-size: 1.1rem;'>专业的 SKU 数据自动化处理工具</p>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("", type=["xlsx"])

if uploaded_file:
    with st.spinner('⚡ 解析中...'):
        final_df = process_sku_data(uploaded_file)
        if not final_df.empty:
            st.toast("✅ 完成！")
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                final_df.to_excel(writer, index=False, sheet_name='汇总')
            
            st.markdown("<br>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.download_button("📥 立即下载汇总表", output.getvalue(), f"汇总_{uploaded_file.name}", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        else:
            st.error("未识别到 SKU 数据")

st.markdown("<div class='footer'>高效工作流 | 纯净中文版</div>", unsafe_allow_html=True)
