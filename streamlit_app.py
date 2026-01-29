import streamlit as st
import pandas as pd
import re

# --- 1. UI 配置与极致嵌套样式 ---
st.set_page_config(page_title="GianTakeshi | Matrix", page_icon="💎", layout="wide")

GITHUB_USERNAME = "GianTakeshi"

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
    .avatar {{ width: 35px; height: 35px; border-radius: 50%; border: 2px solid #38bdf8; object-fit: cover; }}

    /* --- 大盒子外框 --- */
    .attr-card {{
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        margin-bottom: 15px;
        display: flex;
        flex-direction: column;
        min-height: 120px;
        overflow: hidden;
    }}

    /* 品类名称：字体加大 */
    .card-header {{
        background: rgba(56, 189, 248, 0.15);
        color: #38bdf8;
        font-size: 1.1rem; /* 字体加大 */
        font-weight: 900;
        padding: 8px;
        text-align: center;
        letter-spacing: 2px;
        border-bottom: 1px solid rgba(56, 189, 248, 0.1);
    }}

    /* 内部内容区 */
    .card-body {{
        padding: 12px;
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        justify-content: center;
        align-content: flex-start;
    }}

    /* --- 嵌套的小格子（胶囊） --- */
    .nested-capsule {{
        display: inline-flex;
        align-items: center;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        overflow: hidden;
        transition: all 0.2s ease;
    }}
    .nested-capsule:hover {{
        border-color: #38bdf8;
        background: rgba(56, 189, 248, 0.1);
    }}

    /* 胶囊内的 Color 部分 */
    .cap-color {{
        padding: 4px 10px;
        background: rgba(255, 255, 255, 0.05);
        font-size: 0.85rem;
        font-weight: 700;
        color: #ffffff;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }}

    /* 胶囊内的 Size & 数量部分 */
    .cap-size-qty {{
        padding: 4px 10px;
        font-size: 0.8rem;
        color: #94a3b8;
    }}
    .cap-size-qty b {{
        color: #38bdf8;
        margin-left: 4px;
    }}
    </style>

    <div class="user-profile">
        <img src="https://avatars.githubusercontent.com/{GITHUB_USERNAME}" class="avatar">
        <div style="font-weight:700; font-size:0.85rem;">{GITHUB_USERNAME}</div>
    </div>
""", unsafe_allow_html=True)

# --- 2. 逻辑处理 (保持严谨) ---
def process_data(uploaded_file):
    COLOR_REG = r'(?i)Color[:：\s]*([a-zA-Z0-9\-_/]+)'
    SIZE_REG = r'(?i)Size[:：\s]*([a-zA-Z0-9\-\s/]+?)(?=\s*(?:Color|Size|$|[,;，；]))'
    SIZE_MAP = {'HIGH ANKLE SOCKS': 'L', 'KNEE-HIGH SOCKS': 'M'}
    
    df = pd.read_excel(uploaded_file, engine='openpyxl')
    valid_list, error_list = [], []
    
    for idx, row in df.iterrows():
        name_raw = str(row[df.columns[2]]).strip()
        attr_raw = str(row[df.columns[6]])
        qty_str = str(row[df.columns[8]])
        
        if ';' in name_raw or '；' in name_raw:
            error_list.append({'行号': idx+2, '原因': '复合品类'})
            continue

        cat = name_raw.split(' ')[0].upper()
        if cat.startswith('WZ'): cat = 'WZ'
        
        nums = re.findall(r'\d+', qty_str)
        target_qty = int(nums[0]) if nums else 0
        
        chunks = [c.strip() for c in re.split(r'[;；]', attr_raw) if c.strip()]
        temp_items = []
        for chunk in chunks:
            c_m = re.search(COLOR_REG, chunk)
            s_m = re.search(SIZE_REG, chunk)
            if c_m:
                clr = c_m.group(1).strip().upper()
                sze = s_m.group(1).strip().upper() if s_m else "FREE"
                temp_items.append({'Category': cat, 'Color': clr, 'Size': SIZE_MAP.get(sze, sze)})
        
        if len(temp_items) == target_qty and target_qty > 0:
            valid_list.extend(temp_items)
        else:
            error_list.append({'行号': idx+2, '原因': f'数量不符({len(temp_items)}/{target_qty})'})
            
    return pd.DataFrame(valid_list), pd.DataFrame(error_list)

# --- 3. 渲染层 ---
st.markdown("<h2 style='text-align:center; padding-top:40px;'>📦 嵌套属性矩阵</h2>", unsafe_allow_html=True)
file = st.file_uploader("", type=["xlsx"])

if file:
    v_df, e_df = process_data(file)
    t1, t2 = st.tabs(["✅ 汇总矩阵", "❌ 异常拦截"])

    with t1:
        if not v_df.empty:
            # 按品类分大组，确保“一个属性（大类）都在一个框里”
            v_df = v_df.sort_values(['Category', 'Color'])
            cat_groups = list(v_df.groupby('Category'))
            
            # 依然保持横向 4-6 列排列大盒子
            cols_per_row = 4
            for i in range(0, len(cat_groups), cols_per_row):
                batch = cat_groups[i : i + cols_per_row]
                cols = st.columns(cols_per_row)
                for j, (cat, group) in enumerate(batch):
                    
                    # 生成内部的小胶囊 HTML
                    capsules_html = ""
                    # 在大类内部，按 Color+Size 统计
                    sub_groups = group.groupby(['Color', 'Size']).size().reset_index(name='count')
                    for _, sub_row in sub_groups.iterrows():
                        capsules_html += f"""
                            <div class="nested-capsule">
                                <div class="cap-color">{sub_row['Color']}</div>
                                <div class="cap-size-qty">{sub_row['Size']} <b>×{sub_row['count']}</b></div>
                            </div>
                        """
                    
                    cols[j].markdown(f"""
                        <div class="attr-card">
                            <div class="card-header">{cat}</div>
                            <div class="card-body">
                                {capsules_html}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("暂无数据")

    with t2:
        st.dataframe(e_df, use_container_width=True)
