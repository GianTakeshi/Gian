import streamlit as st
import pandas as pd
import re

# --- 1. 页面配置 ---
st.set_page_config(page_title="SKU 属性解析中枢", page_icon="🚀", layout="wide")

GITHUB_USERNAME = "GianTakeshi" 
BASE_URL = "https://inflyway.com/kamelnet/#/kn/fly-link/orders/detail?id="
AVATAR_URL = f"https://github.com/{GITHUB_USERNAME}.png"

# --- 2. 注入深度定制 CSS (流光与霓虹增强) ---
st.markdown(f"""
    <style>
    /* 🎭 背景 */
    .stApp {{ 
        background: radial-gradient(circle at 50% 50%, #0c1e3d 0%, #020617 60%, #000000 100%) !important; 
        color: #ffffff; 
    }}
    header {{visibility: hidden;}}

    /* 🛡️ 用户面板 */
    @keyframes avatarPulse {{
        0%, 100% {{ box-shadow: 0 0 5px rgba(56, 189, 248, 0.3); border-color: rgba(56, 189, 248, 0.3); }}
        50% {{ box-shadow: 0 0 20px rgba(56, 189, 248, 0.7); border-color: rgba(56, 189, 248, 0.9); }}
    }}
    .user-profile {{
        position: fixed; top: 25px; left: 25px; display: flex; align-items: center; gap: 12px; z-index: 1000000; 
        background: rgba(255, 255, 255, 0.05); padding: 8px 18px 8px 8px; border-radius: 50px;
        border: 1px solid rgba(56, 189, 248, 0.2); backdrop-filter: blur(15px);
    }}
    .avatar {{ width: 40px; height: 40px; border-radius: 50%; border: 2px solid #38bdf8; object-fit: cover; animation: avatarPulse 2.5s infinite ease-in-out; }}

    /* 🧊 流光卡片核心动画 */
    @keyframes rotateBorder {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}

    .wide-card {{
        position: relative;
        background: rgba(10, 20, 40, 0.8); /* 稍暗以突出边缘 */
        border-radius: 20px; padding: 25px 30px; margin-bottom: 25px;
        display: flex; flex-direction: row; align-items: center; justify-content: space-between;
        overflow: hidden; /* 裁剪流光 */
        transition: all 0.5s cubic-bezier(0.25, 1, 0.5, 1);
        border: 1px solid rgba(255, 255, 255, 0.05);
    }}

    /* 流光层 - 仅在 Hover 时显现增强 */
    .wide-card::before {{
        content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
        background: conic-gradient(transparent, transparent, transparent, #38bdf8);
        animation: rotateBorder 4s linear infinite;
        opacity: 0; transition: opacity 0.5s; z-index: 0;
    }}
    .error-card::before {{ background: conic-gradient(transparent, transparent, transparent, #f59e0b); }}

    .wide-card:hover::before {{ opacity: 1; }}

    /* 内层遮罩 - 保持内容清晰 */
    .wide-card::after {{
        content: ''; position: absolute; inset: 2px;
        background: rgba(7, 12, 24, 0.95); border-radius: 18px; z-index: 1;
    }}

    .card-content {{ position: relative; z-index: 2; flex: 1; display: flex; align-items: center; justify-content: space-between; width: 100%; }}

    .wide-card:hover {{
        transform: translateY(-10px);
        box-shadow: 0 0 30px rgba(56, 189, 248, 0.2);
    }}

    /* 💊 药丸 Tabs (严格保持基准版) */
    .stTabs [data-baseweb="tab-highlight"] {{ display: none !important; }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 12px; background: transparent !important; }}
    .stTabs [data-baseweb="tab"] {{
        height: 35px !important; padding: 0 25px !important; border-radius: 50px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important; background: rgba(255, 255, 255, 0.02) !important;
        color: rgba(255, 255, 255, 0.4) !important; transition: 0.3s;
    }}
    .stTabs [data-baseweb="tab"]:nth-child(1)[aria-selected="true"] {{
        color: #38bdf8 !important; border-color: #38bdf8 !important; background: rgba(56, 189, 248, 0.1) !important;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.3);
    }}
    .stTabs [data-baseweb="tab"]:nth-child(2)[aria-selected="true"] {{
        color: #f59e0b !important; border-color: #f59e0b !important; background: rgba(245, 158, 11, 0.1) !important;
        box-shadow: 0 0 15px rgba(245, 158, 11, 0.3);
    }}

    /* SN 药丸 */
    .sn-pill {{ padding: 5px 15px; border-radius: 50px !important; font-size: 0.75rem; text-decoration: none !important; transition: 0.3s; }}
    .normal-sn {{ background: rgba(56, 189, 248, 0.1); color: #38bdf8 !important; border: 1px solid rgba(56, 189, 248, 0.2); }}
    .normal-sn:hover {{ background: #38bdf8 !important; color: #000 !important; box-shadow: 0 0 15px #38bdf8; }}

    .grand-title {{
        text-align: center; font-size: 3.5rem !important; font-weight: 900; letter-spacing: 10px;
        background: linear-gradient(to bottom, #ffffff 40%, #38bdf8 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 40px 0;
    }}

    [data-testid="stFileUploader"] {{
        position: fixed; bottom: 35px; left: 50%; transform: translateX(-50%); width: 450px; z-index: 9999;
        background: rgba(255, 255, 255, 0.08) !important; border: 1px solid rgba(56, 189, 248, 0.3) !important;
        border-radius: 50px !important; padding: 15px 35px !important; backdrop-filter: blur(25px) !important;
    }}
    </style>

    <div class="user-profile">
        <img src="{AVATAR_URL}" class="avatar">
        <div style="font-size: 0.9rem; font-weight: 900; color: #fff;">{GITHUB_USERNAME}</div>
    </div>
    <div class="grand-title">SKU 属性解析中枢</div>
""", unsafe_allow_html=True)

