import streamlit as st
import pandas as pd
import re

# --- 1. 页面配置 (浏览器标签页标题与图标) ---
st.set_page_config(page_title="爆单", page_icon="🚀", layout="wide")

# 配置常量：你的 GitHub 信息与订单详情跳转的基础 URL
GITHUB_USERNAME = "GianTakeshi" 
BASE_URL = "https://inflyway.com/kamelnet/#/kn/fly-link/orders/detail?id="
AVATAR_URL = f"https://avatars.githubusercontent.com/{GITHUB_USERNAME}"

# --- 2. 注入深度定制 CSS (决定整个页面的皮肤) ---
st.markdown(f"""
    <style>
    /* 🎭 整体背景：使用径向渐变，营造中心亮、四周暗的深邃感 */
    .stApp {{ 
        background: radial-gradient(circle at 50% 50%, #0c1e3d 0%, #020617 60%, #000000 100%) !important; 
        color: #ffffff; 
        padding-top: 80px !important; 
    }}
    header {{visibility: hidden;}} /* 隐藏 Streamlit 默认的页眉 */

    /* ✨ 动画：上传框的边框呼吸发光效果 */
    @keyframes uploader-glow {{
        0% {{ border-color: rgba(56, 189, 248, 0.2); box-shadow: 0 0 10px rgba(56, 189, 248, 0.1); }}
        50% {{ border-color: rgba(56, 189, 248, 0.6); box-shadow: 0 0 25px rgba(56, 189, 248, 0.3); }}
        100% {{ border-color: rgba(56, 189, 248, 0.2); box-shadow: 0 0 10px rgba(56, 189, 248, 0.1); }}
    }}

    /* ✨ 动画：头像微调呼吸与放大效果 */
    @keyframes avatar-breathing {{
        0% {{ box-shadow: 0 0 0 0 rgba(56, 189, 248, 0.4); transform: scale(1); }}
        50% {{ box-shadow: 0 0 20px 4px rgba(56, 189, 248, 0.7); transform: scale(1.05); }}
        100% {{ box-shadow: 0 0 0 0 rgba(56, 189, 248, 0.4); transform: scale(1); }}
    }}

    /* 🛡️ 左上角用户面板样式 */
    .user-profile {{
        position: fixed; top: 35px; left: 35px; display: flex; align-items: center; gap: 12px; z-index: 1000000; 
        background: rgba(255, 255, 255, 0.05); padding: 8px 20px 8px 8px; border-radius: 60px;
        border: 1.5px solid rgba(56, 189, 248, 0.2); backdrop-filter: blur(15px); /* 毛玻璃效果 */
    }}
    .avatar {{ width: 38px; height: 38px; border-radius: 50%; border: 2px solid #38bdf8; animation: avatar-breathing 3s infinite ease-in-out; }}
    .user-name {{ font-size: 0.95rem; font-weight: 600; color: #fff; letter-spacing: 0.5px; }}

    /* 🧊 数据卡片：包裹每个 Category 的大容器 */
    .wide-card {{
        background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px; padding: 25px 30px; margin-bottom: 25px;
        display: flex; flex-direction: row; align-items: center; justify-content: space-between;
        backdrop-filter: blur(15px); transition: all 0.5s cubic-bezier(0.165, 0.84, 0.44, 1);
    }}
    .normal-card {{ border-left: 5px solid rgba(56, 189, 248, 0.4); }} /* 正常卡片的蓝色侧边 */
    .normal-card:hover {{ transform: translateY(-8px); border-color: #38bdf8; box-shadow: 0 15px 35px rgba(0,0,0,0.5), inset 0 0 80px rgba(56, 189, 248, 0.25); }}
    .error-card {{ border-left: 5px solid rgba(245, 158, 11, 0.4); }} /* 异常卡片的橙色侧边 */
    .error-card:hover {{ transform: translateY(-8px); border-color: #f59e0b; box-shadow: 0 15px 35px rgba(0,0,0,0.5), inset 0 0 80px rgba(245, 158, 11, 0.25); }}

    /* 🏷️ SN 标签：右侧点击跳转的小胶囊 */
    .sn-pill {{ padding: 6px 14px; border-radius: 40px; font-size: 0.8rem; font-weight: 800; text-decoration: none !important; transition: all 0.3s ease; border: 1px solid transparent; }}
    .normal-sn {{ background: rgba(56, 189, 248, 0.08); color: #38bdf8 !important; border: 1px solid rgba(56, 189, 248, 0.3); }}
    .normal-sn:hover {{ background: #38bdf8 !important; color: #000000 !important; box-shadow: 0 0 20px rgba(56, 189, 248, 0.6); transform: scale(1.05); }}
    .error-sn-pill {{ background: rgba(245, 158, 11, 0.08); color: #f59e0b !important; border: 1px solid rgba(245, 158, 11, 0.3); }}
    .error-sn-pill:hover {{ background: #f59e0b !important; color: #000000 !important; box-shadow: 0 0 20px rgba(245, 158, 11, 0.6); transform: scale(1.05); }}

    /* 🚫 Tabs 切换：移除原有的粗横线，改为发光胶囊设计 */
    .stTabs {{ overflow: visible !important; }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 20px; background: transparent !important; padding: 30px 10px !important; margin-bottom: 10px; overflow: visible !important; }}
    .stTabs [data-baseweb="tab"] {{ height: 42px !important; padding: 0 30px !important; font-size: 1rem !important; border-radius: 40px !important; border: 1.5px solid rgba(255, 255, 255, 0.1) !important; background: rgba(255, 255, 255, 0.02) !important; color: rgba(255, 255, 255, 0.5) !important; transition: all 0.4s ease !important; position: relative; z-index: 10; }}
    .stTabs [data-baseweb="tab"][aria-selected="true"]:nth-child(1) {{ color: #38bdf8 !important; border-color: #38bdf8 !important; background: rgba(56, 189, 248, 0.15) !important; box-shadow: 0 0 35px 8px rgba(56, 189, 248, 0.5) !important; }}
    .stTabs [data-baseweb="tab"][aria-selected="true"]:nth-child(2) {{ color: #f59e0b !important; border-color: #f59e0b !important; background: rgba(245, 158, 11, 0.15) !important; box-shadow: 0 0 35px 8px rgba(245, 158, 11, 0.5) !important; }}
    .stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {{ display: none !important; }}

    /* 🔄 重制系统按钮：位于底部的霓虹操作按钮 */
    div.stButton > button {{ 
        background: rgba(56, 189, 248, 0.08) !important; color: #38bdf8 !important; 
        border: 1.5px solid rgba(56, 189, 248, 0.4) !important; border-radius: 40px !important; 
        padding: 10px 45px !important; font-weight: 800 !important; font-size: 1rem !important; 
        transition: all 0.4s ease !important; margin: 50px auto !important; display: block !important; 
    }}
    div.stButton > button:hover {{ background: #38bdf8 !important; color: #000000 !important; box-shadow: 0 0 30px 5px rgba(56, 189, 248, 0.5) !important; transform: scale(1.05); }}

    /* 📥 上传文件界面：悬浮在屏幕底部的控制台 */
    [data-testid="stFileUploader"] {{
        position: fixed; bottom: 100px; left: 50%; transform: translateX(-50%); 
        width: 520px; z-index: 9999;
        background: rgba(12, 30, 61, 0.65) !important; 
        border-radius: 24px !important; 
        padding: 20px !important; 
        backdrop-filter: blur(30px) !important;
        border: 1.5px solid rgba(56, 189, 248, 0.3) !important;
        animation: uploader-glow 4s infinite ease-in-out;
        box-shadow: 0 15px 45px rgba(0,0,0,0.7);
    }}
    [data-testid="stFileUploader"] button {{ font-weight: 800 !important; border-radius: 12px !important; }}

    /* 🌟 大标题样式 */
    .grand-title {{ display: inline-block; font-size: 3.5rem !important; font-weight: 900; letter-spacing: 8px; background: linear-gradient(to bottom, #ffffff 40%, #38bdf8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    </style>

    <div class="user-profile">
        <img src="{AVATAR_URL}" class="avatar">
        <div class="user-name">{GITHUB_USERNAME}</div>
    </div>
    <div style="text-align:center; margin-bottom:100px;"><h1 class="grand-title">祝王哥天天爆单</h1></div>
""", unsafe_allow_html=True)

