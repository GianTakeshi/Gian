import streamlit as st
import pandas as pd
import re
import html

# --- 1. UI 视觉配置 (纯白背景 + 浅色毛玻璃) ---
st.set_page_config(page_title="Gian Matrix", page_icon="💎", layout="wide")

st.markdown(f"""
    <style>
    /* 基础背景：纯白色 */
    .stApp {{
        background-color: #FFFFFF !important;
        color: #1d1d1f;
    }}
    header {{ visibility: hidden; }}

    /* 背景层：Gian 大字 (浅灰色) */
    .background-gian {{
        position: fixed;
        bottom: -5%;
        left: 50%;
        transform: translateX(-50%);
        font-size: clamp(15rem, 35vw, 45rem);
        font-weight: 900;
        color: rgba(0, 0, 0, 0.03); /* 极淡的灰色 */
        letter-spacing: -15px;
        z-index: -2;
        user-select: none;
        white-space: nowrap;
        pointer-events: none;
    }}

    /* 动态流雾：右侧淡蓝色光雾 */
    .mist-light {{
        position: fixed;
        top: 0;
        right: 0;
        width: 70%;
        height: 100%;
        background: radial-gradient(circle at 100% 50%, 
            rgba(0, 122, 255, 0.08) 0%, 
            rgba(0, 199, 190, 0.04) 40%, 
            transparent 80%);
        filter: blur(100px);
        animation: light-flow 12s ease-in-out infinite alternate;
        z-index: -1;
    }}
    
    @keyframes light-flow {{
        0% {{ transform: translateX(10%) scale(1); opacity: 0.5; }}
        100% {{ transform: translateX(-5%) scale(1.1); opacity: 0.9; }}
    }}

    /* 上层毛玻璃格子：浅色半透明 */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: rgba(255, 255, 255, 0.6) !important;
        backdrop-filter: blur(25px) saturate(180%) !important;
        border: 1px solid rgba(0, 0, 0, 0.05) !important;
        border-radius: 24px !important;
        height: 400px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.03);
    }}

    /* Tab 导航：简约白 */
    .stTabs [data-baseweb="tab-list"] {{
        background: rgba(0, 0, 0, 0.02);
        backdrop-filter: blur(10px);
        border-radius: 50px;
        border: 1px solid rgba(0, 0, 0, 0.05);
        margin: 0 auto 20px auto;
        width: fit-content;
    }}

    /* 文件上传框 */
    .stFileUploader {{
        max-width: 500px;
        margin: 40px auto !important;
        background: rgba(255,255,255,0.8);
        border: 1px solid rgba(0, 122, 255, 0.1) !important;
        border-radius: 20px;
    }}

    .err-link {{ color: #007aff !important; text-decoration: none; font-weight: 700; }}
    </style>
    
    <div class="background-gian">Gian</div>
    <div class="mist-light"></div>
""", unsafe_allow_html=True)

# --- 2. 逻辑层 ---
def process_data(uploaded_file):
    COLOR_REG, SIZE_REG = r'(?i)Color[:：\s]*([a-zA-Z0-9\-_/]+)', r'(?i)Size[:：\s]*([a-zA-Z0-9\-\s/]+?)(?=\s*(?:Color|Size|$|[,;，；]))'
    SIZE_MAP = {'HIGH ANKLE SOCKS': 'L', 'KNEE-HIGH SOCKS': 'M'}
    df = pd.read_excel(uploaded_file, engine='openpyxl')
    valid, error = [], []
    for idx, row in df.iterrows():
        try:
            sn, name, attr, qty_raw = str(row.iloc[1]).strip(), str(row.iloc[2]).strip(), str(row.iloc[6]).strip(), str(row.iloc[8]).strip()
            cat = name.split(' ')[0].upper()
            if cat.startswith('WZ'): cat = 'WZ'
            target_qty = int(re.findall(r'\d+', qty_raw)[0]) if re.findall(r'\d+', qty_raw) else 0
            chunks = [c.strip() for c in re.split(r'[;；]', attr) if c.strip()]
            parsed = []
            for chunk in chunks:
                c_m, s_m = re.search(COLOR_REG, chunk), re.search(SIZE_REG, chunk)
                if c_m:
                    clr = c_m.group(1).strip().upper()
                    sze = s_m.group(1).strip().upper() if s_m else "FREE"
                    parsed.append({'Category': cat, 'SN': sn, 'Color': clr, 'Size': SIZE_MAP.get(sze, sze)})
            if len(parsed) == target_qty and parsed: valid.extend(parsed)
            else: error.append({'Category': cat, 'SN': sn, 'Reason': f'数量不符({len(parsed)}/{target_qty})'})
        except: continue
    return pd.DataFrame(valid), pd.DataFrame(error)

# --- 3. 渲染逻辑 ---
def render_item(cat, group, is_error):
    body_html = ""
    if is_error:
        for _, r in group.iterrows():
            url = f"https://inflyway.com/kamelnet/#/kn/fly-link/orders/detail?id={r['SN']}"
            body_html += f'''<div style="margin-bottom:12px; padding:10px; border-left:3px solid #ff3b30; background:rgba(255,59,48,0.03); border-radius:6px;"><a class="err-link" href="{url}" target="_blank">SN: {r['SN']}</a><br><span style="color:#8e8e93; font-size:10px;">{r['Reason']}</span></div>'''
    else:
        for clr, clr_data in group.groupby('Color'):
            size_stats = clr_data['Size'].value_counts().sort_index()
            size_badges = " ".join([f'<span style="background:rgba(0,0,0,0.03); padding:2px 8px; border-radius:4px; margin-right:5px; border:1px solid rgba(0,0,0,0.02);">{s if s!="FREE" else ""}<b>×{q}</b></span>' for s, q in size_stats.items()])
            body_html += f'''<div style="margin-bottom:15px; padding-bottom:10px; border-bottom:1px solid rgba(0,0,0,0.03);"><div style="color:#007aff; font-weight:700; font-size:13px; margin-bottom:5px;">{clr}</div><div style="color:#3a3a3c; font-size:11px;">{size_badges}</div></div>'''
    
    st.markdown(f'''<div style="height:370px; overflow-y:auto;"><div style="padding:15px 0; text-align:center; position:sticky; top:0; background:rgba(255,255,255,0.01); z-index:10;"><span style="font-weight:900; letter-spacing:2px; font-size:1.1rem; color:#1d1d1f;">{cat}</span></div><div style="padding:10px;">{body_html}</div></div>''', unsafe_allow_html=True)

# --- 4. 主程序 ---
file = st.file_uploader("DROP LOGISTICS EXCEL", type=["xlsx"])

if file:
    v_df, e_df = process_data(file)
    t1, t2 = st.tabs(["EXISTING", "ANOMALY"])
    
    cols_count = 6
    for tab, df, is_err in zip([t1, t2], [v_df, e_df], [False, True]):
        with tab:
            if not df.empty:
                cat_list = list(df.groupby('Category'))
                for i in range(0, len(cat_list), cols_count):
                    cols = st.columns(cols_count)
                    batch = cat_list[i : i + cols_count]
                    for col, (cat, g) in zip(cols, batch):
                        with col: render_item(cat, g, is_err)
            else: st.info("No records.")
