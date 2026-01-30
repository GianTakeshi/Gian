import streamlit as st
import pandas as pd
import re

# --- 1. 页面配置 ---
st.set_page_config(page_title="SKU 属性解析中枢", page_icon="🚀", layout="wide")

GITHUB_USERNAME = "GianTakeshi" 
BASE_URL = "https://inflyway.com/kamelnet/#/kn/fly-link/orders/detail?id="
AVATAR_URL = f"https://github.com/{GITHUB_USERNAME}.png"

# --- 2. 注入深度定制 CSS ---
st.markdown(f"""
    <style>
    /* 🎭 背景 */
    .stApp {{ 
        background: radial-gradient(circle at 50% 50%, #0c1e3d 0%, #020617 60%, #000000 100%) !important; 
        color: #ffffff; 
    }}
    header {{visibility: hidden;}}

    /* ✨ 新增：卡片淡入入场动画 */
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(20px); filter: blur(5px); }}
        to {{ opacity: 1; transform: translateY(0); filter: blur(0); }}
    }}

    /* 🛡️ 用户面板 */
    @keyframes avatarPulse {{
        0%, 100% {{ box-shadow: 0 0 5px rgba(56, 189, 248, 0.2); border-color: rgba(56, 189, 248, 0.3); }}
        50% {{ box-shadow: 0 0 20px rgba(56, 189, 248, 0.6); border-color: rgba(56, 189, 248, 0.8); }}
    }}
    .user-profile {{
        position: fixed; top: 25px; left: 25px; display: flex; align-items: center; gap: 12px; z-index: 1000000; 
        background: rgba(255, 255, 255, 0.05); padding: 8px 18px 8px 8px; border-radius: 50px;
        border: 1px solid rgba(56, 189, 248, 0.2); backdrop-filter: blur(15px);
    }}
    .avatar {{ width: 40px; height: 40px; border-radius: 50%; border: 2px solid #38bdf8; object-fit: cover; animation: avatarPulse 2.5s infinite ease-in-out; }}
    
    .grand-title {{
        text-align: center; font-size: 3.5rem !important; font-weight: 900; letter-spacing: 10px;
        background: linear-gradient(to bottom, #ffffff 40%, #38bdf8 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 40px 0;
    }}

    /* 🧊 毛玻璃卡片系统 (已加入入场动画) */
    .wide-card {{
        background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px; padding: 25px 30px; margin-bottom: 25px;
        display: flex; flex-direction: row; align-items: center; justify-content: space-between;
        backdrop-filter: blur(15px); -webkit-backdrop-filter: blur(15px);
        
        /* 💡 注入入场动画：0.5s 淡入并在位移 */
        animation: fadeIn 0.5s ease-out forwards;
        
        transition: all 0.5s cubic-bezier(0.2, 1, 0.3, 1);
    }}
    .normal-card {{ border-left: 5px solid rgba(56, 189, 248, 0.5); }}
    .normal-card:hover {{
        background: rgba(56, 189, 248, 0.06); transform: translateY(-8px); border-color: #38bdf8;
        box-shadow: 0 15px 40px rgba(0,0,0,0.5), 0 0 30px rgba(56, 189, 248, 0.2);
    }}
    .error-card {{ border-left: 5px solid rgba(245, 158, 11, 0.5); }}
    .error-card:hover {{
        background: rgba(245, 158, 11, 0.06); transform: translateY(-8px); border-color: #f59e0b;
        box-shadow: 0 15px 40px rgba(0,0,0,0.5), 0 0 30px rgba(245, 158, 11, 0.2);
    }}

    /* 💊 药丸 Tabs */
    .stTabs [data-baseweb="tab-highlight"] {{ display: none !important; }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 12px; background: transparent !important; }}
    .stTabs [data-baseweb="tab"] {{
        height: 35px !important; padding: 0 25px !important; border-radius: 50px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important; background: rgba(255, 255, 255, 0.02) !important;
        color: rgba(255, 255, 255, 0.4) !important; transition: 0.3s ease !important;
    }}
    .stTabs [data-baseweb="tab"][aria-selected="true"]:nth-child(1) {{
        color: #38bdf8 !important; border-color: #38bdf8 !important; background: rgba(56, 189, 248, 0.1) !important;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.2);
    }}
    .stTabs [data-baseweb="tab"][aria-selected="true"]:nth-child(2) {{
        color: #f59e0b !important; border-color: #f59e0b !important; background: rgba(245, 158, 11, 0.1) !important;
        box-shadow: 0 0 15px rgba(245, 158, 11, 0.2);
    }}

    /* SN 药丸 */
    .sn-pill {{ padding: 5px 15px; border-radius: 50px !important; font-size: 0.75rem; font-weight: 600; text-decoration: none !important; transition: 0.2s; }}
    .normal-sn {{ background: rgba(56, 189, 248, 0.1); color: #38bdf8 !important; border: 1px solid rgba(56, 189, 248, 0.2); }}
    .normal-sn:hover {{ background: #38bdf8 !important; color: #000 !important; }}

    [data-testid="stFileUploader"] {{
        position: fixed; bottom: 35px; left: 50%; transform: translateX(-50%); width: 450px; z-index: 9999;
        background: rgba(255, 255, 255, 0.08) !important; border: 1px solid rgba(56, 189, 248, 0.3) !important;
        border-radius: 50px !important; padding: 15px 35px !important; backdrop-filter: blur(25px) !important;
    }}
    </style>

    <div class="user-profile">
        <img src="{AVATAR_URL}" class="avatar">
        <div class="user-info">
            <div style="font-size: 0.9rem; font-weight: 900; color: #fff;">{GITHUB_USERNAME}</div>
            <div style="font-size: 0.6rem; color: #38bdf8; font-weight: bold;">● QUANTUM ANALYZER</div>
        </div>
    </div>
    <div style="text-align:center;"><h1 class="grand-title">SKU 属性解析中枢</h1></div>
""", unsafe_allow_html=True)

