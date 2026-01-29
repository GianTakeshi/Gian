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

    .user-profile {{
        position: fixed; top: 25px; left: 25px; display: flex; align-items: center; gap: 12px; z-index: 1000000; 
        background: rgba(255, 255, 255, 0.05); padding: 6px 16px 6px 6px; border-radius: 50px;
        border: 1px solid rgba(56, 189, 248, 0.3); backdrop-filter: blur(10px);
    }}
    .avatar {{ width: 40px; height: 40px; border-radius: 50%; border: 2px solid #38bdf8; object-fit: cover; }}
    .user-name {{ font-size: 0.95rem; font-weight: 600; color: #fff; }}
    
    .hero-container {{ text-align: center; width: 100%; padding: 60px 0 20px 0; }}
    .grand-title {{
        display: block; font-family: 'Inter', sans-serif; font-size: 3.2rem !important; font-weight: 900; letter-spacing: 8px;
        background: linear-gradient(to bottom, #ffffff 30%, #38bdf8 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 30px;
    }}

    .wide-card {{
        background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px; padding: 25px; margin-bottom: 20px;
        display: flex; flex-direction: column; gap: 12px;
    }}
    .normal-card {{ border-left: 6px solid #38bdf8; }}

    .cat-header {{ color: #38bdf8; font-weight: 900; font-size: 1.4rem; margin-bottom: 5px; }}
    
    .attr-row {{ display: flex; align-items: center; gap: 15px; padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.03); }}
    .color-label {{ color: #38bdf8; font-weight: 700; font-size: 0.9rem; min-width: 90px; }}
    
    .size-box {{
        display: inline-flex; align-items: center;
        background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 6px; padding: 2px 10px; margin-right: 6px;
    }}
    .size-text {{ color: #ffffff; font-weight: 600; font-size: 0.8rem; }}
    .qty-text {{ color: #38bdf8; font-weight: 800; font-size: 0.8rem; margin-left: 5px; }}

    .sn-container {{ display: flex; flex-wrap: wrap; gap: 6px; margin-top: 15px; }}
    .sn-pill {{
        padding: 3px 12px; background: rgba(56, 189, 248, 0.08);
        color: #38bdf8 !important; border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 20px; 
        text-decoration: none !important; font-size: 0.7rem; font-weight: 600;
    }}

    [data-testid="stFileUploader"] {{
        position: fixed; bottom: 60px; left: 50%; transform: translateX(-50%); width: 400px; z-index: 9999;
        background: rgba(255, 255, 255, 0.12) !important; border: 1px solid rgba(56, 189, 248, 0.3) !important;
        border-radius: 50px !important; padding: 10px 30px !important; backdrop-filter: blur(25px);
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.2);
    }}
    div.stButton > button {{
        background: rgba(56, 189, 248, 0.05) !important; color: #38bdf8 !important;
        border: 2px solid rgba(56, 189, 248, 0.4) !important; border-radius: 50px !important;
        padding: 10px 40px !important; margin: 20px auto !important; display: block !important;
    }}
    </style>

    <div class="user-profile">
        <img src="https://avatars.githubusercontent.com/{GITHUB_USERNAME}" class="avatar">
        <div class="user-info">
            <div class="user-name">{GITHUB_USERNAME}</div>
            <div style="font-size: 0.6rem; color: #10b981; font-weight: bold;">● CONSOLIDATED</div>
        </div>
    </div>
    <div class="hero-container"><h1 class="grand-title">属性看板中枢</h1></div>
""", unsafe_allow_html=True)

# --- 2. 逻辑层 ---
def process_sku_logic(uploaded_file):
    COLOR_REG = r'(?i)Color[:：\s]*([a-zA-Z0-9\-_/]+)'
    SIZE_REG = r'(?i)Size[:：\s]*([a-zA-Z0-9\-\s/]+?)(?=\s*(?:Color|Size|$|[,;，；]))'
    SIZE_MAP = {'HIGH ANKLE SOCKS': 'L', 'KNEE-HIGH SOCKS': 'M'}
    
    try:
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        cols = df.columns
        all_normal_data = []
        all_error_rows = []
        
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
                c_m = re.search(COLOR_REG, chunk)
                s_m = re.search(SIZE_REG, chunk)
                if c_m:
                    clr = c_m.group(1).strip().upper()
                    raw_s = s_m.group(1).strip().upper() if s_m else "FREE"
                    data_pairs.append((clr, SIZE_MAP.get(raw_s, raw_s)))
            
            if len(data_pairs) == i_qty and i_qty > 0:
                for c_val, s_val in data_pairs:
                    all_normal_data.append({'Category': cat, 'Color': c_val, 'Size': s_val, 'SN': sn})
            else:
                all_error_rows.append({'SN': sn, 'Line': index+2})
                
        return pd.DataFrame(all_normal_data), pd.DataFrame(all_error_rows)
    except Exception as e:
        st.error(f"数据处理出错: {e}")
        return pd.DataFrame(), pd.DataFrame()

# --- 3. 渲染层 ---
uploaded_file = st.file_uploader("Upload", type=["xlsx"], key="uploader")

if uploaded_file:
    v_df, e_df = process_sku_logic(uploaded_file)
    
    if not v_df.empty:
        # ✨ 核心聚合：按 Category 分大框 ✨
        for cat in sorted(v_df['Category'].unique()):
            cat_data = v_df[v_df['Category'] == cat]
            
            # 准备颜色行 HTML
            color_html = ""
            for clr in sorted(cat_data['Color'].unique()):
                clr_data = cat_data[cat_data['Color'] == clr]
                size_counts = clr_data['Size'].value_counts().sort_index()
                
                size_html = "".join([f'<div class="size-box"><span class="size-text">{s}</span><span class="qty-text">×{q}</span></div>' for s, q in size_counts.items()])
                color_html += f'<div class="attr-row"><div class="color-label">{clr}</div><div style="flex:1;">{size_html}</div></div>'
            
            # 准备 SN HTML
            sns = sorted(cat_data['SN'].unique())
            sn_html = "".join([f'<a href="{BASE_URL}{sn}" target="_blank" class="sn-pill">{sn}</a>' for sn in sns])
            
            st.markdown(f'''
                <div class="wide-card normal-card">
                    <div class="cat-header">{cat}</div>
                    {color_html}
                    <div class="sn-container">{sn_html}</div>
                </div>
            ''', unsafe_allow_html=True)

        if st.button("↺ 重新部署系统"):
            st.rerun()
