import streamlit as st
import pandas as pd
import re
import html

# --- 1. UI 视觉配置 ---
st.set_page_config(page_title="GianTakeshi | Matrix Hub", page_icon="💎", layout="wide")

st.markdown(f"""
    <style>
    .stApp {{ background: #020617; color: #ffffff; }}
    header {{ visibility: hidden; }}
    
    /* 悬浮头像 */
    .user-profile {{
        position: fixed; top: 20px; left: 20px; display: flex; align-items: center; gap: 12px; z-index: 99999; 
        background: rgba(255, 255, 255, 0.05); padding: 5px 15px 5px 5px; border-radius: 50px;
        border: 1px solid rgba(56, 189, 248, 0.3); backdrop-filter: blur(10px);
    }}

    /* 响应式容器：利用 Flex 布局替代死板的列 */
    .flex-grid {{
        display: flex;
        flex-wrap: wrap;
        gap: 16px;
        justify-content: flex-start;
    }}

    /* 大格子外框：自适应宽度 */
    .cat-card {{
        flex: 1 1 300px; /* 最小300px，自动伸展 */
        max-width: 450px; /* 防止在超宽屏上拉得太离谱 */
        height: 380px;
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        overflow-y: auto;
        position: relative;
    }}

    .cat-card::-webkit-scrollbar {{ width: 4px; }}
    .cat-card::-webkit-scrollbar-thumb {{ background: rgba(56, 189, 248, 0.3); border-radius: 10px; }}

    .err-link {{ color: #38bdf8 !important; text-decoration: none; font-weight: bold; border-bottom: 1px dashed #38bdf8; }}
    </style>
    
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
                error.append({'Category': cat, 'SN': sn, 'Reason': '复合品类'})
                continue
            target_qty = int(re.findall(r'\d+', qty_raw)[0]) if re.findall(r'\d+', qty_raw) else 0
            chunks = [c.strip() for c in re.split(r'[;；]', attr) if c.strip()]
            parsed = []
            for chunk in chunks:
                c_m, s_m = re.search(COLOR_REG, chunk), re.search(SIZE_REG, chunk)
                if c_m:
                    clr = c_m.group(1).strip().upper()
                    sze = s_m.group(1).strip().upper() if s_m else "FREE"
                    parsed.append({'Category': cat, 'SN': sn, 'Color': clr, 'Size': SIZE_MAP.get(sze, sze)})
            if len(parsed) == target_qty and parsed: valid.extend(parsed)
            else: error.append({'Category': cat, 'SN': sn, 'Reason': f'数量不符({len(parsed)}/{target_qty})'})
        except: continue
    return pd.DataFrame(valid), pd.DataFrame(error)

# --- 3. 渲染逻辑 (改为单盒子独立渲染) ---
def render_box(cat, group, is_error):
    head_bg = "rgba(239, 68, 68, 0.2)" if is_error else "rgba(56, 189, 248, 0.2)"
    head_clr = "#f87171" if is_error else "#38bdf8"
    
    body_html = ""
    if is_error:
        for _, r in group.iterrows():
            url = f"https://inflyway.com/kamelnet/#/kn/fly-link/orders/detail?id={r['SN']}"
            body_html += f'''
                <div style="background:rgba(239,68,68,0.05); margin-bottom:6px; padding:8px; border-radius:6px; font-size:11px; border:1px solid rgba(239,68,68,0.1);">
                    SN: <a class="err-link" href="{url}" target="_blank">{r['SN']}</a><br>
                    <span style="color:#94a3b8;">{r['Reason']}</span>
                </div>'''
    else:
        color_groups = group.groupby('Color')
        for clr, clr_data in color_groups:
            size_stats = clr_data['Size'].value_counts().sort_index()
            size_badges = "".join([f'<span style="background:rgba(56,189,248,0.1); padding:2px 6px; border-radius:4px; margin-left:4px; color:#fff;">{"×"+str(q) if s=="FREE" else s+"<b style=\'color:#38bdf8; margin-left:2px;\'>×"+str(q)+"</b>"}</span>' for s, q in size_stats.items()])
            body_html += f'''
                <div style="display:flex; align-items:center; background:rgba(255,255,255,0.05); margin-bottom:4px; padding:6px 10px; border-radius:6px; font-size:11px; border:1px solid rgba(255,255,255,0.05); flex-wrap:wrap;">
                    <span style="color:#38bdf8; font-weight:bold; border-right:1px solid rgba(255,255,255,0.1); padding-right:8px; min-width:45px;">{html.escape(str(clr))}</span>
                    <div style="display:flex; flex-wrap:wrap; gap:4px;">{size_badges}</div>
                </div>'''
    
    # 每一个大格子都是一次独立的 markdown 调用，避开乱码风险
    st.markdown(f'''
        <div class="cat-card">
            <div style="background:{head_bg}; padding:10px; text-align:center; color:{head_clr}; font-weight:900; font-size:1.1rem; border-bottom:1px solid rgba(255,255,255,0.1); position:sticky; top:0; z-index:10;">{cat}</div>
            <div style="padding:10px;">{body_html}</div>
        </div>
    ''', unsafe_allow_html=True)

# --- 4. 主程序 ---
st.markdown("<h2 style='text-align:center; padding-top:50px;'>📊 智能响应式矩阵</h2>", unsafe_allow_html=True)
file = st.file_uploader("", type=["xlsx"])

if file:
    v_df, e_df = process_data(file)
    t1, t2 = st.tabs(["✅ 正常汇总", "❌ 异常拦截"])
    
    with t1:
        if not v_df.empty:
            # 使用原生容器包裹 Flex 布局
            st.markdown('<div class="flex-grid">', unsafe_allow_html=True)
            cols = st.columns(1) # 技巧：用一个 column 来撑开 flex 空间
            with cols[0]:
                c1, c2, c3, c4, c5, c6 = st.columns(6) # 实际上这里我们换个思路，直接循环渲染
                # 为了解决乱码，我们直接利用 Streamlit 的原生列，不写大 HTML
                cat_list = list(v_df.groupby('Category'))
                # 智能分配到 1-6 列（根据屏幕宽度动态调整的最稳妥办法）
                for i, (cat, g) in enumerate(cat_list):
                    render_box(cat, g, False)
            st.markdown('</div>', unsafe_allow_html=True)
    
    with t2:
        if not e_df.empty:
            for cat, g in e_df.groupby('Category'):
                render_box(cat, g, True)
