import streamlit as st
import pandas as pd
import re

# --- 1. 页面配置 ---
st.set_page_config(page_title="SKU 属性解析中枢", page_icon="🚀", layout="wide")

GITHUB_USERNAME = "GianTakeshi" 
BASE_URL = "https://inflyway.com/kamelnet/#/kn/fly-link/orders/detail?id="
AVATAR_URL = f"https://avatars.githubusercontent.com/{GITHUB_USERNAME}"

# --- 2. 注入极致定制 CSS ---
st.markdown(f"""
    <style>
    .stApp {{ 
        background: radial-gradient(circle at 50% 50%, #0c1e3d 0%, #020617 60%, #000000 100%) !important; 
        color: #ffffff; 
        padding: 80px 50px 0 50px !important; 
    }}
    header {{visibility: hidden;}}

    /* 🛡️ 用户面板 */
    .user-profile {{
        position: fixed; top: 35px; left: 35px; display: flex; align-items: center; gap: 12px; z-index: 10000; 
        background: rgba(255, 255, 255, 0.18); padding: 8px 24px 8px 8px; border-radius: 60px;
        border: 1px solid rgba(255, 255, 255, 0.35); backdrop-filter: blur(20px);
    }}
    .avatar {{ 
        width: 38px; height: 38px; border-radius: 50%; border: 2px solid #38bdf8; 
        animation: avatar-pulse 3s infinite ease-in-out; 
    }}
    @keyframes avatar-pulse {{
        0% {{ transform: scale(1); box-shadow: 0 0 5px rgba(56, 189, 248, 0.4); }}
        50% {{ transform: scale(1.1); box-shadow: 0 0 15px rgba(56, 189, 248, 0.8); }}
        100% {{ transform: scale(1); box-shadow: 0 0 5px rgba(56, 189, 248, 0.4); }}
    }}

    /* 🧊 卡片基础 - 强制动画 */
    .wide-card {{ 
        background: rgba(255, 255, 255, 0.03) !important; 
        border: 1px solid rgba(255, 255, 255, 0.1) !important; 
        border-radius: 24px !important; 
        padding: 30px !important; 
        margin-bottom: 25px !important; 
        display: flex !important; 
        transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1) !important;
        position: relative;
    }}

    /* 🔵 汇总数据卡片：重度蓝光内陷 & 浮动 */
    .normal-card:hover {{ 
        transform: translateY(-8px) !important;
        border-color: #38bdf8 !important;
        box-shadow: 
            0 30px 60px rgba(0,0,0,0.6), 
            0 0 30px rgba(56, 189, 248, 0.4), 
            inset 0 0 60px rgba(56, 189, 248, 0.4),
            inset 0 0 120px 20px rgba(56, 189, 248, 0.25) !important;
    }}

    /* 🟠 异常拦截卡片：重度橙光内陷 & 浮动 */
    .error-card:hover {{ 
        transform: translateY(-8px) !important;
        border-color: #f59e0b !important;
        box-shadow: 
            0 30px 60px rgba(0,0,0,0.6), 
            0 0 30px rgba(245, 158, 11, 0.4), 
            inset 0 0 60px rgba(245, 158, 11, 0.4),
            inset 0 0 120px 20px rgba(245, 158, 11, 0.25) !important;
    }}

    /* 🏷️ SN 气泡：绝对不放大，纯光感交互 */
    .sn-pill {{ 
        padding: 6px 16px !important; border-radius: 40px !important; font-size: 0.75rem !important; 
        font-weight: 700 !important; border: 1.5px solid transparent !important; margin: 4px !important; 
        display: inline-block !important; text-decoration: none !important; 
        transition: all 0.2s ease !important;
    }}
    .normal-sn {{ background: rgba(56, 189, 248, 0.1) !important; color: #38bdf8 !important; border-color: rgba(56, 189, 248, 0.4) !important; }}
    .normal-sn:hover {{ background: #38bdf8 !important; color: #000 !important; box-shadow: 0 0 20px #38bdf8 !important; transform: none !important; }}
    
    .error-sn-pill {{ background: rgba(245, 158, 11, 0.1) !important; color: #f59e0b !important; border-color: rgba(245, 158, 11, 0.4) !important; }}
    .error-sn-pill:hover {{ background: #f59e0b !important; color: #000 !important; box-shadow: 0 0 20px #f59e0b !important; transform: none !important; }}

    /* 🚫 Tabs 修正：让光效跟 Tab 走 */
    .stTabs [data-baseweb="tab"][aria-selected="true"]:nth-child(1) {{ color: #38bdf8 !important; border-bottom: 2px solid #38bdf8 !important; }}
    .stTabs [data-baseweb="tab"][aria-selected="true"]:nth-child(2) {{ color: #f59e0b !important; border-bottom: 2px solid #f59e0b !important; }}

    .grand-title {{ font-size: 3.5rem !important; font-weight: 900; letter-spacing: 10px; background: linear-gradient(to bottom, #ffffff 30%, #38bdf8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    </style>
""", unsafe_allow_html=True)

