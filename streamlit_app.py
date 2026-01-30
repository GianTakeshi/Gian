import streamlit as st
import pandas as pd
import re

# --- 1. 页面配置 ---
st.set_page_config(page_title="SKU 属性解析中枢", page_icon="🚀", layout="wide")

GITHUB_USERNAME = "GianTakeshi" 
BASE_URL = "https://inflyway.com/kamelnet/#/kn/fly-link/orders/detail?id="
AVATAR_URL = f"https://avatars.githubusercontent.com/{GITHUB_USERNAME}"

# --- 2. 注入深度定制 CSS ---
st.markdown(f"""
    <style>
    /* 🎭 整体布局 */
    .stApp {{ 
        background: radial-gradient(circle at 50% 50%, #0c1e3d 0%, #020617 60%, #000000 100%) !important; 
        color: #ffffff; 
        padding-top: 80px !important; 
    }}
    header {{visibility: hidden;}}

    /* 🟢 头像呼吸动画 */
    @keyframes avatar-breathing {{
        0% {{ box-shadow: 0 0 0 0 rgba(56, 189, 248, 0.4); transform: scale(1); }}
        50% {{ box-shadow: 0 0 20px 4px rgba(56, 189, 248, 0.7); transform: scale(1.05); }}
        100% {{ box-shadow: 0 0 0 0 rgba(56, 189, 248, 0.4); transform: scale(1); }}
    }}

    .user-profile {{
        position: fixed; top: 35px; left: 35px; display: flex; align-items: center; gap: 12px; z-index: 1000000; 
        background: rgba(255, 255, 255, 0.05); padding: 8px 20px 8px 8px; border-radius: 60px;
        border: 1.5px solid rgba(56, 189, 248, 0.2); backdrop-filter: blur(15px);
    }}
    .avatar {{ 
        width: 38px; height: 38px; border-radius: 50%; border: 2px solid #38bdf8; 
        animation: avatar-breathing 3s infinite ease-in-out; 
    }}

    /* 🧊 卡片样式 */
    .wide-card {{
        background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px; padding: 20px 25px; margin-bottom: 25px;
        display: flex; flex-direction: row; align-items: center; justify-content: space-between;
        backdrop-filter: blur(15px); transition: all 0.5s cubic-bezier(0.165, 0.84, 0.44, 1);
    }}
    .normal-card {{ border-left: 4px solid rgba(56, 189, 248, 0.4); }}
    .normal-card:hover {{ transform: translateY(-8px); border-color: #38bdf8; box-shadow: 0 15px 35px rgba(0,0,0,0.5), inset 0 0 80px rgba(56, 189, 248, 0.25); }}
    .error-card {{ border-left: 4px solid rgba(245, 158, 11, 0.4); }}
    .error-card:hover {{ transform: translateY(-8px); border-color: #f59e0b; box-shadow: 0 15px 35px rgba(0,0,0,0.5), inset 0 0 80px rgba(245, 158, 11, 0.25); }}

    /* 🏷️ SN 标签 */
    .sn-pill {{ padding: 4px 12px; border-radius: 40px; font-size: 0.7rem; font-weight: 600; text-decoration: none !important; }}
    .normal-sn {{ background: rgba(56, 189, 248, 0.08); color: #38bdf8 !important; border: 1px solid rgba(56, 189, 248, 0.2); }}
    .error-sn-pill {{ background: rgba(245, 158, 11, 0.08); color: #f59e0b !important; border: 1px solid rgba(245, 158, 11, 0.2); }}

    /* 🚫 Tabs 切换按钮特效：解决遮挡问题 */
    .stTabs {{
        overflow: visible !important; /* 核心：允许光晕溢出 */
    }}
    .stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {{ display: none !important; }}
    
    .stTabs [data-baseweb="tab-list"] {{ 
        gap: 20px; background: transparent !important; 
        padding: 30px 10px !important; /* 增加内边距给光晕留空间 */
        margin-bottom: 10px;
        overflow: visible !important;
    }}
    
    .stTabs [data-baseweb="tab"] {{ 
        height: 38px !important; padding: 0 25px !important; font-size: 0.95rem !important; 
        border-radius: 40px !important; border: 1.5px solid rgba(255, 255, 255, 0.1) !important; 
        background: rgba(255, 255, 255, 0.02) !important; color: rgba(255, 255, 255, 0.5) !important; 
        transition: all 0.4s ease !important;
        position: relative;
        z-index: 10;
    }}

    /* 🔵 选定“汇总数据”：强化扩散光晕 */
    .stTabs [data-baseweb="tab"][aria-selected="true"]:nth-child(1) {{ 
        color: #38bdf8 !important; 
        border-color: #38bdf8 !important; 
        background: rgba(56, 189, 248, 0.15) !important; 
        box-shadow: 0 0 35px 8px rgba(56, 189, 248, 0.5), 0 0 15px rgba(56, 189, 248, 0.3) !important;
    }}

    /* 🟠 选定“异常拦截”：强化扩散光晕 */
    .stTabs [data-baseweb="tab"][aria-selected="true"]:nth-child(2) {{ 
        color: #f59e0b !important; 
        border-color: #f59e0b !important; 
        background: rgba(245, 158, 11, 0.15) !important; 
        box-shadow: 0 0 35px 8px rgba(245, 158, 11, 0.5), 0 0 15px rgba(245, 158, 11, 0.3) !important;
    }}

    .grand-title {{ font-size: 3rem !important; font-weight: 900; letter-spacing: 8px; background: linear-gradient(to bottom, #ffffff 40%, #38bdf8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    [data-testid="stFileUploader"] {{ position: fixed; bottom: 30px; left: 50%; transform: translateX(-50%); width: 380px; z-index: 9999; background: rgba(255, 255, 255, 0.1) !important; border-radius: 40px !important; backdrop-filter: blur(20px) !important; }}
    </style>

    <div class="user-profile">
        <img src="{AVATAR_URL}" class="avatar">
        <div class="user-name">{GITHUB_USERNAME}</div>
    </div>
    <div style="text-align:center; margin-bottom:40px;"><h1 class="grand-title">SKU 属性解析中枢</h1></div>
""", unsafe_allow_html=True)

