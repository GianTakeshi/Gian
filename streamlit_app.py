import streamlit as st
import pandas as pd
import re
import html

# --- 1. UI 视觉配置 ---
st.set_page_config(page_title="GianTakeshi | Matrix Hub", page_icon="💎", layout="wide")

st.markdown(f"""
    <style>
    .stApp {{ 
        background: radial-gradient(circle at center, #001d3d 0%, #000814 70%, #000000 100%) !important;
        color: #ffffff; 
    }}
    header {{ visibility: hidden; }}
    
    /* 右侧流动雾气 */
    .mist-light {{
        position: fixed;
        top: 0; right: 0; width: 70%; height: 100%;
        background: radial-gradient(circle at 100% 50%, rgba(56, 189, 248, 0.15) 0%, transparent 70%);
        filter: blur(100px); animation: flow 10s ease-in-out infinite alternate; z-index: -1;
    }}
    @keyframes flow {{ from {{ transform: translateX(15%); opacity: 0.4; }} to {{ transform: translateX(-5%); opacity: 0.8; }} }}
    
    /* 胶囊上传框样式 */
    [data-testid="stFileUploader"] {{
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        border-radius: 50px !important; /* 胶囊形状 */
        padding: 10px 30px;
        backdrop-filter: blur(20px);
        max-width: 600px;
        margin: 100px auto !important;
    }}
    [data-testid="stFileUploader"] section {{ border-radius: 40px !important; }}

    /* 药丸 Tab 切换器：居中、平分、毛玻璃 */
    .stTabs {{
        max-width: 600px;
        margin: 0 auto !important;
    }}
    .stTabs [data-baseweb="tab-list"] {{
        display: flex;
        justify-content: center;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 50px;
        padding: 5px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        gap: 0px;
    }}
    .stTabs [data-baseweb="tab"] {{
        flex: 1; /* 平分宽度 */
        text-align: center;
        border-radius: 40px;
        height: 45px;
        transition: all 0.3s;
        color: rgba(255, 255, 255, 0.6);
    }}
    .stTabs [data-baseweb="tab-highlight"] {{ display: none; }} /* 隐藏原有的下划线 */
    .stTabs [aria-selected="true"] {{
        background: rgba(56, 189, 248, 0.2) !important;
        color: #38bdf8 !important;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.1);
    }}

    /* 属性框毛玻璃效果 */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        height: 380px !important; 
        background: rgba(255, 255, 255, 0.05) !important; 
        border-radius: 24px !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        backdrop-filter: blur(35px) saturate(200%) !important; 
        transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
    }}
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
        transform: translateY(-8px);
        border: 1px solid rgba(56, 189, 248, 0.5) !important;
    }}

    .user-profile {{
        position: fixed; top: 20px; left: 20px; display: flex; align-items: center; gap: 12px; z-index: 99999; 
        background: rgba(255, 255, 255, 0.05); padding: 5px 15px 5px 5px; border-radius: 50px;
        border: 1px solid rgba(56, 189, 248, 0.3); backdrop-filter: blur(15px);
    }}
    </style>
    <div class="mist-light"></div>
    <div class="user-profile">
        <img src="https://avatars.githubusercontent.com/GianTakeshi" style="width:35px;height:35px;border-radius:50%;">
        <div style="font-weight:700; font-size:0.85rem; color:white;">GianTakeshi</div>
    </div>
""", unsafe_allow_html=True)

# --- 2. 逻辑层 ---
def process_data(uploaded_file):
    COLOR_REG, SIZE_REG = r'(?i)Color[:：\s]*([a-zA-Z0-9\-_/]+)', r'(?i)Size[:：\s]*([a-zA-Z0-9\-\s/]+?)(?=\s*(?:Color|Size|$|[,;，；]))'
    SIZE_MAP = {'HIGH ANKLE SOCKS': 'L', 'KNEE-HIGH SOCKS': 'M'}
    df = pd.read_excel(uploaded_file, engine='openpyxl')
    valid, error = [], []
    for idx, row in df.iterrows():
        try:
            sn, name, attr, qty_raw = str(row.iloc[1]).strip(), str(row.iloc[2]).strip(), str(row.iloc[6]).strip(), str(row.iloc[8]).strip()
            cat = name.split(' ')[0].upper()
            if cat.startswith('WZ'): cat = 'WZ'
            if ';' in name or '；' in name:
                error.append({'Category': cat, 'SN': sn, 'Reason': '复合品类 (Multiple Items)'})
                continue
            found_qty = re.findall(r'\d+', qty_raw)
            target_qty = int(found_qty[0]) if found_qty else 0
            chunks = [c.strip() for c in re.split(r'[;；]', attr) if c.strip()]
            parsed = []
            for chunk in chunks:
                c_m, s_m = re.search(COLOR_REG, chunk), re.search(SIZE_REG, chunk)
                if c_m:
                    clr = c_m.group(1).strip().upper()
                    sze = s_m.group(1).strip().upper() if s_m else "FREE"
                    parsed.append({'Category': cat, 'Color': clr, 'Size': SIZE_MAP.get(sze, sze)})
            if len(parsed) != target_qty:
                error.append({'Category': cat, 'SN': sn, 'Reason': f'数量不符({len(parsed)}/{target_qty})'})
            elif not parsed:
                error.append({'Category': cat, 'SN': sn, 'Reason': '无法解析颜色属性'})
            else:
                valid.extend(parsed)
        except: continue
    return pd.DataFrame(valid), pd.DataFrame(error)

