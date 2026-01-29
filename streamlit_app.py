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
    .stApp {{ background: radial-gradient(circle at 50% 50%, #1e293b, #010409); color: #ffffff; }}
    header {{visibility: hidden;}}

    /* 悬浮面板 */
    .user-profile {{
        position: fixed; top: 25px; left: 25px; display: flex; align-items: center; gap: 12px; z-index: 1000000; 
        background: rgba(255, 255, 255, 0.05); padding: 6px 16px 6px 6px; border-radius: 50px;
        border: 1px solid rgba(56, 189, 248, 0.3); backdrop-filter: blur(10px);
    }}
    .avatar {{ width: 40px; height: 40px; border-radius: 50%; border: 2px solid #38bdf8; object-fit: cover; }}

    /* 大气标题 */
    .hero-container {{ text-align: center; padding: 50px 0 20px 0; }}
    .grand-title {{
        font-family: 'Inter', sans-serif; font-size: 3.5rem !important; font-weight: 900; letter-spacing: 8px;
        background: linear-gradient(to bottom, #ffffff 30%, #38bdf8 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }}

    /* 【核心修改】看板格子样式：高度自适应 */
    .cat-card-inner {{
        /* 移除固定高度，改为由内容撑开 */
        min-height: 100px; 
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important; 
        border-radius: 16px !important;
        margin-bottom: 15px; 
        backdrop-filter: blur(20px);
        transition: all 0.3s ease;
    }}
    .cat-card-inner:hover {{ 
        transform: translateY(-3px); 
        border: 1px solid rgba(56, 189, 248, 0.4) !important; 
        background: rgba(255, 255, 255, 0.06) !important;
    }}
    
    .sn-button {{
        display: inline-block; padding: 3px 12px; background: rgba(56, 189, 248, 0.1);
        color: #38bdf8 !important; border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 15px; text-decoration: none !important; font-size: 0.75rem;
    }}
    </style>
    
    <div class="user-profile">
        <img src="https://avatars.githubusercontent.com/{GITHUB_USERNAME}" class="avatar">
        <div class="user-info">
            <div class="user-name">{GITHUB_USERNAME}</div>
            <div style="font-size: 0.6rem; color: #10b981;">● ADAPTIVE MODE</div>
        </div>
    </div>

    <div class="hero-container">
        <h1 class="grand-title">属性看板中枢</h1>
    </div>
""", unsafe_allow_html=True)

# --- 2. 逻辑层 (保持严谨性) ---
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
            all_error_rows.append({'行号': index + 2, '订单编号': row[col_a], '原因': "复合品类阻断", '原始属性': str(row[col_g])})
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
            all_error_rows.append({'行号': index + 2, '订单编号': row[col_a], '原因': f"数量不符({len(data_pairs)}/{i_qty})", '原始属性': g_text})
    return pd.DataFrame(all_normal_data), pd.DataFrame(all_error_rows)

# --- 3. 渲染看板格子的函数 (压缩间距，内容自适应) ---
def render_matrix_card(cat, group):
    color_groups = group.groupby('Color')
    body_html = ""
    for clr, clr_data in color_groups:
        size_stats = clr_data['Size'].value_counts().sort_index()
        size_badges = "".join([
            f'<span style="background:rgba(56,189,248,0.08); padding:1px 6px; border-radius:4px; margin:1px; color:#ddd; font-size:10px; border:1px solid rgba(56,189,248,0.1);">'
            f'{s if s not in ["", "FREE", "NAN", "nan"] else ""}' 
            f'<b style="color:#38bdf8; margin-left:2px;">×{q}</b></span>' 
            for s, q in size_stats.items()
        ])
        
        body_html += f'''
            <div style="display:flex; align-items:center; background:rgba(255,255,255,0.02); margin-bottom:4px; padding:4px 8px; border-radius:8px; border:1px solid rgba(255,255,255,0.03); flex-wrap:nowrap; overflow:hidden;">
                <span style="color:#38bdf8; font-weight:700; font-size:10px; margin-right:6px; white-space:nowrap; border-right:1px solid rgba(255,255,255,0.05); padding-right:6px; min-width:40px;">{html.escape(str(clr))}</span>
                <div style="display:flex; flex-wrap:wrap; gap:1px;">{size_badges}</div>
            </div>'''
    
    st.markdown(f'''
        <div class="cat-card-inner">
            <div style="background:rgba(56,189,248,0.15); padding:6px; text-align:center; color:#38bdf8; font-weight:800; font-size:0.95rem; border-bottom:1px solid rgba(255,255,255,0.05); border-radius: 16px 16px 0 0;">{cat}</div>
            <div style="padding:8px;">{body_html}</div>
        </div>
    ''', unsafe_allow_html=True)

# --- 4. 主程序流程 ---
upload_placeholder = st.empty()
uploaded_file = upload_placeholder.file_uploader("", type=["xlsx"])

if uploaded_file:
    upload_placeholder.empty()
    with st.spinner('SYSTEM ANALYZING...'):
        final_df, error_df = process_sku_logic(uploaded_file)
    
    tab1, tab2 = st.tabs(["✅ 正常汇总", "❌ 异常拦截"])

    with tab1:
        if not final_df.empty:
            cat_list = list(final_df.sort_values(['Category']).groupby('Category'))
            # 提高列数到 6 列，让每个框更紧凑
            cols_per_row = 6 
            for i in range(0, len(cat_list), cols_per_row):
                batch, cols = cat_list[i : i + cols_per_row], st.columns(cols_per_row)
                for col, (cat, group) in zip(cols, batch):
                    with col: render_matrix_card(cat, group)
            st.button("↺ 重新部署", on_click=lambda: st.rerun())
        else:
            st.info("暂无有效汇总数据")

    with tab2:
        if not error_df.empty:
            for _, err in error_df.iterrows():
                sn_v = str(err['订单编号'])
                st.markdown(f'''
                <div style="background:rgba(245,158,11,0.02); border:1px solid rgba(245,158,11,0.15); border-radius:10px; padding:10px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
                    <div style="font-size:0.85rem;"><span style="color:#f59e0b; font-weight:bold;">L: {err['行号']}</span> | <span style="color:#eee;">{err['原因']}</span><br><small style="color:#555;">{err['原始属性']}</small></div>
                    <a href="{BASE_URL}{sn_v}" target="_blank" class="sn-button">SN: {sn_v}</a>
                </div>''', unsafe_allow_html=True)
        else:
            st.success("校验全通过。")
