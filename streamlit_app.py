import streamlit as st
import pandas as pd
import re

# --- 1. UI 配置与全局样式 ---
st.set_page_config(page_title="GianTakeshi | Hub", page_icon="🚀", layout="wide")

GITHUB_USERNAME = "GianTakeshi" 
BASE_URL = "https://inflyway.com/kamelnet/#/kn/fly-link/orders/detail?id="

# 注入 CSS 样式
st.markdown(f"""
    <style>
    .stApp {{ background: radial-gradient(circle at 50% 50%, #1e293b, #010409); color: #ffffff; }}
    header {{visibility: hidden;}}

    /* 🛡️ 头像面板 - 重新归位 */
    .user-profile {{
        position: fixed; top: 25px; left: 25px; display: flex; align-items: center; gap: 12px; z-index: 1000000; 
        background: rgba(255, 255, 255, 0.05); padding: 6px 16px 6px 6px; border-radius: 50px;
        border: 1px solid rgba(56, 189, 248, 0.3); backdrop-filter: blur(10px);
    }}
    .avatar {{ width: 40px; height: 40px; border-radius: 50%; border: 2px solid #38bdf8; object-fit: cover; }}
    .user-info {{ line-height: 1.1; }}
    .user-name {{ font-size: 0.9rem; font-weight: 500; color: #fff; }}
    
    /* 标题居中 */
    .hero-container {{ text-align: center; width: 100%; padding: 60px 0 20px 0; }}
    .grand-title {{
        display: block; font-family: 'Inter', sans-serif; font-size: 3.2rem !important; font-weight: 900; letter-spacing: 8px;
        background: linear-gradient(to bottom, #ffffff 30%, #38bdf8 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 30px;
    }}

    /* 卡片通用布局 */
    .wide-card {{
        background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px; padding: 18px 25px; margin-bottom: 12px;
        display: flex; align-items: center; justify-content: space-between; gap: 20px;
        min-height: 85px; box-sizing: border-box;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }}

    /* 汇总卡片（蓝）与 异常卡片（橙） */
    .normal-card {{ border-left: 5px solid rgba(56, 189, 248, 0.6); }}
    .normal-card:hover {{ background: rgba(56, 189, 248, 0.06); border-color: rgba(56, 189, 248, 0.8); transform: translateY(-5px); box-shadow: 0 10px 30px rgba(56, 189, 248, 0.2); }}
    
    .error-card {{ border-left: 5px solid rgba(245, 158, 11, 0.6); background: rgba(245, 158, 11, 0.02); }}
    .error-card:hover {{ background: rgba(245, 158, 11, 0.05); border-color: rgba(245, 158, 11, 0.8); transform: translateY(-5px); box-shadow: 0 10px 30px rgba(245, 158, 11, 0.2); }}

    /* 属性层级配色 */
    .attr-cluster {{ display: flex; align-items: center; gap: 15px; min-width: 450px; flex-shrink: 0; }}
    .cat-label {{ color: #38bdf8; font-weight: 900; font-size: 1.05rem; width: 85px; }}
    .color-text {{ color: #38bdf8; font-weight: 700; font-size: 0.95rem; min-width: 60px; }} /* Color 蓝色 */
    
    /* Size 框框与配色 */
    .size-box {{
        display: inline-flex; align-items: center;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 6px; padding: 2px 10px; margin-right: 6px;
    }}
    .size-text {{ color: #ffffff; font-weight: 600; font-size: 0.85rem; }} /* Size 白色 */
    .qty-text {{ color: #38bdf8; font-weight: 800; font-size: 0.85rem; margin-left: 5px; }} /* 数量蓝色 */

    /* SN 极右对齐 */
    .sn-grid {{ margin-left: auto; display: flex; flex-wrap: wrap; gap: 8px; justify-content: flex-end; max-width: 550px; }}
    .sn-pill {{
        display: inline-block; padding: 3px 14px; background: rgba(255, 255, 255, 0.03);
        color: #38bdf8 !important; border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 20px; 
        text-decoration: none !important; font-size: 0.75rem; font-weight: 600; transition: 0.3s;
    }}
    .sn-pill:hover {{ background: rgba(56, 189, 248, 0.2); transform: scale(1.1); box-shadow: 0 0 12px rgba(56, 189, 248, 0.4); }}

    /* 重新部署按钮 */
    div.stButton > button {{
        background: rgba(56, 189, 248, 0.05) !important; color: #38bdf8 !important;
        border: 2px solid rgba(56, 189, 248, 0.4) !important; border-radius: 50px !important;
        padding: 12px 45px !important; font-weight: 900 !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        display: block !important; margin: 40px auto !important;
    }}
    div.stButton > button:hover {{ background: rgba(56, 189, 248, 0.2) !important; transform: translateY(-8px) !important; box-shadow: 0 15px 35px rgba(56, 189, 248, 0.3) !important; }}

    /* 上传框固定 */
    [data-testid="stFileUploader"] {{
        position: fixed; bottom: 30px; left: 50%; transform: translateX(-50%); width: 400px; z-index: 9999;
        background: rgba(255, 255, 255, 0.12) !important; border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 50px !important; padding: 10px 30px !important; backdrop-filter: blur(25px);
    }}
    [data-testid="stFileUploader"] label, [data-testid="stFileUploader"] small {{ display: none !important; }}
    </style>

    <div class="user-profile">
        <img src="https://avatars.githubusercontent.com/{GITHUB_USERNAME}" class="avatar">
        <div class="user-info">
            <div class="user-name">{GITHUB_USERNAME}</div>
            <div style="font-size: 0.6rem; color: #10b981; font-weight: bold;">● FULL VERSION ACTIVE</div>
        </div>
    </div>

    <div class="hero-container">
        <h1 class="grand-title">属性看板中枢</h1>
    </div>
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
            all_error_rows.append({'SN': sn, '行号': index + 2, '原因': "复合品类阻断", '内容': g_text})
            continue

        data_pairs = []
        for chunk in chunks:
            chunk = chunk.strip()
            if not chunk: continue
            c_m, s_m = re.search(COLOR_REG, chunk), re.search(SIZE_REG, chunk)
            if c_m:
                clr_v = c_m.group(1).strip().upper()
                raw_s = s_m.group(1).strip().upper() if s_m else "FREE"
                if not raw_s: raw_s = "FREE"
                data_pairs.append((clr_v, SIZE_MAP.get(raw_s, raw_s)))
        
        if len(data_pairs) == i_qty and i_qty > 0:
            for c_val, s_val in data_pairs:
                all_normal_data.append({'Category': cat, 'Color': c_val, 'Size': s_val, 'SN': sn})
        else:
            all_error_rows.append({'SN': sn, '行号': index + 2, '原因': f"数量不符({len(data_pairs)}/{i_qty})", '内容': g_text})
    return pd.DataFrame(all_normal_data), pd.DataFrame(all_error_rows)

# --- 3. 渲染层 ---
upload_placeholder = st.empty()
uploaded_file = upload_placeholder.file_uploader("Upload", type=["xlsx"])

if uploaded_file:
    v_df, e_df = process_sku_logic(uploaded_file)
    upload_placeholder.empty()
    
    t1, t2 = st.tabs(["💎 汇总数据流", "📡 异常拦截"])
    
    with t1:
        if not v_df.empty:
            for (cat, clr), group in v_df.groupby(['Category', 'Color']):
                size_counts = group['Size'].value_counts().sort_index()
                attr_display = "".join([f'<div class="size-box"><span class="size-text">{("" if s=="FREE" else s)}</span><span class="qty-text">×{q}</span></div>' for s, q in size_counts.items()])
                sns = sorted(list(set(group['SN'].tolist())))
                sn_pills = "".join([f'<a href="{BASE_URL}{sn}" target="_blank" class="sn-pill">{sn}</a>' for sn in sns])
                
                st.markdown(f'''
                    <div class="wide-card normal-card">
                        <div class="attr-cluster">
                            <div class="cat-label">{cat}</div>
                            <div class="color-text">{clr}</div>
                            <div style="display:flex; flex-wrap:wrap; gap:2px;">{attr_display}</div>
                        </div>
                        <div class="sn-grid">{sn_pills}</div>
                    </div>
                ''', unsafe_allow_html=True)
            if st.button("↺ 重新部署系统"): st.rerun()
        else: st.info("暂无汇总数据")

    with t2:
        if not e_df.empty:
            for _, err in e_df.iterrows():
                st.markdown(f'''
                    <div class="wide-card error-card">
                        <div style="flex: 1; display:flex; flex-direction:column; justify-content:center;">
                            <div>
                                <span style="color:#f59e0b; font-weight:bold; font-size:0.85rem;">LINE: {err['行号']}</span>
                                <span style="color:#ffffff; margin-left:15px; font-weight:600;">{err['原因']}</span>
                            </div>
                            <div style="margin-top:6px; font-size:0.8rem; color:#94a3b8; line-height:1.2;">{err['内容']}</div>
                        </div>
                        <div class="sn-grid">
                            <a href="{BASE_URL}{err['SN']}" target="_blank" class="sn-pill" style="border-color:#f59e0b; color:#f59e0b !important;">{err['SN']}</a>
                        </div>
                    </div>
                ''', unsafe_allow_html=True)
        else: st.success("系统扫描完毕：未发现异常订单")
