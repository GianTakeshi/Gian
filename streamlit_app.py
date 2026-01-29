import streamlit as st
import pandas as pd
import re

# --- 1. UI 配置与全局样式 ---
st.set_page_config(page_title="GianTakeshi | Hub", page_icon="🚀", layout="wide")

GITHUB_USERNAME = "GianTakeshi" 
BASE_URL = "https://inflyway.com/kamelnet/#/kn/fly-link/orders/detail?id="

# 注入 CSS
st.markdown(f"""
    <style>
    .stApp {{ background: radial-gradient(circle at 50% 50%, #1e293b, #010409); color: #ffffff; }}
    header {{visibility: hidden;}}

    /* 🛡️ 用户面板 */
    .user-profile {{
        position: fixed; top: 25px; left: 25px; display: flex; align-items: center; gap: 12px; z-index: 1000000; 
        background: rgba(255, 255, 255, 0.05); padding: 6px 16px 6px 6px; border-radius: 50px;
        border: 1px solid rgba(56, 189, 248, 0.3); backdrop-filter: blur(10px);
    }}
    .avatar {{ width: 40px; height: 40px; border-radius: 50%; border: 2px solid #38bdf8; object-fit: cover; }}
    .user-name {{ font-size: 0.95rem; font-weight: 600; color: #fff; letter-spacing: 1.2px; }}
    
    .hero-container {{ text-align: center; width: 100%; padding: 60px 0 20px 0; }}
    .grand-title {{
        display: block; font-family: 'Inter', sans-serif; font-size: 3.2rem !important; font-weight: 900; letter-spacing: 8px;
        background: linear-gradient(to bottom, #ffffff 30%, #38bdf8 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 30px;
    }}

    /* 📦 卡片交互动效 */
    .wide-card {{
        background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px; padding: 20px 25px; margin-bottom: 15px;
        display: flex; flex-direction: row; align-items: center; justify-content: space-between; gap: 30px;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        cursor: default;
    }}
    .normal-card {{ border-left: 6px solid #38bdf8; }}
    .error-card {{ border-left: 6px solid #f59e0b; background: rgba(245, 158, 11, 0.05); }}

    /* ✨ 悬浮与点击反馈 ✨ */
    .wide-card:hover {{
        background: rgba(56, 189, 248, 0.08);
        transform: translateY(-5px) scale(1.002);
        box-shadow: 0 10px 30px rgba(56, 189, 248, 0.2);
        border-color: rgba(56, 189, 248, 0.5);
    }}
    .wide-card:active {{
        transform: translateY(-1px) scale(0.995);
        filter: brightness(1.2);
    }}

    .main-info {{ flex: 1; }}
    .cat-header {{ color: #38bdf8; font-weight: 900; font-size: 1.3rem; margin-bottom: 8px; }}
    .attr-row {{ display: flex; align-items: center; gap: 15px; padding: 4px 0; }}
    .color-label {{ color: #38bdf8; font-weight: 700; font-size: 0.9rem; min-width: 90px; }}
    
    .size-box {{
        display: inline-flex; align-items: center;
        background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 6px; padding: 2px 10px; margin-right: 6px;
    }}
    .qty-text {{ color: #38bdf8; font-weight: 800; font-size: 0.85rem; }}

    /* ✨ SN 极右对齐与发光效果 ✨ */
    .sn-side {{ display: flex; flex-wrap: wrap; gap: 6px; justify-content: flex-end; max-width: 450px; min-width: 200px; }}
    .sn-pill {{
        padding: 3px 12px; background: rgba(56, 189, 248, 0.05);
        color: #38bdf8 !important; border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 20px; 
        text-decoration: none !important; font-size: 0.7rem; font-weight: 600;
        transition: all 0.3s ease;
    }}
    .sn-pill:hover {{ 
        background: #38bdf8; color: #000 !important; 
        box-shadow: 0 0 15px #38bdf8;
        transform: scale(1.1);
    }}

    /* ✨ 强力霓虹上传框 ✨ */
    [data-testid="stFileUploader"] {{
        position: fixed; bottom: 30px; left: 50%; transform: translateX(-50%); width: 420px; z-index: 9999;
        background: rgba(255, 255, 255, 0.15) !important; 
        border: 2px solid rgba(56, 189, 248, 0.5) !important;
        border-radius: 50px !important; padding: 10px 30px !important; backdrop-filter: blur(25px);
        box-shadow: 0 0 30px rgba(56, 189, 248, 0.4);
        transition: 0.4s;
    }}
    [data-testid="stFileUploader"]:hover {{
        box-shadow: 0 0 50px rgba(56, 189, 248, 0.7);
        border-color: #38bdf8 !important;
    }}
    [data-testid="stFileUploader"] label, [data-testid="stFileUploader"] small {{ display: none !important; }}

    /* 按钮动效 */
    div.stButton > button {{
        background: rgba(56, 189, 248, 0.05) !important; color: #38bdf8 !important;
        border: 2px solid rgba(56, 189, 248, 0.4) !important; border-radius: 50px !important;
        padding: 10px 40px !important; margin: 30px auto !important; display: block !important;
        transition: 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    }}
    div.stButton > button:hover {{
        background: #38bdf8 !important; color: #000 !important;
        box-shadow: 0 0 25px rgba(56, 189, 248, 0.5);
        transform: translateY(-3px);
    }}
    </style>

    <div class="user-profile">
        <img src="https://avatars.githubusercontent.com/{GITHUB_USERNAME}" class="avatar">
        <div class="user-info">
            <div class="user-name">{GITHUB_USERNAME}</div>
            <div style="font-size: 0.6rem; color: #10b981; font-weight: bold;">● CONSOLIDATED V5.0</div>
        </div>
    </div>
    <div class="hero-container"><h1 class="grand-title">属性看板中枢</h1></div>
""", unsafe_allow_html=True)