# --- 3. 核心逻辑 (与基准版一致) ---
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
                attr_html = ""
                for clr in sorted(cat_group['Color'].unique()):
                    clr_group = cat_group[cat_group['Color'] == clr]
                    size_counts = clr_group['Size'].value_counts().sort_index()
                    sizes_html = "".join([f"<div style='display:inline-flex; align-items:center; background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); border-radius:8px; padding:3px 12px; margin-right:8px;'><span style='color:#fff; font-size:0.8rem; font-weight:600;'>{s if s!='FREE' else ''}</span><span style='color:#38bdf8; font-weight:800; margin-left:5px;'>{'×' if s!='FREE' else ''}{q}</span></div>" for s, q in size_counts.items()])
                    attr_html += f"<div style='display:flex; align-items:center; gap:20px; padding:8px 0;'><div style='color:#38bdf8; font-weight:700; min-width:100px;'>{clr}</div><div>{sizes_html}</div></div>"
                
                sns = sorted(list(set(cat_group['SN'].tolist())))
                sn_html = "".join([f'<a href="{BASE_URL}{sn}" target="_blank" class="sn-pill normal-sn">{sn}</a>' for sn in sns])
                
                # 注意这里嵌套了 card-content 层以配合流光效果
                st.markdown(f'''
                    <div class="wide-card">
                        <div class="card-content">
                            <div style="flex:1;">
                                <div style="color:#38bdf8; font-weight:900; font-size:1.6rem; margin-bottom:12px;">{cat}</div>
                                {attr_html}
                            </div>
                            <div style="display:flex; flex-wrap:wrap; gap:8px; justify-content:flex-end; max-width:400px;">{sn_html}</div>
                        </div>
                    </div>
                ''', unsafe_allow_html=True)

    with t2:
        if not e_df.empty:
            for _, err in e_df.iterrows():
                sn_link = f'<a href="{BASE_URL}{err["SN"]}" target="_blank" class="sn-pill normal-sn" style="color:#f59e0b !important; border-color:#f59e0b !important;">{err["SN"]}</a>'
                st.markdown(f'''
                    <div class="wide-card error-card">
                        <div class="card-content">
                            <div style="flex:1;">
                                <div style="color:#f59e0b; font-weight:900;">LINE {err["Line"]} | {err["Reason"]}</div>
                                <div style="font-size:0.85rem; color:#cbd5e1; margin-top:8px;">{err["Content"]}</div>
                            </div>
                            <div>{sn_link}</div>
                        </div>
                    </div>
                ''', unsafe_allow_html=True)
