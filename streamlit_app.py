import streamlit as st
import pandas as pd
import re

# --- 1. 页面配置 ---
st.set_page_config(page_title="爆单", page_icon="🚀", layout="wide")

# 配置常量
GITHUB_USERNAME = "GianTakeshi" 
BASE_URL = "https://inflyway.com/kamelnet/#/kn/fly-link/orders/detail?id="
AVATAR_URL = f"https://avatars.githubusercontent.com/{GITHUB_USERNAME}"

# --- 2. 注入 CSS (仅针对颜色值做了 HDR 提亮处理) ---
st.markdown(f"""
    <style>
        /* 🎨 [平滑优化版] 背景：增加中间色阶，确保向四周平滑消隐至全黑 */
    .stApp {{ 
        background: radial-gradient(
            circle at 50% 45%, 
            #0c1e3d 0%, 
            #061126 25%, 
            #030814 50%, 
            #010308 75%, 
            #000000 100%
        ) !important; 
        color: #ffffff; 
        padding-top: 80px !important; 
    }}

    header {{visibility: hidden;}}

    /* ✨ 上传框呼吸：改用 color(display-p3 ...) 实现 HDR 高亮 */
    @keyframes uploader-glow {{
        0% {{ border-color: rgba(56, 189, 248, 0.2); box-shadow: 0 0 10px rgba(56, 189, 248, 0.1); }}
        50% {{ border-color: color(display-p3 0.22 0.74 0.97); box-shadow: 0 0 25px color(display-p3 0.22 0.74 0.97 / 0.5); }}
        100% {{ border-color: rgba(56, 189, 248, 0.2); box-shadow: 0 0 10px rgba(56, 189, 248, 0.1); }}
    }}

    /* ✨ 头像呼吸：HDR 提亮 */
    @keyframes avatar-breathing {{
        0% {{ box-shadow: 0 0 0 0 rgba(56, 189, 248, 0.4); transform: scale(1); }}
        50% {{ box-shadow: 0 0 20px 4px color(display-p3 0.22 0.74 0.97 / 0.8); transform: scale(1.05); }}
        100% {{ box-shadow: 0 0 0 0 rgba(56, 189, 248, 0.4); transform: scale(1); }}
    }}

    .user-profile {{
        position: fixed; top: 35px; left: 35px; display: flex; align-items: center; gap: 12px; z-index: 1000000; 
        background: rgba(255, 255, 255, 0.05); padding: 8px 20px 8px 8px; border-radius: 60px;
        border: 1.5px solid rgba(56, 189, 248, 0.2); backdrop-filter: blur(15px);
    }}
    .avatar {{ width: 38px; height: 38px; border-radius: 50%; border: 2px solid #38bdf8; animation: avatar-breathing 3s infinite ease-in-out; }}
    .user-name {{ font-size: 0.95rem; font-weight: 600; color: #fff; letter-spacing: 0.5px; }}

    .wide-card {{
        background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px; padding: 25px 30px; margin-bottom: 25px;
        display: flex; flex-direction: row; align-items: center; justify-content: space-between;
        backdrop-filter: blur(15px); transition: all 0.5s cubic-bezier(0.165, 0.84, 0.44, 1);
    }}
    .normal-card {{ border-left: 5px solid rgba(56, 189, 248, 0.4); }}
    /* 🧊 卡片悬停：加入 HDR 内发光 */
    .normal-card:hover {{ 
        transform: translateY(-8px); 
        border-color: color(display-p3 0.22 0.74 0.97); 
        box-shadow: 0 15px 35px rgba(0,0,0,0.5), inset 0 0 80px color(display-p3 0.22 0.74 0.97 / 0.25); 
    }}
    .error-card {{ border-left: 5px solid rgba(245, 158, 11, 0.4); }}
    /* 🧊 异常卡片悬停：加入 HDR 橙色发光 */
    .error-card:hover {{ 
        transform: translateY(-8px); 
        border-color: color(display-p3 0.96 0.62 0.04); 
        box-shadow: 0 15px 35px rgba(0,0,0,0.5), inset 0 0 80px color(display-p3 0.96 0.62 0.04 / 0.25); 
    }}

    .sn-pill {{ padding: 6px 14px; border-radius: 40px; font-size: 0.8rem; font-weight: 800; text-decoration: none !important; transition: all 0.3s ease; border: 1px solid transparent; }}
    .normal-sn {{ background: rgba(56, 189, 248, 0.08); color: #38bdf8 !important; border: 1px solid rgba(56, 189, 248, 0.3); }}
    /* 🏷️ SN 悬停：HDR 蓝 */
    .normal-sn:hover {{ background: color(display-p3 0.22 0.74 0.97) !important; color: #000000 !important; box-shadow: 0 0 20px color(display-p3 0.22 0.74 0.97 / 0.6); transform: scale(1.05); }}
    .error-sn-pill {{ background: rgba(245, 158, 11, 0.08); color: #f59e0b !important; border: 1px solid rgba(245, 158, 11, 0.3); }}
    .error-sn-pill:hover {{ background: color(display-p3 0.96 0.62 0.04) !important; color: #000000 !important; box-shadow: 0 0 20px color(display-p3 0.96 0.62 0.04 / 0.6); transform: scale(1.05); }}

    .stTabs {{ overflow: visible !important; }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 20px; background: transparent !important; padding: 30px 10px !important; margin-bottom: 10px; overflow: visible !important; }}
    .stTabs [data-baseweb="tab"] {{ height: 42px !important; padding: 0 30px !important; font-size: 1rem !important; border-radius: 40px !important; border: 1.5px solid rgba(255, 255, 255, 0.1) !important; background: rgba(255, 255, 255, 0.02) !important; color: rgba(255, 255, 255, 0.5) !important; transition: all 0.4s ease !important; position: relative; z-index: 10; }}
    /* 🚫 Tabs 选中：HDR 霓虹效果 */
    .stTabs [data-baseweb="tab"][aria-selected="true"]:nth-child(1) {{ color: color(display-p3 0.22 0.74 0.97) !important; border-color: color(display-p3 0.22 0.74 0.97) !important; background: rgba(56, 189, 248, 0.15) !important; box-shadow: 0 0 35px 8px color(display-p3 0.22 0.74 0.97 / 0.5) !important; }}
    .stTabs [data-baseweb="tab"][aria-selected="true"]:nth-child(2) {{ color: color(display-p3 0.96 0.62 0.04) !important; border-color: color(display-p3 0.96 0.62 0.04) !important; background: rgba(245, 158, 11, 0.15) !important; box-shadow: 0 0 35px 8px color(display-p3 0.96 0.62 0.04 / 0.5) !important; }}
    .stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {{ display: none !important; }}

    div.stButton > button {{ 
        background: rgba(56, 189, 248, 0.08) !important; color: #38bdf8 !important; 
        border: 1.5px solid rgba(56, 189, 248, 0.4) !important; border-radius: 40px !important; 
        padding: 10px 45px !important; font-weight: 800 !important; font-size: 1rem !important; 
        transition: all 0.4s ease !important; margin: 50px auto !important; display: block !important; 
    }}
    div.stButton > button:hover {{ background: color(display-p3 0.22 0.74 0.97) !important; color: #000000 !important; box-shadow: 0 0 30px 5px color(display-p3 0.22 0.74 0.97 / 0.5) !important; transform: scale(1.05); }}

    [data-testid="stFileUploader"] {{
        position: fixed; bottom: 100px; left: 50%; transform: translateX(-50%); 
        width: 520px; z-index: 9999;
        background: rgba(12, 30, 61, 0.65) !important; 
        border-radius: 24px !important; 
        padding: 20px !important; 
        backdrop-filter: blur(30px) !important;
        border: 1.5px solid rgba(56, 189, 248, 0.3) !important;
        animation: uploader-glow 4s infinite ease-in-out;
        box-shadow: 0 15px 45px rgba(0,0,0,0.7);
    }}
    .grand-title {{ display: inline-block; font-size: 3.5rem !important; font-weight: 900; letter-spacing: 8px; background: linear-gradient(to bottom, #ffffff 40%, #38bdf8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    </style>

    <div class="user-profile">
        <img src="{AVATAR_URL}" class="avatar">
        <div class="user-name">{GITHUB_USERNAME}</div>
    </div>
    <div style="text-align:center; margin-bottom:100px;"><h1 class="grand-title">祝王哥天天爆单</h1></div>
""", unsafe_allow_html=True)

