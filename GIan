import pandas as pd
import re
import os
import sys
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Alignment, Border, Side

# --- 配置信息 ---
COLOR_REG = r'(?i)Color[:：\s]*([a-zA-Z0-9\-_/]+)'
SIZE_REG = r'(?i)Size[:：\s]*([a-zA-Z0-9\-\s/]+?)(?=\s*(?:Color|Size|$|[,;，；]))'
SIZE_MAP = {'HIGH ANKLE SOCKS': 'L', 'KNEE-HIGH SOCKS': 'M'}
BLUE_FILL = PatternFill(start_color='D9E1F2', end_color='D9E1F2', fill_type='solid')
THIN_BORDER = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))

def process_file(file_path):
    if not os.path.exists(file_path):
        print(f"错误: 找不到文件 {file_path}")
        return

    base_dir = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)
    name_part = os.path.splitext(file_name)[0]
    save_path = os.path.join(base_dir, f"汇总_{name_part}.xlsx")
    error_log_path = os.path.join(base_dir, f"异常_{name_part}.xlsx")

    try:
        print(f"正在处理: {file_name} ...")
        df = pd.read_excel(file_path, engine='openpyxl')
        
        if len(df.columns) < 9:
            print("错误:傻逼选错表了！")
            return

        col_a, col_c, col_g, col_i = df.columns[0], df.columns[2], df.columns[6], df.columns[8]
        all_normal_data, all_error_rows = [], []

        for index, row in df.iterrows():
            c_raw = str(row[col_c]).strip()
            if not c_raw or c_raw == 'nan': continue
            
            if ';' in c_raw or '；' in c_raw:
                all_error_rows.append({'商品名称': c_raw, '订单编号': row[col_a], '原因': "多个商品", 'SKU属性': str(row[col_g])})
                continue

            category_name = c_raw.split(' ')[0].upper()
            if category_name.startswith('WZ'): category_name = 'WZ'

            g_text = str(row[col_g])
            i_val = str(row[col_i])
            i_nums = re.findall(r'\d+', i_val)
            i_qty = int(i_nums[0]) if i_nums else 0

            # --- 【核心改动：分号块切割提取法】 ---
            # 逻辑：先按分号切开，解决多组数据问题。如果没有分号，chunks 也包含整行内容。
            chunks = re.split(r'[;；]', g_text)
            data_pairs = []

            for chunk in chunks:
                chunk = chunk.strip()
                if not chunk: continue
                
                # 在每个分号块内部独立搜寻 Color 和 Size，无视先后顺序
                c_match = re.search(COLOR_REG, chunk)
                s_match = re.search(SIZE_REG, chunk)
                
                if c_match:
                    color_val = c_match.group(1).strip().upper()
                    # 【改动】如果没有 Size 关键字，设为空字符串 ""，输出时会自动变 *数量
                    raw_size = s_match.group(1).strip().upper() if s_match else ""
                    size_val = SIZE_MAP.get(raw_size, raw_size) 
                    data_pairs.append((color_val, size_val))
            # --- 【改动结束】 ---

            if len(data_pairs) == i_qty and i_qty > 0:
                for c_val, s_val in data_pairs:
                    all_normal_data.append({'Category': category_name, 'Color': c_val, 'Size': s_val})
            else:
                all_error_rows.append({'商品名称': category_name, '订单编号': row[col_a], '原因': f"解析数({len(data_pairs)})与购买数量({i_qty})不符", 'SKU属性': g_text})

        if all_error_rows:
            pd.DataFrame(all_error_rows).to_excel(error_log_path, index=False)
            print(f"已记录异常数据至: {os.path.basename(error_log_path)}")

        if all_normal_data:
            final_df = pd.DataFrame(all_normal_data)
            categories = sorted(final_df['Category'].unique())
            
            # 【检查】确保排序逻辑包含空字符串 ""
            size_order = ['XXS', 'XS', 'S', 'M', 'L', 'XL', '2XL', '3XL', '4XL', 'FREE', '']
            def sort_sizes(s_list):
                return sorted(s_list, key=lambda x: size_order.index(x) if x in size_order else 99)
            def extract_num(s):
                nums = re.findall(r'\d+', str(s))
                return int(nums[0]) if nums else 999999

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
                            # 【改动】空尺码直接显示 *数量，不再显示 N/A*数量
                            row_dict[col_key] = f"*{qty}" if s_name == "" else f"{s_name}*{qty}"
                    output_rows.append(row_dict)
                
                category_blocks.append((start_row, len(output_rows), 1 + len(distinct_sizes)))
                output_rows.append({}) 

            pd.DataFrame(output_rows).to_excel(save_path, index=False, header=False)
            
            wb = load_workbook(save_path)
            ws = wb.active
            for start, end, col_limit in category_blocks:
                ws.cell(row=start, column=1).alignment = Alignment(horizontal='center')
                for r in range(start + 1, end + 1):
                    for c in range(1, col_limit + 1):
                        cell = ws.cell(row=r, column=c)
                        cell.fill, cell.border, cell.alignment = BLUE_FILL, THIN_BORDER, Alignment(horizontal='center')
            
            for col in ws.columns: ws.column_dimensions[col[0].column_letter].width = 15
            wb.save(save_path)
            print(f"成功! 结果已保存至: {os.path.basename(save_path)}")
        else:
            print("提示: 未发现有效数据，未生成汇总表。")

    except Exception as e:
        print(f"运行出错: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for path in sys.argv[1:]:
            process_file(path)
        print("\n所有任务处理完毕。")
    else:
        print("="*40)
        print("使用说明: 直接将 Excel 文件拖动到此脚本图标上运行")
        print("="*40)
        input("\n按回车键退出...")
