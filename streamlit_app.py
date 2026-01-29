import streamlit as st
import pandas as pd
import re
import io
from openpyxl.styles import PatternFill, Alignment, Border, Side

# --- 1. 页面配置与高亮 CSS ---
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
        padding-top: 100px;
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

    /* --- 上传区域文字高亮修复 --- */
    /* 1. 修改 "Drag and drop file here" 和 "Limit 200MB" 的颜色 */
    .stFileUploader label, .stFileUploader p, .stFileUploader small {
        color: #e2e8f0 !important; /* 浅灰色/白色 */
        font-weight: 500 !important;
    }
    /* 2. 修改上传框内部的说明文字 */
    div[data-testid="stFileUploadDropzone"] div {
        color: #38bdf8 !important; /* 天蓝色 */
    }
    /* 3. 上传框背景和边框 */
    .stFileUploader section {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 2px dashed #38bdf8 !important;
        border-radius: 24px !important;
        padding: 40px !important;
    }
    /* 4. 修改已上传文件的文件名颜色 */
    .stFileUploader [data-testid="stFileUploadFileName"] {
        color: #ffffff !important;
    }

    .footer {
        text-align: center;
        margin-top: 120px;
        color: rgba(71, 85, 105, 0.5);
        font-size: 0.75rem;
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
st.markdown("<p style='color: #94a3b8; font-size: 1.1rem;'>Professional SKU Data Processor</p>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# 上传组件 - 现在的提示文字会非常清晰
uploaded_file = st.file_uploader("请上传您的 Excel 文件", type=["xlsx"])

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
            st.error("无法识别有效 SKU 数据，请检查 G 列格式。")

st.markdown("<div class='footer'>EFFICIENT WORKFLOW | POWERED BY STREAMLIT</div>", unsafe_allow_html=True)
