import streamlit as st
import pandas as pd
import re
import io
import plotly.express as px  # 用于生成右侧的科技感柱状图
from openpyxl.styles import PatternFill, Alignment, Border, Side

# --- 1. 页面配置与深色主题 CSS ---
st.set_page_config(page_title="Smart Tools | SKU汇总", layout="wide")

st.markdown("""
    <style>
    /* 全局背景：深色渐变 */
    .stApp {
        background: radial-gradient(circle at top right, #1e293b, #0f172a);
        color: #ffffff;
    }
    /* 隐藏顶部白条 */
    header {visibility: hidden;}
    
    /* 自定义大标题 */
    .hero-title {
        font-size: 3.5rem !important;
        font-weight: 800;
        background: linear-gradient(to right, #ffffff, #94a3b8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .hero-subtitle {
        font-size: 2.5rem !important;
        font-weight: 700;
        color: #38bdf8; /* 天蓝色 */
        margin-bottom: 1.5rem;
    }
    .hero-desc {
        color: #94a3b8;
        font-size: 1.1rem;
        line-height: 1.6;
        margin-bottom: 2rem;
    }
    
    /* 上传按钮模拟样式的容器 */
    .upload-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 30px;
        backdrop-filter: blur(10px);
    }

    /* 真正的上传组件样式覆盖 */
    .stFileUploader section {
        background-color: transparent !important;
        border: 2px dashed #38bdf8 !important;
        border-radius: 15px !important;
    }

    /* 底部统计栏样式 */
    .stat-box {
        text-align: center;
        padding: 20px;
    }
    .stat-val { font-size: 2rem; font-weight: bold; color: #fff; }
    .stat-label { color: #64748b; font-size: 0.9rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 核心逻辑函数 ---
def process_data(uploaded_file):
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
# 顶部 Logo 栏
st.markdown("✨ **Smart Tools** &nbsp;&nbsp; Features &nbsp;&nbsp; Pricing &nbsp;&nbsp; Blog")

# 主内容区：左文右图
col_left, col_right = st.columns([1, 1.2], gap="large")

with col_left:
    st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
    st.markdown("<h1 class='hero-title'>智能商品</h1>", unsafe_allow_html=True)
    st.markdown("<h1 class='hero-subtitle'>属性汇总大师 🚀</h1>", unsafe_allow_html=True)
    st.markdown("""
        <p class='hero-desc'>
        We are bringing data processing to a new level.<br>
        一键上传，精准解析，轻松获取美化报表。
        </p>
    """, unsafe_allow_html=True)
    
    # 上传卡片
    with st.container():
        uploaded_file = st.file_uploader("点击下方上传 Excel 插件", type=["xlsx"])
        if uploaded_file:
            st.success("文件已就绪")

with col_right:
    # 右侧放置模拟图表或实际数据预览
    if uploaded_file:
        final_df = process_data(uploaded_file)
        if not final_df.empty:
            # 生成柱状图
            fig_df = final_df['Category'].value_counts().reset_index()
            fig_df.columns = ['Category', 'Count']
            fig = px.bar(fig_df, x='Category', y='Count', 
                         color='Count', template="plotly_dark",
                         color_continuous_scale=['#38bdf8', '#818cf8'])
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                              margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("未能解析数据")
    else:
        # 默认占位图（未上传时显示）
        st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)
        dummy_df = pd.DataFrame({'Category': ['WZ', 'Clothing', 'Shoes', 'Accessories'], 'Count': [20, 45, 30, 60]})
        fig = px.bar(dummy_df, x='Category', y='Count', template="plotly_dark")
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# 底部统计信息
st.markdown("<br><br>", unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown("<div class='stat-box'><p class='stat-val'>Earn More</p><p class='stat-label'>快速处理</p></div>", unsafe_allow_html=True)
with c2: st.markdown("<div class='stat-box'><p class='stat-val'>10M +</p><p class='stat-label'>数据容量</p></div>", unsafe_allow_html=True)
with c3: st.markdown("<div class='stat-box'><p class='stat-val'>08 +</p><p class='stat-label'>报表美化</p></div>", unsafe_allow_html=True)
with c4: st.markdown("<div class='stat-box'><p class='stat-val'>08 +</p><p class='stat-label'>智能分析</p></div>", unsafe_allow_html=True)

# 处理下载逻辑
if uploaded_file and 'final_df' in locals():
    # 这里放置你之前写的 Excel 导出逻辑... (由于篇幅略，逻辑同前)
    st.download_button("📥 获取美化报表", data=b"...", file_name="result.xlsx")
