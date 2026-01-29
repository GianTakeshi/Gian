import streamlit as st
import pandas as pd
import re
import io
import plotly.express as px
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
    /* 隐藏默认页眉 */
    header {visibility: hidden;}
    
    /* 自定义大标题 */
    .hero-title {
        font-size: 3.5rem !important;
        font-weight: 800;
        background: linear-gradient(to right, #ffffff, #94a3b8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: -10px;
    }
    .hero-subtitle {
        font-size: 2.5rem !important;
        font-weight: 700;
        color: #38bdf8; 
        margin-bottom: 1.5rem;
    }
    .hero-desc {
        color: #94a3b8;
        font-size: 1.1rem;
        line-height: 1.6;
        margin-bottom: 2rem;
    }

    /* 上传组件样式美化 */
    .stFileUploader section {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 2px dashed #38bdf8 !important;
        border-radius: 15px !important;
        padding: 20px !important;
    }

    /* 底部统计栏 */
    .stat-container {
        display: flex;
        justify-content: space-between;
        margin-top: 60px;
        border-top: 1px solid rgba(255,255,255,0.1);
        padding-top: 30px;
    }
    .stat-box { text-align: center; flex: 1; }
    .stat-val { font-size: 1.8rem; font-weight: bold; color: #ffffff; margin-bottom: 5px; }
    .stat-label { color: #64748b; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 数据处理核心函数 ---
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

# --- 3. 页面布局排版 ---
st.markdown("✨ **Smart Tools** &nbsp;&nbsp;&nbsp;&nbsp; Features &nbsp;&nbsp;&nbsp;&nbsp; Blog &nbsp;&nbsp;&nbsp;&nbsp; Pricing")

col_left, col_right = st.columns([1, 1.2], gap="large")

with col_left:
    st.markdown("<div style='margin-top: 70px;'></div>", unsafe_allow_html=True)
    st.markdown("<h1 class='hero-title'>智能商品</h1>", unsafe_allow_html=True)
    st.markdown("<h1 class='hero-subtitle'>属性汇总大师 🚀</h1>", unsafe_allow_html=True)
    st.markdown("""
        <p class='hero-desc'>
        We are bringing data processing to a new level.<br>
        一键解析 SKU 属性，告别繁琐的人工核对，生成精美汇总报表。
        </p>
    """, unsafe_allow_html=True)
    
    # 文件上传
    uploaded_file = st.file_uploader("", type=["xlsx"])
    
    if uploaded_file:
        final_df = process_sku_data(uploaded_file)
        if not final_df.empty:
            st.success("✅ 数据解析成功！")
            
            # 生成 Excel 下载包
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                final_df.to_excel(writer, index=False, sheet_name='SKU汇总')
            
            st.download_button(
                label="📥 立即获取美化报表",
                data=output.getvalue(),
                file_name=f"汇总_{uploaded_file.name}",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

with col_right:
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
    if uploaded_file and 'final_df' in locals() and not final_df.empty:
        # 实时生成柱状图
        fig_df = final_df['Category'].value_counts().reset_index()
        fig_df.columns = ['Category', 'Count']
        fig = px.bar(fig_df, x='Category', y='Count', 
                     color='Count',
                     template="plotly_dark",
                     color_continuous_scale=['#38bdf8', '#818cf8'])
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', 
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=20, b=20, l=20, r=20),
            xaxis_title="商品类别",
            yaxis_title="SKU 数量"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        # 未上传时的模拟图表
        st.markdown("<p style='text-align:center; color:#64748b; margin-bottom:0;'>等待数据上传分析...</p>", unsafe_allow_html=True)
        dummy_df = pd.DataFrame({'Category': ['WZ', 'Clothing', 'Shoes', 'Socks'], 'Count': [25, 40, 20, 55]})
        fig = px.bar(dummy_df, x='Category', y='Count', template="plotly_dark")
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        # 修复位置：透明度放在 traces 里
        fig.update_traces(marker_color='#38bdf8', marker_opacity=0.2)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# --- 4. 底部展示区 ---
st.markdown("""
    <div class='stat-container'>
        <div class='stat-box'><p class='stat-val'>Earn More</p><p class='stat-label'>快速处理</p></div>
        <div class='stat-box'><p class='stat-val'>10M +</p><p class='stat-label'>数据容量</p></div>
        <div class='stat-box'><p class='stat-val'>08 +</p><p class='stat-label'>报表美化</p></div>
        <div class='stat-box'><p class='stat-val'>08 +</p><p class='stat-label'>智能分析</p></div>
    </div>
    """, unsafe_allow_html=True)
