import streamlit as st
import pandas as pd
import re

# --- 1. UI 配置与全局样式 ---
st.set_page_config(page_title="GianTakeshi | Data Hub", page_icon="🚀", layout="wide")

GITHUB_USERNAME = "GianTakeshi" 
BASE_URL = "https://inflyway.com/kamelnet/#/kn/fly-link/orders/detail?id="

st.markdown(f"""
    <style>
    .stApp {{ background: #020617; color: #ffffff; }}
    header {{visibility: hidden;}}

    /* 固定悬浮面板 - 缩小化 */
    .user-profile {{
        position: fixed; top: 15px; left: 15px; display: flex; align-items: center; gap: 10px; z-index: 1000000; 
        background: rgba(255, 255, 255, 0.03); padding: 4px 12px; border-radius: 50px;
        border: 1px solid rgba(56, 189, 248, 0.2); backdrop-filter: blur(10px);
    }}
    .avatar {{ width: 28px; height: 28px; border-radius: 50%; border: 1.5px solid #38bdf8; }}
    .user-name {{ font-weight: 600; font-size: 0.8rem; color: #ffffff; }}

    /* 标题区域 - 紧凑化 */
    .hero-container {{ text-align: left; padding: 40px 0 20px 0; border-bottom: 1px solid rgba(255,255,255,0.05); margin-bottom: 20px; }}
    .grand-title {{
        font-size: 2.2rem !important; font-weight: 900; letter-spacing: 2px;
        color: #ffffff; margin-bottom: 5px;
    }}
    
    /* --- 核心：紧贴式横向流布局 --- */
    .tight-flow-container {{
        display: block; /* 允许内部元素流式排布 */
        width: 100%;
        line-height: 2.5; /* 控制行间距 */
    }}
    
    .glass-tag {{
        display: inline-flex;
        align-items: center;
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 6px;
        margin-right: 8px;   /* 元素之间的横向间距 */
        margin-bottom: 8px;  /* 元素之间的纵向间距 */
        overflow: hidden;
        transition: all 0.2s ease;
        vertical-align: middle;
    }}
    
    .glass-tag:hover {{
        border-color: #38bdf8;
        background: rgba(56, 189, 248, 0.1);
        transform: translateY(-1px);
    }}

    /* 侧边类目小标签 */
    .tag-cat {{
        background: rgba(56, 189, 248, 0.2);
        color: #38bdf8;
        font-size: 0.65rem;
        font-weight: 800;
        padding: 4px 8px;
        border-right: 1px solid rgba(56, 189, 248, 0.2);
        text-transform: uppercase;
    }}

    /* 颜色名称 */
    .tag-color {{
        font-size: 0.85rem;
        font-weight: 700;
        color: #f8fafc;
        padding: 4px 10px;
    }}

    /* 尺码区域 */
    .tag-sizes {{
        display: flex;
        gap: 4px;
        padding: 4px 10px 4px 0;
    }}
    
    .size-mini-pill {{
        font-size: 0.75rem;
        color: #94a3b8;
    }}
    .size-mini-pill b {{ color: #38bdf8; }}

    .sn-link {{
        color: #38bdf8; text-decoration: none; font-size: 0.8rem; border-bottom: 1px solid transparent;
    }}
    .sn-link:hover {{ border-bottom: 1px solid #38bdf8; }}
    </style>
    
    <div class="user-profile">
        <img src="https://avatars.githubusercontent.com/{GITHUB_USERNAME}" class="avatar">
        <div class="user-name">{GITHUB_USERNAME}</div>
    </div>

    <div class="hero-container">
        <h1 class="grand-title">核心属性看板</h1>
    </div>
    """, unsafe_allow_html=True)

# --- 2. 核心逻辑 (保持之前的高效逻辑) ---
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
            all_error_rows.append({'行号': index + 2, '订单编号': row[col_a], '原因': "复合品类阻断"})
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
            all_error_rows.append({'行号': index + 2, '订单编号': row[col_a], '原因': f"不匹配({len(data_pairs)}/{i_qty})"})
    return pd.DataFrame(all_normal_data), pd.DataFrame(all_error_rows)

# --- 3. 渲染逻辑 ---
upload_container = st.empty()
uploaded_file = upload_container.file_uploader("", type=["xlsx"])

if uploaded_file:
    upload_container.empty() # 解析后隐藏
    final_df, error_df = process_sku_logic(uploaded_file)
    
    tab1, tab2 = st.tabs(["💎 汇总数据", "📡 异常监控"])

    with tab1:
        if not final_df.empty:
            # 这里的 tight-flow-container 是实现“一个挨着一个”的关键
            html_content = '<div class="tight-flow-container">'
            
            final_df = final_df.sort_values(by=['Category', 'Color'])
            groups = final_df.groupby(['Category', 'Color'])
            
            for (cat, clr), group in groups:
                size_counts = group['Size'].value_counts()
                size_html = " ".join([f'<span class="size-mini-pill">{s if s!="" else "FREE"}<b>×{q}</b></span>' for s, q in size_counts.items()])
                
                html_content += f"""
                <div class="glass-tag">
                    <div class="tag-cat">{cat}</div>
                    <div class="tag-color">{clr}</div>
                    <div class="tag-sizes">{size_html}</div>
                </div>
                """
            
            html_content += '</div>'
            st.markdown(html_content, unsafe_allow_html=True)
        
        if st.button("↺ 重新上传"):
            st.rerun()

    with tab2:
        if not error_df.empty:
            for _, err in error_df.iterrows():
                full_link = f"{BASE_URL}{err['订单编号']}"
                st.markdown(f"🚩 行 {err['行号']} | {err['原因']} | <a href='{full_link}' target='_blank' class='sn-link'>查看单据 {err['订单编号']}</a>", unsafe_allow_html=True)
        else:
            st.success("暂无异常数据")

st.markdown("<div style='height:80px;'></div>", unsafe_allow_html=True)
