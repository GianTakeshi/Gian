import streamlit as st
import pandas as pd
import re

# --- 1. 页面配置 ---
st.set_page_config(page_title="SKU 属性解析中枢", page_icon="🚀", layout="wide")

GITHUB_USERNAME = "GianTakeshi" 
BASE_URL = "https://inflyway.com/kamelnet/#/kn/fly-link/orders/detail?id="

# --- 2. 注入深度霓虹 CSS ---
st.markdown(f"""
    <style>
    /* 🎭 舞台底色 */
    .stApp {{ 
        background: radial-gradient(circle at 50% 50%, #0c1e3d 0%, #020617 60%, #000000 100%) !important; 
        color: #ffffff; 
    }}
    header {{visibility: hidden;}}

    /* 🛡️ 用户面板 - 头像呼吸灯 */
    @keyframes avatarPulse {{
        0% {{ box-shadow: 0 0 5px rgba(56, 189, 248, 0.4); border-color: rgba(56, 189, 248, 0.4); }}
        50% {{ box-shadow: 0 0 20px rgba(56, 189, 248, 0.8); border-color: rgba(56, 189, 248, 1); }}
        100% {{ box-shadow: 0 0 5px rgba(56, 189, 248, 0.4); border-color: rgba(56, 189, 248, 0.4); }}
    }}
    .user-profile {{
        position: fixed; top: 25px; left: 25px; display: flex; align-items: center; gap: 12px; z-index: 1000000; 
        background: rgba(255, 255, 255, 0.05); padding: 8px 20px 8px 8px; border-radius: 50px;
        border: 1px solid rgba(56, 189, 248, 0.3); backdrop-filter: blur(15px);
        transition: 0.2s; cursor: pointer;
    }}
    .user-profile:active {{ transform: scale(0.92); }}
    .avatar {{ 
        width: 40px; height: 40px; border-radius: 50%; border: 2px solid #38bdf8; 
        animation: avatarPulse 2.5s infinite ease-in-out; 
    }}
    
    .grand-title {{
        text-align: center; font-size: 3.5rem !important; font-weight: 900; letter-spacing: 10px;
        background: linear-gradient(to bottom, #ffffff 40%, #38bdf8 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 0 15px rgba(56, 189, 248, 0.4));
        margin: 40px 0;
    }}

    /* 🧊 霓虹卡片系统 */
    .wide-card {{
        background: rgba(255, 255, 255, 0.03); border-radius: 20px; padding: 25px 30px; margin-bottom: 25px;
        display: flex; flex-direction: row; align-items: center; justify-content: space-between;
        backdrop-filter: blur(15px); transition: all 0.5s cubic-bezier(0.2, 1, 0.3, 1);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }}
    /* 正常卡片霓虹光 */
    .normal-card {{ border-left: 5px solid #38bdf8; }}
    .normal-card:hover {{
        background: rgba(56, 189, 248, 0.08); transform: translateY(-5px);
        border-color: #38bdf8;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5), 0 0 20px rgba(56, 189, 248, 0.3);
    }}
    /* 异常卡片霓虹光 */
    .error-card {{ border-left: 5px solid #f59e0b; }}
    .error-card:hover {{
        background: rgba(245, 158, 11, 0.08); transform: translateY(-5px);
        border-color: #f59e0b;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5), 0 0 20px rgba(245, 158, 11, 0.3);
    }}

    /* 💊 SN 码霓虹特效 */
    .sn-pill {{ 
        padding: 6px 16px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; 
        transition: 0.3s; text-decoration: none !important; display: inline-block;
    }}
    .normal-sn {{ 
        background: rgba(56, 189, 248, 0.1); color: #38bdf8 !important; 
        border: 1px solid rgba(56, 189, 248, 0.3); 
    }}
    .normal-sn:hover {{ 
        background: #38bdf8 !important; color: #000 !important; 
        box-shadow: 0 0 15px #38bdf8; transform: scale(1.05);
    }}
    .error-sn {{ 
        background: rgba(245, 158, 11, 0.1); color: #f59e0b !important; 
        border: 1px solid rgba(245, 158, 11, 0.4); 
    }}
    .error-sn:hover {{ 
        background: #f59e0b !important; color: #000 !important; 
        box-shadow: 0 0 15px #f59e0b; transform: scale(1.05);
    }}

    /* 🔘 重制按钮 - 强光反馈 */
    div.stButton > button {{
        background: linear-gradient(145deg, rgba(56, 189, 248, 0.1), rgba(0,0,0,0.4)) !important;
        color: #38bdf8 !important; border: 1px solid #38bdf8 !important;
        border-radius: 50px !important; padding: 12px 60px !important;
        font-weight: 800 !important; letter-spacing: 2px;
        transition: all 0.3s !important; margin: 40px auto !important; display: block !important;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.2);
    }}
    div.stButton > button:hover {{
        background: #38bdf8 !important; color: #000 !important;
        box-shadow: 0 0 30px rgba(56, 189, 248, 0.6) !important;
        transform: translateY(-3px);
    }}
    div.stButton > button:active {{ transform: scale(0.95) !important; }}

    /* Tabs 样式优化 */
    .stTabs [data-baseweb="tab"] {{
        height: 38px !important; padding: 0 25px !important; border-radius: 50px !important;
        background: rgba(255, 255, 255, 0.03) !important; border: 1px solid rgba(255, 255, 255, 0.1) !important;
        transition: 0.3s !important;
    }}
    .stTabs [aria-selected="true"] {{
        border: 1px solid #38bdf8 !important; color: #38bdf8 !important;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.2);
    }}
    </style>
""", unsafe_allow_html=True)

