import streamlit as st
import pandas as pd
import re
import html

# --- 1. UI 视觉配置 (仅修改背景层，保留原逻辑) ---
st.set_page_config(page_title="GianTakeshi | Matrix Hub", page_icon="💎", layout="wide")

st.markdown(f"""
    <style>
    /* 注入聚光灯背景：中心蓝，四周黑 */
    .stApp {{ 
        background: radial-gradient(circle at center, #001d3d 0%, #000814 70%, #000000 100%) !important;
        color: #ffffff; 
    }}
    header {{ visibility: hidden; }}
    
    /* 注入底部 Gian 标识 */
    .background-gian {{
        position: fixed;
        bottom: -2%;
        left: 50%;
        transform: translateX(-50%);
        font-size: clamp(10rem, 30vw, 40rem);
        font-weight: 900;
        color: rgba(255, 255, 255, 0.06);
        letter-spacing: -15px;
        z-index: -2;
        user-select: none;
        white-space: nowrap;
        pointer-events: none;
    }}

    /* 注入右侧流动雾气 */
    .mist-light {{
        position: fixed;
        top: 0;
        right: 0;
        width: 70%;
        height: 100%;
        background: radial-gradient(circle at 100% 50%, rgba(56, 189, 248, 0.12) 0%, transparent 70%);
        filter: blur(100px);
        animation: flow 10s ease-in-out infinite alternate;
        z-index: -1;
    }}
    @keyframes flow {{
        from {{ transform: translateX(15%); opacity: 0.4; }}
        to {{ transform: translateX(-5%); opacity: 0.7; }}
    }}
    
    /* 保留你原有的容器样式 */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        height: 380px !important; 
        overflow-y: auto !important;
        background: rgba(255, 255, 255, 0.02);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(20px); /* 增加毛玻璃度以适配新背景 */
    }}
    
    .user-profile {{
        position: fixed; top: 20px; left: 20px; display: flex; align-items: center; gap: 12px; z-index: 99999; 
        background: rgba(255, 255, 255, 0.05); padding: 5px 15px 5px 5px; border-radius: 50px;
        border: 1px solid rgba(56, 189, 248, 0.3); backdrop-filter: blur(10px);
    }}
    .sn-link {{ color: #38bdf8 !important; text-decoration: none; font-weight: bold; border-bottom: 1px dashed #38bdf8; }}
    </style>

    <div class="background-gian">Gian</div>
    <div class="mist-light"></div>

    <div class="user-profile">
        <img src="https://avatars.githubusercontent.com/GianTakeshi" style="width:35px;height:35px;border-radius:50%;">
        <div style="font-weight:700; font-size:0.85rem; color:white;">GianTakeshi</div>
    </div>
""", unsafe_allow_html=True)

# --- 2. 逻辑层 (完全保留你的原始逻辑) ---
def process_data(uploaded_file):
    COLOR_REG = r'(?i)Color[:：\s]*([a-zA-Z0-9\-_/]+)'
    SIZE_REG = r'(?i)Size[:：\s]*([a-zA-Z0-9\-\s/]+?)(?=\s*(?:Color|Size|$|[,;，；]))'
    SIZE_MAP = {'HIGH ANKLE SOCKS': 'L', 'KNEE-HIGH SOCKS': 'M'}
    df = pd.read_excel(uploaded_file, engine='openpyxl')
    valid, error = [], []
    for idx, row in df.iterrows():
        try:
            sn = str(row.iloc[1]).strip()
            name = str(row.iloc[2]).strip()
            attr = str(row.iloc[6]).strip()
            qty_raw = str(row.iloc[8]).strip()
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
                c_m = re.search(COLOR_REG, chunk)
                s_m = re.search(SIZE_REG, chunk)
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
        except Exception as e:
            error.append({'Category': 'ERROR', 'SN': 'N/A', 'Reason': str(e)})
    return pd.DataFrame(valid), pd.DataFrame(error)

# --- 3. 渲染组件 (完全保留你的原始渲染逻辑) ---
def render_matrix(data_df, is_error=False):
    if data_df.empty:
        st.info("暂无数据")
        return
    data_df = data_df.sort_values(['Category'])
    cat_groups = list(data_df.groupby('Category'))
    cols_per_row = 6
    for i in range(0, len(cat_groups), cols_per_row):
        batch = cat_groups[i : i + cols_per_row]
        cols = st.columns(cols_per_row)
        for idx, (cat, group) in enumerate(batch):
            with cols[idx].container(border=True):
                head_bg = "rgba(239, 68, 68, 0.2)" if is_error else "rgba(56, 189, 248, 0.2)"
                head_clr = "#f87171" if is_error else "#38bdf8"
                st.markdown(f'<div style="background:{head_bg}; margin:-1rem -1rem 10px -1rem; padding:10px; text-align:center; color:{head_clr}; font-weight:900; font-size:1.1rem; border-bottom:1px solid rgba(255,255,255,0.1); position:sticky; top:-1rem; z-index:10;">{cat}</div>', unsafe_allow_html=True)
                if is_error:
                    for _, row in group.iterrows():
                        url = f"https://inflyway.com/kamelnet/#/kn/fly-link/orders/detail?id={row['SN']}" 
                        st.markdown(f'<div style="background:rgba(239,68,68,0.05); margin-bottom:6px; padding:8px; border-radius:6px; font-size:11px; border:1px solid rgba(239,68,68,0.1);"><div style="margin-bottom:4px;">SN: <a class="sn-link" href="{url}" target="_blank">{row["SN"]}</a></div><div style="color:#94a3b8;">{row["Reason"]}</div></div>', unsafe_allow_html=True)
                else:
                    color_groups = group.groupby('Color')
                    for clr, clr_data in color_groups:
                        size_stats = clr_data['Size'].value_counts().sort_index()
                        size_html = "".join([f'<span style="background:rgba(56,189,248,0.1); padding:2px 6px; border-radius:4px; margin-left:4px; color:#fff;">{"×"+str(q) if s=="FREE" else s+"<b style=\'color:#38bdf8; margin-left:2px;\'>×"+str(q)+"</b>"}</span>' for s, q in size_stats.items()])
                        st.markdown(f'<div style="display:flex; align-items:center; background:rgba(255,255,255,0.05); margin-bottom:6px; padding:6px 10px; border-radius:6px; font-size:11px; border:1px solid rgba(255,255,255,0.05); flex-wrap:wrap;"><span style="color:#38bdf8; font-weight:bold; border-right:1px solid rgba(255,255,255,0.1); padding-right:8px; min-width:45px;">{html.escape(str(clr))}</span><div style="display:flex; flex-wrap:wrap; gap:4px;">{size_html}</div></div>', unsafe_allow_html=True)

# --- 4. 主程序 ---
st.markdown("<h2 style='text-align:center; padding-top:50px;'>📊 智能属性全矩阵</h2>", unsafe_allow_html=True)
file = st.file_uploader("", type=["xlsx"])
if file:
    v_df, e_df = process_data(file)
    t1, t2 = st.tabs(["✅ 正常汇总", "❌ 异常拦截"])
    with t1: render_matrix(v_df, is_error=False)
    with t2: render_matrix(e_df, is_error=True)
