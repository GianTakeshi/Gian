import streamlit as st
import pandas as pd
import re
import io
from openpyxl.styles import PatternFill, Alignment, Border, Side

# --- 1. 页面配置与深度自定义 CSS ---
st.set_page_config(page_title="SKU汇总工具", page_icon="🚀", layout="centered")

st.markdown("""
    <style>
    /* 全局背景 */
    .stApp {
        background: radial-gradient(circle at 50% 50%, #1e293b, #020617);
        color: #ffffff;
    }
    header {visibility: hidden;}

    /* 标题部分 */
    .hero-section {
        text-align: center;
        padding-top: 80px;
        margin-bottom: 40px;
    }
    .hero-title {
        font-size: 4rem !important;
        font-weight: 800;
        background: linear-gradient(to bottom, #ffffff, #94a3b8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-subtitle {
        font-size: 2.5rem !important;
        font-weight: 700;
        color: #38bdf8;
        margin-top: -10px;
    }

    /* --- 核心修复：强制汉化并高亮上传区域 --- */
    
    /* 隐藏原本的英文文字 */
    [data-testid="stFileUploadDropzone"] div div {
        font-size: 0 !important;
    }
    [data-testid="stFileUploadDropzone"] div small {
        font-size: 0 !important;
    }

    /* 注入中文提示 - 主文字 */
    [data-testid="stFileUploadDropzone"] div div::before {
        content: "请将 Excel 文件拖拽至此处";
        font-size: 1.2rem !important;
        color: #ffffff !important;
        visibility: visible !important;
        display: block;
        margin-bottom: 10px;
    }

    /* 注入中文提示 - 副文字 */
    [data-testid="stFileUploadDropzone"] div div::after {
        content: "支持 XLSX 格式 | 最大 200MB";
        font-size: 0.9rem !important;
        color: #94a3b8 !important;
        visibility: visible !important;
        display: block;
    }

    /* 修改按钮文字（通过覆盖内部按钮样式） */
    [data-testid="stFileUploadDropzone"] button {
        border: 1px solid #38bdf8 !important;
        background-color: rgba(56, 189, 248, 0.2) !important;
        color: #ffffff !important;
    }
    [data-testid="stFileUploadDropzone"] button span::before {
        content: "选择文件";
        font-size: 1rem;
    }
    [data-testid="stFileUploadDropzone"] button span {
        font-size: 0 !important;
    }

    /* 上传框整体效果 */
    .stFileUploader section {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 2px dashed #38bdf8 !important;
        border-radius: 24px !important;
        padding: 50px 20px !important;
    }

    /* 已上传文件名 */
    [data-testid="stFileUploadFileName"] {
        color: #38bdf8 !important;
    }

    .footer {
        text-align: center;
        margin-top: 120px;
        color: rgba(71, 85, 105, 0.6);
        font-size: 0.8rem;
        letter-spacing: 2px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 核心处理函数 ---
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

# --- 3. 页面布局 ---
st.markdown("<div class='hero-section'>", unsafe_allow_html=True)
st.markdown("<h1 class='hero-title'>智能商品</h1>", unsafe_allow_html=True)
st.markdown("<h1 class='hero-subtitle'>属性汇总大师 🚀</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #94a3b8; font-size: 1.1rem;'>专业的 SKU 数据自动化处理工具</p>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# 上传组件
uploaded_file = st.file_uploader("", type=["xlsx"])

if uploaded_file:
    with st.spinner('⚡ 正在深度解析数据...'):
        final_df = process_sku_data(uploaded_file)
        if not final_df.empty:
            st.toast("✅ 数据处理完成！", icon="🎉")
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                final_df.to_excel(writer, index=False, sheet_name='SKU汇总')
            
            st.markdown("<br>", unsafe_allow_html=True)
            col_bt1, col_bt2, col_bt3 = st.columns([1, 2, 1])
            with col_bt2:
                st.download_button(
                    label="📥 立即获取汇总报表",
                    data=output.getvalue(),
                    file_name=f"汇总_{uploaded_file.name}",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        else:
            st.error("未识别到有效 SKU 数据，请检查 G 列内容。")

st.markdown("<div class='footer'>高效工作流 | 由科技驱动办公</div>", unsafe_allow_html=True)
