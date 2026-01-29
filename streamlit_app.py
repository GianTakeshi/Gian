import streamlit as st
import pandas as pd
import re
import html

# =============================
# ⚙️ CONFIG
# =============================
st.set_page_config("Matrix Hub Pro", "💎", layout="wide")

st.markdown("""
<style>
.stApp {background:#020617;color:white;}
header{visibility:hidden;}

.metric-box{
    background:rgba(255,255,255,0.03);
    border:1px solid rgba(56,189,248,0.2);
    border-radius:14px;
    padding:14px;
    text-align:center;
    backdrop-filter:blur(10px);
}
.metric-title{font-size:12px;color:#94a3b8;}
.metric-value{font-size:26px;font-weight:900;color:#38bdf8;}

.matrix-card{
    background:rgba(255,255,255,0.02);
    border:1px solid rgba(255,255,255,0.08);
    border-radius:12px;
    padding:10px;
    height:360px;
    overflow:auto;
}
.cat-title{
    background:rgba(56,189,248,0.15);
    padding:6px;
    border-radius:8px;
    text-align:center;
    font-weight:900;
    color:#38bdf8;
    margin-bottom:8px;
}
.badge{
    padding:2px 6px;
    border-radius:6px;
    font-size:11px;
    background:rgba(56,189,248,0.15);
    margin-right:4px;
}
.err-card{
    background:rgba(239,68,68,0.05);
    border:1px solid rgba(239,68,68,0.2);
    border-radius:8px;
    padding:6px;
    font-size:11px;
    margin-bottom:6px;
}
</style>
""", unsafe_allow_html=True)

# =============================
# 🧠 COLUMN MATCH ENGINE
# =============================
def find_col(df, keywords):
    for col in df.columns:
        col_str = str(col).upper()
        for k in keywords:
            if k.upper() in col_str:
                return col
    return None

# =============================
# 🧠 PARSER ENGINE
# =============================
@st.cache_data(show_spinner=False)
def parse_excel(file):
    COLOR_REG = r'(?i)(?:color|颜色)[:：\s]*([a-zA-Z0-9\-_/]+)'
    SIZE_REG = r'(?i)(?:size|尺码)[:：\s]*([a-zA-Z0-9\-\s/]+)'
    
    df = pd.read_excel(file, engine="openpyxl")

    sn_col   = find_col(df, ["SN", "编号", "商品编号", "SKU", "货号"])
    name_col = find_col(df, ["品", "NAME", "商品", "名称", "标题"])
    attr_col = find_col(df, ["属", "ATTR", "属性", "规格", "参数"])
    qty_col  = find_col(df, ["数", "QTY", "数量", "件数"])

    # 🚨 防崩溃：列不存在
    missing = []
    if sn_col is None: missing.append("SN")
    if name_col is None: missing.append("NAME")
    if attr_col is None: missing.append("ATTR")
    if qty_col is None: missing.append("QTY")

    if missing:
        st.error(f"❌ Excel 缺少关键列: {missing}")
        st.write("📋 当前 Excel 列名：", list(df.columns))
        return pd.DataFrame(), pd.DataFrame()

    valid, error = [], []

    for _, row in df.iterrows():
        try:
            sn = str(row[sn_col]).strip()
            name = str(row[name_col]).strip()
            attr = str(row[attr_col]).strip()
            qty_raw = str(row[qty_col]).strip()

            if not name or name == "nan":
                error.append({"Category":"EMPTY","SN":sn,"Reason":"EMPTY_ROW"})
                continue

            cat = name.split()[0].upper()
            if cat.startswith("WZ"): cat="WZ"

            if re.search(r'[;；]', name):
                error.append({"Category":cat,"SN":sn,"Reason":"MULTI_ITEM"})
                continue

            qty_match = re.findall(r'\d+', qty_raw)
            qty = int(qty_match[0]) if qty_match else 0

            parsed=[]
            for chunk in re.split(r'[;；]', attr):
                c = re.search(COLOR_REG, chunk)
                s = re.search(SIZE_REG, chunk)
                if c:
                    clr = c.group(1).upper()
                    size = s.group(1).upper() if s else "FREE"
                    parsed.append({"Category":cat,"Color":clr,"Size":size})

            if not parsed:
                error.append({"Category":cat,"SN":sn,"Reason":"ATTR_PARSE_FAIL"})
            elif len(parsed)!=qty:
                error.append({"Category":cat,"SN":sn,"Reason":f"QTY_MISMATCH({len(parsed)}/{qty})"})
            else:
                valid.extend(parsed)

        except Exception as e:
            error.append({"Category":"ERROR","SN":sn,"Reason":str(e)})

    return pd.DataFrame(valid), pd.DataFrame(error)

# =============================
# 📊 METRICS
# =============================
def calc_metrics(v_df, e_df):
    total = len(v_df)
    cats = v_df["Category"].nunique() if not v_df.empty else 0
    colors = v_df["Color"].nunique() if not v_df.empty else 0
    err_rate = round(len(e_df) / (len(v_df)+len(e_df)+1) * 100, 1)
    top_cat = v_df["Category"].value_counts().idxmax() if not v_df.empty else "-"
    return total, cats, colors, err_rate, top_cat

# =============================
# 🧩 MATRIX UI
# =============================
def render_matrix(df, error=False):
    if df.empty:
        st.info("No Data")
        return

    groups = df.groupby("Category")
    cats = list(groups.keys())
    cols_per_row = 5

    for i in range(0,len(cats),cols_per_row):
        row = cats[i:i+cols_per_row]
        cols = st.columns(cols_per_row)

        for j,cat in enumerate(row):
            g = groups.get_group(cat)

            with cols[j]:
                st.markdown("<div class='matrix-card'>", unsafe_allow_html=True)
                st.markdown(f"<div class='cat-title'>{cat}</div>", unsafe_allow_html=True)

                if error:
                    for _,r in g.iterrows():
                        st.markdown(f"""
                        <div class='err-card'>
                            <b>SN:</b> {r['SN']}<br>
                            <span style='color:#94a3b8'>{r['Reason']}</span>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    for clr, cg in g.groupby("Color"):
                        stats = cg["Size"].value_counts()
                        badges = "".join([f"<span class='badge'>{s}×{q}</span>" for s,q in stats.items()])
                        st.markdown(f"""
                        <div style="margin-bottom:6px;font-size:12px;">
                            <span style="color:#38bdf8;font-weight:700;">{html.escape(clr)}</span>
                            <div>{badges}</div>
                        </div>
                        """, unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)

# =============================
# 🚀 MAIN
# =============================
st.markdown("<h2 style='text-align:center;margin-top:40px;'>💎 Matrix Hub Pro</h2>", unsafe_allow_html=True)

file = st.file_uploader("Upload Excel", type=["xlsx"])

if file:
    v_df, e_df = parse_excel(file)

    total, cats, colors, err_rate, top_cat = calc_metrics(v_df, e_df)

    c1,c2,c3,c4,c5 = st.columns(5)
    metrics = [
        ("Total SKU", total),
        ("Categories", cats),
        ("Colors", colors),
        ("Error Rate", f"{err_rate}%"),
        ("Top Category", top_cat)
    ]

    for col,(t,v) in zip([c1,c2,c3,c4,c5], metrics):
        col.markdown(f"""
        <div class="metric-box">
            <div class="metric-title">{t}</div>
            <div class="metric-value">{v}</div>
        </div>
        """, unsafe_allow_html=True)

    t1,t2 = st.tabs(["✅ Normal Matrix","❌ Error Matrix"])
    with t1: render_matrix(v_df, False)
    with t2: render_matrix(e_df, True)
