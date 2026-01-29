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

    /* 标题 */
    .hero-container {{ text-align: center; padding: 50px 0 20px 0; }}
    .grand-title {{
        font-family: 'Inter', sans-serif; font-size: 3.2rem !important; font-weight: 900; letter-spacing: 8px;
        background: linear-gradient(to bottom, #ffffff 30%, #38bdf8 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }}

    /* 正常汇总格子：固定高度 + 统一对齐 */
    .cat-card-inner {{
        height: 280px;
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important; 
        border-radius: 16px !important;
        margin-bottom: 15px; 
        backdrop-filter: blur(20px);
        transition: all 0.3s ease;
        display: flex;
        flex-direction: column;
    }}
    .cat-card-inner:hover {{ transform: translateY(-3px); border: 1px solid rgba(56, 189, 248, 0.4) !important; }}
    
    .scroll-area {{ flex: 1; overflow-y: auto; padding: 10px; }}
    .scroll-area::-webkit-scrollbar {{ width: 3px; }}
    .scroll-area::-webkit-scrollbar-thumb {{ background: rgba(56, 189, 248, 0.2); border-radius: 10px; }}

    /* 异常卡片按钮样式 */
    .sn-button {{
        display: inline-block; padding: 4px 14px; background: rgba(56, 189, 248, 0.15);
        color: #38bdf8 !important; border: 1px solid rgba(56, 189, 248, 0.4);
        border-radius: 20px; text-decoration: none !important; font-size: 0.8rem; font-weight: 600;
        transition: all 0.2s ease;
    }}
    .sn-button:hover {{ background: #38bdf8; color: #000; transform: scale(1.05); }}
    </style>
    
    <div class="user-profile">
        <img src="https://avatars.githubusercontent.com/{GITHUB_USERNAME}" class="avatar">
        <div class="user-info">
            <div class="user-name">{GITHUB_USERNAME}</div>
            <div style="font-size: 0.6rem; color: #10b981; font-weight: bold;">● V0.03</div>
        </div>
    </div>

    <div class="hero-container">
        <h1 class="grand-title">属性看板中枢</h1>
    </div>
""", unsafe_allow_html=True)

# --- 2. 逻辑层 ---
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
            all_error_rows.append({'行号': index + 2, '订单编号': row[col_a], '品名': c_raw, '原因': "多个商品", '原始属性': str(row[col_g])})
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
            all_error_rows.append({'行号': index + 2, '订单编号': row[col_a], '品名': cat, '原因': f"数量不符({len(data_pairs)}/{i_qty})", '原始属性': g_text})
    return pd.DataFrame(all_normal_data), pd.DataFrame(all_error_rows)

# --- 3. 正常数据渲染函数 (矩阵) ---
def render_normal_card(cat, group):
    body_html = ""
    for clr, clr_data in group.groupby('Color'):
        size_stats = clr_data['Size'].value_counts().sort_index()
        size_badges = "".join([f'<span style="background:rgba(56,189,248,0.1); padding:1px 5px; border-radius:4px; margin:1px; color:#eee; font-size:10px;">{s if s not in ["", "FREE", "NAN", "nan"] else ""}<b style="color:#38bdf8; margin-left:2px;">×{q}</b></span>' for s, q in size_stats.items()])
        body_html += f'''
            <div style="display:flex; align-items:center; background:rgba(255,255,255,0.02); margin-bottom:4px; padding:4px 8px; border-radius:8px; border:1px solid rgba(255,255,255,0.03);">
                <span style="color:#38bdf8; font-weight:700; font-size:10px; margin-right:6px; border-right:1px solid rgba(255,255,255,0.05); padding-right:6px; min-width:35px; white-space:nowrap;">{html.escape(str(clr))}</span>
                <div style="display:flex; flex-wrap:wrap; gap:1px;">{size_badges}</div>
            </div>'''
    
    st.markdown(f'''
        <div class="cat-card-inner">
            <div style="background:rgba(56,189,248,0.2); padding:8px; text-align:center; color:#38bdf8; font-weight:800; font-size:0.9rem; border-bottom:1px solid rgba(255,255,255,0.05); border-radius: 16px 16px 0 0;">{cat}</div>
            <div class="scroll-area">{body_html}</div>
        </div>
    ''', unsafe_allow_html=True)

# --- 4. 主程序 ---
upload_placeholder = st.empty()
uploaded_file = upload_placeholder.file_uploader("", type=["xlsx"])

if uploaded_file:
    upload_placeholder.empty()
    with st.spinner('ANALYZING...'):
        v_df, e_df = process_sku_logic(uploaded_file)
    
    t1, t2 = st.tabs(["正常汇总", "异常数据"])

    with t1:
        if not v_df.empty:
            cat_list = list(v_df.sort_values(['Category']).groupby('Category'))
            cols_per_row = 6 
            for i in range(0, len(cat_list), cols_per_row):
                batch, cols = cat_list[i : i + cols_per_row], st.columns(cols_per_row)
                for col, (cat, g) in zip(cols, batch):
                    with col: render_normal_card(cat, g)
        else: st.info("暂无数据")

    with t2:
        if not e_df.empty:
            for _, err in e_df.iterrows():
                sn_v = str(err['订单编号'])
                st.markdown(f"""
                <div style="background:rgba(245,158,11,0.03); border:1px solid rgba(245,158,11,0.2); border-radius:12px; padding:15px; margin-bottom:10px; display: flex; justify-content: space-between; align-items: center;">
                    <div style="flex: 1;">
                        <span style="color:#f59e0b; font-weight:bold; font-size:0.8rem;">LINE: {err['行号']}</span>
                        <span style="color:#ffffff; margin-left:15px; font-weight:600;">{err['原因']}</span>
                        <div style="margin-top:6px; font-size:0.8rem; color:#64748b;"><b>原始属性:</b> {err['原始属性']}</div>
                    </div>
                    <a href="{BASE_URL}{sn_v}" target="_blank" class="sn-button">跳转至订单: {sn_v}</a>
                </div>
                """, unsafe_allow_html=True)
        else: st.success("所有数据均通过校验。")

st.markdown("<div style='height:100px;'></div>", unsafe_allow_html=True)
