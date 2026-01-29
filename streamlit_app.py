import streamlit as st
import pandas as pd
import re

# --- 1. UI 配置与悬浮面板 ---
st.set_page_config(page_title="GianTakeshi | Data System", page_icon="🚀", layout="wide")

GITHUB_USERNAME = "GianTakeshi" 
BASE_URL = "https://inflyway.com/kamelnet/#/kn/fly-link/orders/detail?id="

st.markdown(f"""
    <style>
    .stApp {{ background: radial-gradient(circle at 50% 50%, #0f172a, #020617); color: #ffffff; }}
    header {{visibility: hidden;}}

    /* 固定悬浮面板 */
    .user-profile {{
        position: fixed; top: 25px; left: 25px; display: flex; align-items: center; gap: 12px; z-index: 1000000; 
        background: rgba(255, 255, 255, 0.05); padding: 6px 16px 6px 6px; border-radius: 50px;
        border: 1px solid rgba(56, 189, 248, 0.3); backdrop-filter: blur(15px);
    }}
    .avatar {{ width: 40px; height: 40px; border-radius: 50%; border: 2px solid #38bdf8; object-fit: cover; }}
    .user-name {{ font-weight: 700; font-size: 0.95rem; color: #ffffff; }}
    .user-status {{ font-size: 0.65rem; color: #10b981; font-weight: bold; }}

    /* 大气标题 */
    .hero-container {{ text-align: center; padding: 100px 0 40px 0; }}
    .grand-title {{
        font-family: 'Inter', sans-serif; font-size: 5rem !important; font-weight: 900; letter-spacing: 12px;
        background: linear-gradient(to bottom, #ffffff 40%, #38bdf8 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }}
    
    /* --- 毛玻璃卡片网格 --- */
    .grid-container {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
        gap: 25px;
        padding: 20px 0;
    }}
    
    .glass-card {{
        position: relative;
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 0; /* 改为0，内部单独控制间距 */
        overflow: hidden;
        transition: all 0.3s ease;
        display: flex;
        flex-direction: column;
        min-height: 180px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }}
    
    .glass-card:hover {{
        border-color: rgba(56, 189, 248, 0.6);
        background: rgba(255, 255, 255, 0.07);
        transform: translateY(-8px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5);
    }}

    /* --- 加大显眼的类目顶部条 --- */
    .card-header {{
        background: rgba(56, 189, 248, 0.15);
        padding: 8px 15px;
        text-align: center;
        border-bottom: 1px solid rgba(56, 189, 248, 0.2);
    }}
    .card-cat {{
        font-size: 0.9rem; /* 字体加大 */
        font-weight: 900;
        color: #38bdf8;
        text-transform: uppercase;
        letter-spacing: 3px; /* 字间距拉开，更显眼 */
        text-shadow: 0 0 10px rgba(56, 189, 248, 0.5);
    }}

    /* 中间内容区 */
    .card-body {{
        padding: 20px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        flex-grow: 1;
    }}

    .card-color {{
        font-size: 1.4rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 12px;
        text-align: center;
    }}

    .card-sizes {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        justify-content: center;
    }}
    
    .size-pill {{
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 4px 12px;
        border-radius: 10px;
        font-size: 0.85rem;
        color: #f1f5f9;
    }}

    .sn-button {{
        display: inline-block; padding: 4px 14px; background: rgba(56, 189, 248, 0.15);
        color: #38bdf8 !important; border: 1px solid rgba(56, 189, 248, 0.4);
        border-radius: 20px; text-decoration: none !important; font-size: 0.8rem; font-weight: 600;
    }}
    </style>
    
    <div class="user-profile">
        <img src="https://avatars.githubusercontent.com/{GITHUB_USERNAME}" class="avatar">
        <div class="user-info">
            <div class="user-name">{GITHUB_USERNAME}</div>
            <div class="user-status">● 测试版 V0.3</div>
        </div>
    </div>

    <div class="hero-container">
        <h1 class="grand-title">属性解析中枢</h1>
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

# --- 3. 动态渲染 ---
upload_container = st.empty()
uploaded_file = upload_container.file_uploader("", type=["xlsx"])

if uploaded_file:
    upload_container.empty()
    with st.spinner('同步矩阵架构...'):
        final_df, error_df = process_sku_logic(uploaded_file)
    
    tab1, tab2 = st.tabs(["💎 结构化属性汇总", "📡 实时异常捕获"])

    with tab1:
        if not final_df.empty:
            st.markdown('<div class="grid-container">', unsafe_allow_html=True)
            
            final_df = final_df.sort_values(by=['Category', 'Color'])
            unique_color_groups = final_df.groupby(['Category', 'Color'])
            
            for (cat, clr), group in unique_color_groups:
                size_counts = group['Size'].value_counts()
                size_html = "".join([f'<div class="size-pill">{s if s!="" else "FREE"} <b style="color:#38bdf8;">× {q}</b></div>' for s, q in size_counts.items()])
                
                st.markdown(f"""
                    <div class="glass-card">
                        <div class="card-header">
                            <div class="card-cat">{cat}</div>
                        </div>
                        <div class="card-body">
                            <div class="card-color">{clr}</div>
                            <div class="card-sizes">{size_html}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.button("↺ 重新部署数据源", on_click=lambda: st.rerun())

    with tab2:
        if not error_df.empty:
            for _, err in error_df.iterrows():
                sn_val, full_link = str(err['订单编号']), f"{BASE_URL}{err['订单编号']}"
                st.markdown(f"""
                <div style="background:rgba(245,158,11,0.03); border:1px solid rgba(245,158,11,0.2); border-radius:15px; padding:18px; margin-bottom:12px; backdrop-filter: blur(10px);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div><span style="color:#f59e0b; font-weight:bold;">LINE: {err['行号']}</span> <span style="margin-left:15px;">{err['原因']}</span></div>
                        <a href="{full_link}" target="_blank" class="sn-button">SN: {sn_val}</a>
                    </div>
                    <div style="margin-top:10px; font-size:0.85rem; color:#94a3b8; font-family: monospace;">{err['原始属性']}</div>
                </div>
                """, unsafe_allow_html=True)

st.markdown("<div style='height:100px;'></div>", unsafe_allow_html=True)
