import streamlit as st
import pandas as pd
import re

# --- 1. 顶部 UI 增强 ---
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
    .user-name {{ font-weight: 700; font-size: 0.85rem; color: #ffffff; }}

    /* 每个属性框的独立样式 */
    .attr-box {{
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 14px;
        margin-bottom: 15px;
        height: 140px;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    
    .attr-box:hover {{
        border-color: #38bdf8;
        background: rgba(56, 189, 248, 0.08);
        transform: translateY(-4px);
        box-shadow: 0 10px 20px -10px rgba(56, 189, 248, 0.3);
    }}

    .box-header {{
        background: rgba(56, 189, 248, 0.15);
        color: #38bdf8;
        font-size: 0.75rem;
        font-weight: 900;
        padding: 6px;
        text-align: center;
        letter-spacing: 1px;
        border-bottom: 1px solid rgba(56, 189, 248, 0.1);
    }}

    .box-content {{
        flex-grow: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 10px;
        text-align: center;
    }}
    
    .box-color {{
        font-size: 1rem;
        font-weight: 800;
        color: #ffffff;
        line-height: 1.2;
    }}

    .box-footer {{
        background: rgba(0, 0, 0, 0.2);
        padding: 6px;
        display: flex;
        flex-wrap: wrap;
        gap: 4px;
        justify-content: center;
        min-height: 32px;
    }}
    
    .size-badge {{
        font-size: 0.65rem;
        color: #94a3b8;
        background: rgba(255,255,255,0.08);
        padding: 1px 6px;
        border-radius: 4px;
        border: 1px solid rgba(255,255,255,0.05);
    }}
    .size-badge b {{ color: #38bdf8; font-weight: 900; }}
    </style>

    <div class="user-profile">
        <img src="https://avatars.githubusercontent.com/{GITHUB_USERNAME}" class="avatar">
        <div class="user-name">{GITHUB_USERNAME}</div>
    </div>
""", unsafe_allow_html=True)

# --- 2. 逻辑层：过滤错误并聚合 ---
def process_data(uploaded_file):
    COLOR_REG = r'(?i)Color[:：\s]*([a-zA-Z0-9\-_/]+)'
    SIZE_REG = r'(?i)Size[:：\s]*([a-zA-Z0-9\-\s/]+?)(?=\s*(?:Color|Size|$|[,;，；]))'
    SIZE_MAP = {'HIGH ANKLE SOCKS': 'L', 'KNEE-HIGH SOCKS': 'M'}
    
    df = pd.read_excel(uploaded_file, engine='openpyxl')
    cols = df.columns
    
    valid_list = []
    error_list = []
    
    for idx, row in df.iterrows():
        # 获取基础信息
        item_name = str(row[cols[2]]).strip()
        attr_text = str(row[cols[6]])
        qty_val = str(row[cols[8]])
        order_sn = str(row[cols[0]])

        # 1. 过滤复合品类
        if ';' in item_name or '；' in item_name:
            error_list.append({'行号': idx+2, '订单号': order_sn, '原因': '复合品类阻断'})
            continue

        # 2. 解析属性
        target_qty = int(re.findall(r'\d+', qty_val)[0]) if re.findall(r'\d+', qty_val) else 0
        chunks = [c.strip() for c in re.split(r'[;；]', attr_text) if c.strip()]
        
        parsed_items = []
        for chunk in chunks:
            c_m = re.search(COLOR_REG, chunk)
            s_m = re.search(SIZE_REG, chunk)
            if c_m:
                clr = c_m.group(1).strip().upper()
                sze = s_m.group(1).strip().upper() if s_m else "FREE"
                parsed_items.append({'Color': clr, 'Size': SIZE_MAP.get(sze, sze)})
        
        # 3. 校验数量
        if len(parsed_items) == target_qty and target_qty > 0:
            cat = item_name.split(' ')[0].upper()
            if cat.startswith('WZ'): cat = 'WZ'
            for item in parsed_items:
                item['Category'] = cat
                valid_list.append(item)
        else:
            error_list.append({'行号': idx+2, '订单号': order_sn, '原因': f'数量不符({len(parsed_items)}/{target_qty})'})

    return pd.DataFrame(valid_list), pd.DataFrame(error_list)

# --- 3. 渲染层 ---
st.markdown("<h2 style='text-align:center; padding-top:40px;'>💎 属性矩阵看板</h2>", unsafe_allow_html=True)
file = st.file_uploader("", type=["xlsx"])

if file:
    v_df, e_df = process_data(file)
    t1, t2 = st.tabs(["✅ 正确汇总", "❌ 异常拦截"])

    with t1:
        if not v_df.empty:
            # 排序并分组：确保每个属性组合只占一个框
            v_df = v_df.sort_values(['Category', 'Color'])
            groups = list(v_df.groupby(['Category', 'Color']))
            
            # 核心：每行 6 个框排开
            row_size = 6
            for i in range(0, len(groups), row_size):
                batch = groups[i : i + row_size]
                cols = st.columns(row_size)
                for j, ((cat, clr), data) in enumerate(batch):
                    sizes = data['Size'].value_counts()
                    size_html = "".join([f'<div class="size-badge">{s} <b>×{q}</b></div>' for s, q in sizes.items()])
                    
                    cols[j].markdown(f"""
                        <div class="attr-box">
                            <div class="box-header">{cat}</div>
                            <div class="box-content"><div class="box-color">{clr}</div></div>
                            <div class="box-footer">{size_html}</div>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("没有可显示的属性数据")

    with t2:
        if not e_df.empty:
            st.dataframe(e_df, use_container_width=True)
        else:
            st.success("全部数据解析正确！")

    if st.button("清空并重新上传"):
        st.rerun()
