import streamlit as st
import pandas as pd
import re

# --- 1. UI 配置与全局样式 ---
st.set_page_config(page_title="GianTakeshi | Hub", page_icon="🚀", layout="wide")

GITHUB_USERNAME = "GianTakeshi" 
BASE_URL = "https://inflyway.com/kamelnet/#/kn/fly-link/orders/detail?id="

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

    /* 📦 品类大框布局 */
    .wide-card {{
        background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px; padding: 25px; margin-bottom: 25px;
        display: flex; flex-direction: column; 
        transition: all 0.3s ease;
    }}
    .normal-card {{ border-left: 6px solid #38bdf8; }}
    .normal-card:hover {{ background: rgba(56, 189, 248, 0.04); transform: translateY(-3px); }}

    .cat-header {{ color: #38bdf8; font-weight: 900; font-size: 1.5rem; margin-bottom: 15px; letter-spacing: 1px; }}
    
    /* 属性行布局 */
    .attr-row {{ 
        display: flex; align-items: center; gap: 20px; 
        padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.05); 
    }}
    .color-label {{ color: #38bdf8; font-weight: 700; font-size: 0.95rem; min-width: 100px; }}
    
    .size-box {{
        display: inline-flex; align-items: center;
        background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 6px; padding: 3px 12px; margin-right: 8px;
    }}
    .size-text {{ color: #ffffff; font-weight: 600; font-size: 0.85rem; }}
    .qty-text {{ color: #38bdf8; font-weight: 800; font-size: 0.85rem; margin-left: 6px; }}

    /* 🛡️ SN 码平铺区（放在大框最后） */
    .sn-footer {{ 
        display: flex; flex-wrap: wrap; gap: 8px; 
        margin-top: 20px; padding-top: 15px; 
        border-top: 1px dashed rgba(255,255,255,0.1); 
    }}
    .sn-pill {{
        padding: 4px 14px; background: rgba(56, 189, 248, 0.1);
        color: #38bdf8 !important; border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 20px; 
        text-decoration: none !important; font-size: 0.75rem; font-weight: 600; transition: 0.2s;
    }}
    .sn-pill:hover {{ background: rgba(56, 189, 248, 0.25); border-color: #38bdf8; }}

    /* 悬浮上传框 */
    [data-testid="stFileUploader"] {{
        position: fixed; bottom: 60px; left: 50%; transform: translateX(-50%); width: 400px; z-index: 9999;
        background: rgba(255, 255, 255, 0.12) !important; border: 1px solid rgba(56, 189, 248, 0.3) !important;
        border-radius: 50px !important; padding: 10px 30px !important; backdrop-filter: blur(25px);
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.2);
    }}
    div.stButton > button {{
        background: rgba(56, 189, 248, 0.05) !important; color: #38bdf8 !important;
        border: 2px solid rgba(56, 189, 248, 0.4) !important; border-radius: 50px !important;
        padding: 12px 60px !important; margin: 40px auto !important; display: block !important;
    }}
    </style>

    <div class="user-profile">
        <img src="https://avatars.githubusercontent.com/{GITHUB_USERNAME}" class="avatar">
        <div class="user-info">
            <div class="user-name">{GITHUB_USERNAME}</div>
            <div style="font-size: 0.6rem; color: #10b981; font-weight: bold;">● DATA CONSOLIDATED</div>
        </div>
    </div>
    <div class="hero-container"><h1 class="grand-title">属性看板中枢</h1></div>
""", unsafe_allow_html=True)

# --- 2. 核心逻辑 ---
def process_sku_logic(uploaded_file):
    COLOR_REG, SIZE_REG = r'(?i)Color[:：\s]*([a-zA-Z0-9\-_/]+)', r'(?i)Size[:：\s]*([a-zA-Z0-9\-\s/]+?)(?=\s*(?:Color|Size|$|[,;，；]))'
    SIZE_MAP = {'HIGH ANKLE SOCKS': 'L', 'KNEE-HIGH SOCKS': 'M'}
    
    df = pd.read_excel(uploaded_file, engine='openpyxl')
    cols = df.columns
    all_normal_data = []
    
    for index, row in df.iterrows():
        c_raw = str(row[cols[2]]).strip()
        if not c_raw or c_raw == 'nan': continue
        cat = c_raw.split(' ')[0].upper()
        if cat.startswith('WZ'): cat = 'WZ'
        
        g_text, i_val, sn = str(row[cols[6]]), str(row[cols[8]]), str(row[cols[0]])
        i_qty = int(re.findall(r'\d+', i_val)[0]) if re.findall(r'\d+', i_val) else 0
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
    
    return pd.DataFrame(all_normal_data)

# --- 3. 渲染层 ---
upload_placeholder = st.empty()
uploaded_file = upload_placeholder.file_uploader("Upload", type=["xlsx"], key="uploader")

if uploaded_file:
    v_df = process_sku_logic(uploaded_file)
    upload_placeholder.empty()
    
    if not v_df.empty:
        # ✨ 顶层品类循环 ✨
        for cat in sorted(v_df['Category'].unique()):
            cat_group = v_df[v_df['Category'] == cat]
            
            # 生成内部属性行 HTML
            inner_rows_html = ""
            for clr in sorted(cat_group['Color'].unique()):
                clr_group = cat_group[cat_group['Color'] == clr]
                size_counts = clr_group['Size'].value_counts().sort_index()
                size_html = "".join([f'<div class="size-box"><span class="size-text">{s}</span><span class="qty-text">×{q}</span></div>' for s, q in size_counts.items()])
                inner_rows_html += f'<div class="attr-row"><div class="color-label">{clr}</div><div style="flex:1;">{size_html}</div></div>'
            
            # ✨ 生成底部 SN 区域 HTML ✨
            all_sns = sorted(cat_group['SN'].unique())
            sn_html = "".join([f'<a href="{BASE_URL}{sn}" target="_blank" class="sn-pill">{sn}</a>' for sn in all_sns])
            
            st.markdown(f'''
                <div class="wide-card normal-card">
                    <div class="cat-header">{cat}</div>
                    {inner_rows_html}
                    <div class="sn-footer">
                        {sn_html}
                    </div>
                </div>
            ''', unsafe_allow_html=True)
            
        if st.button("↺ 重新部署系统"): st.rerun()
