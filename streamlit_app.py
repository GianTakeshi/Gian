import streamlit as st
import pandas as pd
import re
import html

# --- 1. UI 视觉配置 (精准修改 Tab 样式) ---
st.set_page_config(page_title="GianTakeshi | Matrix Hub", page_icon="💎", layout="wide")

st.markdown(f"""
    <style>
    /* 背景保持：聚光灯渐变 */
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
    
    /* 【核心修改】药丸形 Tab 切换器：居中、平分、毛玻璃 */
    .stTabs {{
        max-width: 500px; /* 限制胶囊宽度 */
        margin: 0 auto 30px auto !important; /* 居中并与下方保持间距 */
    }}
    .stTabs [data-baseweb="tab-list"] {{
        display: flex;
        justify-content: center;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 50px; /* 胶囊圆角 */
        padding: 4px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        gap: 0px;
    }}
    .stTabs [data-baseweb="tab"] {{
        flex: 1; /* 各占一半宽度 */
        text-align: center;
        border-radius: 40px;
        height: 42px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        color: rgba(255, 255, 255, 0.5);
        border: none !important;
    }}
    .stTabs [data-baseweb="tab-highlight"] {{ display: none; }} /* 彻底隐藏原有的底部横线 */
    
    .stTabs [aria-selected="true"] {{
        background: rgba(56, 189, 248, 0.2) !important; /* 选中的色块效果 */
        color: #38bdf8 !important;
        font-weight: 700;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.1);
    }}

    /* 属性框毛玻璃效果 (保持原样) */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        height: 380px !important; 
        overflow-y: auto !important;
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

# --- 2. 逻辑层 (原封不动) ---
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

# --- 3. 渲染组件 (保持不变) ---
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

# --- 4. 主程序 ---
st.markdown("<h2 style='text-align:center; padding-top:50px; letter-spacing:4px;'>📊 智能属性全矩阵</h2>", unsafe_allow_html=True)
file = st.file_uploader("", type=["xlsx"])

if file:
    v_df, e_df = process_data(file)
    # 此处的 Tab 已经应用了上方的药丸 CSS 样式
    t1, t2 = st.tabs(["✅ 正常数据", "❌ 异常汇总"])
    with t1: render_matrix(v_df, is_error=False)
    with t2: render_matrix(e_df, is_error=True)
