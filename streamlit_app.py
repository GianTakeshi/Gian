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
        font-family: 'Inter', sans-serif; font-size: 3.2rem !important; font-weight: 900; letter-spacing: 8px;
        background: linear-gradient(to bottom, #ffffff 30%, #38bdf8 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }}

    /* 【核心修改】看板格子样式：强制高度一致 + 内部滚动 */
    .cat-card-inner {{
        height: 280px; /* 强制所有框高度一致 */
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important; 
        border-radius: 16px !important;
        margin-bottom: 15px; 
        backdrop-filter: blur(20px);
        transition: all 0.3s ease;
        display: flex;
        flex-direction: column;
    }}
    .cat-card-inner:hover {{ 
        transform: translateY(-3px); 
        border: 1px solid rgba(56, 189, 248, 0.4) !important; 
    }}
    
    .scroll-area {{
        flex: 1;
        overflow-y: auto;
        padding: 10px;
    }}
    .scroll-area::-webkit-scrollbar {{ width: 3px; }}
    .scroll-area::-webkit-scrollbar-thumb {{ background: rgba(56, 189, 248, 0.2); border-radius: 10px; }}

    .sn-link {{ color: #38bdf8 !important; text-decoration: none; font-weight: bold; font-size: 10px; border-bottom: 1px dashed #38bdf8; }}
    </style>
    
    <div class="user-profile">
        <img src="https://avatars.githubusercontent.com/{GITHUB_USERNAME}" class="avatar">
        <div class="user-info">
            <div class="user-name">{GITHUB_USERNAME}</div>
            <div style="font-size: 0.6rem; color: #10b981; font-weight: bold;">● UNIFIED MATRIX V1.0</div>
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
            all_error_rows.append({'Category': 'ERR-复合', '行号': index + 2, '订单编号': row[col_a], '原因': "品名带分号", '原始属性': str(row[col_g])})
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
            all_error_rows.append({'Category': cat, '行号': index + 2, '订单编号': row[col_a], '原因': f"校验失败({len(data_pairs)}/{i_qty})", '原始属性': g_text})
    return pd.DataFrame(all_normal_data), pd.DataFrame(all_error_rows)

# --- 3. 统一渲染函数 ---
def render_unified_card(cat, group, is_error=False):
    header_color = "rgba(239, 68, 68, 0.2)" if is_error else "rgba(56, 189, 248, 0.2)"
    text_color = "#f87171" if is_error else "#38bdf8"
    
    body_html = ""
    if is_error:
        for _, r in group.iterrows():
            url = f"{BASE_URL}{r['订单编号']}"
            body_html += f'''
                <div style="background:rgba(239,68,68,0.05); margin-bottom:6px; padding:6px; border-radius:8px; border:1px solid rgba(239,68,68,0.1);">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:2px;">
                        <span style="font-size:10px; color:#f87171; font-weight:bold;">L:{r['行号']}</span>
                        <a href="{url}" target="_blank" class="sn-link">{r['订单编号']}</a>
                    </div>
                    <div style="font-size:9px; color:#94a3b8; line-height:1.2;">{r['原因']}</div>
                </div>'''
    else:
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
            <div style="background:{header_color}; padding:8px; text-align:center; color:{text_color}; font-weight:800; font-size:0.9rem; border-bottom:1px solid rgba(255,255,255,0.05); border-radius: 16px 16px 0 0;">{cat}</div>
            <div class="scroll-area">{body_html}</div>
        </div>
    ''', unsafe_allow_html=True)

# --- 4. 主程序 ---
upload_placeholder = st.empty()
uploaded_file = upload_placeholder.file_uploader("", type=["xlsx"])

if uploaded_file:
    upload_placeholder.empty()
    with st.spinner('SYSTEM ANALYZING...'):
        v_df, e_df = process_sku_logic(uploaded_file)
    
    t1, t2 = st.tabs(["✅ 正常汇总", "❌ 异常拦截"])
    cols_per_row = 6 

    with t1:
        if not v_df.empty:
            cat_list = list(v_df.sort_values(['Category']).groupby('Category'))
            for i in range(0, len(cat_list), cols_per_row):
                batch, cols = cat_list[i : i + cols_per_row], st.columns(cols_per_row)
                for col, (cat, g) in zip(cols, batch):
                    with col: render_unified_card(cat, g, is_error=False)
        else: st.info("无有效数据")

    with t2:
        if not e_df.empty:
            cat_list = list(e_df.sort_values(['Category']).groupby('Category'))
            for i in range(0, len(cat_list), cols_per_row):
                batch, cols = cat_list[i : i + cols_per_row], st.columns(cols_per_row)
                for col, (cat, g) in zip(cols, batch):
                    with col: render_unified_card(cat, g, is_error=True)
        else: st.success("校验全通过")

st.markdown("<div style='height:100px;'></div>", unsafe_allow_html=True)