# --- 3. 核心提取逻辑 (完全未动) ---
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

# --- 4. UI 渲染 (完全未动) ---
upload_zone = st.empty()
uploaded_file = upload_zone.file_uploader("", type=["xlsx"])

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
                    size_badges = [f'<div style="display:inline-flex; align-items:center; background:rgba(255,255,255,0.05); border:1.5px solid rgba(255,255,255,0.12); border-radius:8px; padding:4px 12px; margin-right:8px;"><span style="color:#fff; font-size:0.9rem; font-weight:800;">{(s if s!="FREE" else "")}</span><span style="color:#38bdf8; font-weight:800; font-size:0.9rem; margin-left:5px;">{("×" if s!="FREE" else "")}{q}</span></div>' for s, q in clr_group['Size'].value_counts().sort_index().items()]
                    attr_html_list.append(f'<div style="display:flex; align-items:center; gap:20px; padding:10px 0;"><div style="color:#38bdf8; font-weight:700; min-width:100px; font-size:1.1rem;">{clr}</div><div>{"".join(size_badges)}</div></div>')
                sn_html = "".join([f'<a href="{BASE_URL}{sn}" target="_blank" class="sn-pill normal-sn">{sn}</a>' for sn in sorted(list(set(cat_group['SN'].tolist())))])
                st.markdown(f'<div class="wide-card normal-card"><div style="flex:1;"><div style="color:#38bdf8; font-weight:900; font-size:1.8rem; margin-bottom:15px; letter-spacing:1px;">{cat}</div>{"".join(attr_html_list)}</div><div style="display:flex; flex-wrap:wrap; gap:8px; justify-content:flex-end; max-width:400px;">{sn_html}</div></div>', unsafe_allow_html=True)
            if st.button("↺ 刷新页面"): st.rerun()
    with t2:
        if not e_df.empty:
            for _, err in e_df.iterrows():
                sn_link = f'<a href="{BASE_URL}{err["SN"]}" target="_blank" class="sn-pill error-sn-pill">{err["SN"]}</a>'
                st.markdown(f'<div class="wide-card error-card"><div style="flex:1;"><div style="color:#f59e0b; font-weight:900; font-size:1.1rem;">LINE {err["Line"]} | {err["Reason"]}</div><div style="font-size:0.95rem; color:#cbd5e1; margin-top:8px; line-height:1.4;">{err["Content"]}</div></div><div>{sn_link}</div></div>', unsafe_allow_html=True)
