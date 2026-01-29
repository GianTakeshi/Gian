import streamlit as st
import pandas as pd
import re
import html

# --- 1. UI 视觉配置 (底层大字 + 强力毛玻璃) ---
st.set_page_config(page_title="Gian Matrix", page_icon="💎", layout="wide")

st.markdown(f"""
    <style>
    /* 基础背景：纯黑 */
    .stApp {{
        background-color: #000000 !important;
        color: #ffffff;
    }}
    header {{ visibility: hidden; }}

    /* 背景层：Gian 大字 */
    .background-gian {{
        position: fixed;
        bottom: 8%;
        left: 50%;
        transform: translateX(-50%);
        font-size: clamp(10rem, 25vw, 30rem); /* 随屏幕缩放 */
        font-weight: 900;
        color: rgba(255, 255, 255, 0.05); /* 稍微调亮一点，防止全黑 */
        letter-spacing: -10px;
        z-index: -2;
        user-select: none;
        white-space: nowrap;
        pointer-events: none;
    }}

    /* 动态流雾：右侧发光 */
    .mist-glow {{
        position: fixed;
        top: 0;
        right: 0;
        width: 70%;
        height: 100%;
        background: radial-gradient(circle at 100% 50%, 
            rgba(56, 189, 248, 0.12) 0%, 
            rgba(139, 92, 246, 0.05) 30%, 
            transparent 70%);
        filter: blur(80px);
        animation: drift 12s ease-in-out infinite alternate;
        z-index: -1;
    }}
    @keyframes drift {{
        from {{ transform: translateX(10%); opacity: 0.5; }}
        to {{ transform: translateX(-5%); opacity: 0.8; }}
    }}

    /* 上层毛玻璃格子 */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: rgba(20, 20, 20, 0.6) !important;
        backdrop-filter: blur(20px) saturate(160%) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important;
        height: 400px !important;
    }}

    /* 自定义上传组件样式 - 让它在黑夜里亮起来 */
    .stFileUploader {{
        max-width: 600px;
        margin: 100px auto !important;
        background: rgba(255,255,255,0.02);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(56, 189, 248, 0.2);
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
            else: error.append({'Category': cat, 'SN': sn, 'Reason': f'数量不符({len(parsed)}/{target_qty})'})
        except: continue
    return pd.DataFrame(valid), pd.DataFrame(error)

# --- 3. 渲染逻辑 ---
def render_item(cat, group, is_error):
    body_html = ""
    if is_error:
        for _, r in group.iterrows():
            url = f"https://inflyway.com/kamelnet/#/kn/fly-link/orders/detail?id={r['SN']}"
            body_html += f'''<div style="margin-bottom:12px; padding:10px; border-left:3px solid #ef4444; background:rgba(239,68,68,0.03); border-radius:4px;"><a style="color:#38bdf8; text-decoration:none; font-weight:600;" href="{url}" target="_blank">SN: {r['SN']}</a><br><span style="color:rgba(255,255,255,0.4); font-size:10px;">{r['Reason']}</span></div>'''
    else:
        for clr, clr_data in group.groupby('Color'):
            size_stats = clr_data['Size'].value_counts().sort_index()
            size_badges = " ".join([f'<span style="background:rgba(255,255,255,0.08); padding:2px 8px; border-radius:4px; margin-right:5px;">{s if s!="FREE" else ""}<b>×{q}</b></span>' for s, q in size_stats.items()])
            body_html += f'''<div style="margin-bottom:15px; padding-bottom:8px; border-bottom:1px solid rgba(255,255,255,0.03);"><div style="color:#38bdf8; font-weight:700; font-size:13px; margin-bottom:4px;">{clr}</div><div style="color:rgba(255,255,255,0.6); font-size:11px;">{size_badges}</div></div>'''
    
    st.markdown(f'''<div style="height:370px; overflow-y:auto;"><div style="padding:20px 0; text-align:center; position:sticky; top:0; background:rgba(20,20,20,0.01); z-index:10;"><span style="font-weight:800; letter-spacing:2px; font-size:1.1rem;">{cat}</span></div><div style="padding:10px;">{body_html}</div></div>''', unsafe_allow_html=True)

# --- 4. 主程序 ---
file = st.file_uploader("DROP LOGISTICS EXCEL HERE", type=["xlsx"])

if file:
    # 只要上传了文件，就把上传框顶上去，腾出空间显示矩阵
    st.markdown("<style>.stFileUploader { margin-top: 20px !important; }</style>", unsafe_allow_html=True)
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
            else: st.info("No data found.")
