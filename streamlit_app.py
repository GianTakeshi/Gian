import streamlit as st
import pandas as pd
import re

# --- 1. UI 配置与样式 ---
st.set_page_config(page_title="GianTakeshi | Category Matrix", page_icon="📦", layout="wide")

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

    /* --- 品类大框容器 --- */
    .category-container {{
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 30px;
    }}
    
    .category-title {{
        font-size: 1.5rem;
        font-weight: 900;
        color: #38bdf8;
        margin-bottom: 20px;
        padding-left: 10px;
        border-left: 5px solid #38bdf8;
        letter-spacing: 2px;
    }}

    /* --- 内部 Color 九宫格布局 --- */
    .color-grid {{
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
    }}

    .color-card {{
        flex: 0 0 calc(16.66% - 12px); 
        min-width: 150px;
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 12px;
        text-align: center;
        transition: all 0.2s;
    }}
    
    .color-card:hover {{
        border-color: #38bdf8;
        background: rgba(56, 189, 248, 0.1);
        transform: translateY(-3px);
    }}

    .color-name {{
        font-size: 0.95rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 10px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        padding-bottom: 5px;
    }}

    .size-row {{
        display: flex;
        flex-wrap: wrap;
        gap: 4px;
        justify-content: center;
    }}
    
    .size-mini {{
        font-size: 0.7rem;
        color: #94a3b8;
        background: rgba(0,0,0,0.3);
        padding: 1px 6px;
        border-radius: 4px;
    }}
    .size-mini b {{ color: #38bdf8; }}
    </style>

    <div class="user-profile">
        <img src="https://avatars.githubusercontent.com/{GITHUB_USERNAME}" class="avatar">
        <div class="user-info">
            <div style="font-weight:700; font-size:0.85rem;">{GITHUB_USERNAME}</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 2. 逻辑处理 ---
def process_logic(uploaded_file):
    COLOR_REG = r'(?i)Color[:：\s]*([a-zA-Z0-9\-_/]+)'
    SIZE_REG = r'(?i)Size[:：\s]*([a-zA-Z0-9\-\s/]+?)(?=\s*(?:Color|Size|$|[,;，；]))'
    SIZE_MAP = {'HIGH ANKLE SOCKS': 'L', 'KNEE-HIGH SOCKS': 'M'}
    
    df = pd.read_excel(uploaded_file, engine='openpyxl')
    valid_data = []
    error_rows = []
    
    for idx, row in df.iterrows():
        c_raw = str(row[df.columns[2]]).strip()
        g_text = str(row[df.columns[6]])
        
        # --- 修正后的数量提取逻辑 ---
        qty_str = str(row[df.columns[8]])
        found_qty = re.findall(r'\d+', qty_str)
        i_qty = int(found_qty[0]) if found_qty else 0
        
        # 品类清洗
        if ';' in c_raw or '；' in c_raw:
            error_rows.append({'行号': idx+2, '原因': '复合品类阻断', '订单编号': str(row[df.columns[0]])})
            continue
            
        cat = c_raw.split(' ')[0].upper()
        if cat.startswith('WZ'): cat = 'WZ'
        
        # 属性解析
        chunks = [c.strip() for c in re.split(r'[;；]', g_text) if c.strip()]
        temp_items = []
        for chunk in chunks:
            c_m = re.search(COLOR_REG, chunk)
            s_m = re.search(SIZE_REG, chunk)
            if c_m:
                clr = c_m.group(1).strip().upper()
                sze = s_m.group(1).strip().upper() if s_m else "FREE"
                temp_items.append({'Category': cat, 'Color': clr, 'Size': SIZE_MAP.get(sze, sze)})
        
        if len(temp_items) == i_qty and i_qty > 0:
            valid_data.extend(temp_items)
        else:
            error_rows.append({'行号': idx+2, '原因': f'数量不符({len(temp_items)}/{i_qty})', '订单编号': str(row[df.columns[0]])})
            
    return pd.DataFrame(valid_data), pd.DataFrame(error_rows)

# --- 3. 渲染 ---
st.markdown("<h1 style='text-align:center; padding-top:60px;'>📦 品类聚合阵列</h1>", unsafe_allow_html=True)
file = st.file_uploader("", type=["xlsx"])

if file:
    v_df, e_df = process_logic(file)
    t1, t2 = st.tabs(["💎 聚合汇总", "📡 异常报告"])

    with t1:
        if not v_df.empty:
            # 排序：品类 -> 颜色
            v_df = v_df.sort_values(['Category', 'Color'])
            
            # 按品类分大组显示
            for cat, cat_group in v_df.groupby('Category'):
                st.markdown(f'<div class="category-container"><div class="category-title">📂 品类分类: {cat}</div>', unsafe_allow_html=True)
                
                color_groups = cat_group.groupby('Color')
                color_grid_html = '<div class="color-grid">'
                
                for clr, clr_group in color_groups:
                    size_counts = clr_group['Size'].value_counts()
                    size_html = "".join([f'<div class="size-mini">{s} <b>×{q}</b></div>' for s, q in size_counts.items()])
                    
                    color_grid_html += f"""
                        <div class="color-card">
                            <div class="color-name">{clr}</div>
                            <div class="size-row">{size_html}</div>
                        </div>
                    """
                color_grid_html += '</div></div>'
                st.markdown(color_grid_html, unsafe_allow_html=True)
        else:
            st.info("暂无有效汇总数据，请检查上传文件。")

    with t2:
        if not e_df.empty:
            st.warning(f"检测到 {len(e_df)} 条异常行：")
            st.dataframe(e_df, use_container_width=True)
        else:
            st.success("数据解析完美！")
