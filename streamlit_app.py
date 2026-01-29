import streamlit as st
import pandas as pd
import re
import io
import time

# --- 1. 页面配置与 CSS ---
st.set_page_config(page_title="SKU汇总工具", page_icon="🚀", layout="centered")

GITHUB_USERNAME = "GianTakeshi" 

st.markdown(f"""
    <style>
    .stApp {{ background: radial-gradient(circle at 50% 50%, #1e293b, #010409); color: #ffffff; }}
    header {{visibility: hidden;}}

    /* 磨砂玻璃通用卡片 */
    .glass-card {{
        border-radius: 20px; padding: 20px; text-align: center;
        backdrop-filter: blur(10px); animation: fadeIn 0.6s ease-out; margin-bottom: 20px;
    }}
    .success-card {{ background: rgba(16, 185, 129, 0.1); border: 1px solid #10b981; }}
    .error-card {{ background: rgba(245, 158, 11, 0.15); border: 1px solid #f59e0b; }}

    @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}

    /* 左上角头像 */
    .user-profile {{
        position: fixed; top: 25px; left: 25px; display: flex; align-items: center; gap: 12px; z-index: 9999;
        background: rgba(255, 255, 255, 0.05); padding: 6px 16px 6px 6px; border-radius: 50px;
        border: 1px solid rgba(255, 255, 255, 0.1); backdrop-filter: blur(15px);
    }}
    .avatar {{ width: 38px; height: 38px; border-radius: 50%; border: 2px solid #38bdf8; object-fit: cover; }}

    /* 上传框汉化覆盖 */
    [data-testid="stFileUploadDropzone"] > div {{ color: transparent !important; }}
    [data-testid="stFileUploadDropzone"]::before {{ content: "拖拽文件到这里"; position: absolute; top: 40%; color: #ffffff; font-size: 1.4rem; font-weight: bold; }}
    [data-testid="stFileUploadDropzone"] button::after {{ content: "选择文件"; position: absolute; left: 0; width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; color: #000; font-weight: 800; visibility: visible; }}
    .stFileUploader section {{ background: rgba(255, 255, 255, 0.03) !important; backdrop-filter: blur(20px) !important; border: 1px solid rgba(56, 189, 248, 0.3) !important; border-radius: 30px !important; min-height: 250px; }}
    </style>
    
    <div class="user-profile">
        <img src="https://avatars.githubusercontent.com/{GITHUB_USERNAME}" class="avatar">
        <div style="display: flex; flex-direction: column;">
            <span style="font-weight:700; font-size:0.9rem;">{GITHUB_USERNAME}</span>
            <span style="font-size:0.65rem; color:#10b981;">● 核心模式</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 2. 增强的数据处理函数 ---
def process_sku_data(uploaded_file):
    COLOR_REG = r'(?i)Color[:：\s]*([a-zA-Z0-9\-_/]+)'
    SIZE_REG = r'(?i)Size[:：\s]*([a-zA-Z0-9\-\s/]+?)(?=\s*(?:Color|Size|$|[,，;；]))'
    SIZE_MAP = {'HIGH ANKLE SOCKS': 'L', 'KNEE-HIGH SOCKS': 'M'}
    
    df = pd.read_excel(uploaded_file, engine='openpyxl')
    all_normal_data = []
    error_logs = []
    
    for index, row in df.iterrows():
        try:
            c_raw = str(row[df.columns[2]]).strip()
            if not c_raw or c_raw == 'nan': continue
            
            cat = c_raw.split(' ')[0].upper()
            if cat.startswith('WZ'): cat = 'WZ'
            
            qty_match = re.findall(r'\d+', str(row[df.columns[8]]))
            qty = int(qty_match[0]) if qty_match else 0
            
            prop_str = str(row[df.columns[6]])
            chunks = re.split(r'[;；,，\n]', prop_str)
            pairs = []
            for chunk in chunks:
                c_m = re.search(COLOR_REG, chunk)
                s_m = re.search(SIZE_REG, chunk)
                if c_m:
                    cv = c_m.group(1).strip().upper()
                    sv = s_m.group(1).strip().upper() if s_m else ""
                    pairs.append((cv, SIZE_MAP.get(sv, sv)))
            
            # 校验：解析出的属性数量必须等于订单数量
            if len(pairs) == qty and qty > 0:
                for cv, sv in pairs:
                    all_normal_data.append({'Category': cat, 'Color': cv, 'Size': sv})
            else:
                error_logs.append({
                    '行号': index + 2,
                    '品名': c_raw,
                    '原始属性': prop_str,
                    '订单数量': qty,
                    '解析数量': len(pairs),
                    '原因': '数量不匹配或属性格式错误'
                })
        except Exception as e:
            error_logs.append({'行号': index + 2, '原因': str(e)})

    return pd.DataFrame(all_normal_data), pd.DataFrame(error_logs)

# --- 3. 页面布局 ---
st.markdown("<div style='text-align:center; padding-top:50px;'><h1 style='font-size:4rem; font-weight:800;'>智能商品</h1><h1 style='color:#38bdf8; font-size:2.5rem; margin-top:-15px;'>属性汇总大师 🚀</h1></div>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("", type=["xlsx"])

if uploaded_file:
    progress = st.progress(0)
    for i in range(100):
        time.sleep(0.005)
        progress.progress(i + 1)
    
    final_df, error_df = process_sku_data(uploaded_file)
    progress.empty()

    # 1. 处理成功展示
    if not final_df.empty:
        st.markdown("<div class='glass-card success-card'><h3 style='color:#10b981; margin:0;'>✨ 解析成功</h3><p style='color:#a7f3d0; margin-top:5px;'>已成功提取 {} 条 SKU 属性</p></div>".format(len(final_df)), unsafe_allow_html=True)
        
        out_ok = io.BytesIO()
        with pd.ExcelWriter(out_ok, engine='openpyxl') as writer:
            final_df.to_excel(writer, index=False, sheet_name='汇总')
        
        st.download_button("📥 下载汇总报表 (XLSX)", out_ok.getvalue(), f"汇总_{uploaded_file.name}", use_container_width=True)

    # 2. 处理错误展示
    if not error_df.empty:
        st.markdown(f"<div class='glass-card error-card'><h3 style='color:#f59e0b; margin:0;'>⚠️ 异常提醒</h3><p style='color:#fcd34d; margin-top:5px;'>发现 {len(error_df)} 行数据无法自动解析，请人工核对</p></div>", unsafe_allow_html=True)
        
        out_err = io.BytesIO()
        with pd.ExcelWriter(out_err, engine='openpyxl') as writer:
            error_df.to_excel(writer, index=False, sheet_name='错误记录')
        
        st.download_button("🚩 下载错误记录以便核对", out_err.getvalue(), f"错误检查_{uploaded_file.name}", use_container_width=True)

st.markdown("<div style='text-align:center; margin-top:80px; color:rgba(148,163,184,0.4); font-size:0.8rem;'>GianTakeshi CUSTOM SYSTEM v2.0</div>", unsafe_allow_html=True)
