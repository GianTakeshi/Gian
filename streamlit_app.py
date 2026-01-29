import streamlit as st
import pandas as pd
import re
import io
import time
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Alignment, Border, Side

# --- 1. 页面配置与玻璃拟态 UI ---
st.set_page_config(page_title="SKU汇总工具", page_icon="🚀", layout="centered")

GITHUB_USERNAME = "GianTakeshi" 

st.markdown(f"""
    <style>
    .stApp {{ background: radial-gradient(circle at 50% 50%, #1e293b, #010409); color: #ffffff; }}
    header {{visibility: hidden;}}

    /* 玻璃拟态卡片 */
    .glass-card {{
        border-radius: 20px; padding: 20px; text-align: center;
        backdrop-filter: blur(15px); animation: fadeIn 0.6s ease-out; margin-bottom: 20px;
        background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1);
    }}
    .success-card {{ border-left: 5px solid #10b981; }}
    .error-card {{ border-left: 5px solid #f59e0b; }}

    @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}

    /* 左上角头像面板 */
    .user-profile {{
        position: fixed; top: 25px; left: 25px; display: flex; align-items: center; gap: 12px; z-index: 9999;
        background: rgba(255, 255, 255, 0.05); padding: 6px 16px 6px 6px; border-radius: 50px;
        border: 1px solid rgba(56, 189, 248, 0.3); backdrop-filter: blur(10px);
    }}
    .avatar {{ width: 38px; height: 38px; border-radius: 50%; border: 2px solid #38bdf8; object-fit: cover; }}

    /* 上传框样式 */
    .stFileUploader section {{ 
        background: rgba(255, 255, 255, 0.03) !important; 
        backdrop-filter: blur(20px) !important; 
        border: 2px dashed rgba(56, 189, 248, 0.4) !important; 
        border-radius: 30px !important; 
    }}
    [data-testid="stFileUploadDropzone"] > div {{ color: transparent !important; }}
    [data-testid="stFileUploadDropzone"]::before {{ content: "拖拽文件到这里"; position: absolute; top: 40%; color: #ffffff; font-size: 1.4rem; font-weight: bold; }}
    [data-testid="stFileUploadDropzone"] button::after {{ content: "选择文件"; position: absolute; left: 0; width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; color: #000; font-weight: 800; visibility: visible; }}
    </style>
    
    <div class="user-profile">
        <img src="https://avatars.githubusercontent.com/{GITHUB_USERNAME}" class="avatar">
        <div style="display: flex; flex-direction: column;">
            <span style="font-weight:700; font-size:0.9rem;">{GITHUB_USERNAME}</span>
            <span style="font-size:0.65rem; color:#10b981;">● 开发模式 v3.0</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 2. 完美复刻源代码的核心逻辑 ---
COLOR_REG = r'(?i)Color[:：\s]*([a-zA-Z0-9\-_/]+)'
SIZE_REG = r'(?i)Size[:：\s]*([a-zA-Z0-9\-\s/]+?)(?=\s*(?:Color|Size|$|[,;，；]))'
SIZE_MAP = {'HIGH ANKLE SOCKS': 'L', 'KNEE-HIGH SOCKS': 'M'}
BLUE_FILL = PatternFill(start_color='D9E1F2', end_color='D9E1F2', fill_type='solid')
THIN_BORDER = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))

def process_sku_logic(uploaded_file):
    df = pd.read_excel(uploaded_file, engine='openpyxl')
    if len(df.columns) < 9:
        return None, None, "错误: 表格格式不正确（列数不足）"

    col_a, col_c, col_g, col_i = df.columns[0], df.columns[2], df.columns[6], df.columns[8]
    all_normal_data, all_error_rows = [], []

    for index, row in df.iterrows():
        c_raw = str(row[col_c]).strip()
        if not c_raw or c_raw == 'nan': continue
        
        # 异常：多个商品
        if ';' in c_raw or '；' in c_raw:
            all_error_rows.append({'商品名称': c_raw, '订单编号': row[col_a], '原因': "多个商品", 'SKU属性': str(row[col_g])})
            continue

        category_name = c_raw.split(' ')[0].upper()
        if category_name.startswith('WZ'): category_name = 'WZ'

        g_text = str(row[col_g])
        i_val = str(row[col_i])
        i_qty = int(re.findall(r'\d+', i_val)[0]) if re.findall(r'\d+', i_val) else 0

        # 分号块切割提取
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
                size_val = SIZE_MAP.get(raw_size, raw_size) 
                data_pairs.append((color_val, size_val))

        if len(data_pairs) == i_qty and i_qty > 0:
            for c_val, s_val in data_pairs:
                all_normal_data.append({'Category': category_name, 'Color': c_val, 'Size': s_val})
        else:
            all_error_rows.append({
                '商品名称': category_name, 
                '订单编号': row[col_a], 
                '原因': f"解析数({len(data_pairs)})与购买数量({i_qty})不符", 
                'SKU属性': g_text
            })

    return pd.DataFrame(all_normal_data), pd.DataFrame(all_error_rows), None

# --- 3. 页面渲染逻辑 ---
st.markdown("<div style='text-align:center; padding-top:50px;'><h1 style='font-size:4.2rem; font-weight:800; background:linear-gradient(to bottom, #fff, #64748b); -webkit-background-clip:text; -webkit-text-fill-color:transparent;'>智能商品</h1><h1 style='color:#38bdf8; font-size:2.6rem; margin-top:-15px;'>属性汇总大师 🚀</h1></div>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("", type=["xlsx"])

if uploaded_file:
    with st.status("正在进行量子扫描并穿透玻璃面板...", expanded=True) as status:
        final_df, error_df, err_msg = process_sku_logic(uploaded_file)
        time.sleep(0.5)
        status.update(label="解析完成!", state="complete", expanded=False)

    if err_msg:
        st.error(err_msg)
    else:
        # --- 汇总表处理与美化导出 ---
        if not final_df.empty:
            st.markdown("<div class='glass-card success-card'><h3 style='color:#10b981; margin:0;'>✨ 汇总就绪</h3><p style='color:#a7f3d0;'>已成功重构 {} 条 SKU 属性</p></div>".format(len(final_df)), unsafe_allow_html=True)
            
            # 这里复刻你源码中的复杂排序和多列格式
            categories = sorted(final_df['Category'].unique())
            size_order = ['XXS', 'XS', 'S', 'M', 'L', 'XL', '2XL', '3XL', '4XL', 'FREE', '']
            def sort_sizes(s_list): return sorted(s_list, key=lambda x: size_order.index(x) if x in size_order else 99)
            def extract_num(s): 
                n = re.findall(r'\d+', str(s))
                return int(n[0]) if n else 999999

            output_rows, category_blocks = [], []
            for cat in categories:
                start_row = len(output_rows) + 1
                cat_data = final_df[final_df['Category'] == cat]
                distinct_sizes = sort_sizes(cat_data['Size'].unique())
                output_rows.append({'A': cat})
                sorted_colors = sorted(cat_data['Color'].unique(), key=extract_num)
                for color in sorted_colors:
                    color_data = cat_data[cat_data['Color'] == color]
                    size_counts = color_data['Size'].value_counts()
                    row_dict = {'A': f"Color {color}"}
                    for idx, s_name in enumerate(distinct_sizes):
                        col_key = chr(66 + idx) if idx < 25 else f"Z{idx}"
                        if s_name in size_counts:
                            qty = size_counts[s_name]
                            row_dict[col_key] = f"*{qty}" if s_name == "" else f"{s_name}*{qty}"
                    output_rows.append(row_dict)
                category_blocks.append((start_row, len(output_rows), 1 + len(distinct_sizes)))
                output_rows.append({})

            # 导出带格式的 Excel
            out_ok = io.BytesIO()
            pd.DataFrame(output_rows).to_excel(out_ok, index=False, header=False)
            wb = load_workbook(out_ok)
            ws = wb.active
            for start, end, col_limit in category_blocks:
                ws.cell(row=start, column=1).alignment = Alignment(horizontal='center')
                for r in range(start + 1, end + 1):
                    for c in range(1, col_limit + 1):
                        cell = ws.cell(row=r, column=c)
                        cell.fill, cell.border, cell.alignment = BLUE_FILL, THIN_BORDER, Alignment(horizontal='center')
            for col in ws.columns: ws.column_dimensions[col[0].column_letter].width = 15
            
            final_out = io.BytesIO()
            wb.save(final_out)
            st.download_button("📥 下载汇总报表 (完美格式版)", final_out.getvalue(), f"汇总_{uploaded_file.name}", use_container_width=True)

        # --- 异常表处理与导出 ---
        if not error_df.empty:
            st.markdown(f"<div class='glass-card error-card'><h3 style='color:#f59e0b; margin:0;'>⚠️ 异常拦截</h3><p style='color:#fcd34d;'>拦截到 {len(error_df)} 条无法解析的原始订单</p></div>", unsafe_allow_html=True)
            
            out_err = io.BytesIO()
            error_df.to_excel(out_err, index=False)
            st.download_button("🚩 下载异常明细 (核对用)", out_err.getvalue(), f"异常_{uploaded_file.name}", use_container_width=True)

st.markdown("<div style='text-align:center; margin-top:80px; color:rgba(148,163,184,0.4); font-size:0.8rem;'>GianTakeshi CUSTOM SYSTEM v3.0 | 2026</div>", unsafe_allow_html=True)