# --- 3. 核心逻辑 ---
def process_sku_logic(uploaded_file):
    COLOR_REG, SIZE_REG = r'(?i)Color[:：\s]*([a-zA-Z0-9\-_/]+)', r'(?i)Size[:：\s]*([a-zA-Z0-9\-\s/]+?)(?=\s*(?:Color|Size|$|[,;，；]))'
    SIZE_MAP = {'HIGH ANKLE SOCKS': 'L', 'KNEE-HIGH SOCKS': 'M'}
    df = pd.read_excel(uploaded_file, engine='openpyxl')
    cols = df.columns
    all_normal_data, all_error_rows = [], []
    for index, row in df.iterrows():
        c_raw = str(row[cols[2]]).strip()
        if not c_raw or c_raw == 'nan': continue
        cat = c_raw.split(' ')[0].upper()
        if cat.startswith('WZ'): cat = 'WZ'
        g_text, i_val, sn = str(row[cols[6]]), str(row[cols[8]]), str(row[cols[0]])
        i_qty = int(re.findall(r'\d+', i_val)[0]) if re.findall(r'\d+', i_val) else 0
        if ';' in c_raw or '；' in c_raw:
            all_error_rows.append({'SN': sn, 'Line': index+2, 'Reason': "品类冲突", 'Content': g_text})
            continue
        chunks = [c.strip() for c in re.split(r'[;；]', g_text) if c.strip()]
        data_pairs = []
        for chunk in chunks:
            c_m, s_m = re.search(COLOR_REG, chunk), re.search(SIZE_REG, chunk)
            if c_m:
                clr = c_m.group(1).strip().upper()
                raw_s = s_m.group(1).strip().upper() if s_m else "FREE"
                data_pairs.append((clr, SIZE_MAP.get(raw_s, raw_s)))
        if len(data_pairs) == i_qty and i_qty > 0:
            for c_val, s_val in data_pairs:
                all_normal_data.append({'Category': cat, 'Color': c_val, 'Size': s_val, 'SN': sn})
        else:
            all_error_rows.append({'SN': sn, 'Line': index+2, 'Reason': f"数量异常({len(data_pairs)}/{i_qty})", 'Content': g_text})
    return pd.DataFrame(all_normal_data), pd.DataFrame(all_error_rows)

# --- 4. 渲染 ---
uploaded_file = st.file_uploader("Upload", type=["xlsx"])

if uploaded_file:
    v_df, e_df = process_sku_logic(uploaded_file)
    t1, t2 = st.tabs(["💎 汇总数据流", "📡 异常拦截"])
    
    with t1:
        if not v_df.empty:
            for cat in sorted(v_df['Category'].unique()):
                cat_group = v_df[v_df['Category'] == cat]
                attr_html = "".join([f"<div style='display:flex; align-items:center; gap:20px; padding:8px 0;'><div style='color:#38bdf8; font-weight:700; min-width:100px;'>{clr}</div><div>{''.join([f'<div style=\"display:inline-flex; align-items:center; background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); border-radius:8px; padding:3px 12px; margin-right:8px;\"><span style=\"color:#fff; font-size:0.8rem;\">{(s if s!=\"FREE\" else \"\")}</span><span style=\"color:#38bdf8; font-weight:800; margin-left:5px;\">{(\"×\" if s!=\"FREE\" else \"\")}{q}</span></div>' for s, q in cat_group[cat_group['Color']==clr]['Size'].value_counts().sort_index().items()])}</div></div>" for clr in sorted(cat_group['Color'].unique())])
                sn_html = "".join([f'<a href=\"{BASE_URL}{sn}\" target=\"_blank\" class=\"sn-pill normal-sn\">{sn}</a>' for sn in sorted(list(set(cat_group['SN'].tolist())))])
                st.markdown(f'<div class=\"wide-card normal-card\"><div style=\"flex:1;\"><div style=\"color:#38bdf8; font-weight:900; font-size:1.6rem; margin-bottom:12px;\">{cat}</div>{attr_html}</div><div style=\"display:flex; flex-wrap:wrap; gap:8px; justify-content:flex-end; max-width:400px;\">{sn_html}</div></div>', unsafe_allow_html=True)
            if st.button("↺ 重制系统"): st.rerun()

    with t2:
        if not e_df.empty:
            for _, err in e_df.iterrows():
                sn_link = f'<a href=\"{BASE_URL}{err[\"SN\"]}\" target=\"_blank\" class=\"sn-pill normal-sn\" style=\"color:#f59e0b !important; border-color:#f59e0b !important;\">{err[\"SN\"]}</a>'
                st.markdown(f'<div class=\"wide-card error-card\"><div style=\"flex:1;\"><div style=\"color:#f59e0b; font-weight:900;\">LINE {err[\"Line"]} | {err[\"Reason"]}</div><div style=\"font-size:0.85rem; color:#cbd5e1; margin-top:8px;\">{err[\"Content\"]}</div></div><div>{sn_link}</div></div>', unsafe_allow_html=True)
