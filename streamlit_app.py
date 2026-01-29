import streamlit as st
import pandas as pd
import re

# --- 1. 基础配置与头像 ---
st.set_page_config(page_title="GianTakeshi | Matrix", page_icon="💎", layout="wide")

st.markdown(f"""
    <style>
    .stApp {{ background: #020617; color: #ffffff; }}
    header {{ visibility: hidden; }}
    /* 悬浮头像样式保持 */
    .user-profile {{
        position: fixed; top: 20px; left: 20px; display: flex; align-items: center; gap: 12px; z-index: 9999; 
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

# --- 3. 渲染层 (摒弃大段 HTML，改用 Streamlit 原生组件嵌套) ---
st.markdown("<h2 style='text-align:center; padding-top:40px;'>📦 属性层级看板</h2>", unsafe_allow_html=True)
file = st.file_uploader("", type=["xlsx"])

if file:
    v_df, e_df = process_data(file)
    t1, t2 = st.tabs(["✅ 矩阵汇总", "❌ 异常拦截"])
    
    with t1:
        if not v_df.empty:
            # 1. 按品类分组
            cat_groups = v_df.groupby('Category')
            
            for cat, cat_data in cat_groups:
                # 每个品类用一个原生 container 包裹
                with st.container(border=True):
                    # 顶部大标题
                    st.markdown(f"### 📂 品类: {cat} <span style='font-size:0.8rem; color:#94a3b8;'>(Total: {len(cat_data)})</span>", unsafe_allow_html=True)
                    
                    # 2. 内部颜色属性并排排列
                    # 统计该品类下的所有颜色+尺码
                    sub_stats = cat_data.groupby(['Color', 'Size']).size().reset_index(name='count')
                    
                    # 这里是关键：用 st.columns 来实现“格子”感，不再强行写 HTML
                    # 我们每排固定放 4 个小格子
                    cols_per_row = 4
                    sub_list = [sub_stats.iloc[i:i+cols_per_row] for i in range(0, len(sub_stats), cols_per_row)]
                    
                    for batch in sub_list:
                        grid_cols = st.columns(cols_per_row)
                        for idx, (_, row) in enumerate(batch.iterrows()):
                            # 每个小格子的内容
                            with grid_cols[idx]:
                                st.markdown(f"""
                                <div style="background:rgba(56,189,248,0.1); border:1px solid rgba(56,189,248,0.3); border-radius:8px; padding:8px; text-align:center;">
                                    <div style="color:#38bdf8; font-weight:bold; font-size:14px;">{row['Color']}</div>
                                    <div style="color:#cbd5e1; font-size:12px;">{row['Size']} <b style="color:white;">×{row['count']}</b></div>
                                </div>
                                """, unsafe_allow_html=True)
                st.write("") # 增加品类间的空隙
        else:
            st.info("解析结果为空")
    
    with t2:
        st.dataframe(e_df, use_container_width=True)
