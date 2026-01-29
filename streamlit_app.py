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
    
    /* 统一大格子容器 */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        height: 400px !important; 
        overflow-y: auto !important;
        background: rgba(255, 255, 255, 0.02);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }}
    
    /* 链接样式优化 */
    .sn-link {{
        color: #38bdf8 !important;
        text-decoration: none;
        font-weight: bold;
        transition: all 0.2s;
        font-size: 10px;
    }}
    .sn-link:hover {{
        color: #7dd3fc !important;
        text-shadow: 0 0 8px rgba(56, 189, 248, 0.5);
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
    COLOR_REG = r'(?i)Color[:：\s]*([a-zA-Z0-9\-_/]+)'
    SIZE_REG = r'(?i)Size[:：\s]*([a-zA-Z0-9\-\s/]+?)(?=\s*(?:Color|Size|$|[,;，；]))'
    SIZE_MAP = {'HIGH ANKLE SOCKS': 'L', 'KNEE-HIGH SOCKS': 'M'}
    
    df = pd.read_excel(uploaded_file, engine='openpyxl')
    valid, error = [], []
    
    for idx, row in df.iterrows():
        try:
            sn = str(row.iloc[1]).strip() # 订单编号
            name = str(row.iloc[2]).strip() # 品类
            attr = str(row.iloc[6]).strip() # 属性
            qty_raw = str(row.iloc[8]).strip() # 数量
            
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
                    # 关键：正常数据也带上 SN
                    parsed.append({'Category': cat, 'SN': sn, 'Color': clr, 'Size': SIZE_MAP.get(sze, sze)})
            
            if len(parsed) == target_qty and parsed:
                valid.extend(parsed)
            else:
                error.append({'Category': cat, 'SN': sn, 'Reason': f'解析/数量异常({len(parsed)}/{target_qty})'})
        except: continue
    return pd.DataFrame(valid), pd.DataFrame(error)

# --- 3. 渲染组件 ---
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
                        st.markdown(f'<div style="background:rgba(239,68,68,0.05); margin-bottom:6px; padding:8px; border-radius:6px; font-size:11px; border:1px solid rgba(239,68,68,0.1);">SN: <a class="sn-link" href="{url}" target="_blank">{row["SN"]}</a><br><span style="color:#94a3b8;">{row["Reason"]}</span></div>', unsafe_allow_html=True)
                else:
                    # 正常汇总渲染：按 Color 聚合，但内部要能展示 SN
                    color_groups = group.groupby('Color')
                    for clr, clr_data in color_groups:
                        # 统计尺码
                        size_stats = clr_data['Size'].value_counts().sort_index()
                        size_html = "".join([f'<span style="background:rgba(56,189,248,0.1); padding:2px 6px; border-radius:4px; margin-left:4px; color:#fff;">{"×"+str(q) if s=="FREE" else s+"<b style=\'color:#38bdf8; margin-left:2px;\'>×"+str(q)+"</b>"}</span>' for s, q in size_stats.items()])
                        
                        # 获取该颜色涉及的所有订单 SN (去重并生成链接)
                        sns = clr_data['SN'].unique()
                        sn_links = " ".join([f'<a class="sn-link" href="https://inflyway.com/kamelnet/#/kn/fly-link/orders/detail?id={s}" target="_blank">#{s[-4:]}</a>' for s in sns]) # 显示后四位省空间

                        st.markdown(f"""
                            <div style="background:rgba(255,255,255,0.05); margin-bottom:8px; padding:8px; border-radius:8px; border:1px solid rgba(255,255,255,0.05);">
                                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px; border-bottom:1px solid rgba(255,255,255,0.05); padding-bottom:4px;">
                                    <span style="color:#38bdf8; font-weight:bold; font-size:12px;">{html.escape(str(clr))}</span>
                                    <div style="display:flex; gap:5px;">{sn_links}</div>
                                </div>
                                <div style="display:flex; flex-wrap:wrap; gap:4px; padding-top:2px;">{size_html}</div>
                            </div>
                        """, unsafe_allow_html=True)

# --- 4. 主程序 ---
st.markdown("<h2 style='text-align:center; padding-top:50px;'>📊 订单全链路矩阵</h2>", unsafe_allow_html=True)
file = st.file_uploader("", type=["xlsx"])
if file:
    v_df, e_df = process_data(file)
    t1, t2 = st.tabs(["✅ 正常汇总", "❌ 异常拦截"])
    with t1: render_matrix(v_df, is_error=False)
    with t2: render_matrix(e_df, is_error=True)