# --- 3. 隐藏的逻辑触发器 (头像点击重置) ---
with st.sidebar:
    if st.button("RESET", key="trigger_reset"):
        st.rerun()

# 用户面板渲染
st.markdown(f"""
    <div class="user-profile" onclick="document.querySelector('button[kind=secondary]').click();">
        <img src="https://avatars.githubusercontent.com/{GITHUB_USERNAME}" class="avatar">
        <div style="font-size: 0.95rem; font-weight: 900; color: #fff; margin-left: 5px;">{GITHUB_USERNAME}</div>
    </div>
    <div class="hero-container"><h1 class="grand-title">SKU 属性解析中枢</h1></div>
""", unsafe_allow_html=True)

# --- 4. 数据解析逻辑 ---
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

# --- 5. 交互界面渲染 ---
upload_zone = st.empty()
uploaded_file = upload_zone.file_uploader("Upload", type=["xlsx"])

if uploaded_file:
    v_df, e_df = process_sku_logic(uploaded_file)
    upload_zone.empty() 
    
    t1, t2 = st.tabs(["💎 汇总数据流", "📡 异常拦截"])
    
    with t1:
        if not v_df.empty:
            for cat in sorted(v_df['Category'].unique()):
                cat_group = v_df[v_df['Category'] == cat]
                attr_html = ""
                for clr in sorted(cat_group['Color'].unique()):
                    clr_group = cat_group[cat_group['Color'] == clr]
                    size_counts = clr_group['Size'].value_counts().sort_index()
                    sizes_html = "".join([f"<div style='display:inline-flex; align-items:center; background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); border-radius:8px; padding:3px 12px; margin-right:8px;'><span style='color:#fff; font-size:0.8rem; font-weight:600;'>{(s if s!='FREE' else '')}</span><span style='color:#38bdf8; font-weight:800; margin-left:5px;'>{('×' if s!='FREE' else '')}{q}</span></div>" for s, q in size_counts.items()])
                    attr_html += f"<div style='display:flex; align-items:center; gap:20px; padding:8px 0;'><div style='color:#38bdf8; font-weight:700; font-size:1rem; min-width:100px;'>{clr}</div><div>{sizes_html}</div></div>"
                
                sns = sorted(list(set(cat_group['SN'].tolist())))
                sn_html = "".join([f'<a href="{BASE_URL}{sn}" target="_blank" class="sn-pill normal-sn">{sn}</a>' for sn in sns])
                st.markdown(f'<div class="wide-card normal-card"><div style="flex:1;"><div style="color:#38bdf8; font-weight:900; font-size:1.6rem; margin-bottom:12px; letter-spacing:1px;">{cat}</div>{attr_html}</div><div style="display:flex; flex-wrap:wrap; gap:8px; justify-content:flex-end; max-width:400px;">{sn_html}</div></div>', unsafe_allow_html=True)
            if st.button("↺ 重制系统", key="main_reset"): st.rerun()

    with t2:
        if not e_df.empty:
            for _, err in e_df.iterrows():
                sn_link = f'<a href="{BASE_URL}{err["SN"]}" target="_blank" class="sn-pill error-sn">{err["SN"]}</a>'
                st.markdown(f'<div class="wide-card error-card"><div style="flex:1;"><div style="color:#f59e0b; font-weight:900; font-size:1.1rem;">LINE {err["Line"]} | {err["Reason"]}</div><div style="font-size:0.85rem; color:#cbd5e1; margin-top:8px; line-height:1.5;">{err["Content"]}</div></div><div style="display:flex; flex-wrap:wrap; gap:8px; justify-content:flex-end; max-width:400px;">{sn_link}</div></div>', unsafe_allow_html=True)
