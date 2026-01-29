def classify_excel(df):
    COLOR_REG = r'(?i)Color[:：\s]*([a-zA-Z0-9\-_/]+)'
    SIZE_REG  = r'(?i)Size[:：\s]*([a-zA-Z0-9\-\s/]+)'
    SIZE_MAP  = {'HIGH ANKLE SOCKS': 'L', 'KNEE-HIGH SOCKS': 'M'}

    normal_data = []
    error_data = []

    # 自动列识别（避免硬编码）
    def find_col(keys):
        for col in df.columns:
            col_str = str(col)
            for k in keys:
                if k in col_str:
                    return col
        return None

    col_sn   = find_col(["SN", "编号", "订单"])
    col_name = find_col(["品", "名称", "商品"])
    col_attr = find_col(["属", "属性", "规格"])
    col_qty  = find_col(["数", "数量", "QTY"])

    if not all([col_sn, col_name, col_attr, col_qty]):
        return pd.DataFrame(), pd.DataFrame([{
            "Category":"SYSTEM",
            "SN":"-",
            "Reason":"Excel列名无法识别",
        }])

    for _, row in df.iterrows():
        name_raw = str(row[col_name]).strip()
        sn = str(row[col_sn]).strip()
        attr_text = str(row[col_attr])
        qty_text = str(row[col_qty])

        if not name_raw or name_raw == "nan":
            continue

        # 1️⃣ 复合商品检测
        if re.search(r'[;；]', name_raw):
            error_data.append({
                "Category":"MULTI",
                "SN":sn,
                "Reason":"多个商品",
                "Raw":attr_text
            })
            continue

        # 2️⃣ 分类名
        category = name_raw.split()[0].upper()
        if category.startswith("WZ"):
            category = "WZ"

        # 3️⃣ 数量解析
        qty_match = re.findall(r'\d+', qty_text)
        qty = int(qty_match[0]) if qty_match else 0

        # 4️⃣ 核心逻辑：分号块解析（保留你的算法🔥）
        chunks = re.split(r'[;；]', attr_text)
        pairs = []

        for chunk in chunks:
            chunk = chunk.strip()
            if not chunk:
                continue

            c_match = re.search(COLOR_REG, chunk)
            s_match = re.search(SIZE_REG, chunk)

            if c_match:
                color = c_match.group(1).strip().upper()
                size = s_match.group(1).strip().upper() if s_match else ""
                size = SIZE_MAP.get(size, size)
                pairs.append((color, size))

        # 5️⃣ 数量校验
        if qty > 0 and len(pairs) == qty:
            for c, s in pairs:
                normal_data.append({
                    "Category": category,
                    "Color": c,
                    "Size": s
                })
        else:
            error_data.append({
                "Category": category,
                "SN": sn,
                "Reason": f"数量不匹配({len(pairs)}/{qty})",
                "Raw": attr_text
            })

    return pd.DataFrame(normal_data), pd.DataFrame(error_data)
