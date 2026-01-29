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

    /* 🛡️ 头像面板 */
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
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 30px;
    }}

    /* 宽卡片布局 - 增加自适应高度 */
    .wide-card {{
        background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px; padding: 25px; margin-bottom: 20px;
        display: flex; flex-direction: column; gap: 15px;
        transition: all 0.4s ease;
    }}
    .normal-card {{ border-left: 6px solid #38bdf8; }}
    .normal-card:hover {{ background: rgba(56, 189, 248, 0.04); box-shadow: 0 15px 40px rgba(0,0,0,0.4); }}

    /* 内部属性行布局 */
    .attr-row {{ display: flex; align-items: flex-start; gap: 20px; padding-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.05); }}
    .cat-header {{ color: #38bdf8; font-weight: 900; font-size: 1.4rem; letter-spacing: 1px; margin-bottom: 10px; }}
    
    .color-pill {{ color: #38bdf8; font-weight: 700; font-size: 0.9rem; min-width: 100px; padding-top: 4px; }}
    
    .size-box {{
        display: inline-flex; align-items: center;
        background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 6px; padding: 3px 12px; margin-right: 8px; margin-bottom: 4px;
    }}
    .size-text {{ color: #ffffff; font-weight: 600; font-size: 0.85rem; }}
    .qty-text {{ color: #38bdf8; font-weight: 800; font-size: 0.85rem; margin-left: 6px; }}

    .sn-container {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; padding-top: 10px; }}
    .sn-pill {{
        padding: 4px 15px; background: rgba(56, 189, 248, 0.1);
        color: #38bdf8 !important; border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 20px; 
        text-decoration: none !important; font-size: 0.75rem; font-weight: 600;
    }}

    /* 上传框与按钮 */
    [data-testid="stFileUploader"] {{
        position: fixed; bottom: 60px; left: 50%; transform: translateX(-50%); width: 400px; z-index: 9999;
        background: rgba(255, 255, 255, 0.12) !important; border: 1px solid rgba(56, 189, 248, 0.3) !important;
        border-radius: 50px !important; padding: 10px 30px !important; backdrop-filter: blur(25px);
        box-shadow: 0 0 25px rgba(56, 189, 248, 0.2);
    }}
    div.stButton > button {{
        background: rgba(56, 189, 248, 0.05) !important; color: #38bdf8 !important;
        border: 2px solid rgba(56, 189, 248, 0.4) !important; border-radius: 50px !important;
        padding: 12px 60px !important; font-weight: 900 !important; margin: 40px auto !important; display: block !important;
    }}
    </style>

    <div class="user-profile">
        <img src="https://avatars.githubusercontent.com/{GITHUB_USERNAME}" class="avatar">
        <div class="user-info">
            <div class="user-name">{GITHUB_USERNAME}</div>
            <div style="font-size: 0.6rem; color: #10b981; font-weight: bold;">● CONSOLIDATED MODE</div>
        </div>
    </div>
    <div class="hero-container"><h1 class="grand-title">属性看板中枢</h1></div>
""", unsafe_allow_html=True)

# --- 2. 逻辑层 ---
def process_sku_logic(uploaded_file):
    COLOR_REG, SIZE_REG = r'(?i)Color[:：\s]*([a-zA-Z0-9\-_/]+)', r'(?i)Size[:：\s]*([a-zA-Z0-9\-\s/]+?)(?=\s*(?:Color|Size|$|[,;，；]))'
    SIZE_MAP = {'HIGH ANKLE SOCKS': 'L', 'KNEE-HIGH SOCKS': 'M'}
    df = pd.read_excel(uploaded_file, engine='openpyxl')
    col_a, col_c, col_g, col_i = df.columns[0], df.columns[2], df.columns[6], df.columns[8]
    all_normal_data, all_error_rows = [], []
    
    for index, row in df.iterrows():
        c_raw = str(row[col_c]).strip()
        if not c_raw or c_raw == 'nan': continue
        cat = c_raw.split(' ')[0].upper()
        if cat.startswith('WZ'): cat = 'WZ'
        g_text, i_val, sn = str(row[col_g]), str(row[col_i]), str(row[col_a])
        i_qty = int(re.findall(r'\d+', i_val)[0]) if re.findall(r'\d+', i_val) else 0
        chunks = re.split(r'[;；]', g_text)
        
        if ';' in c_raw or '；' in c_raw:
            all_error_rows.append({'SN': sn, '行号': index + 2, '原因': "复合品类阻断"})
            continue

        data_pairs = []
        for chunk in chunks:
            chunk = chunk.strip()
            if not chunk: continue
            c_m, s_m = re.search(COLOR_REG, chunk), re.search(SIZE_REG, chunk)
            if c_m:
                clr_v = c_m.group(1).strip().upper()
                raw_s = s_m.group(1).strip().upper() if s_m else "FREE"
                data_pairs.append((clr_v, SIZE_MAP.get(raw_s, raw_s)))
        
        if len(data_pairs) == i_qty and i_qty > 0:
            for c_val, s_val in data_pairs:
                all_normal_data.append({'Category': cat, 'Color': c_val, 'Size': s_val, 'SN': sn})
        else:
            all_error_rows.append({'SN': sn, '行号': index + 2, '原因': f"数量不符"})
            
    return pd.DataFrame(all_normal_data), pd.DataFrame(all_error_rows)

# --- 3. 渲染层 ---
upload_placeholder = st.empty()
uploaded_file = upload_placeholder.file_uploader("Upload", type=["xlsx"], key="main_uploader")

if uploaded_file:
    v_df, e_df = process_sku_logic(uploaded_file)
    upload_placeholder.empty()
    
    t1, t2 = st.tabs(["💎 汇总数据流", "📡 异常拦截"])
    
    with t1:
        if not v_df.empty:
            # ✨ 核心变动：按 Category 聚合所有数据 ✨
            for cat, cat_group in v_df.groupby('Category'):
                # 记录该品类下所有的 SN
                all_sns = sorted(list(set(cat_group['SN'].tolist())))
                sn_pills_html = "".join([f'<a href="{BASE_URL}{sn}" target="_blank" class="sn-pill">{sn}</a>' for sn in all_sns])
                
                # 构造内部属性行（颜色分组）
                color_rows_html = ""
                for clr, clr_group in cat_group.groupby('Color'):
                    size_counts = clr_group['Size'].value_counts().sort_index()
                    sizes_html = "".join([f'<div class="size-box"><span class="size-text">{s}</span><span class="qty-text">×{q}</span></div>' for s, q in size_counts.items()])
                    color_rows_html += f'''
                        <div class="attr-row">
                            <div class="color-pill">{clr}</div>
                            <div style="flex:1;">{sizes_html}</div>
                        </div>
                    '''

                st.markdown(f'''
                    <div class="wide-card normal-card">
                        <div class="cat-header">{cat}</div>
                        {color_rows_html}
                        <div class="sn-container">{sn_pills_html}</div>
                    </div>
                ''', unsafe_allow_html=True)
            
            if st.button("↺ 重新部署系统", key="reboot"): st.rerun()

    with t2:
        if not e_df.empty:
            for _, err in e_df.iterrows():
                st.markdown(f'<div class="wide-card" style="border-left:5px solid #f59e0b;">{err["SN"]} - LINE {err["行号"]} - {err["原因"]}</div>', unsafe_allow_html=True)
