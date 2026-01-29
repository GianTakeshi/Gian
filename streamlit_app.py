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
    .stApp {{ background: radial-gradient(circle at 50% 50%, #1e293b, #010409); color: #ffffff; }}
    header {{visibility: hidden;}}

    /* 🛡️ 用户面板 - 霓虹头像 */
    .user-profile {{
        position: fixed; top: 25px; left: 25px; display: flex; align-items: center; gap: 12px; z-index: 1000000; 
        background: rgba(255, 255, 255, 0.05); padding: 6px 16px 6px 6px; border-radius: 50px;
        border: 1px solid rgba(56, 189, 248, 0.3); backdrop-filter: blur(10px);
        transition: 0.3s; cursor: pointer;
    }}
    .user-profile:hover {{ transform: scale(1.05); box-shadow: 0 0 20px rgba(56, 189, 248, 0.4); }}
    .user-profile:active {{ transform: scale(0.95); filter: brightness(1.2); }}
    .avatar {{ width: 40px; height: 40px; border-radius: 50%; border: 2px solid #38bdf8; object-fit: cover; }}
    
    .hero-container {{ text-align: center; width: 100%; padding: 60px 0 20px 0; }}
    .grand-title {{
        display: block; font-family: 'Inter', sans-serif; font-size: 3.2rem !important; font-weight: 900; letter-spacing: 8px;
        background: linear-gradient(to bottom, #ffffff 30%, #38bdf8 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 30px;
    }}

    /* 📦 基础卡片 */
    .wide-card {{
        background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px; padding: 20px 25px; margin-bottom: 15px;
        display: flex; flex-direction: row; align-items: center; justify-content: space-between;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }}

    /* 💎 正常卡片：蓝霓虹 */
    .normal-card {{ border-left: 6px solid #38bdf8; }}
    .normal-card:hover {{
        background: rgba(56, 189, 248, 0.08);
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(56, 189, 248, 0.3);
        border-color: #38bdf8;
    }}
    .normal-sn {{ 
        background: rgba(56, 189, 248, 0.1); color: #38bdf8 !important; border: 1px solid rgba(56, 189, 248, 0.3); 
    }}
    .normal-sn:hover {{ background: #38bdf8 !important; color: #000 !important; box-shadow: 0 0 15px #38bdf8; }}

    /* ☢️ 异常卡片：橙霓虹 */
    .error-card {{ border-left: 6px solid #f59e0b; background: rgba(245, 158, 11, 0.03); }}
    .error-card:hover {{
        background: rgba(245, 158, 11, 0.08);
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(245, 158, 11, 0.4);
        border-color: #f59e0b;
    }}
    .error-sn {{ 
        background: rgba(245, 158, 11, 0.1); color: #f59e0b !important; border: 1px solid rgba(245, 158, 11, 0.4); 
    }}
    .error-sn:hover {{ background: #f59e0b !important; color: #000 !important; box-shadow: 0 0 15px #f59e0b; }}

    /* 通用组件 */
    .sn-side {{ display: flex; flex-wrap: wrap; gap: 6px; justify-content: flex-end; max-width: 450px; min-width: 200px; }}
    .sn-pill {{
        padding: 3px 12px; border-radius: 20px; text-decoration: none !important; 
        font-size: 0.75rem; font-weight: 600; transition: 0.3s;
    }}
    
    .cat-header {{ color: #38bdf8; font-weight: 900; font-size: 1.3rem; margin-bottom: 8px; }}
    .color-label {{ color: #38bdf8; font-weight: 700; font-size: 0.9rem; min-width: 90px; }}
    .size-box {{
        display: inline-flex; align-items: center;
        background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 6px; padding: 2px 10px; margin-right: 6px;
    }}

    /* ✨ 霓虹上传框 */
    [data-testid="stFileUploader"] {{
        position: fixed; bottom: 30px; left: 50%; transform: translateX(-50%); width: 420px; z-index: 9999;
        background: rgba(255, 255, 255, 0.12) !important; border: 2px solid rgba(56, 189, 248, 0.5) !important;
        border-radius: 50px !important; padding: 10px 30px !important; backdrop-filter: blur(25px);
        box-shadow: 0 0 30px rgba(56, 189, 248, 0.4);
    }}
    [data-testid="stFileUploader"] label, [data-testid="stFileUploader"] small {{ display: none !important; }}
    </style>

    <div class="user-profile">
        <img src="https://avatars.githubusercontent.com/{GITHUB_USERNAME}" class="avatar">
        <div class="user-info">
            <div class="user-name">{GITHUB_USERNAME}</div>
            <div style="font-size: 0.6rem; color: #10b981; font-weight: bold;">● NEON ACTIVE</div>
        </div>
    </div>
    <div class="hero-container"><h1 class="grand-title">属性看板中枢</h1></div>
""", unsafe_allow_html=True)

# --- 2. 逻辑处理 ---
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

# --- 3. 页面渲染 ---
# 使用 empty 容器实现解析后隐藏上传框
upload_zone = st.empty()
uploaded_file = upload_zone.file_uploader("Upload", type=["xlsx"])

if uploaded_file:
    v_df, e_df = process_sku_logic(uploaded_file)
    upload_zone.empty()  # ✨ 关键：解析完成后清空上传界面
    
    t1, t2 = st.tabs(["💎 汇总数据流", "📡 异常拦截"])
    
    with t1:
        if not v_df.empty:
            for cat in sorted(v_df['Category'].unique()):
                cat_group = v_df[v_df['Category'] == cat]
                attr_html = ""
                for clr in sorted(cat_group['Color'].unique()):
                    clr_group = cat_group[cat_group['Color'] == clr]
                    size_counts = clr_group['Size'].value_counts().sort_index()
                    sizes_html = "".join([f'<div class="size-box"><span style="color:#fff; font-size:0.8rem; font-weight:600;">{("" if s=="FREE" else s)}</span><span style="color:#38bdf8; font-weight:800;">{"×" if s!="FREE" else ""}{q}</span></div>' for s, q in size_counts.items()])
                    attr_html += f'<div style="display:flex; align-items:center; gap:15px; padding:4px 0;"><div class="color-label">{clr}</div>{sizes_html}</div>'
                
                sns = sorted(list(set(cat_group['SN'].tolist())))
                sn_html = "".join([f'<a href="{BASE_URL}{sn}" target="_blank" class="sn-pill normal-sn">{sn}</a>' for sn in sns])
                
                st.markdown(f'''
                    <div class="wide-card normal-card">
                        <div style="flex:1;"><div class="cat-header">{cat}</div>{attr_html}</div>
                        <div class="sn-side">{sn_html}</div>
                    </div>
                ''', unsafe_allow_html=True)
            if st.button("↺ 重置系统"): st.rerun()

    with t2:
        if not e_df.empty:
            for _, err in e_df.iterrows():
                st.markdown(f'''
                    <div class="wide-card error-card">
                        <div style="flex:1;">
                            <div style="color:#f59e0b; font-weight:900;">LINE {err["Line"]} | {err["Reason"]}</div>
                            <div style="font-size:0.8rem; color:#94a3b8; margin-top:5px;">{err["Content"]}</div>
                        </div>
                        <div class="sn-side">
                            <a href="{BASE_URL}{err["SN"]}" target="_blank" class="sn-pill error-sn">{err["SN"]}</a>
                        </div>
                    </div>
                ''', unsafe_allow_html=True)
        else:
            st.success("数据校验完成，系统环境洁净。")
