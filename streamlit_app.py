import streamlit as st
import pandas as pd
import re
import html

# --- 1. UI 配置与全局样式 ---
st.set_page_config(page_title="GianTakeshi | Matrix Hub", page_icon="🚀", layout="wide")

GITHUB_USERNAME = "GianTakeshi" 
BASE_URL = "https://inflyway.com/kamelnet/#/kn/fly-link/orders/detail?id="

st.markdown(f"""
    <style>
    /* 背景：代码2标志性的聚光灯渐变 */
    .stApp {{ background: radial-gradient(circle at 50% 50%, #1e293b, #010409); color: #ffffff; }}
    header {{visibility: hidden;}}

    /* 固定悬浮面板 */
    .user-profile {{
        position: fixed; top: 25px; left: 25px; display: flex; align-items: center; gap: 12px; z-index: 1000000; 
        background: rgba(255, 255, 255, 0.05); padding: 6px 16px 6px 6px; border-radius: 50px;
        border: 1px solid rgba(56, 189, 248, 0.3); backdrop-filter: blur(10px);
    }}
    .avatar {{ width: 40px; height: 40px; border-radius: 50%; border: 2px solid #38bdf8; object-fit: cover; }}
    .user-name {{ font-weight: 700; font-size: 0.95rem; color: #ffffff; }}
    .user-status {{ font-size: 0.65rem; color: #10b981; font-weight: bold; }}

    /* 大气标题 */
    .hero-container {{ text-align: center; padding: 80px 0 40px 0; }}
    .grand-title {{
        font-family: 'Inter', sans-serif; font-size: 5rem !important; font-weight: 900; letter-spacing: 12px;
        background: linear-gradient(to bottom, #ffffff 30%, #38bdf8 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }}
    .grand-subtitle {{ font-size: 1rem; letter-spacing: 6px; color: rgba(148, 163, 184, 0.5); }}

    /* 【代码1植入】属性看板格子样式：毛玻璃 + 圆角 + 悬浮 */
    .cat-card-inner {{
        height: 400px;
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important;
        overflow-y: auto;
        margin-bottom: 25px;
        backdrop-filter: blur(20px) saturate(160%) !important;
        transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
    }}
    .cat-card-inner:hover {{
        transform: translateY(-8px);
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(56, 189, 248, 0.5) !important;
        box-shadow: 0 12px 40px rgba(0,0,0,0.4);
    }}
    .cat-card-inner::-webkit-scrollbar {{ width: 4px; }}
    .cat-card-inner::-webkit-scrollbar-thumb {{ background: rgba(56, 189, 248, 0.3); border-radius: 10px; }}

    /* 异常跳转按钮 */
    .sn-button {{
        display: inline-block; padding: 4px 14px; background: rgba(56, 189, 248, 0.15);
        color: #38bdf8 !important; border: 1px solid rgba(56, 189, 248, 0.4);
        border-radius: 20px; text-decoration: none !important; font-size: 0.8rem; font-weight: 600;
        transition: all 0.2s ease; margin-left: 10px;
    }}
    .sn-button:hover {{ background: #38bdf8; color: #000000 !important; transform: scale(1.05); }}
    
    /* 药丸 Tab 样式 */
    .stTabs [data-baseweb="tab-list"] {{ gap: 20px; }}
    .stTabs [data-baseweb="tab"] {{ font-weight: 700; font-size: 1.1rem; }}
    </style>
    
    <div class="user-profile">
        <img src="https://avatars.githubusercontent.com/{GITHUB_USERNAME}" class="avatar">
        <div class="user-info">
            <div class="user-name">{GITHUB_USERNAME}</div>
            <div class="user-status">● MATRIX HUB ACTIVE</div>
        </div>
    </div>

    <div class="hero-container">
        <h1 class="grand-title">属性看板中枢</h1>
        <p class="grand-subtitle">CORE PROPERTY MATRIX HUB</p>
    </div>
""", unsafe_allow_html=True)

