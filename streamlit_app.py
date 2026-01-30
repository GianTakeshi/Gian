import streamlit as st
import pandas as pd
import re

# --- 1. 页面配置 ---
st.set_page_config(page_title="SKU 属性解析中枢", page_icon="🚀", layout="wide")

GITHUB_USERNAME = "GianTakeshi" 
BASE_URL = "https://inflyway.com/kamelnet/#/kn/fly-link/orders/detail?id="

# --- 2. 注入 JS 逻辑：实时追踪鼠标位置 ---
st.markdown("""
    <script>
    function updateMousePos(e) {
        const cards = document.querySelectorAll('.wide-card');
        cards.forEach(card => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            card.style.setProperty('--x', `${x}px`);
            card.style.setProperty('--y', `${y}px`);
        });
    }
    document.addEventListener('mousemove', updateMousePos);
    </script>
""", unsafe_allow_html=True)

# --- 3. 注入动态光源 CSS ---
st.markdown(f"""
    <style>
    /* 🎭 全局背景与 V11 基础样式 */
    .stApp {{ background: radial-gradient(circle at 50% 50%, #0c1e3d 0%, #020617 60%, #000000 100%) !important; color: #ffffff; }}
    header {{visibility: hidden;}}
    
    .user-profile {{
        position: fixed; top: 25px; left: 25px; display: flex; align-items: center; gap: 12px; z-index: 1000000; 
        background: rgba(255, 255, 255, 0.05); padding: 8px 18px 8px 8px; border-radius: 50px;
        border: 1px solid rgba(56, 189, 248, 0.2); backdrop-filter: blur(15px);
    }}
    .avatar {{ width: 40px; height: 40px; border-radius: 50%; border: 2px solid #38bdf8; animation: avatarPulse 2.5s infinite ease-in-out; }}
    @keyframes avatarPulse {{ 0%, 100% {{ box-shadow: 0 0 5px rgba(56, 189, 248, 0.2); }} 50% {{ box-shadow: 0 0 20px rgba(56, 189, 248, 0.6); }} }}

    /* 🧊 核心：随动光源卡片 */
    .wide-card {{
        position: relative;
        background: rgba(255, 255, 255, 0.03); 
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px; padding: 25px 30px; margin-bottom: 25px;
        display: flex; flex-direction: row; align-items: center; justify-content: space-between;
        backdrop-filter: blur(15px);
        overflow: hidden; /* 确保光晕不溢出 */
        transition: transform 0.4s ease, border-color 0.4s ease;
        /* 默认流水动画 */
        animation: cardReveal 0.6s ease-out both;
    }}

    @keyframes cardReveal {{ from {{ opacity: 0; transform: translateY(20px); }} to {{ opacity: 1; transform: translateY(0); }} }}

    /* ✨ 随动蓝色光晕底层 */
    .wide-card::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        /* 这里的 var(--x) 和 var(--y) 由 JS 动态提供 */
        background: radial-gradient(circle 300px at var(--x, 50%) var(--y, 50%), 
                    rgba(56, 189, 248, 0.15), 
                    transparent 80%);
        opacity: 0;
        transition: opacity 0.3s ease;
        pointer-events: none;
        z-index: 1;
    }}

    .wide-card:hover {{
        transform: translateY(-5px);
        border-color: rgba(56, 189, 248, 0.5);
        box-shadow: 0 0 30px rgba(56, 189, 248, 0.1);
    }}

    .wide-card:hover::before {{
        opacity: 1;
    }}

    /* 💊 保持 V11 药丸与按钮逻辑 */
    .sn-pill {{ position: relative; z-index: 10; padding: 5px 15px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; text-decoration: none !important; }}
    .normal-sn {{ background: rgba(56, 189, 248, 0.1); color: #38bdf8 !important; border: 1px solid rgba(56, 189, 248, 0.2); }}
    .normal-sn:hover {{ background: #38bdf8 !important; color: #000 !important; box-shadow: 0 0 15px #38bdf8; }}
    
    div.stButton > button {{
        background: rgba(255, 255, 255, 0.03) !important; color: #38bdf8 !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important; border-radius: 50px !important;
        padding: 10px 50px !important; display: block !important; margin: 30px auto !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 4. 逻辑部分 ---
def process_sku_logic(uploaded_file):
    COLOR_REG, SIZE_REG = r'(?i)Color[:：\s]*([a-zA-Z0-9\-_/]+)', r'(?i)Size[:：\s]*([a-zA-Z0-9\-\s/]+?)(?=\s*(?:Color|Size|$|[,;，；]))'
    SIZE_MAP = {'HIGH ANKLE SOCKS': 'L', 'KNEE-HIGH SOCKS': 'M'}
    df = pd.read_excel(uploaded_file, engine='openpyxl')
    cols = df.columns
    all_normal_data, all_error_rows = [], []
    for index, row in df.iterrows():
        c_raw = str(row[cols[2]]).strip()
        if not c_raw or c_raw == 'nan': continue
        cat = c_raw.split(' ')[0].upper()
        if cat.startswith('WZ'): cat = 'WZ'
        g_text, i_val, sn = str(row[cols[6]]), str(row[cols[8]]), str(row[cols[0]])
        i_qty = int(re.findall(r'\d+', i_val)[0]) if re.findall(r'\d+', i_val) else 0
        if ';' in c_raw or '；' in c_raw:
            all_error_rows.append({'SN': sn, 'Line': index+2, 'Reason': "品类冲突", 'Content': g_text})
            continue
        chunks = [c.strip() for c in re.split(r'[;；]', g_text) if c.strip()]
        data_pairs = []
        for chunk in chunks:
            c_m, s_m = re.search(COLOR_REG, chunk), re.search(SIZE_REG, chunk)
            if c_m:
                clr = c_m.group(1).strip().upper()
                raw_s = s_m.group(1).strip().upper() if s_m else "FREE"
                data_pairs.append((clr, SIZE_MAP.get(raw_s, raw_s)))
        if len(data_pairs) == i_qty and i_qty > 0:
            for c_val, s_val in data_pairs:
                all_normal_data.append({'Category': cat, 'Color': c_val, 'Size': s_val, 'SN': sn})
        else:
            all_error_rows.append({'SN': sn, 'Line': index+2, 'Reason': f"数量异常({len(data_pairs)}/{i_qty})", 'Content': g_text})
    return pd.DataFrame(all_normal_data), pd.DataFrame(all_error_rows)

# --- 5. 渲染循环 ---
upload_zone = st.empty()
uploaded_file = upload_zone.file_uploader("Upload", type=["xlsx"])

if uploaded_file:
    v_df, e_df = process_sku_logic(uploaded_file)
    upload_zone.empty() 
    t1, t2 = st.tabs(["💎 汇总数据流", "📡 异常拦截"])
    
    with t1:
        if not v_df.empty:
            cats = sorted(v_df['Category'].unique())
            for i, cat in enumerate(cats):
                delay = i * 0.08
                cat_group = v_df[v_df['Category'] == cat]
                attr_html = ""
                for clr in sorted(cat_group['Color'].unique()):
                    clr_group = cat_group[cat_group['Color'] == clr]
                    size_counts = clr_group['Size'].value_counts().sort_index()
                    sizes_html = "".join([f"<div style='display:inline-flex; align-items:center; background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); border-radius:8px; padding:3px 12px; margin-right:8px;'><span style='color:#fff; font-size:0.8rem; font-weight:600;'>{(s if s!='FREE' else '')}</span><span style='color:#38bdf8; font-weight:800; margin-left:5px;'>{('×' if s!='FREE' else '')}{q}</span></div>" for s, q in size_counts.items()])
                    attr_html += f"<div style='display:flex; align-items:center; gap:20px; padding:8px 0;'><div style='color:#38bdf8; font-weight:700; font-size:1rem; min-width:100px;'>{clr}</div><div>{sizes_html}</div></div>"
                
                sns = sorted(list(set(cat_group['SN'].tolist())))
                sn_html = "".join([f'<a href="{BASE_URL}{sn}" target="_blank" class="sn-pill normal-sn">{sn}</a>' for sn in sns])
                
                # 渲染卡片：注意 z-index 确保内容在光晕上方
                st.markdown(f'''<div class="wide-card normal-card" style="animation-delay: {delay}s;">
                    <div style="flex:1; position:relative; z-index:5;">
                        <div style="color:#38bdf8; font-weight:900; font-size:1.6rem; margin-bottom:12px; letter-spacing:1px;">{cat}</div>
                        {attr_html}
                    </div>
                    <div style="display:flex; flex-wrap:wrap; gap:8px; justify-content:flex-end; max-width:400px; position:relative; z-index:5;">
                        {sn_html}
                    </div>
                </div>''', unsafe_allow_html=True)
            if st.button("↺ 重制系统"): st.rerun()
