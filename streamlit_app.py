import streamlit as st
import pandas as pd
import re
import io
from openpyxl.styles import PatternFill, Alignment, Border, Side

# --- 1. 页面配置 ---
st.set_page_config(page_title="SKU汇总工具", page_icon="🚀", layout="centered")

## ----------------- 用户名锁定 ----------------- ##
GITHUB_USERNAME = "GianTakeshi" 
## --------------------------------------------- ##

st.markdown(f"""
    <style>
    /* 全局背景：加深径向渐变，增强对比度 */
    .stApp {{
        background: radial-gradient(circle at 50% 50%, #1e293b, #010409);
        color: #ffffff;
    }}
    header {{visibility: hidden;}}

    /* --- 左上角 GianTakeshi 个人面板 --- */
    .user-profile {{
        position: fixed;
        top: 25px;
        left: 25px;
        display: flex;
        align-items: center;
        gap: 12px;
        z-index: 9999;
        background: rgba(255, 255, 255, 0.05); /* 玻璃底色 */
        padding: 6px 16px 6px 6px;
        border-radius: 50px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(15px); /* 核心磨砂效果 */
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
    }}
    .avatar {{
        width: 38px;
        height: 38px;
        border-radius: 50%;
        border: 2px solid #38bdf8;
        object-fit: cover;
    }}
    .user-name {{ font-weight: 700; font-size: 0.9rem; color: #ffffff; }}
    .user-status {{ font-size: 0.65rem; color: #10b981; font-weight: bold; }}

    /* 标题美化 */
    .hero-section {{ text-align: center; padding-top: 50px; margin-bottom: 40px; }}
    .hero-title {{
        font-size: 4.2rem !important;
        font-weight: 800;
        background: linear-gradient(to bottom, #ffffff, #64748b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    .hero-subtitle {{
        font-size: 2.6rem !important;
        font-weight: 700;
        color: #38bdf8;
        margin-top: -10px;
        text-shadow: 0 0 20px rgba(56, 189, 248, 0.3);
    }}

    /* --- 核心升级：上传框磨砂玻璃化 --- */
    .stFileUploader section {{
        background: rgba(255, 255, 255, 0.03) !important; /* 极透底色 */
        backdrop-filter: blur(20px) !important; /* 更强烈的模糊 */
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        border-radius: 30px !important;
        min-height: 280px;
        display: flex;
        justify-content: center;
        align-items: center;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
        transition: all 0.4s ease;
    }}
    
    .stFileUploader section:hover {{
        background: rgba(255, 255, 255, 0.07) !important;
        border-color: #38bdf8 !important;
        transform: translateY(-5px); /* 悬浮动效 */
    }}

    /* 强制汉化文字 */
    [data-testid="stFileUploadDropzone"] > div {{ color: transparent !important; }}
    [data-testid="stFileUploadDropzone"]::before {{
        content: "拖拽文件到这里";
        position: absolute; top: 40%; color: #ffffff; font-size: 1.4rem; font-weight: bold;
    }}
    [data-testid="stFileUploadDropzone"]::after {{
        content: "支持 XLSX 报表 | 最大 200MB";
        position: absolute; top: 55%; color: #94a3b8; font-size: 0.9rem;
    }}
    
    /* 汉化按钮 */
    [data-testid="stFileUploadDropzone"] button {{
        color: transparent !important;
        background: #38bdf8 !important;
        border-radius: 12px !important;
        width: 150px; height: 48px;
    }}
    [data-testid="stFileUploadDropzone"] button::after {{
        content: "选择文件";
        position: absolute; left: 0; width: 100%; height: 100%;
        display: flex; align-items: center; justify-content: center;
        color: #000000 !important; font-weight: 800; visibility: visible;
    }}

    /* 底部美化 */
    .footer {{ text-align: center; margin-top: 100px; color: rgba(148, 163, 184, 0.4); font-size: 0.8rem; letter-spacing: 2px; }}
    </style>
    
    <div class="user-profile">
        <img src="https://avatars.githubusercontent.com/{GITHUB_USERNAME}" class="avatar">
        <div class="user-info">
            <span class="user-name">{GITHUB_USERNAME}</span>
            <span class="user-status">● 已连接</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 数据处理逻辑 (保持不变) ---
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

# --- 布局 ---
st.markdown("<div class='hero-section'>", unsafe_allow_html=True)
st.markdown("<h1 class='hero-title'>智能商品</h1>", unsafe_allow_html=True)
st.markdown("<h1 class='hero-subtitle'>属性汇总大师 🚀</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #64748b; font-size: 1.1rem;'>GianTakeshi 专属自动化工作台</p>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("", type=["xlsx"])

if uploaded_file:
    with st.spinner('⚡ 正在穿透玻璃面板处理数据...'):
        final_df = process_sku_data(uploaded_file)
        if not final_df.empty:
            st.toast("✅ 数据处理完成！")
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                final_df.to_excel(writer, index=False, sheet_name='汇总')
            st.markdown("<br>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.download_button("📥 立即获取汇总报表", output.getvalue(), f"汇总_{uploaded_file.name}", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        else:
            st.error("未识别到 SKU 数据")

st.markdown("<div class='footer'>UI CRAFTED WITH GLASSMORPHISM | 2024</div>", unsafe_allow_html=True)