# --- 2. 逻辑层 ---
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
            all_error_rows.append({'SN': sn, 'Line': index+2, 'Reason': "品类冲突", 'Content': c_raw})
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

# --- 3. 渲染层 ---
uploaded_file = st.file_uploader("Upload", type=["xlsx"], key="v5_final")
if uploaded_file:
    v_df, e_df = process_sku_logic(uploaded_file)
    t1, t2 = st.tabs(["💎 汇总数据流", "📡 异常拦截"])
    with t1:
        if not v_df.empty:
            # ✨ 品类强力合并渲染逻辑 ✨
            for cat in sorted(v_df['Category'].unique()):
                cat_group = v_df[v_df['Category'] == cat]
                attr_html = ""
                for clr in sorted(cat_group['Color'].unique()):
                    clr_group = cat_group[cat_group['Color'] == clr]
                    size_counts = clr_group['Size'].value_counts().sort_index()
                    # ✨ 核心：FREE 隐藏逻辑
                    sizes_html = "".join([f'<div class="size-box"><span style="color:#fff; font-size:0.8rem; font-weight:600;">{("" if s=="FREE" else s)}</span><span class="qty-text">{"×" if s!="FREE" else ""}{q}</span></div>' for s, q in size_counts.items()])
                    attr_html += f'<div class="attr-row"><div class="color-label">{clr}</div>{sizes_html}</div>'
                
                # ✨ SN 去重并放在右侧
                sn_list = sorted(list(set(cat_group['SN'].tolist())))
                sn_html = "".join([f'<a href="{BASE_URL}{sn}" target="_blank" class="sn-pill">{sn}</a>' for sn in sn_list])
                
                st.markdown(f'''
                    <div class="wide-card normal-card">
                        <div class="main-info">
                            <div class="cat-header">{cat}</div>
                            {attr_html}
                        </div>
                        <div class="sn-side">{sn_html}</div>
                    </div>
                ''', unsafe_allow_html=True)
            if st.button("↺ 重新部署系统"): st.rerun()

    with t2:
        if not e_df.empty:
            for _, err in e_df.iterrows():
                st.markdown(f'''
                    <div class="wide-card error-card">
                        <div class="main-info">
                            <div style="color:#f59e0b; font-weight:900;">LINE {err["Line"]} | {err["Reason"]}</div>
                            <div style="font-size:0.8rem; color:#94a3b8; margin-top:5px;">{err["Content"]}</div>
                        </div>
                        <div class="sn-side">
                            <a href="{BASE_URL}{err["SN"]}" target="_blank" class="sn-pill" style="color:#f59e0b !important; border-color:#f59e0b;">{err["SN"]}</a>
                        </div>
                    </div>
                ''', unsafe_allow_html=True)
