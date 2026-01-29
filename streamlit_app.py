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

    /* 左上角头像悬浮面板 */
    .user-profile {{
        position: fixed; top: 25px; left: 25px; display: flex; align-items: center; gap: 12px; z-index: 1000000 !important; 
        background: rgba(255, 255, 255, 0.05); padding: 6px 16px 6px 6px; border-radius: 50px;
        border: 1px solid rgba(56, 189, 248, 0.3); backdrop-filter: blur(10px);
    }}
    .avatar {{ width: 40px; height: 40px; border-radius: 50%; border: 2px solid #38bdf8; object-fit: cover; }}

    /* 标题居中 */
    .hero-container {{ text-align: center; width: 100%; padding: 80px 0 40px 0; }}
    .grand-title {{
        display: block; font-family: 'Inter', sans-serif; font-size: 3.5rem !important; font-weight: 900; letter-spacing: 10px;
        background: linear-gradient(to bottom, #ffffff 30%, #38bdf8 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 0 15px rgba(56, 189, 248, 0.1));
    }}

    /* 白色磨砂药丸上传框 */
    [data-testid="stFileUploader"] {{
        position: fixed; bottom: 120px; left: 50%; transform: translateX(-50%); width: 480px; z-index: 9999;
        background: rgba(255, 255, 255, 0.12) !important; border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 50px !important; padding: 8px 25px !important; backdrop-filter: blur(25px) saturate(180%);
        box-shadow: 0 15px 35px rgba(0,0,0,0.3); transition: all 0.4s ease;
    }}
    [data-testid="stFileUploader"]:hover {{ border: 1px solid rgba(56, 189, 248, 0.6) !important; transform: translateX(-50%) translateY(-5px); }}

    /* 通用格子样式 */
    .matrix-card {{
        height: 280px; background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important; border-radius: 16px !important;
        margin-bottom: 15px; backdrop-filter: blur(20px); display: flex; flex-direction: column;
        transition: all 0.3s ease;
    }}
    .matrix-card:hover {{ transform: translateY(-5px); }}
    
    /* 异常专用格子边框 */
    .error-card {{ border: 1px solid rgba(239, 68, 68, 0.3) !important; }}
    .error-card:hover {{ border: 1px solid rgba(239, 68, 68, 0.8) !important; box-shadow: 0 0 20px rgba(239, 68, 68, 0.2); }}

    .scroll-area {{ flex: 1; overflow-y: auto; padding: 10px; }}
    .scroll-area::-webkit-scrollbar {{ width: 3px; }}
    .scroll-area::-webkit-scrollbar-thumb {{ background: rgba(255, 255, 255, 0.1); border-radius: 10px; }}

    .sn-link {{ color: #38bdf8 !important; text-decoration: none; font-size: 10px; font-weight: bold; border-bottom: 1px dashed rgba(56,189,248,0.4); }}
    </style>
""", unsafe_allow_html=True)

# --- 2. 核心逻辑层 (修复分类抓取) ---
def process_sku_logic(uploaded_file):
    COLOR_REG, SIZE_REG = r'(?i)Color[:：\s]*([a-zA-Z0-9\-_/]+)', r'(?i)Size[:：\s]*([a-zA-Z0-9\-\s/]+?)(?=\s*(?:Color|Size|$|[,;，；]))'
    SIZE_MAP = {'HIGH ANKLE SOCKS': 'L', 'KNEE-HIGH SOCKS': 'M'}
    df = pd.read_excel(uploaded_file, engine='openpyxl')
    col_a, col_c, col_g, col_i = df.columns[0], df.columns[2], df.columns[6], df.columns[8]
    
    all_normal_data, all_error_rows = [], []
    
    for index, row in df.iterrows():
        c_raw = str(row[col_c]).strip()
        if not c_raw or c_raw == 'nan': continue
        
        # 提取 Category
        cat = c_raw.split(' ')[0].upper()
        if cat.startswith('WZ'): cat = 'WZ'
        
        if ';' in c_raw or '；' in c_raw:
            all_error_rows.append({'Category': cat, '行号': index + 2, '订单编号': row[col_a], '原因': "复合品类阻断", '内容': str(row[col_g])})
            continue

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
            for c_val, s_val in data_pairs:
                all_normal_data.append({'Category': cat, 'Color': c_val, 'Size': s_val})
        else:
            all_error_rows.append({'Category': cat, '行号': index + 2, '订单编号': row[col_a], '原因': f"数量不符({len(data_pairs)}/{i_qty})", '内容': g_text})
            
    return pd.DataFrame(all_normal_data), pd.DataFrame(all_error_rows)

# --- 3. 渲染函数 (分类渲染) ---
def render_matrix_box(cat, group, is_error=False):
    css_class = "matrix-card error-card" if is_error else "matrix-card"
    header_bg = "rgba(239, 68, 68, 0.25)" if is_error else "rgba(56, 189, 248, 0.2)"
    text_clr = "#f87171" if is_error else "#38bdf8"
    
    body_html = ""
    if is_error:
        for _, r in group.iterrows():
            body_html += f'''
                <div style="background:rgba(239,68,68,0.05); margin-bottom:6px; padding:6px; border-radius:8px; border:1px solid rgba(239,68,68,0.1);">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size:10px; color:#f87171; font-weight:bold;">L:{r['行号']}</span>
                        <a href="{BASE_URL}{r['订单编号']}" target="_blank" class="sn-link">{r['订单编号']}</a>
                    </div>
                    <div style="font-size:9px; color:#94a3b8; margin-top:2px;">{r['原因']}</div>
                </div>'''
    else:
        for clr, clr_data in group.groupby('Color'):
            size_stats = clr_data['Size'].value_counts().sort_index()
            badges = "".join([f'<span style="background:rgba(56,189,248,0.1); padding:1px 5px; border-radius:4px; margin:1px; color:#eee; font-size:10px;">{s}<b style="color:#38bdf8; margin-left:2px;">×{q}</b></span>' for s, q in size_stats.items()])
            body_html += f'<div style="display:flex; align-items:center; background:rgba(255,255,255,0.02); margin-bottom:4px; padding:4px 8px; border-radius:8px;"><span style="color:#38bdf8; font-weight:700; font-size:10px; min-width:35px;">{clr}</span>{badges}</div>'

    st.markdown(f'''
        <div class="{css_class}">
            <div style="background:{header_bg}; padding:8px; text-align:center; color:{text_clr}; font-weight:800; font-size:0.9rem; border-radius: 16px 16px 0 0;">{cat}</div>
            <div class="scroll-area">{body_html}</div>
        </div>
    ''', unsafe_allow_html=True)

# --- 4. 主程序 ---
st.markdown(f'<div class="user-profile"><img src="https://avatars.githubusercontent.com/{GITHUB_USERNAME}" class="avatar"><div class="user-info"><div class="user-name">{GITHUB_USERNAME}</div><div style="font-size:0.6rem; color:#10b981; font-weight:bold;">● MATRIX OPTIMIZED</div></div></div><div class="hero-container"><h1 class="grand-title">属性看板中枢</h1></div>', unsafe_allow_html=True)

upload_box = st.empty()
uploaded_file = upload_box.file_uploader("Upload", type=["xlsx"])

if uploaded_file:
    with st.spinner('SYNCING...'):
        v_df, e_df = process_sku_logic(uploaded_file)
    upload_box.empty()
    
    t1, t2 = st.tabs(["💎 结构化看板", "📡 异常分类捕获"])
    
    with t1:
        if not v_df.empty:
            cat_list = list(v_df.sort_values(['Category']).groupby('Category'))
            for i in range(0, len(cat_list), 6):
                cols = st.columns(6)
                for col, (cat, g) in zip(cols, cat_list[i:i+6]):
                    with col: render_matrix_box(cat, g, False)
            if st.button("↺ 重置"): st.rerun()
        else: st.info("无数据")

    with t2:
        if not e_df.empty:
            # 【修复点】异常数据现在也按 Category 分组显示
            err_cat_list = list(e_df.sort_values(['Category']).groupby('Category'))
            for i in range(0, len(err_cat_list), 6):
                cols = st.columns(6)
                for col, (cat, g) in zip(cols, err_cat_list[i:i+6]):
                    with col: render_matrix_box(cat, g, True)
        else: st.success("全线通过")