st.markdown(f"""
    <div class="user-profile">
        <img src="{AVATAR_URL}" class="avatar">
        <div class="user-name">{GITHUB_USERNAME}</div>
    </div>
    <div style="text-align:center; margin-bottom:50px;"><h1 class="grand-title">SKU 属性解析中枢</h1></div>
""", unsafe_allow_html=True)

# --- 3. 逻辑函数 (保持稳定) ---
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
            all_error_rows.append({'SN': sn, 'Line': index+2, 'Reason': "多个商品", 'Content': g_text})
            continue
        chunks = [c.strip() for c in re.split(r'[;；]', g_text) if c.strip()]
        data_pairs = []
        for chunk in chunks:
            c_m, s_m = re.search(COLOR_REG, chunk), re.search(SIZE_REG, chunk)
            if c_m: clr = c_m.group(1).strip().upper(); raw_s = s_m.group(1).strip().upper() if s_m else "FREE"; data_pairs.append((clr, SIZE_MAP.get(raw_s, raw_s)))
        if len(data_pairs) == i_qty and i_qty > 0:
            for c_val, s_val in data_pairs: all_normal_data.append({'Category': cat, 'Color': c_val, 'Size': s_val, 'SN': sn})
        else: all_error_rows.append({'SN': sn, 'Line': index+2, 'Reason': f"数量异常({len(data_pairs)}/{i_qty})", 'Content': g_text})
    return pd.DataFrame(all_normal_data), pd.DataFrame(all_error_rows)

# --- 4. 渲染 ---
uploaded_file = st.file_uploader("Upload SKU Data", type=["xlsx"])

if uploaded_file:
    v_df, e_df = process_sku_logic(uploaded_file)
    t1, t2 = st.tabs(["汇总数据", "异常拦截"])
    
    with t1:
        if not v_df.empty:
            for cat in sorted(v_df['Category'].unique()):
                cat_group = v_df[v_df['Category'] == cat]
                attr_html = ""
                for clr in sorted(cat_group['Color'].unique()):
                    clr_group = cat_group[cat_group['Color'] == clr]
                    size_badges = "".join([f'<div style="display:inline-flex; align-items:center; background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); border-radius:6px; padding:2px 10px; margin-right:6px;"><span style="color:#fff; font-size:0.75rem;">{(s if s!="FREE" else "")}</span><span style="color:#38bdf8; font-weight:800; margin-left:4px;">{("×" if s!="FREE" else "")}{q}</span></div>' for s, q in clr_group['Size'].value_counts().sort_index().items()])
                    attr_html += f'<div style="display:flex; align-items:center; gap:15px; padding:6px 0;"><div style="color:#38bdf8; font-weight:700; min-width:80px;">{clr}</div><div>{size_badges}</div></div>'
                
                sn_html = "".join([f'<a href="{BASE_URL}{sn}" target="_blank" class="sn-pill normal-sn">{sn}</a>' for sn in sorted(list(set(cat_group['SN'].tolist())))])
                
                # 关键：手动拼接 HTML 确保 class 准确挂载
                card_template = f"""
                <div class="wide-card normal-card">
                    <div style="flex:1;">
                        <div style="color:#38bdf8; font-weight:900; font-size:1.4rem; margin-bottom:10px;">{cat}</div>
                        {attr_html}
                    </div>
                    <div style="display:flex; flex-wrap:wrap; gap:6px; justify-content:flex-end; max-width:350px;">
                        {sn_html}
                    </div>
                </div>
                """
                st.markdown(card_template, unsafe_allow_html=True)
        if st.button("↺ 重制系统", key="reset1"): st.rerun()

    with t2:
        if not e_df.empty:
            for _, err in e_df.iterrows():
                sn_link = f'<a href="{BASE_URL}{err["SN"]}" target="_blank" class="sn-pill error-sn-pill">{err["SN"]}</a>'
                error_template = f"""
                <div class="wide-card error-card">
                    <div style="flex:1;">
                        <div style="color:#f59e0b; font-weight:900; font-size:1rem;">LINE {err["Line"]} | {err["Reason"]}</div>
                        <div style="font-size:0.85rem; color:#cbd5e1; margin-top:5px;">{err["Content"]}</div>
                    </div>
                    <div>{sn_link}</div>
                </div>
                """
                st.markdown(error_template, unsafe_allow_html=True)