# --- 3. 核心提取逻辑 (处理 SKU 文本的核心引擎) ---
def process_sku_logic(uploaded_file):
    # 正则表达式：提取 Color 和 Size
    COLOR_REG, SIZE_REG = r'(?i)Color[:：\s]*([a-zA-Z0-9\-_/]+)', r'(?i)Size[:：\s]*([a-zA-Z0-9\-\s/]+?)(?=\s*(?:Color|Size|$|[,;，；]))'
    # 尺码转换映射：将 Excel 里的冗长名字转为简称
    SIZE_MAP = {'HIGH ANKLE SOCKS': 'L', 'KNEE-HIGH SOCKS': 'M'}
    
    df = pd.read_excel(uploaded_file, engine='openpyxl')
    cols = df.columns
    all_normal_data, all_error_rows = [], []
    
    for index, row in df.iterrows():
        # 获取分类名并规范化处理 (如 WZ01 -> WZ)
        c_raw = str(row[cols[2]]).strip()
        if not c_raw or c_raw == 'nan': continue
        cat = c_raw.split(' ')[0].upper()
        if cat.startswith('WZ'): cat = 'WZ'
        
        # 获取 SKU 文本内容、计划数量、SN号
        g_text, i_val, sn = str(row[cols[6]]), str(row[cols[8]]), str(row[cols[0]])
        i_qty = int(re.findall(r'\d+', i_val)[0]) if re.findall(r'\d+', i_val) else 0
        
        # 异常拦截 1：如果分类里有分号，说明一行有多个不同商品，标记异常
        if ';' in c_raw or '；' in c_raw:
            all_error_rows.append({'SN': sn, 'Line': index+2, 'Reason': "多个商品", 'Content': g_text})
            continue
            
        # 拆分 SKU 块并进行正则匹配
        chunks = [c.strip() for c in re.split(r'[;；]', g_text) if c.strip()]
        data_pairs = []
        for chunk in chunks:
            c_m, s_m = re.search(COLOR_REG, chunk), re.search(SIZE_REG, chunk)
            if c_m: 
                clr = c_m.group(1).strip().upper()
                raw_s = s_m.group(1).strip().upper() if s_m else "FREE" # 没写 Size 默认为 FREE
                data_pairs.append((clr, SIZE_MAP.get(raw_s, raw_s)))
        
        # 异常拦截 2：匹配到的 SKU 数量与计划数量不符
        if len(data_pairs) == i_qty and i_qty > 0:
            for c_val, s_val in data_pairs: 
                all_normal_data.append({'Category': cat, 'Color': c_val, 'Size': s_val, 'SN': sn})
        else:
            all_error_rows.append({'SN': sn, 'Line': index+2, 'Reason': f"数量异常({len(data_pairs)}/{i_qty})", 'Content': g_text})
            
    return pd.DataFrame(all_normal_data), pd.DataFrame(all_error_rows)

