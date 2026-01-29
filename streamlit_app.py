import streamlit as st
import pandas as pd
import re
import html

# --- 1. UI 配置与全局样式 ---
st.set_page_config(page_title="GianTakeshi | Matrix Hub", page_icon="🚀", layout="wide")

GITHUB_USERNAME = "GianTakeshi" 
BASE_URL = "https://inflyway.com/kamelnet/#/kn/fly-link/orders/detail?id="

st.markdown(f"""
    <style>
    .stApp {{ background: radial-gradient(circle at 50% 50%, #1e293b, #010409); color: #ffffff; }}
    header {{visibility: hidden;}}

    /* 头像面板 */
    .user-profile {{
        position: fixed; top: 25px; left: 25px; display: flex; align-items: center; gap: 12px; z-index: 1000000 !important; 
        background: rgba(255, 255, 255, 0.05); padding: 6px 16px 6px 6px; border-radius: 50px;
        border: 1px solid rgba(56, 189, 248, 0.3); backdrop-filter: blur(10px);
    }}
    .avatar {{ width: 40px; height: 40px; border-radius: 50%; border: 2px solid #38bdf8; object-fit: cover; }}

    /* 标题绝对居中 */
    .hero-container {{ text-align: center; width: 100%; padding: 60px 0 20px 0; }}
    .grand-title {{
        display: block; font-family: 'Inter', sans-serif; font-size: 3.2rem !important; font-weight: 900; letter-spacing: 8px;
        background: linear-gradient(to bottom, #ffffff 30%, #38bdf8 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin: 0 auto; filter: drop-shadow(0 0 10px rgba(56, 189, 248, 0.2));
    }}

    /* 白色磨砂药丸上传框 */
    [data-testid="stFileUploader"] {{
        position: fixed; bottom: 120px; left: 50%; transform: translateX(-50%); width: 480px; z-index: 9999;
        background: rgba(255, 255, 255, 0.12) !important; border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 50px !important; padding: 8px 25px !important; backdrop-filter: blur(25px) saturate(180%);
        box-shadow: 0 15px 35px rgba(0,0,0,0.3); transition: all 0.4s ease;
    }}
    [data-testid="stFileUploader"]:hover {{ border: 1px solid rgba(56, 189, 248, 0.6) !important; transform: translateX(-50%) translateY(-5px); }}

    /* 通用长条卡片 */
    .wide-card {{
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px; padding: 12px 20px; margin-bottom: 8px;
        display: flex; align-items: center; justify-content: space-between;
        transition: all 0.2s ease;
    }}
    .wide-card:hover {{ background: rgba(255, 255, 255, 0.08); transform: translateX(5px); }}

    .normal-card {{ border-left: 4px solid #38bdf8; }}
    .error-card {{ border-left: 4px solid #f59e0b; background: rgba(245, 158, 11, 0.02); }}

    .cat-tag {{ color: #38bdf8; font-weight: 800; font-size: 0.9rem; min-width: 100px; }}
    .attr-info {{ flex: 1; margin-left: 20px; color: #eee; font-size: 0.9rem; }}
    .attr-highlight {{ color: #38bdf8; font-weight: 600; margin-right: 15px; }}

    .sn-button {{
        display: inline-block; padding: 4px 14px; background: rgba(56, 189, 248, 0.1);
        color: #38bdf8 !important; border: 1px solid rgba(56, 189, 248, 0.4); border-radius: 20px; 
        text-decoration: none !important; font-size: 0.8rem; font-weight: 600; transition: all 0.2s;
    }}
    .sn-button:hover {{ background: rgba(56, 189, 248, 0.3); box-shadow: 0 0 10px #38bdf8; }}

    [data-testid="stFileUploader"] section {{ padding: 0 !important; min-height: 60px !important; }}
    [data-testid="stFileUploader"] label, [data-testid="stFileUploader"] small {{ display: none !important; }}
    </style>
    
    <div class="user-profile">
        <img src="https://avatars.githubusercontent.com/{GITHUB_USERNAME}" class="avatar">
        <div class="user-info">
            <div class="user-name">{GITHUB_USERNAME}</div>
            <div style="font-size: 0.6rem; color: #10b981; font-weight: bold;">● DATA SYNC ACTIVE</div>
        </div>
    </div>

    <div class="hero-container">
        <h1 class="grand-title">属性看板中枢</h1>
    </div>
""", unsafe_allow_html=True)

# --- 2. 逻辑层 (增加 SN 追踪) ---
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
        
        # 错误拦截：复合品类
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
                raw_s = s_m.group(1).strip().upper() if s_m else ""
                data_pairs.append((clr_v, SIZE_MAP.get(raw_s, raw_s)))
        
        # 校验数量
        if len(data_pairs) == i_qty and i_qty > 0:
            for c_val, s_val in data_pairs:
                all_normal_data.append({'Category': cat, 'Color': c_val, 'Size': s_val, 'SN': sn})
        else:
            all_error_rows.append({'SN': sn, '行号': index + 2, '原因': f"数量不符({len(data_pairs)}/{i_qty})", '内容': g_text})
            
    return pd.DataFrame(all_normal_data), pd.DataFrame(all_error_rows)

# --- 3. 主程序流程 ---
upload_placeholder = st.empty()
uploaded_file = upload_placeholder.file_uploader("Upload", type=["xlsx"])

if uploaded_file:
    with st.spinner('SYNCING DATA...'):
        v_df, e_df = process_sku_logic(uploaded_file)
    upload_placeholder.empty()
    
    t1, t2 = st.tabs(["💎 汇总订单流", "📡 异常拦截流"])
    
    with t1:
        if not v_df.empty:
            # 按品类排序显示
            for _, r in v_df.sort_values(['Category', 'SN']).iterrows():
                st.markdown(f'''
                    <div class="wide-card normal-card">
                        <div class="cat-tag">{r['Category']}</div>
                        <div class="attr-info">
                            <span class="attr-highlight">{r['Color']}</span>
                            <span style="opacity: 0.7;">SIZE: {r['Size']}</span>
                        </div>
                        <a href="{BASE_URL}{r['SN']}" target="_blank" class="sn-button">SN: {r['SN']}</a>
                    </div>
                ''', unsafe_allow_html=True)
            if st.button("↺ 重新加载"): st.rerun()
        else: st.info("暂无正常数据")

    with t2:
        if not e_df.empty:
            for _, err in e_df.iterrows():
                st.markdown(f'''
                    <div class="wide-card error-card">
                        <div style="flex: 1;">
                            <span style="color:#f59e0b; font-weight:bold; font-size:0.85rem;">LINE: {err['行号']}</span>
                            <span style="color:#ffffff; margin-left:15px; font-weight:600;">{err['原因']}</span>
                            <div style="margin-top:4px; font-size:0.8rem; color:#64748b;">{err['内容']}</div>
                        </div>
                        <a href="{BASE_URL}{err['SN']}" target="_blank" class="sn-button">SN: {err['SN']}</a>
                    </div>
                ''', unsafe_allow_html=True)
        else: st.success("全线通过校验")
