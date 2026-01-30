import streamlit as st
import pandas as pd
import re

# --- 1. 页面配置 ---
st.set_page_config(page_title="SKU 属性解析中枢", page_icon="🚀", layout="wide")

GITHUB_USERNAME = "GianTakeshi" 
BASE_URL = "https://inflyway.com/kamelnet/#/kn/fly-link/orders/detail?id="
# 动态头像地址
AVATAR_URL = f"https://github.com/{GITHUB_USERNAME}.png"

# --- 2. 注入核心 CSS ---
st.markdown(f"""
    <style>
    /* 🎭 背景 */
    .stApp {{ 
        background: radial-gradient(circle at 50% 50%, #0c1e3d 0%, #020617 60%, #000000 100%) !important; 
        color: #ffffff; 
    }}
    header {{visibility: hidden;}}

    /* 🛡️ 用户面板修复 (补全动画) */
    @keyframes avatarPulse {{
        0% {{ box-shadow: 0 0 5px rgba(56, 189, 248, 0.2); border-color: rgba(56, 189, 248, 0.3); }}
        50% {{ box-shadow: 0 0 20px rgba(56, 189, 248, 0.6); border-color: rgba(56, 189, 248, 0.8); }}
        100% {{ box-shadow: 0 0 5px rgba(56, 189, 248, 0.2); border-color: rgba(56, 189, 248, 0.3); }}
    }}
    .user-profile {{
        position: fixed; top: 25px; left: 25px; display: flex; align-items: center; gap: 12px; z-index: 1000000; 
        background: rgba(255, 255, 255, 0.05); padding: 8px 18px 8px 8px; border-radius: 50px;
        border: 1px solid rgba(56, 189, 248, 0.2); backdrop-filter: blur(15px);
    }}
    .avatar {{ 
        width: 40px; height: 40px; border-radius: 50%; border: 2px solid #38bdf8; 
        object-fit: cover; animation: avatarPulse 2.5s infinite ease-in-out; 
    }}

    .grand-title {{
        text-align: center; font-family: 'Inter', sans-serif; font-size: 3.5rem !important; font-weight: 900; letter-spacing: 10px;
        background: linear-gradient(to bottom, #ffffff 40%, #38bdf8 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 40px 0;
        filter: drop-shadow(0 0 15px rgba(56, 189, 248, 0.3));
    }}

    /* 💊 强效胶囊 Tab 锁定 (button 元素) */
    div[data-baseweb="tab-list"] {{ gap: 16px !important; background: transparent !important; }}
    div[data-baseweb="tab-highlight"] {{ display: none !important; }}
    
    button[data-baseweb="tab"] {{
        border-radius: 50px !important; 
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        background-color: rgba(255, 255, 255, 0.03) !important;
        padding: 8px 30px !important;
        height: 42px !important;
        transition: all 0.3s ease !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        background-color: rgba(56, 189, 248, 0.15) !important;
        border: 1.5px solid #38bdf8 !important;
        color: #38bdf8 !important;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.3) !important;
    }}

    /* 🧊 卡片浮动效果 */
    .wide-card {{
        background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px; padding: 25px 30px; margin-bottom: 25px;
        display: flex; flex-direction: row; align-items: center; justify-content: space-between;
        backdrop-filter: blur(15px);
        transition: all 0.4s cubic-bezier(0.2, 1, 0.3, 1) !important;
    }}
    .wide-card:hover {{
        transform: translateY(-12px) !important;
        border-color: rgba(56, 189, 248, 0.6) !important;
        box-shadow: 0 20px 40px rgba(0,0,0,0.5), 0 0 30px rgba(56, 189, 248, 0.25) !important;
    }}
    .normal-card {{ border-left: 5px solid rgba(56, 189, 248, 0.5); }}

    /* SN 药丸 */
    .sn-pill {{ padding: 6px 18px; border-radius: 50px !important; font-size: 0.75rem; font-weight: 600; text-decoration: none !important; transition: 0.2s; }}
    .normal-sn {{ background: rgba(56, 189, 248, 0.1); color: #38bdf8 !important; border: 1px solid rgba(56, 189, 248, 0.2); }}

    /* 上传框固定 */
    [data-testid="stFileUploader"] {{
        position: fixed; bottom: 35px; left: 50%; transform: translateX(-50%); width: 450px; z-index: 9999;
        background: rgba(255, 255, 255, 0.08) !important; border: 1px solid rgba(56, 189, 248, 0.3) !important;
        border-radius: 50px !important; padding: 15px 35px !important; backdrop-filter: blur(25px) !important;
    }}
    </style>

    <div class="user-profile">
        < img src="{AVATAR_URL}" class="avatar">
        <div style="font-size: 0.9rem; font-weight: 900; color: #fff; margin-left: 10px;">{GITHUB_USERNAME}</div>
    </div>
    <div class="grand-title">SKU 属性解析中枢</div>
""", unsafe_allow_html=True)

# --- 3. 逻辑处理 (维持原样) ---
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

# --- 4. 渲染界面 ---
uploaded_file = st.file_uploader("Upload", type=["xlsx"])

if uploaded_file:
    v_df, e_df = process_sku_logic(uploaded_file)
    t1, t2 = st.tabs(["💎 汇总数据流", "📡 异常拦截"])
    
    with t1:
        if not v_df.empty:
            cats = sorted(v_df['Category'].unique())
            for cat in cats:
                cat_group = v_df[v_df['Category'] == cat]
                attr_html = ""
                for clr in sorted(cat_group['Color'].unique()):
                    clr_group = cat_group[cat_group['Color'] == clr]
                    size_counts = clr_group['Size'].value_counts().sort_index()
                    sizes_html = "".join([f"<div style='display:inline-flex; align-items:center; background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); border-radius:8px; padding:3px 12px; margin-right:8px;'><span style='color:#fff; font-size:0.8rem;'>{s}</span><span style='color:#38bdf8; font-weight:800; margin-left:5px;'>×{q}</span></div>" for s, q in size_counts.items()])
                    attr_html += f"<div style='display:flex; align-items:center; gap:20px; padding:6px 0;'><div style='color:#38bdf8; font-weight:700; min-width:100px;'>{clr}</div><div>{sizes_html}</div></div>"
                
                sns = sorted(list(set(cat_group['SN'].tolist())))
                sn_html = "".join([f'<a href=" " target="_blank" class="sn-pill normal-sn">{sn}</a >' for sn in sns])
                
                st.markdown(f'''<div class="wide-card normal-card"><div style="flex:1;">
                    <div style="color:#38bdf8; font-weight:900; font-size:1.6rem; margin-bottom:10px;">{cat}</div>{attr_html}</div>
                    <div style="display:flex; flex-wrap:wrap; gap:8px; justify-content:flex-end; max-width:400px;">{sn_html}</div></div>''', unsafe_allow_html=True)
            if st.button("↺ 重制系统"): st.rerun()

    with t2:
        if not e_df.empty:
            for _, err in e_df.iterrows():
                sn_link = f'<a href="{BASE_URL}{err["SN"]}" target="_blank" class="sn-pill normal-sn" style="color:#f59e0b !important; border-color:#f59e0b !important;">{err["SN"]}</a >'
                st.markdown(f'''<div class="wide-card" style="border-left: 5px solid #f59e0b;"><div style="flex:1;">
                    <div style="color:#f59e0b; font-weight:900;">LINE {err["Line"]} | {err["Reason"]}</div>
                    <div style="font-size:0.85rem; color:#cbd5e1; margin-top:8px;">{err["Content"]}</div></div>
                    <div>{sn_link}</div></div>''', unsafe_allow_html=True)