# --- 4. UI 渲染 (将处理后的数据画到网页上) ---
upload_zone = st.empty() # 创建占位符，上传后清空
uploaded_file = upload_zone.file_uploader("DROP FILE TO PARSE", type=["xlsx"])

if uploaded_file:
    v_df, e_df = process_sku_logic(uploaded_file)
    upload_zone.empty() # 上传成功后，隐藏上传框，腾出空间显示结果
    
    t1, t2 = st.tabs(["汇总数据", "异常拦截"])
    
    with t1:
        if not v_df.empty:
            # 按分类 Category 循环生成卡片
            for cat in sorted(v_df['Category'].unique()):
                cat_group = v_df[v_df['Category'] == cat]
                attr_html_list = []
                # 分类内部按颜色 Color 再次细分
                for clr in sorted(cat_group['Color'].unique()):
                    clr_group = cat_group[cat_group['Color'] == clr]
                    # 生成 Size 徽章：Size 字符与 ×数量 的 HTML 拼接
                    size_badges = [f'<div style="display:inline-flex; align-items:center; background:rgba(255,255,255,0.05); border:1.5px solid rgba(255,255,255,0.12); border-radius:8px; padding:4px 12px; margin-right:8px;"><span style="color:#fff; font-size:0.9rem; font-weight:800;">{(s if s!="FREE" else "")}</span><span style="color:#38bdf8; font-weight:800; font-size:0.9rem; margin-left:5px;">{("×" if s!="FREE" else "")}{q}</span></div>' for s, q in clr_group['Size'].value_counts().sort_index().items()]
                    # 生成每一行颜色对应的 HTML 块
                    attr_html_list.append(f'<div style="display:flex; align-items:center; gap:20px; padding:10px 0;"><div style="color:#38bdf8; font-weight:700; min-width:100px; font-size:1.1rem;">{clr}</div><div>{"".join(size_badges)}</div></div>')
                
                # 生成右侧的 SN 跳转标签链接
                sn_html = "".join([f'<a href="{BASE_URL}{sn}" target="_blank" class="sn-pill normal-sn">{sn}</a>' for sn in sorted(list(set(cat_group['SN'].tolist())))])
                # 渲染完整的大卡片
                st.markdown(f'<div class="wide-card normal-card"><div style="flex:1;"><div style="color:#38bdf8; font-weight:900; font-size:1.8rem; margin-bottom:15px; letter-spacing:1px;">{cat}</div>{"".join(attr_html_list)}</div><div style="display:flex; flex-wrap:wrap; gap:8px; justify-content:flex-end; max-width:400px;">{sn_html}</div></div>', unsafe_allow_html=True)
            
            # 渲染重制按钮
            if st.button("↺ 重制系统"): st.rerun()

    with t2:
        # 如果存在异常行，渲染橙色的错误警告卡片
        if not e_df.empty:
            for _, err in e_df.iterrows():
                sn_link = f'<a href="{BASE_URL}{err["SN"]}" target="_blank" class="sn-pill error-sn-pill">{err["SN"]}</a>'
                st.markdown(f'<div class="wide-card error-card"><div style="flex:1;"><div style="color:#f59e0b; font-weight:900; font-size:1.1rem;">LINE {err["Line"]} | {err["Reason"]}</div><div style="font-size:0.95rem; color:#cbd5e1; margin-top:8px; line-height:1.4;">{err["Content"]}</div></div><div>{sn_link}</div></div>', unsafe_allow_html=True)