# --- 2. 核心逻辑 (代码2的严谨逻辑) ---
def process_sku_logic(uploaded_file):
    COLOR_REG, SIZE_REG = r'(?i)Color[:：\s]*([a-zA-Z0-9\-_/]+)', r'(?i)Size[:：\s]*([a-zA-Z0-9\-\s/]+?)(?=\s*(?:Color|Size|$|[,;，；]))'
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
            c_m, s_m = re.search(COLOR_REG, chunk), re.search(SIZE_REG, chunk)
            if c_m:
                clr_v = c_m.group(1).strip().upper()
                raw_s = s_m.group(1).strip().upper() if s_m else ""
                data_pairs.append((clr_v, SIZE_MAP.get(raw_s, raw_s)))
        if len(data_pairs) == i_qty and i_qty > 0:
            for c_val, s_val in data_pairs: all_normal_data.append({'Category': cat, 'Color': c_val, 'Size': s_val})
        else:
            all_error_rows.append({'行号': index + 2, '订单编号': row[col_a], '品名': cat, '原因': f"校验不匹配({len(data_pairs)}/{i_qty})", '原始属性': g_text})
    return pd.DataFrame(all_normal_data), pd.DataFrame(all_error_rows)

# --- 3. 渲染看板格子的函数 ---
def render_matrix_card(cat, group):
    color_groups = group.groupby('Color')
    body_html = ""
    for clr, clr_data in color_groups:
        size_stats = clr_data['Size'].value_counts().sort_index()
        size_badges = "".join([f'<span style="background:rgba(56,189,248,0.12); padding:2px 8px; border-radius:6px; margin:2px; color:#fff; display:inline-block; font-size:10px;">{s if s!="" else "FREE"} <b style=\'color:#38bdf8; margin-left:3px;\'>×{q}</b></span>' for s, q in size_stats.items()])
        body_html += f'''
            <div style="background:rgba(255,255,255,0.03); margin-bottom:10px; padding:10px; border-radius:12px; border:1px solid rgba(255,255,255,0.05);">
                <div style="color:#38bdf8; font-weight:800; font-size:12px; margin-bottom:6px; border-bottom:1px solid rgba(255,255,255,0.05); padding-bottom:4px;">{html.escape(str(clr))}</div>
                <div style="display:flex; flex-wrap:wrap; gap:2px;">{size_badges}</div>
            </div>'''
    
    st.markdown(f'''
        <div class="cat-card-inner">
            <div style="background:rgba(56,189,248,0.2); padding:12px; text-align:center; color:#38bdf8; font-weight:900; font-size:1.1rem; border-bottom:1px solid rgba(255,255,255,0.1); position:sticky; top:0; z-index:10; border-radius: 18px 18px 0 0;">{cat}</div>
            <div style="padding:15px;">{body_html}</div>
        </div>
    ''', unsafe_allow_html=True)

# --- 4. 主程序流程 ---
upload_placeholder = st.empty()
uploaded_file = upload_placeholder.file_uploader("", type=["xlsx"])

if uploaded_file:
    upload_placeholder.empty() # 解析完成，隐藏上传框
    
    with st.spinner('SYSTEM ANALYZING...'):
        final_df, error_df = process_sku_logic(uploaded_file)
    
    tab1, tab2 = st.tabs(["💎 结构化看板", "📡 异常捕获"])

    with tab1:
        if not final_df.empty:
            cat_list = list(final_df.sort_values(['Category']).groupby('Category'))
            cols_per_row = 5 # 设置每行5个格子，兼顾宽度与密度
            for i in range(0, len(cat_list), cols_per_row):
                batch = cat_list[i : i + cols_per_row]
                cols = st.columns(cols_per_row)
                for col, (cat, group) in zip(cols, batch):
                    with col:
                        render_matrix_card(cat, group)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("↺ 重新部署数据源"):
                st.rerun()
        else:
            st.info("暂无有效汇总数据")

    with tab2:
        if not error_df.empty:
            for _, err in error_df.iterrows():
                sn_val = str(err['订单编号'])
                full_link = f"{BASE_URL}{sn_val}"
                st.markdown(f"""
                <div style="background:rgba(245,158,11,0.03); border:1px solid rgba(245,158,11,0.2); border-radius:12px; padding:15px; margin-bottom:10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="color:#f59e0b; font-weight:bold; font-size:0.8rem;">LINE: {err['行号']}</span>
                            <span style="color:#ffffff; margin-left:15px; font-weight:600;">{err['原因']}</span>
                        </div>
                        <a href="{full_link}" target="_blank" class="sn-button">查看详情 SN: {sn_val}</a>
                    </div>
                    <div style="margin-top:8px; font-size:0.85rem; color:#64748b;">
                        <b>原始属性:</b> {err['原始属性']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("所有数据均通过校验。")

st.markdown("<div style='height:100px;'></div>", unsafe_allow_html=True)