# --- 3. 核心逻辑 (维持原样) ---
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
upload_zone = st.empty()
uploaded_file = upload_zone.file_uploader("Upload", type=["xlsx"])

if uploaded_file:
    v_df, e_df = process_sku_logic(uploaded_file)
    upload_zone.empty() 
    t1, t2 = st.tabs(["汇总数据", "异常拦截"])
    
    with t1:
        if not v_df.empty:
            for cat in sorted(v_df['Category'].unique()):
                cat_group = v_df[v_df['Category'] == cat]
                attr_html_list = []
                for clr in sorted(cat_group['Color'].unique()):
                    clr_group = cat_group[cat_group['Color'] == clr]
                    size_badges = [f'<div style="display:inline-flex; align-items:center; background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); border-radius:6px; padding:2px 10px; margin-right:6px;"><span style="color:#fff; font-size:0.75rem; font-weight:800;">{(s if s!="FREE" else "")}</span><span style="color:#38bdf8; font-weight:800; margin-left:4px;">{("×" if s!="FREE" else "")}{q}</span></div>' for s, q in clr_group['Size'].value_counts().sort_index().items()]
                    attr_html_list.append(f'<div style="display:flex; align-items:center; gap:15px; padding:6px 0;"><div style="color:#38bdf8; font-weight:700; min-width:80px; font-size:0.9rem;">{clr}</div><div>{"".join(size_badges)}</div></div>')
                sn_html = "".join([f'<a href="{BASE_URL}{sn}" target="_blank" class="sn-pill normal-sn">{sn}</a>' for sn in sorted(list(set(cat_group['SN'].tolist())))])
                st.markdown(f'<div class="wide-card normal-card"><div style="flex:1;"><div style="color:#38bdf8; font-weight:900; font-size:1.4rem; margin-bottom:10px;">{cat}</div>{"".join(attr_html_list)}</div><div style="display:flex; flex-wrap:wrap; gap:6px; justify-content:flex-end; max-width:350px;">{sn_html}</div></div>', unsafe_allow_html=True)
            if st.button("↺ 重制系统"): st.rerun()

    with t2:
        if not e_df.empty:
            for _, err in e_df.iterrows():
                sn_link = f'<a href="{BASE_URL}{err["SN"]}" target="_blank" class="sn-pill error-sn-pill">{err["SN"]}</a>'
                st.markdown(f'<div class="wide-card error-card"><div style="flex:1;"><div style="color:#f59e0b; font-weight:900; font-size:0.9rem;">LINE {err["Line"]} | {err["Reason"]}</div><div style="font-size:0.8rem; color:#cbd5e1; margin-top:5px;">{err["Content"]}</div></div><div>{sn_link}</div></div>', unsafe_allow_html=True)