def render_matrix(data_df, is_error=False):
    if data_df.empty:
        st.info("暂无数据")
        return
    cat_groups = list(data_df.sort_values(['Category']).groupby('Category'))
    cols_per_row = 6
    for i in range(0, len(cat_groups), cols_per_row):
        batch, cols = cat_groups[i : i + cols_per_row], st.columns(cols_per_row)
        for idx, (cat, group) in enumerate(batch):
            with cols[idx].container(border=True):
                head_bg = "rgba(239, 68, 68, 0.2)" if is_error else "rgba(56, 189, 248, 0.2)"
                head_clr = "#f87171" if is_error else "#38bdf8"
                st.markdown(f'<div style="background:{head_bg}; margin:-1rem -1rem 10px -1rem; padding:10px; text-align:center; color:{head_clr}; font-weight:900; font-size:1.1rem; border-bottom:1px solid rgba(255,255,255,0.1); position:sticky; top:-1rem; z-index:10; border-radius: 20px 20px 0 0;">{cat}</div>', unsafe_allow_html=True)
                if is_error:
                    for _, row in group.iterrows():
                        url = f"https://inflyway.com/kamelnet/#/kn/fly-link/orders/detail?id={row['SN']}" 
                        st.markdown(f'<div style="background:rgba(239,68,68,0.05); margin-bottom:6px; padding:8px; border-radius:12px; font-size:11px; border:1px solid rgba(239,68,68,0.1);"><div style="margin-bottom:4px;">SN: <a style="color:#38bdf8;text-decoration:none;" href="{url}" target="_blank">{row["SN"]}</a></div><div style="color:#94a3b8;">{row["Reason"]}</div></div>', unsafe_allow_html=True)
                else:
                    for clr, clr_data in group.groupby('Color'):
                        size_stats = clr_data['Size'].value_counts().sort_index()
                        size_html = "".join([f'<span style="background:rgba(56,189,248,0.1); padding:2px 6px; border-radius:6px; margin-left:4px; color:#fff;">{"×"+str(q) if s=="FREE" else s+"<b style=\'color:#38bdf8; margin-left:2px;\'>×"+str(q)+"</b>"}</span>' for s, q in size_stats.items()])
                        st.markdown(f'<div style="display:flex; align-items:center; background:rgba(255,255,255,0.05); margin-bottom:6px; padding:6px 10px; border-radius:10px; font-size:11px; border:1px solid rgba(255,255,255,0.05); flex-wrap:wrap;"><span style="color:#38bdf8; font-weight:bold; border-right:1px solid rgba(255,255,255,0.1); padding-right:8px; min-width:45px;">{html.escape(str(clr))}</span><div style="display:flex; flex-wrap:wrap; gap:4px;">{size_html}</div></div>', unsafe_allow_html=True)

# --- 3. 动态界面渲染 ---
placeholder = st.empty()

if 'parsed' not in st.session_state:
    st.session_state.parsed = False

if not st.session_state.parsed:
    with placeholder.container():
        st.markdown("<h2 style='text-align:center; padding-top:80px; letter-spacing:4px;'>GIAN MATRIX SYSTEM</h2>", unsafe_allow_html=True)
        file = st.file_uploader("", type=["xlsx"])
        if file:
            st.session_state.v_df, st.session_state.e_df = process_data(file)
            st.session_state.parsed = True
            st.rerun() # 触发重绘以隐藏上传框
else:
    # 解析完成后，这里不包含 file_uploader，因此它会消失
    st.markdown("<div style='height:40px;'></div>", unsafe_allow_html=True) # 留白
    t1, t2 = st.tabs(["✅ NORMAL SUMMARY", "❌ ANOMALY DATA"])
    with t1: render_matrix(st.session_state.v_df, is_error=False)
    with t2: render_matrix(st.session_state.e_df, is_error=True)
    
    if st.button("RELOAD SYSTEM", use_container_width=False):
        st.session_state.parsed = False
        st.rerun()
