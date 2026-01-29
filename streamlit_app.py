import streamlit as st
import pandas as pd
import re
import html

# --- 1. UI 视觉配置 (精准收复被压缩的空间) ---
st.set_page_config(page_title="GianTakeshi | Matrix Hub", page_icon="💎", layout="wide")

st.markdown(f"""
    <style>
    .stApp {{ 
        background: radial-gradient(circle at center, #001d3d 0%, #000814 70%, #000000 100%) !important;
        color: #ffffff; 
    }}
    header {{ visibility: hidden; }}
    
    /* 动态流雾背景 */
    .mist-light {{
        position: fixed;
        top: 0; right: 0; width: 70%; height: 100%;
        background: radial-gradient(circle at 100% 50%, rgba(56, 189, 248, 0.15) 0%, transparent 70%);
        filter: blur(100px); animation: flow 10s ease-in-out infinite alternate; z-index: -1;
    }}
    @keyframes flow {{ from {{ transform: translateX(15%); opacity: 0.4; }} to {{ transform: translateX(-5%); opacity: 0.8; }} }}

    /* 【核心修改】强制取消列间距压缩 */
    [data-testid="column"] {{
        padding: 0 5px !important; /* 极小化列间距，释放横向空间 */
    }}

    /* 药丸 Tab 切换器 */
    .stTabs {{ max-width: 500px; margin: 0 auto 30px auto !important; }}
    .stTabs [data-baseweb="tab-list"] {{
        display: flex; justify-content: center; background: rgba(255, 255, 255, 0.05);
        border-radius: 50px; padding: 4px; border: 1px solid rgba(255, 255, 255, 0.1); gap: 0px;
    }}
    .stTabs [data-baseweb="tab"] {{
        flex: 1; text-align: center; border-radius: 40px; height: 42px; border: none !important;
        transition: all 0.3s; color: rgba(255, 255, 255, 0.5);
    }}
    .stTabs [data-baseweb="tab-highlight"] {{ display: none; }}
    .stTabs [aria-selected="true"] {{
        background: rgba(56, 189, 248, 0.2) !important; color: #38bdf8 !important; font-weight: 700;
    }}

    /* 属性大框：深度优化毛玻璃与空间利用率 */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        height: 420px !important; 
        background: rgba(255, 255, 255, 0.04) !important; 
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        backdrop-filter: blur(30px) saturate(160%) !important; 
        padding: 0 !important; /* 取消外层 padding，让内部 header 撑满 */
        margin-bottom: 10px;
        transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }}
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
        transform: scale(1.02); /* 悬浮时轻微放大而非仅仅上移，增加呼吸感 */
        border: 1px solid rgba(56, 189, 248, 0.4) !important;
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

# --- 2. 逻辑层 (保持不变) ---
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
                error.append({'Category': cat, 'SN': sn, 'Reason': '复合品类'})
                continue
            f_qty = re.findall(r'\d+', qty_raw)
            t_qty = int(f_qty[0]) if f_qty else 0
            chunks = [c.strip() for c in re.split(r'[;；]', attr) if c.strip()]
            parsed = []
            for chunk in chunks:
                c_m, s_m = re.search(COLOR_REG, chunk), re.search(SIZE_REG, chunk)
                if c_m:
                    clr = c_m.group(1).strip().upper()
                    sze = s_m.group(1).strip().upper() if s_m else "FREE"
                    parsed.append({'Category': cat, 'Color': clr, 'Size': SIZE_MAP.get(sze, sze)})
            if len(parsed) != t_qty:
                error.append({'Category': cat, 'SN': sn, 'Reason': f'数量不符({len(parsed)}/{t_qty})'})
            elif not parsed: error.append({'Category': cat, 'SN': sn, 'Reason': '解析失败'})
            else: valid.extend(parsed)
        except: continue
    return pd.DataFrame(valid), pd.DataFrame(error)

# --- 3. 渲染组件 (重新定义比例，确保不压缩) ---
def render_matrix(data_df, is_error=False):
    if data_df.empty:
        st.info("暂无数据")
        return
    cat_groups = list(data_df.sort_values(['Category']).groupby('Category'))
    # 将 6 改为 5，给每个格子更多呼吸空间
    cols_per_row = 5 
    for i in range(0, len(cat_groups), cols_per_row):
        batch, cols = cat_groups[i : i + cols_per_row], st.columns(cols_per_row)
        for idx, (cat, group) in enumerate(batch):
            with cols[idx].container(border=True):
                head_bg = "rgba(239, 68, 68, 0.25)" if is_error else "rgba(56, 189, 248, 0.25)"
                head_clr = "#f87171" if is_error else "#38bdf8"
                # 满幅 Header
                st.markdown(f'<div style="background:{head_bg}; margin:0; padding:12px; text-align:center; color:{head_clr}; font-weight:900; font-size:1.1rem; border-bottom:1px solid rgba(255,255,255,0.1); border-radius: 18px 18px 0 0;">{cat}</div>', unsafe_allow_html=True)
                
                # 内容区域增加 padding
                content_html = ""
                if is_error:
                    for _, r in group.iterrows():
                        url = f"https://inflyway.com/kamelnet/#/kn/fly-link/orders/detail?id={r['SN']}" 
                        content_html += f'<div style="background:rgba(239,68,68,0.06); margin-bottom:8px; padding:8px; border-radius:10px; border:1px solid rgba(239,68,68,0.1); font-size:11px;">SN: <a style="color:#38bdf8;text-decoration:none;font-weight:bold;" href="{url}" target="_blank">{r["SN"]}</a><br><span style="color:#94a3b8;">{r["Reason"]}</span></div>'
                else:
                    for clr, clr_data in group.groupby('Color'):
                        size_stats = clr_data['Size'].value_counts().sort_index()
                        size_badges = "".join([f'<span style="background:rgba(255,255,255,0.08); padding:2px 6px; border-radius:5px; margin:1px; color:#eee; font-size:10px;">{s if s!="FREE" else ""}<b>×{q}</b></span>' for s, q in size_stats.items()])
                        content_html += f'<div style="margin-bottom:10px; padding:8px; background:rgba(255,255,255,0.03); border-radius:12px; border:1px solid rgba(255,255,255,0.05);"><div style="color:#38bdf8; font-weight:bold; font-size:12px; margin-bottom:4px;">{html.escape(str(clr))}</div><div style="display:flex; flex-wrap:wrap; gap:2px;">{size_badges}</div></div>'
                
                st.markdown(f'<div style="padding:12px; overflow-y:auto; height:340px;">{content_html}</div>', unsafe_allow_html=True)

# --- 4. 主程序 ---
st.markdown("<h2 style='text-align:center; padding-top:40px; letter-spacing:4px;'>📊 智能属性全矩阵</h2>", unsafe_allow_html=True)
file = st.file_uploader("", type=["xlsx"])

if file:
    v_df, e_df = process_data(file)
    t1, t2 = st.tabs(["✅ 正常数据", "❌ 异常汇总"])
    with t1: render_matrix(v_df, is_error=False)
    with t2: render_matrix(e_df, is_error=True)
