import streamlit as st
import pandas as pd
import re
import html

# --- 1. UI 视觉配置 (底层大字 + 强力毛玻璃) ---
st.set_page_config(page_title="Gian Matrix", page_icon="💎", layout="wide")

st.markdown(f"""
    <style>
    /* 1. 基础深邃黑 */
    .stApp {{
        background: #000000;
        color: #ffffff;
    }}
    header {{ visibility: hidden; }}

    /* 2. 背景层：Gian 大字 (置于最底层) */
    .background-gian {{
        position: fixed;
        bottom: 5%;
        left: 50%;
        transform: translateX(-50%);
        font-size: 25rem; /* 巨大占据感 */
        font-weight: 900;
        color: rgba(255, 255, 255, 0.03); /* 极低透明度，像暗纹一样 */
        letter-spacing: -10px;
        z-index: -2;
        user-select: none;
        white-space: nowrap;
    }}

    /* 3. 明显的动态流雾 (从右侧涌入) */
    .mist-glow {{
        position: fixed;
        top: 0;
        right: 0;
        width: 60%;
        height: 100%;
        background: radial-gradient(circle at 100% 50%, 
            rgba(56, 189, 248, 0.15) 0%, 
            rgba(139, 92, 246, 0.08) 30%, 
            transparent 70%);
        filter: blur(80px);
        animation: drift 10s ease-in-out infinite alternate;
        z-index: -1;
    }}
    @keyframes drift {{
        from {{ transform: translateX(10%) scale(1); opacity: 0.6; }}
        to {{ transform: translateX(-5%) scale(1.1); opacity: 0.9; }}
    }}

    /* 4. 上层元素：强力毛玻璃效果 */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: rgba(20, 20, 20, 0.4) !important; /* 降低透明度让背后的 Gian 隐约可见 */
        backdrop-filter: blur(25px) saturate(180%) !important; /* 强力毛玻璃 */
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 20px !important;
        height: 400px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
    }}

    /* Tab 导航毛玻璃 */
    .stTabs [data-baseweb="tab-list"] {{
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border-radius: 50px;
        padding: 5px 20px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        width: fit-content;
        margin: 0 auto 30px auto;
    }}

    /* 链接与文字细节 */
    .err-link {{ color: #38bdf8 !important; text-decoration: none; font-weight: 600; }}
    .cat-title {{
        font-size: 1.2rem;
        font-weight: 800;
        letter-spacing: 2px;
        color: #fff;
        text-shadow: 0 0 10px rgba(255,255,255,0.2);
    }}
    </style>
    
    <div class="background-gian">Gian</div>
    <div class="mist-glow"></div>
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
            else: error.append({'Category': cat, 'SN': sn, 'Reason': f'解析异常({len(parsed)}/{target_qty})'})
        except: continue
    return pd.DataFrame(valid), pd.DataFrame(error)

# --- 3. 渲染逻辑 ---
def render_item(cat, group, is_error):
    body_html = ""
    if is_error:
        for _, r in group.iterrows():
            url = f"https://inflyway.com/kamelnet/#/kn/fly-link/orders/detail?id={r['SN']}"
            body_html += f'''
                <div style="margin-bottom:12px; padding:10px; border-left:3px solid #ef4444; background:rgba(239,68,68,0.03); border-radius:4px;">
                    <a class="err-link" href="{url}" target="_blank">SN: {r['SN']}</a><br>
                    <span style="color:rgba(255,255,255,0.4); font-size:10px;">{r['Reason']}</span>
                </div>'''
    else:
        for clr, clr_data in group.groupby('Color'):
            size_stats = clr_data['Size'].value_counts().sort_index()
            size_badges = " ".join([f'<span style="background:rgba(255,255,255,0.05); padding:2px 8px; border-radius:4px; margin-right:5px;">{s if s!="FREE" else ""}<b>×{q}</b></span>' for s, q in size_stats.items()])
            body_html += f'''
                <div style="margin-bottom:15px; padding-bottom:8px; border-bottom:1px solid rgba(255,255,255,0.03);">
                    <div style="color:#38bdf8; font-weight:700; font-size:13px; margin-bottom:4px;">{clr}</div>
                    <div style="color:rgba(255,255,255,0.6); font-size:11px;">{size_badges}</div>
                </div>'''
    
    st.markdown(f'''
        <div style="height:370px; overflow-y:auto; padding-right:5px;">
            <div style="padding:20px 0; text-align:center; position:sticky; top:0; background:rgba(20,20,20,0.01); z-index:10;">
                <span class="cat-title">{cat}</span>
            </div>
            <div style="padding:10px;">{body_html}</div>
        </div>
    ''', unsafe_allow_html=True)

# --- 4. 主程序 ---
st.markdown("<div style='height:40px;'></div>", unsafe_allow_html=True) # 顶部留白
file = st.file_uploader("", type=["xlsx"])

if file:
    v_df, e_df = process_data(file)
    t1, t2 = st.tabs(["EXISTING DATA", "ANOMALY REPORTS"])
    
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
            else:
                st.info("No data available.")
