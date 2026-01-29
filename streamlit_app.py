import streamlit as st
import pandas as pd
import re
import html

# --- 1. UI 配置 ---
st.set_page_config(page_title="GianTakeshi | Matrix Hub", page_icon="📊", layout="wide")

st.markdown(f"""
    <style>
    .stApp {{ background: #020617; color: #ffffff; }}
    header {{ visibility: hidden; }}
    .user-profile {{
        position: fixed; top: 20px; left: 20px; display: flex; align-items: center; gap: 12px; z-index: 99999; 
        background: rgba(255, 255, 255, 0.05); padding: 5px 15px 5px 5px; border-radius: 50px;
        border: 1px solid rgba(56, 189, 248, 0.3); backdrop-filter: blur(10px);
    }}
    .color-row {{ background: rgba(255, 255, 255, 0.03); margin: 6px 0; padding: 8px 12px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.08); }}
    .clr-label {{ font-size: 0.9rem; font-weight: 800; color: #38bdf8; margin-bottom: 4px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 2px; }}
    .size-chips {{ display: flex; flex-wrap: wrap; gap: 6px; }}
    .size-chip {{ font-size: 0.75rem; color: #cbd5e1; background: rgba(255,255,255,0.05); padding: 1px 6px; border-radius: 4px; border: 1px solid rgba(255,255,255,0.1); }}
    .size-chip b {{ color: #38bdf8; margin-left: 2px; }}
    </style>
    <div class="user-profile">
        <img src="https://avatars.githubusercontent.com/GianTakeshi" style="width:35px;height:35px;border-radius:50%;">
        <div style="font-weight:700; font-size:0.85rem; color:white;">GianTakeshi</div>
    </div>
""", unsafe_allow_html=True)

# --- 2. 逻辑层 (增强容错) ---
def process_data(uploaded_file):
    # 更加灵活的正则：支持冒号可选，支持更多字符
    COLOR_REG = r'(?i)Color[:：\s]*([a-zA-Z0-9\-_/]+)'
    SIZE_REG = r'(?i)Size[:：\s]*([a-zA-Z0-9\-\s/]+?)(?=\s*(?:Color|Size|$|[,;，；]))'
    SIZE_MAP = {'HIGH ANKLE SOCKS': 'L', 'KNEE-HIGH SOCKS': 'M'}
    
    df = pd.read_excel(uploaded_file, engine='openpyxl')
    valid, error = [], []
    
    for idx, row in df.iterrows():
        try:
            # 自动对齐列，防止列名变动
            name = str(row.iloc[2]).strip()   # 品类列
            attr = str(row.iloc[6]).strip()   # 属性列
            qty_raw = str(row.iloc[8]).strip() # 数量列
            
            if ';' in name or '；' in name:
                error.append({'行': idx+2, '原因': '复合品类'})
                continue

            # 处理品类前缀
            cat = name.split(' ')[0].upper()
            if cat.startswith('WZ'): cat = 'WZ'
            
            # 解析数量
            found_qty = re.findall(r'\d+', qty_raw)
            target_qty = int(found_qty[0]) if found_qty else 0
            
            # 解析属性块
            chunks = [c.strip() for c in re.split(r'[;；]', attr) if c.strip()]
            parsed_items = []
            for chunk in chunks:
                c_m = re.search(COLOR_REG, chunk)
                s_m = re.search(SIZE_REG, chunk)
                if c_m:
                    clr = c_m.group(1).strip().upper()
                    sze_raw = s_m.group(1).strip().upper() if s_m else "FREE"
                    parsed_items.append({'Category': cat, 'Color': clr, 'Size': SIZE_MAP.get(sze_raw, sze_raw)})
            
            # 即使数量对不上，只要抓到了属性就先显示，不再强行拦截
            if parsed_items:
                valid.extend(parsed_items)
                if len(parsed_items) != target_qty:
                    error.append({'行': idx+2, '原因': f'数量偏差({len(parsed_items)}/{target_qty})'})
            else:
                error.append({'行': idx+2, '原因': '无法解析属性内容'})
        except Exception as e:
            error.append({'行': idx+2, '原因': f'代码报错: {str(e)}'})
            
    return pd.DataFrame(valid), pd.DataFrame(error)

# --- 3. 渲染层 ---
st.markdown("<h2 style='text-align:center; padding-top:50px;'>📊 颜色聚合看板 (修复版)</h2>", unsafe_allow_html=True)
file = st.file_uploader("上传 Excel 文件", type=["xlsx"])

if file:
    v_df, e_df = process_data(file)
    t1, t2 = st.tabs(["✅ 矩阵汇总", "❌ 异常/日志"])
    
    with t1:
        if not v_df.empty:
            v_df = v_df.sort_values(['Category', 'Color'])
            cat_groups = list(v_df.groupby('Category'))
            
            cols_per_row = 6
            for i in range(0, len(cat_groups), cols_per_row):
                batch = cat_groups[i : i + cols_per_row]
                cols = st.columns(cols_per_row)
                
                for idx, (cat, group) in enumerate(batch):
                    with cols[idx].container(border=True):
                        st.markdown(f"""<div style="text-align:center; color:#38bdf8; font-weight:900; font-size:1.1rem; border-bottom:1px solid rgba(56,189,248,0.2); padding-bottom:5px;">{cat}</div>""", unsafe_allow_html=True)
                        st.markdown(f"""<div style="text-align:center; color:#94a3b8; font-size:0.7rem; margin-bottom:8px;">Total items: {len(group)}</div>""", unsafe_allow_html=True)
                        
                        # 颜色聚合显示
                        color_groups = group.groupby('Color')
                        for clr, clr_data in color_groups:
                            size_stats = clr_data['Size'].value_counts().sort_index()
                            size_html = "".join([f'<span class="size-chip">{s}<b>×{q}</b></span>' for s, q in size_stats.items()])
                            
                            st.markdown(f"""
                            <div class="color-row">
                                <div class="clr-label">{html.escape(str(clr))}</div>
                                <div class="size-chips">{size_html}</div>
                            </div>
                            """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ 解析结果仍为空，请检查：1. 文件是否加密？ 2. 属性列是否包含 'Color' 关键词？")
            
    with t2:
        st.dataframe(e_df, use_container_width=True)
