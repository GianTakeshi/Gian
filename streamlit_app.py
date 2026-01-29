import streamlit as st
import pandas as pd
import re
import time

# --- 1. 页面配置与 UI (增强玻璃感) ---
st.set_page_config(page_title="SKU预览工具", page_icon="🚀", layout="wide") # 宽屏显示效果更好

GITHUB_USERNAME = "GianTakeshi" 

st.markdown(f"""
    <style>
    .stApp {{ background: radial-gradient(circle at 50% 50%, #1e293b, #010409); color: #ffffff; }}
    header {{visibility: hidden;}}

    /* 结果显示面板 */
    .result-container {{
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 20px;
        padding: 25px;
        margin-top: 20px;
    }}
    .category-header {{
        color: #38bdf8;
        font-size: 1.8rem;
        font-weight: 800;
        border-bottom: 2px solid rgba(56, 189, 248, 0.3);
        margin-bottom: 15px;
        padding-bottom: 5px;
    }}
    .data-row {{
        display: flex;
        justify-content: space-between;
        padding: 8px 15px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        transition: background 0.3s;
    }}
    .data-row:hover {{ background: rgba(56, 189, 248, 0.1); }}
    .color-label {{ font-weight: 600; color: #e2e8f0; }}
    .size-tag {{
        background: rgba(56, 189, 248, 0.2);
        color: #38bdf8;
        padding: 2px 10px;
        border-radius: 6px;
        font-size: 0.85rem;
        margin-left: 10px;
    }}

    /* 左上角头像面板 */
    .user-profile {{
        position: fixed; top: 25px; left: 25px; display: flex; align-items: center; gap: 12px; z-index: 9999;
        background: rgba(255, 255, 255, 0.05); padding: 6px 16px 6px 6px; border-radius: 50px;
        border: 1px solid rgba(56, 189, 248, 0.3); backdrop-filter: blur(10px);
    }}
    .avatar {{ width: 38px; height: 38px; border-radius: 50%; border: 2px solid #38bdf8; object-fit: cover; }}
    </style>
    
    <div class="user-profile">
        <img src="https://avatars.githubusercontent.com/{GITHUB_USERNAME}" class="avatar">
        <div style="display: flex; flex-direction: column;">
            <span style="font-weight:700; font-size:0.9rem;">{GITHUB_USERNAME}</span>
            <span style="font-size:0.65rem; color:#10b981;">● 实时预览模式</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 2. 核心逻辑 (保持你的源代码提取逻辑) ---
def process_sku_logic(uploaded_file):
    COLOR_REG = r'(?i)Color[:：\s]*([a-zA-Z0-9\-_/]+)'
    SIZE_REG = r'(?i)Size[:：\s]*([a-zA-Z0-9\-\s/]+?)(?=\s*(?:Color|Size|$|[,;，；]))'
    SIZE_MAP = {'HIGH ANKLE SOCKS': 'L', 'KNEE-HIGH SOCKS': 'M'}
    
    df = pd.read_excel(uploaded_file, engine='openpyxl')
    col_a, col_c, col_g, col_i = df.columns[0], df.columns[2], df.columns[6], df.columns[8]
    all_normal_data, all_error_rows = [], []

    for index, row in df.iterrows():
        c_raw = str(row[col_c]).strip()
        if not c_raw or c_raw == 'nan': continue
        
        category_name = c_raw.split(' ')[0].upper()
        if category_name.startswith('WZ'): category_name = 'WZ'

        g_text = str(row[col_g])
        i_qty = int(re.findall(r'\d+', str(row[col_i]))[0]) if re.findall(r'\d+', str(row[col_i])) else 0

        chunks = re.split(r'[;；]', g_text)
        data_pairs = []
        for chunk in chunks:
            chunk = chunk.strip()
            if not chunk: continue
            c_match = re.search(COLOR_REG, chunk)
            s_match = re.search(SIZE_REG, chunk)
            if c_match:
                color_val = c_match.group(1).strip().upper()
                raw_size = s_match.group(1).strip().upper() if s_match else ""
                data_pairs.append((color_val, SIZE_MAP.get(raw_size, raw_size)))

        if len(data_pairs) == i_qty and i_qty > 0:
            for c_val, s_val in data_pairs:
                all_normal_data.append({'Category': category_name, 'Color': c_val, 'Size': s_val})
        else:
            all_error_rows.append({'行号': index + 2, '品名': category_name, '原因': f"解析({len(data_pairs)})≠购买({i_qty})"})

    return pd.DataFrame(all_normal_data), pd.DataFrame(all_error_rows)

# --- 3. 页面渲染 ---
st.markdown("<div style='text-align:center; padding-top:30px;'><h1 style='color:#38bdf8; font-size:3rem; font-weight:800;'>数据实时看板 🚀</h1></div>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("", type=["xlsx"])

if uploaded_file:
    with st.spinner('正在透视数据...'):
        final_df, error_df = process_sku_logic(uploaded_file)
    
    # --- 分栏显示：左边预览结果，右边显示异常 ---
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown("### 📊 汇总结果")
        if not final_df.empty:
            categories = sorted(final_df['Category'].unique())
            for cat in categories:
                st.markdown(f"""<div class="result-container">
                    <div class="category-header">{cat}</div>
                """, unsafe_allow_html=True)
                
                cat_data = final_df[final_df['Category'] == cat]
                # 按颜色分组
                colors = sorted(cat_data['Color'].unique(), key=lambda x: int(re.findall(r'\d+', str(x))[0]) if re.findall(r'\d+', str(x)) else 999)
                
                for clr in colors:
                    color_data = cat_data[cat_data['Color'] == clr]
                    counts = color_data['Size'].value_counts()
                    # 拼接 Size 标签
                    size_tags = "".join([f'<span class="size-tag">{"无尺码" if s=="" else s} *{q}</span>' for s, q in counts.items()])
                    
                    st.markdown(f"""
                        <div class="data-row">
                            <span class="color-label">Color {clr}</span>
                            <div class="tags-container">{size_tags}</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("暂无有效汇总数据")

    with col_right:
        st.markdown("### ⚠️ 异常监控")
        if not error_df.empty:
            for _, err in error_df.iterrows():
                st.markdown(f"""
                    <div style="background:rgba(245, 158, 11, 0.1); border:1px solid #f59e0b; padding:15px; border-radius:15px; margin-bottom:10px;">
                        <span style="color:#f59e0b; font-weight:bold;">行 {err['行号']}</span> | {err['品名']}<br>
                        <small style="color:#94a3b8;">{err['原因']}</small>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div style="background:rgba(16, 185, 129, 0.1); border:1px solid #10b981; padding:15px; border-radius:15px; text-align:center;">
                    <span style="color:#10b981;">✅ 暂无异常数据</span>
                </div>
            """, unsafe_allow_html=True)

st.markdown("<div style='text-align:center; margin-top:50px; color:rgba(148,163,184,0.3);'>GianTakeshi LIVE VIEW v4.0</div>", unsafe_allow_html=True)
