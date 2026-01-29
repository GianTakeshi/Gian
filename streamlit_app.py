import streamlit as st
import pandas as pd
import re
import html

# --- 1. UI 视觉配置 (Grok 艺术风格) ---
st.set_page_config(page_title="Gian Matrix", page_icon="💎", layout="wide")

st.markdown(f"""
    <style>
    /* 1. 基础背景：极简深空黑 */
    .stApp {{
        background: #000000;
        color: #ffffff;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }}
    header {{ visibility: hidden; }}

    /* 2. 背景流雾效果 (动态光影) */
    .mist-container {{
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: 
            radial-gradient(circle at 80% 50%, rgba(56, 189, 248, 0.08) 0%, transparent 40%),
            radial-gradient(circle at 90% 20%, rgba(139, 92, 246, 0.05) 0%, transparent 30%);
        pointer-events: none;
        z-index: 0;
    }}
    
    .mist-flow {{
        position: fixed; top: 0; right: -50%; width: 100%; height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.03), transparent);
        transform: skewX(-20deg);
        animation: flow 8s linear infinite;
        z-index: 1;
    }}
    @keyframes flow {{
        from {{ transform: translateX(0) skewX(-20deg); }}
        to {{ transform: translateX(-150%) skewX(-20deg); }}
    }}

    /* 3. 核心标题：Gian (动态扫光) */
    .hero-container {{
        position: relative;
        text-align: center;
        padding: 80px 0 40px 0;
        z-index: 2;
    }}
    
    .gian-title {{
        font-size: 10rem;
        font-weight: 800;
        letter-spacing: -5px;
        background: linear-gradient(90deg, #111, #fff, #111);
        background-size: 80% 100%;
        background-repeat: no-repeat;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine 5s linear infinite;
        margin: 0;
    }}
    @keyframes shine {{
        0% {{ background-position: -500%; }}
        100% {{ background-position: 500%; }}
    }}

    /* 4. 格子样式：Grok 悬浮玻璃 */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        height: 380px !important;
        background: rgba(15, 15, 15, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        backdrop-filter: blur(20px);
        overflow-y: auto !important;
        transition: border 0.3s;
    }}
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
        border: 1px solid rgba(56, 189, 248, 0.4) !important;
    }}

    /* 5. 异常链接样式 */
    .err-link {{ 
        color: #38bdf8 !important; 
        text-decoration: none; 
        border-bottom: 1px solid rgba(56, 189, 248, 0.2);
    }}
    
    /* 隐藏上传组件的默认样式以适配黑色 */
    .stFileUploader section {{
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px dashed rgba(255, 255, 255, 0.2) !important;
    }}
    </style>
    
    <div class="mist-container"></div>
    <div class="mist-flow"></div>
    
    <div class="hero-container">
        <h1 class="gian-title">Gian</h1>
        <p style="color: rgba(255,255,255,0.4); letter-spacing: 2px;">MATRIX LOGISTICS HUB</p>
    </div>
""", unsafe_allow_html=True)

# --- 2. 逻辑层 (稳健解析) ---
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
            else: error.append({'Category': cat, 'SN': sn, 'Reason': f'解析异常({len(parsed)}/{target_qty})'})
        except: continue
    return pd.DataFrame(valid), pd.DataFrame(error)

# --- 3. 渲染函数 ---
def render_item(cat, group, is_error):
    head_clr = "#f87171" if is_error else "#ffffff"
    body_html = ""
    if is_error:
        for _, r in group.iterrows():
            url = f"https://inflyway.com/kamelnet/#/kn/fly-link/orders/detail?id={r['SN']}"
            body_html += f'<div style="margin-bottom:8px; padding:8px; font-size:11px; border-left:2px solid #ef4444; background:rgba(239,68,68,0.02);"><a class="err-link" href="{url}" target="_blank">#{r["SN"][-6:]}</a><br><span style="color:#666;">{r["Reason"]}</span></div>'
    else:
        for clr, clr_data in group.groupby('Color'):
            size_stats = clr_data['Size'].value_counts().sort_index()
            size_badges = " ".join([f'<span>{s if s!="FREE" else ""}<b>×{q}</b></span>' for s, q in size_stats.items()])
            body_html += f'<div style="margin-bottom:10px; font-size:12px;"><div style="color:#38bdf8; font-weight:bold; margin-bottom:2px;">{clr}</div><div style="color:#888; font-size:11px;">{size_badges}</div></div>'
    
    st.markdown(f'''
        <div style="height:350px;">
            <div style="padding:15px 0; text-align:center; color:{head_clr}; font-weight:bold; letter-spacing:1px; border-bottom:1px solid rgba(255,255,255,0.05); position:sticky; top:0; background:rgba(15,15,15,0.9); z-index:5;">{cat}</div>
            <div style="padding:15px;">{body_html}</div>
        </div>
    ''', unsafe_allow_html=True)

# --- 4. 主程序 ---
file = st.file_uploader("", type=["xlsx"])
if file:
    v_df, e_df = process_data(file)
    t1, t2 = st.tabs(["EXISTING", "ANOMALY"])
    
    cols_count = 6 # 基准列数
    for tab, df, is_err in zip([t1, t2], [v_df, e_df], [False, True]):
        with tab:
            if not df.empty:
                cat_list = list(df.groupby('Category'))
                for i in range(0, len(cat_list), cols_count):
                    cols = st.columns(cols_count)
                    batch = cat_list[i : i + cols_count]
                    for col, (cat, g) in zip(cols, batch):
                        with col: render_item(cat, g, is_err)
