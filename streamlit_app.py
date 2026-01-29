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
    /* 🎭 深邃舞台光背景：调暗蓝色，拉高四周全黑的范围 */
    .stApp {{ 
        background: radial-gradient(circle at 50% 50%, #0c1e3d 0%, #020617 60%, #000000 100%) !important; 
        color: #ffffff; 
    }}
    header {{visibility: hidden;}}

    /* 🛡️ 用户面板 */
    .user-profile {{
        position: fixed; top: 25px; left: 25px; display: flex; align-items: center; gap: 12px; z-index: 1000000; 
        background: rgba(255, 255, 255, 0.05); padding: 8px 18px 8px 8px; border-radius: 50px;
        border: 1px solid rgba(56, 189, 248, 0.2); backdrop-filter: blur(15px);
        transition: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1); cursor: pointer;
    }}
    .user-profile:hover {{ transform: scale(1.05); box-shadow: 0 0 20px rgba(56, 189, 248, 0.4); border-color: #38bdf8; }}
    .avatar {{ width: 40px; height: 40px; border-radius: 50%; border: 2px solid #38bdf8; object-fit: cover; }}
    
    .hero-container {{ text-align: center; width: 100%; padding: 40px 0 20px 0; }}
    .grand-title {{
        display: block; font-family: 'Inter', sans-serif; font-size: 3.5rem !important; font-weight: 900; letter-spacing: 10px;
        background: linear-gradient(to bottom, #ffffff 40%, #38bdf8 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 40px;
        filter: drop-shadow(0 0 15px rgba(56, 189, 248, 0.3));
    }}

    /* 🧊 毛玻璃卡片系统 */
    .wide-card {{
        background: rgba(255, 255, 255, 0.03); 
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px; padding: 25px 30px; margin-bottom: 25px;
        display: flex; flex-direction: row; align-items: center; justify-content: space-between;
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        transition: all 0.6s cubic-bezier(0.22, 1, 0.36, 1);
        position: relative;
    }}

    /* ✨ 霓虹光蔓延效果 */
    .normal-card {{ border-left: 5px solid rgba(56, 189, 248, 0.5); }}
    .normal-card:hover {{
        background: rgba(56, 189, 248, 0.06);
        transform: translateY(-10px) scale(1.005);
        border-color: #38bdf8;
        box-shadow: 
            0 25px 50px rgba(0, 0, 0, 0.6),
            0 0 45px rgba(56, 189, 248, 0.35),
            0 -5px 25px rgba(56, 189, 248, 0.15);
        z-index: 10;
    }}

    .error-card {{ border-left: 5px solid rgba(245, 158, 11, 0.5); }}
    .error-card:hover {{
        background: rgba(245, 158, 11, 0.06);
        transform: translateY(-10px) scale(1.005);
        border-color: #f59e0b;
        box-shadow: 
            0 25px 50px rgba(0, 0, 0, 0.6),
            0 0 45px rgba(245, 158, 11, 0.35),
            0 -5px 25px rgba(245, 158, 11, 0.15);
        z-index: 10;
    }}

    /* ✨ SN 码显示：去除下划线 ✨ */
    .sn-pill {{
        padding: 5px 15px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; 
        transition: all 0.3s ease;
        text-decoration: none !important; /* 彻底去除下划线 */
        display: inline-block;
    }}
    .normal-sn {{ background: rgba(56, 189, 248, 0.1); color: #38bdf8 !important; border: 1px solid rgba(56, 189, 248, 0.2); }}
    .normal-sn:hover {{ background: #38bdf8 !important; color: #000 !important; box-shadow: 0 0 15px #38bdf8; }}
    .error-sn {{ background: rgba(245, 158, 11, 0.1); color: #f59e0b !important; border: 1px solid rgba(245, 158, 11, 0.3); }}
    .error-sn:hover {{ background: #f59e0b !important; color: #000 !important; box-shadow: 0 0 15px #f59e0b; }}

    /* 重制按钮 */
    div.stButton > button {{
        background: rgba(255, 255, 255, 0.03) !important;
        color: #38bdf8 !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        border-radius: 50px !important;
        padding: 12px 60px !important; font-weight: 800 !important;
        backdrop-filter: blur(10px) !important;
        transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
    }}
    div.stButton > button:hover {{ background: #38bdf8 !important; color: #000 !important; box-shadow: 0 0 30px rgba(56, 189, 248, 0.5); transform: translateY(-5px); }}

    /* 底部上传框 */
    [data-testid="stFileUploader"] {{
        position: fixed; bottom: 35px; left: 50%; transform: translateX(-50%); width: 450px; z-index: 9999;
        background: rgba(255, 255, 255, 0.08) !important; 
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        border-radius: 50px !important; padding: 15px 35px !important; 
        backdrop-filter: blur(25px) !important;
        box-shadow: 0 0 40px rgba(0, 0, 0, 0.7);
    }}
    [data-testid="stFileUploader"] label, [data-testid="stFileUploader"] small {{ display: none !important; }}
    </style>

    <div class="user-profile">
        <img src="https://avatars.githubusercontent.com/{GITHUB_USERNAME}" class="avatar">
        <div class="user-info">
            <div style="font-size: 0.9rem; font-weight: 900; color: #fff;">{GITHUB_USERNAME}</div>
            <div style="font-size: 0.6rem; color: #38bdf8; font-weight: bold;">● MIDNIGHT STAGE ACTIVE</div>
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

# --- 3. 渲染层 ---
upload_zone = st.empty()
uploaded_file = upload_zone.file_uploader("Upload", type=["xlsx"], key="deep_v1")

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
                    sizes_html = "".join([f'<div style="display:inline-flex; align-items:center; background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); border-radius:8px; padding:3px 12px; margin-right:8px;"><span style="color:#fff; font-size:0.8rem; font-weight:600;">{("" if s=="FREE" else s)}</span><span style="color:#38bdf8; font-weight:800; margin-left:5px;">{"×" if s!="FREE" else ""}{q}</span></div>' for s, q in size_counts.items()])
                    attr_html += f'<div style="display:flex; align-items:center; gap:20px; padding:8px 0;"><div style="color:#38bdf8; font-weight:700; font-size:1rem; min-width:100px;">{clr}</div>{sizes_html}</div>'
                
                sns = sorted(list(set(cat_group['SN'].tolist())))
                sn_html = "".join([f'<a href="{BASE_URL}{sn}" target="_blank" class="sn-pill normal-sn">{sn}</a>' for sn in sns])
                
                st.markdown(f'''
                    <div class="wide-card normal-card">
                        <div style="flex:1;"><div style="color:#38bdf8; font-weight:900; font-size:1.6rem; margin-bottom:12px; letter-spacing:1px;">{cat}</div>{attr_html}</div>
                        <div style="display:flex; flex-wrap:wrap; gap:8px; justify-content:flex-end; max-width:400px;">{sn_html}</div>
                    </div>
                ''', unsafe_allow_html=True)
            if st.button("↺ 重制系统"): st.rerun()

    with t2:
        if not e_df.empty:
            for _, err in e_df.iterrows():
                st.markdown(f'''
                    <div class="wide-card error-card">
                        <div style="flex:1;">
                            <div style="color:#f59e0b; font-weight:900; font-size:1.1rem;">LINE {err["Line"]} | {err["Reason"]}</div>
                            <div style="font-size:0.85rem; color:#cbd5e1; margin-top:8px; line-height:1.5;">{err["Content"]}</div>
                        </div>
                        <div style="display:flex; flex-wrap:wrap; gap:8px; justify-content:flex-end; max-width:400px;">
                            <a href="{BASE_URL}{err["SN"]}" target="_blank" class="sn-pill error-sn">{err["SN"]}</a>
                        </div>
                    </div>
                ''', unsafe_allow_html=True)
