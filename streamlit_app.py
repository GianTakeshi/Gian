import streamlit as st
import pandas as pd
import re

# --- 1. UI 配置与样式 (回归九宫格视觉) ---
st.set_page_config(page_title="GianTakeshi | Matrix Hub", page_icon="🚀", layout="wide")

GITHUB_USERNAME = "GianTakeshi"

st.markdown(f"""
    <style>
    .stApp {{ background: #020617; color: #ffffff; }}
    header {{ visibility: hidden; }}

    /* 固定悬浮头像 */
    .user-profile {{
        position: fixed; top: 20px; left: 20px; display: flex; align-items: center; gap: 12px; z-index: 1000000; 
        background: rgba(255, 255, 255, 0.05); padding: 5px 15px 5px 5px; border-radius: 50px;
        border: 1px solid rgba(56, 189, 248, 0.3); backdrop-filter: blur(15px);
    }}
    .avatar {{ width: 35px; height: 35px; border-radius: 50%; border: 2px solid #38bdf8; object-fit: cover; }}
    .user-name {{ font-weight: 700; font-size: 0.85rem; color: #ffffff; }}

    /* 每一个属性盒子的样式 */
    .attr-card {{
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        transition: all 0.2s ease;
        margin-bottom: 15px;
        height: 140px; /* 统一高度 */
    }}
    .attr-card:hover {{ border-color: #38bdf8; background: rgba(56, 189, 248, 0.05); transform: translateY(-3px); }}

    .card-header {{ background: rgba(56, 189, 248, 0.2); color: #38bdf8; font-size: 0.7rem; font-weight: 800; padding: 5px; text-align: center; text-transform: uppercase; }}
    .card-body {{ padding: 10px; text-align: center; flex-grow: 1; display: flex; align-items: center; justify-content: center; }}
    .card-color {{ font-size: 0.9rem; font-weight: 700; color: #ffffff; }}
    .card-footer {{ padding: 5px; background: rgba(255, 255, 255, 0.02); display: flex; flex-wrap: wrap; gap: 4px; justify-content: center; border-top: 1px solid rgba(255, 255, 255, 0.05); }}
    
    .size-tag {{ font-size: 0.65rem; color: #94a3b8; background: rgba(255,255,255,0.06); padding: 1px 5px; border-radius: 4px; }}
    .size-tag b {{ color: #38bdf8; }}
    </style>

    <div class="user-profile">
        <img src="https://avatars.githubusercontent.com/{GITHUB_USERNAME}" class="avatar">
        <div class="user-name">{GITHUB_USERNAME}</div>
    </div>
""", unsafe_allow_html=True)

# --- 2. 逻辑层：严格过滤异常 ---
def process_data(uploaded_file):
    COLOR_REG = r'(?i)Color[:：\s]*([a-zA-Z0-9\-_/]+)'
    SIZE_REG = r'(?i)Size[:：\s]*([a-zA-Z0-9\-\s/]+?)(?=\s*(?:Color|Size|$|[,;，；]))'
    SIZE_MAP = {'HIGH ANKLE SOCKS': 'L', 'KNEE-HIGH SOCKS': 'M'}
    
    df = pd.read_excel(uploaded_file, engine='openpyxl')
    cols = df.columns
    valid_list, error_list = [], []
    
    for idx, row in df.iterrows():
        name_raw = str(row[cols[2]]).strip()
        attr_raw = str(row[cols[6]])
        qty_raw = str(row[cols[8]])
        
        # 排除复合品类
        if ';' in name_raw or '；' in name_raw:
            error_list.append({'行号': idx+2, '订单号': str(row[cols[0]]), '原因': '复合品类'})
            continue

        cat = name_raw.split(' ')[0].upper()
        if cat.startswith('WZ'): cat = 'WZ'
        
        # 提取数量
        nums = re.findall(r'\d+', qty_raw)
        target_qty = int(nums[0]) if nums else 0
        
        # 解析属性块
        chunks = [c.strip() for c in re.split(r'[;；]', attr_raw) if c.strip()]
        temp_items = []
        for chunk in chunks:
            c_m = re.search(COLOR_REG, chunk)
            s_m = re.search(SIZE_REG, chunk)
            if c_m:
                clr = c_m.group(1).strip().upper()
                sze = s_m.group(1).strip().upper() if s_m else "FREE"
                temp_items.append({'Category': cat, 'Color': clr, 'Size': SIZE_MAP.get(sze, sze)})
        
        # 数量对得上才进汇总
        if len(temp_items) == target_qty and target_qty > 0:
            valid_list.extend(temp_items)
        else:
            error_list.append({'行号': idx+2, '订单号': str(row[cols[0]]), '原因': f'数量不符({len(temp_items)}/{target_qty})'})
            
    return pd.DataFrame(valid_list), pd.DataFrame(error_list)

# --- 3. 渲染层：分列显示 ---
st.markdown("<h2 style='text-align:center; padding-top:40px;'>💎 属性解析矩阵</h2>", unsafe_allow_html=True)
file = st.file_uploader("", type=["xlsx"])

if file:
    v_df, e_df = process_data(file)
    t1, t2 = st.tabs(["✅ 汇总矩阵", "❌ 异常拦截"])

    with t1:
        if not v_df.empty:
            # 排序并按 品类+颜色 聚合显示
            v_df = v_df.sort_values(['Category', 'Color'])
            groups = list(v_df.groupby(['Category', 'Color']))
            
            # 每行固定 6 个盒子并列
            cols_per_row = 6
            for i in range(0, len(groups), cols_per_row):
                batch = groups[i : i + cols_per_row]
                cols = st.columns(cols_per_row)
                for j, ((cat, clr), data) in enumerate(batch):
                    sizes = data['Size'].value_counts()
                    size_html = "".join([f'<div class="size-tag">{s}<b>×{q}</b></div>' for s, q in sizes.items()])
                    
                    cols[j].markdown(f"""
                        <div class="attr-card">
                            <div class="card-header">{cat}</div>
                            <div class="card-body"><div class="card-color">{clr}</div></div>
                            <div class="card-footer">{size_html}</div>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("暂无数据")

    with t2:
        st.dataframe(e_df, use_container_width=True)
