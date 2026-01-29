import streamlit as st
import pandas as pd
import re
import html

# --- 1. UI 配置 ---
st.set_page_config(page_title="GianTakeshi | Matrix", page_icon="💎", layout="wide")

st.markdown(f"""
    <style>
    .stApp {{ background: #020617; color: #ffffff; }}
    header {{ visibility: hidden; }}
    
    /* 悬浮头像 */
    .user-profile {{
        position: fixed; top: 20px; left: 20px; display: flex; align-items: center; gap: 12px; z-index: 1000000; 
        background: rgba(255, 255, 255, 0.05); padding: 5px 15px 5px 5px; border-radius: 50px;
        border: 1px solid rgba(56, 189, 248, 0.3); backdrop-filter: blur(15px);
    }}
    .avatar {{ width: 35px; height: 35px; border-radius: 50%; border: 2px solid #38bdf8; }}

    /* 大盒子样式 */
    .category-card {{
        background: rgba(255, 255, 255, 0.03);
        border: 1.5px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 0;
        margin-bottom: 20px;
        overflow: hidden;
    }}
    </style>
    <div class="user-profile">
        <img src="https://avatars.githubusercontent.com/GianTakeshi" class="avatar">
        <div style="font-weight:700; font-size:0.85rem;">GianTakeshi</div>
    </div>
""", unsafe_allow_html=True)

# --- 2. 核心逻辑 (保持鲁棒性) ---
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

# --- 3. 渲染层 (极致精简 HTML 结构防止乱码) ---
st.markdown("<h2 style='text-align:center; padding: 40px 0 20px 0;'>📦 属性层级看板</h2>", unsafe_allow_html=True)
file = st.file_uploader("", type=["xlsx"])

if file:
    v_df, e_df = process_data(file)
    t1, t2 = st.tabs(["✅ 矩阵汇总", "❌ 异常拦截"])
    
    with t1:
        if not v_df.empty:
            v_df = v_df.sort_values(['Category', 'Color'])
            cat_groups = list(v_df.groupby('Category'))
            
            # 使用 3 列布局让空间更充裕
            cols = st.columns(3)
            for i, (cat, group) in enumerate(cat_groups):
                # 计算这个品类的总数
                total_pcs = len(group)
                
                # 构造小格子的内容
                sub_stats = group.groupby(['Color', 'Size']).size().reset_index(name='count')
                inner_html = ""
                for _, r in sub_stats.iterrows():
                    # 采用最扁平的标签结构，避免嵌套过深导致乱码
                    inner_html += f"""
                    <div style="display:inline-block; margin:4px; border:1px solid rgba(255,255,255,0.1); border-radius:4px; overflow:hidden; font-family:sans-serif;">
                        <span style="background:rgba(56,189,248,0.2); color:#38bdf8; padding:2px 8px; font-size:12px; font-weight:bold; border-right:1px solid rgba(255,255,255,0.1);">{html.escape(str(r['Color']))}</span>
                        <span style="padding:2px 8px; font-size:12px; color:#ccc;">{r['Size']} <b style="color:#38bdf8;">×{r['count']}</b></span>
                    </div>
                    """
                
                # 渲染大框
                cols[i % 3].markdown(f"""
                <div class="category-card">
                    <div style="background:rgba(56,189,248,0.15); padding:12px; text-align:center; border-bottom:1px solid rgba(255,255,255,0.1);">
                        <span style="font-size:1.4rem; font-weight:900; color:#38bdf8; letter-spacing:1px;">{cat}</span>
                        <div style="font-size:0.7rem; color:#94a3b8; margin-top:4px;">TOTAL: {total_pcs} PCS</div>
                    </div>
                    <div style="padding:15px; text-align:left;">
                        {inner_html}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("解析结果为空")
    
    with t2:
        st.dataframe(e_df, use_container_width=True)
