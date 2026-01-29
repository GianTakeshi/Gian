import streamlit as st
import pandas as pd
import re
import io
from openpyxl.styles import PatternFill, Alignment, Border, Side

# --- 1. 页面配置与极简深色 CSS ---
st.set_page_config(page_title="Smart Tools | SKU汇总", layout="centered") # 改为 centered 更聚拢

st.markdown("""
    <style>
    /* 全局背景：深色径向渐变，更有深度感 */
    .stApp {
        background: radial-gradient(circle at 50% 50%, #1e293b, #020617);
        color: #ffffff;
    }
    header {visibility: hidden;}
    
    /* 标题居中设计 */
    .hero-section {
        text-align: center;
        padding-top: 80px;
        margin-bottom: 40px;
    }
    .hero-title {
        font-size: 3.8rem !important;
        font-weight: 800;
        letter-spacing: -1px;
        background: linear-gradient(to bottom, #ffffff, #94a3b8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-subtitle {
        font-size: 2.2rem !important;
        font-weight: 700;
        color: #38bdf8;
        margin-top: -10px;
    }
    
    /* 磨砂玻璃上传卡片 */
    .stFileUploader section {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(12px);
        border-radius: 24px !important;
        padding: 40px !important;
        transition: all 0.4s ease;
    }
    .stFileUploader section:hover {
        border-color: #38bdf8 !important;
        background: rgba(255, 255, 255, 0.08) !important;
    }

    /* 底部统计栏 */
    .stat-container {
        display: flex;
        justify-content: space-around;
        margin-top: 80px;
        border-top: 1px solid rgba(255,255,255,0.1);
        padding-top: 40px;
    }
    .stat-box { text-align: center; }
    .stat-val { font-size: 1.6rem; font-weight: bold; color: #fff; }
    .stat-label { color: #64748b; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 2px; margin-top: 5px; }
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
# 顶部导航
st.markdown("<div style='text-align:center; padding: 20px; color: #94a3b8; font-weight: 500;'>✨ SMART TOOLS GLOBAL</div>", unsafe_allow_html=True)

# 主体内容
st.markdown("<div class='hero-section'>", unsafe_allow_html=True)
st.markdown("<h1 class='hero-title'>智能商品</h1>", unsafe_allow_html=True)
st.markdown("<h1 class='hero-subtitle'>属性汇总大师 🚀</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #64748b; font-size: 1.1rem;'>Professional SKU Data Processor for Global Business</p>", unsafe_allow_html=True)
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
            
            # 下载按钮居中处理
            col_bt1, col_bt2, col_bt3 = st.columns([1, 2, 1])
            with col_bt2:
                st.download_button(
                    label="📥 立即获取美化报表",
                    data=output.getvalue(),
                    file_name=f"汇总_{uploaded_file.name}",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        else:
            st.error("无法识别有效 SKU 数据，请检查 G 列格式。")

# 底部指标
st.markdown("""
    <div class='stat-container'>
        <div class='stat-box'><p class='stat-val'>Earn More</p><p class='stat-label'>快速处理</p></div>
        <div class='stat-box'><p class='stat-val'>10M +</p><p class='stat-label'>数据容量</p></div>
        <div class='stat-box'><p class='stat-val'>08 +</p><p class='stat-label'>报表美化</p></div>
        <div class='stat-box'><p class='stat-val'>08 +</p><p class='stat-label'>智能分析</p></div>
    </div>
    """, unsafe_allow_html=True)
