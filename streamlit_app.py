import streamlit as st
import pandas as pd
import re
import io
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Alignment, Border, Side

# --- 1. 配置信息 ---
COLOR_REG = r'(?i)Color[:：\s]*([a-zA-Z0-9\-_/]+)'
SIZE_REG = r'(?i)Size[:：\s]*([a-zA-Z0-9\-\s/]+?)(?=\s*(?:Color|Size|$|[,，;；]))'
SIZE_MAP = {'HIGH ANKLE SOCKS': 'L', 'KNEE-HIGH SOCKS': 'M'}
BLUE_FILL = PatternFill(start_color='D9E1F2', end_color='D9E1F2', fill_type='solid')
THIN_BORDER = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))

# --- 2. 网页设置 ---
st.set_page_config(page_title="汇总工具", layout="centered")
st.title("📊 商品属性汇总工具")
st.info("请上传原始 Excel 文件，解析完成后点击下载按钮获取结果。")

uploaded_file = st.file_uploader("选择 Excel 文件", type=["xlsx"])

if uploaded_file:
    try:
        # 读取上传的文件
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        col_a, col_c, col_g, col_i = df.columns[0], df.columns[2], df.columns[6], df.columns[8]
        all_normal_data = []

        for index, row in df.iterrows():
            c_raw = str(row[col_c]).strip()
            if not c_raw or c_raw == 'nan': continue
            category_name = c_raw.split(' ')[0].upper()
            if category_name.startswith('WZ'): category_name = 'WZ'
            i_nums = re.findall(r'\d+', str(row[col_i]))
            i_qty = int(i_nums[0]) if i_nums else 0
            
            g_text = str(row[col_g])
            chunks = re.split(r'[;；,，\n]', g_text)
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
                for cv, sv in data_pairs:
                    all_normal_data.append({'Category': category_name, 'Color': cv, 'Size': sv})

        if all_normal_data:
            # 数据统计逻辑
            final_df = pd.DataFrame(all_normal_data)
            categories = sorted(final_df['Category'].unique())
            size_order = ['XXS', 'XS', 'S', 'M', 'L', 'XL', '2XL', '3XL', '4XL', 'FREE', '']
            
            # 在内存中生成 Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                output_rows, category_blocks = [], []
                for cat in categories:
                    start_row = len(output_rows) + 1
                    cat_data = final_df[final_df['Category'] == cat]
                    distinct_sizes = sorted(cat_data['Size'].unique(), key=lambda x: size_order.index(x) if x in size_order else 99)
                    output_rows.append({'A': cat})
                    colors = sorted(cat_data['Color'].unique(), key=lambda x: int(re.findall(r'\d+', str(x))[0]) if re.findall(r'\d+', str(x)) else 999)
                    for color in colors:
                        c_data = cat_data[cat_data['Color'] == color]
                        counts = c_data['Size'].value_counts()
                        row_dict = {'A': f"Color {color}"}
                        for idx, s_name in enumerate(distinct_sizes):
                            col_key = chr(66 + idx) if idx < 25 else f"Z{idx}"
                            if s_name in counts:
                                row_dict[col_key] = f"*{counts[s_name]}" if s_name == "" else f"{s_name}*{counts[s_name]}"
                        output_rows.append(row_dict)
                    category_blocks.append((start_row, len(output_rows), 1 + len(distinct_sizes)))
                    output_rows.append({})
                
                pd.DataFrame(output_rows).to_excel(writer, index=False, header=False, sheet_name='Sheet1')
                
                # 美化
                ws = writer.sheets['Sheet1']
                for start, end, col_limit in category_blocks:
                    ws.cell(row=start, column=1).alignment = Alignment(horizontal='center')
                    for r in range(start + 1, end + 1):
                        for c in range(1, col_limit + 1):
                            cell = ws.cell(row=r, column=c)
                            cell.fill, cell.border, cell.alignment = BLUE_FILL, THIN_BORDER, Alignment(horizontal='center')
                for col in ws.columns: ws.column_dimensions[col[0].column_letter].width = 15

            st.success("✅ 处理完毕！")
            st.download_button(
                label="📥 点击下载汇总表",
                data=output.getvalue(),
                file_name=f"汇总_{uploaded_file.name}",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.error("❌ 未能识别到有效数据，请检查 G 列内容格式。")
    except Exception as e:
        st.error(f"❌ 程序运行出错: {e}")
