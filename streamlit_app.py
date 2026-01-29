import streamlit as st
import pandas as pd
import re
import html

# --- 1. UI 配置与样式锁定 ---
st.set_page_config(page_title="GianTakeshi | Matrix Hub", page_icon="📊", layout="wide")

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

    /* 模拟大格子的样式：移除 st.container 默认边距 */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: rgba(255, 255, 255, 0.02);
        border-radius: 12px;
    }}

    /* 内部竖向清单行样式 */
    .row-item {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(255, 255, 255, 0.04);
        margin: 4px 0;
        padding: 6px 12px;
        border-radius: 6px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }}
    .clr-text {{ font-size: 0.85rem; font-weight: 700; color: #ffffff; }}
    .sze-text {{ font-size: 0.8rem; color: #94a3b8; }}
    .sze-text b {{ color: #38bdf8; margin-left: 4px; font-family: monospace; }}
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
            name, attr, qty = str(row[df.columns[2]]), str(row[df.columns[6]]), str(row[df.columns[8]])
            if ';' in name or '；' in name:
                error.append({'行': idx+2, '原因': '复合品类'})
                continue
            cat = name.split(' ')[0].upper()
            if cat.startswith('WZ'): cat = 'WZ'
            target_qty = int(re.findall(r'\d+', qty)[0]) if re.findall(r'\d+', qty) else 0
            chunks = [c.strip() for c in re.split(r'[;；]', attr) if c.strip()]
            parsed = []
            for chunk in chunks:
                c_m, s_m = re.search(COLOR_REG, chunk), re.search(SIZE_REG, chunk)
                if c_m:
                    clr = c_m.group(1).strip().upper()
                    sze = s_m.group(1).strip().upper() if s_m else "FREE"
                    parsed.append({'Category': cat, 'Color': clr, 'Size': SIZE_MAP.get(sze, sze)})
            if len(parsed) == target_qty: valid.extend(parsed)
            else: error.append({'行': idx+2, '原因': f'数量不符({len(parsed)}/{target_qty})'})
        except: continue
    return pd.DataFrame(valid), pd.DataFrame(error)

# --- 3. 渲染层 ---
st.markdown("<h2 style='text-align:center; padding-top:50px;'>📊 极稳属性清单</h2>", unsafe_allow_html=True)
file = st.file_uploader("", type=["xlsx"])

if file:
    v_df, e_df = process_data(file)
    t1, t2 = st.tabs(["✅ 矩阵汇总", "❌ 异常拦截"])
    
    with t1:
        if not v_df.empty:
            v_df = v_df.sort_values(['Category', 'Color'])
            cat_groups = list(v_df.groupby('Category'))
            
            # 维持每行 6 个大盒子的布局
            cols_per_row = 6
            for i in range(0, len(cat_groups), cols_per_row):
                batch = cat_groups[i : i + cols_per_row]
                cols = st.columns(cols_per_row)
                
                for idx, (cat, group) in enumerate(batch):
                    # 使用原生 container(border=True) 替代 HTML 大盒子，物理解决乱码问题
                    with cols[idx].container(border=True):
                        # 盒子头部：品类名
                        st.markdown(f"""<div style="text-align:center; color:#38bdf8; font-weight:900; font-size:1.1rem; border-bottom:1px solid rgba(56,189,248,0.2); padding-bottom:8px; margin-bottom:8px;">{cat}</div>""", unsafe_allow_html=True)
                        
                        # 盒子内容：竖向清单
                        sub_stats = group.groupby(['Color', 'Size']).size().reset_index(name='count')
                        for _, r in sub_stats.iterrows():
                            # 每一行独立渲染，不进行大拼接
                            st.markdown(f"""
                            <div class="row-item">
                                <span class="clr-text">{html.escape(str(r['Color']))}</span>
                                <span class="sze-text">{r['Size']}<b>×{r['count']}</b></span>
                            </div>
                            """, unsafe_allow_html=True)
        else:
            st.info("数据解析后为空")
            
    with t2:
        st.dataframe(e_df, use_container_width=True)
