import streamlit as st
import pandas as pd
import re
import html

# --- 1. UI 配置 ---
st.set_page_config(page_title="GianTakeshi | Matrix Hub", page_icon="💎", layout="wide")

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

    /* 大盒子：属性分类框 */
    .attr-card {{
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 16px;
        margin-bottom: 20px;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }}

    .card-header {{
        background: rgba(56, 189, 248, 0.2);
        color: #38bdf8;
        font-size: 1.2rem; /* 字体加大 */
        font-weight: 900;
        padding: 10px;
        text-align: center;
        border-bottom: 1px solid rgba(56, 189, 248, 0.1);
    }}

    .card-body {{
        padding: 15px;
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        justify-content: flex-start;
    }}

    /* 嵌套的小格子：Color + Size 胶囊 */
    .nested-capsule {{
        display: inline-flex;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 6px;
        overflow: hidden;
        background: rgba(255, 255, 255, 0.02);
    }}

    .cap-color {{
        background: rgba(56, 189, 248, 0.1);
        padding: 4px 10px;
        font-size: 0.85rem;
        font-weight: 700;
        color: #ffffff;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }}

    .cap-size-qty {{
        padding: 4px 10px;
        font-size: 0.8rem;
        color: #cbd5e1;
    }}
    .cap-size-qty b {{ color: #38bdf8; margin-left: 2px; }}
    </style>

    <div class="user-profile">
        <img src="https://avatars.githubusercontent.com/{GITHUB_USERNAME}" class="avatar">
        <div style="font-weight:700; font-size:0.85rem;">{GITHUB_USERNAME}</div>
    </div>
""", unsafe_allow_html=True)

# --- 2. 增强版解析逻辑 ---
def safe_process(uploaded_file):
    COLOR_REG = r'(?i)Color[:：\s]*([a-zA-Z0-9\-_/]+)'
    SIZE_REG = r'(?i)Size[:：\s]*([a-zA-Z0-9\-\s/]+?)(?=\s*(?:Color|Size|$|[,;，；]))'
    SIZE_MAP = {'HIGH ANKLE SOCKS': 'L', 'KNEE-HIGH SOCKS': 'M'}
    
    df = pd.read_excel(uploaded_file, engine='openpyxl')
    valid_list, error_list = [], []
    
    for idx, row in df.iterrows():
        try:
            name_raw = str(row[df.columns[2]]).strip()
            attr_raw = str(row[df.columns[6]])
            qty_raw = str(row[df.columns[8]])
            
            if ';' in name_raw or '；' in name_raw:
                error_list.append({'行号': idx+2, '原因': '复合品类'})
                continue

            cat = name_raw.split(' ')[0].upper()
            if cat.startswith('WZ'): cat = 'WZ'
            
            nums = re.findall(r'\d+', qty_raw)
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
                error_list.append({'行号': idx+2, '原因': f'数量不对({len(temp_items)}/{target_qty})'})
        except Exception as e:
            error_list.append({'行号': idx+2, '原因': f'解析崩溃: {str(e)}'})
            
    return pd.DataFrame(valid_list), pd.DataFrame(error_list)

# --- 3. 渲染渲染 ---
st.markdown("<h2 style='text-align:center; padding-top:50px;'>📦 属性大盒矩阵</h2>", unsafe_allow_html=True)
file = st.file_uploader("", type=["xlsx"])

if file:
    v_df, e_df = safe_process(file)
    t1, t2 = st.tabs(["✅ 汇总矩阵", "❌ 拦截详情"])

    with t1:
        if not v_df.empty:
            v_df = v_df.sort_values(['Category', 'Color', 'Size'])
            cat_groups = list(v_df.groupby('Category'))
            
            # 为了防止报错，减少每行显示的列数，让内部小格子有更多空间
            cols_per_row = 3 
            for i in range(0, len(cat_groups), cols_per_row):
                batch = cat_groups[i : i + cols_per_row]
                cols = st.columns(cols_per_row)
                for j, (cat, group) in enumerate(batch):
                    
                    caps_html = ""
                    # 按照 Color + Size 聚合显示
                    sub_stats = group.groupby(['Color', 'Size']).size().reset_index(name='count')
                    for _, s_row in sub_stats.iterrows():
                        # 安全转义颜色名，防止 HTML 报错
                        safe_clr = html.escape(str(s_row['Color']))
                        caps_html += f"""
                            <div class="nested-capsule">
                                <div class="cap-color">{safe_clr}</div>
                                <div class="cap-size-qty">{s_row['Size']}<b>×{s_row['count']}</b></div>
                            </div>
                        """
                    
                    cols[j].markdown(f"""
                        <div class="attr-card">
                            <div class="card-header">{cat}</div>
                            <div class="card-body">{caps_html}</div>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("数据解析后为空，请检查文件格式。")

    with t2:
        st.dataframe(e_df, use_container_width=True)
