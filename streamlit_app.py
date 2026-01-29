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
    
    /* 核心：响应式网格容器 */
    .responsive-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); /* 自动计算：最小280px，撑满剩余空间 */
        gap: 15px;
        padding: 10px 0;
    }}

    /* 统一大格子内部高度 */
    .cat-container {{
        height: 380px; 
        overflow-y: auto;
        background: rgba(255, 255, 255, 0.02);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        scrollbar-width: thin;
        scrollbar-color: rgba(56, 189, 248, 0.3) transparent;
        position: relative;
    }}
    
    .cat-container::-webkit-scrollbar {{ width: 4px; }}
    .cat-container::-webkit-scrollbar-thumb {{
        background: rgba(56, 189, 248, 0.3); border-radius: 10px;
    }}

    .err-link {{
        color: #38bdf8 !important;
        text-decoration: none;
        font-weight: bold;
        border-bottom: 1px dashed rgba(56, 189, 248, 0.4);
    }}

    .user-profile {{
        position: fixed; top: 20px; left: 20px; display: flex; align-items: center; gap: 12px; z-index: 99999; 
        background: rgba(255, 255, 255, 0.05); padding: 5px 15px 5px 5px; border-radius: 50px;
        border: 1px solid rgba(56, 189, 248, 0.3); backdrop-filter: blur(10px);
    }}
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
                    parsed.append({'Category': cat, 'Color': clr, 'Size': SIZE_MAP.get(sze, sze)})
            if len(parsed) == target_qty and parsed: valid.extend(parsed)
            else: error.append({'Category': cat, 'SN': sn, 'Reason': f'数量不符({len(parsed)}/{target_qty})'})
        except: continue
    return pd.DataFrame(valid), pd.DataFrame(error)

# --- 3. 渲染逻辑 (封装 HTML 生成) ---
def get_box_html(cat, group, is_error):
    head_bg = "rgba(239, 68, 68, 0.2)" if is_error else "rgba(56, 189, 248, 0.2)"
    head_clr = "#f87171" if is_error else "#38bdf8"
    
    content_html = ""
    if is_error:
        for _, r in group.iterrows():
            url = f"https://inflyway.com/kamelnet/#/kn/fly-link/orders/detail?id={r['SN']}"
            content_html += f'''
                <div style="background:rgba(239,68,68,0.05); margin-bottom:6px; padding:8px; border-radius:6px; font-size:11px; border:1px solid rgba(239,68,68,0.1);">
                    SN: <a class="err-link" href="{url}" target="_blank">{r['SN']}</a><br>
                    <span style="color:#94a3b8;">{r['Reason']}</span>
                </div>
            '''
    else:
        color_groups = group.groupby('Color')
        for clr, clr_data in color_groups:
            size_stats = clr_data['Size'].value_counts().sort_index()
            size_badges = "".join([f'<span style="background:rgba(56,189,248,0.1); padding:2px 6px; border-radius:4px; margin-left:4px; color:#fff;">{"×"+str(q) if s=="FREE" else s+"<b style=\'color:#38bdf8; margin-left:2px;\'>×"+str(q)+"</b>"}</span>' for s, q in size_stats.items()])
            content_html += f'''
                <div style="display:flex; align-items:center; background:rgba(255,255,255,0.05); margin-bottom:4px; padding:6px 10px; border-radius:6px; font-size:11px; border:1px solid rgba(255,255,255,0.05); flex-wrap:wrap;">
                    <span style="color:#38bdf8; font-weight:bold; border-right:1px solid rgba(255,255,255,0.1); padding-right:8px; min-width:45px;">{html.escape(str(clr))}</span>
                    <div style="display:flex; flex-wrap:wrap; gap:4px;">{size_badges}</div>
                </div>
            '''
    
    return f'''
        <div class="cat-container">
            <div style="background:{head_bg}; padding:10px; text-align:center; color:{head_clr}; font-weight:900; font-size:1.1rem; border-bottom:1px solid rgba(255,255,255,0.1); position:sticky; top:0; z-index:10;">{cat}</div>
            <div style="padding:10px;">{content_html}</div>
        </div>
    '''

# --- 4. 主程序 ---
st.markdown("<h2 style='text-align:center; padding-top:50px;'>📊 智能响应式看板</h2>", unsafe_allow_html=True)
file = st.file_uploader("", type=["xlsx"])

if file:
    v_df, e_df = process_data(file)
    t1, t2 = st.tabs(["✅ 正常汇总", "❌ 异常拦截"])
    
    for tab, df, is_err in zip([t1, t2], [v_df, e_df], [False, True]):
        with tab:
            if not df.empty:
                df = df.sort_values(['Category'])
                # 使用自定义网格布局
                boxes_html = "".join([get_box_html(cat, g, is_err) for cat, g in df.groupby('Category')])
                st.markdown(f'<div class="responsive-grid">{boxes_html}</div>', unsafe_allow_html=True)
            else:
                st.info("暂无数据")
