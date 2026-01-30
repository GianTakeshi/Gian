import streamlit as st  # 核心框架：用于构建交互式 Web 页面
import pandas as pd     # 数据处理：用于读取和操作 Excel 表格数据
import re               # 正则表达式：用于从复杂的 SKU 文本中提取关键信息

# --- 1. 页面配置 (定义浏览器标签页的元数据) ---
st.set_page_config(page_title="爆单", page_icon="🚀", layout="wide") # 设置标题、小火箭图标及宽屏模式

# 配置常量：定义你的 GitHub 身份信息和订单跳转的固定链接前缀
GITHUB_USERNAME = "GianTakeshi" 
BASE_URL = "https://inflyway.com/kamelnet/#/kn/fly-link/orders/detail?id=" # 详情页跳转基地址
AVATAR_URL = f"https://avatars.githubusercontent.com/{GITHUB_USERNAME}" # 动态拼接 GitHub 头像地址

# --- 2. 注入深度定制 CSS (控制网页所有视觉元素的样式表) ---
st.markdown(f"""
    <style>
    /* 🎭 页面主体：设置背景为深邃的径向渐变黑蓝色，并调整顶部边距 */
    .stApp {{ 
        background: radial-gradient(circle at 50% 50%, #0c1e3d 0%, #020617 60%, #000000 100%) !important; 
        color: #ffffff; 
        padding-top: 80px !important; 
    }}
    header {{visibility: hidden;}} /* 隐藏 Streamlit 页面原有的顶部装饰条 */

    /* ✨ 动画定义：上传控件边框的呼吸发光效果 (颜色深浅交替) */
    @keyframes uploader-glow {{
        0% {{ border-color: rgba(56, 189, 248, 0.2); box-shadow: 0 0 10px rgba(56, 189, 248, 0.1); }}
        50% {{ border-color: rgba(56, 189, 248, 0.6); box-shadow: 0 0 25px rgba(56, 189, 248, 0.3); }}
        100% {{ border-color: rgba(56, 189, 248, 0.2); box-shadow: 0 0 10px rgba(56, 189, 248, 0.1); }}
    }}

    /* ✨ 动画定义：左上角头像的轻微缩放和外发光呼吸效果 */
    @keyframes avatar-breathing {{
        0% {{ box-shadow: 0 0 0 0 rgba(56, 189, 248, 0.4); transform: scale(1); }}
        50% {{ box-shadow: 0 0 20px 4px rgba(56, 189, 248, 0.7); transform: scale(1.05); }}
        100% {{ box-shadow: 0 0 0 0 rgba(56, 189, 248, 0.4); transform: scale(1); }}
    }}

    /* 🛡️ 用户信息面板：固定在左上角，采用半透明毛玻璃背景 */
    .user-profile {{
        position: fixed; top: 35px; left: 35px; display: flex; align-items: center; gap: 12px; z-index: 1000000; 
        background: rgba(255, 255, 255, 0.05); padding: 8px 20px 8px 8px; border-radius: 60px;
        border: 1.5px solid rgba(56, 189, 248, 0.2); backdrop-filter: blur(15px);
    }}
    /* 🛡️ 头像样式：圆形展示，并绑定上面定义的缩放动画 */
    .avatar {{ width: 38px; height: 38px; border-radius: 50%; border: 2px solid #38bdf8; animation: avatar-breathing 3s infinite ease-in-out; }}
    /* 🛡️ 用户名样式：设置字体大小、粗细及字母间距 */
    .user-name {{ font-size: 0.95rem; font-weight: 600; color: #fff; letter-spacing: 0.5px; }}

    /* 🧊 通用数据卡片：设置圆角、内边距、背景及平滑过渡动画 */
    .wide-card {{
        background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px; padding: 25px 30px; margin-bottom: 25px;
        display: flex; flex-direction: row; align-items: center; justify-content: space-between;
        backdrop-filter: blur(15px); transition: all 0.5s cubic-bezier(0.165, 0.84, 0.44, 1);
    }}
    /* 🧊 正常卡片侧边条：左侧蓝色装饰线 */
    .normal-card {{ border-left: 5px solid rgba(56, 189, 248, 0.4); }}
    /* 🧊 正常卡片悬停反馈：向上移动 8 像素，增加强烈的内发光和外阴影 */
    .normal-card:hover {{ transform: translateY(-8px); border-color: #38bdf8; box-shadow: 0 15px 35px rgba(0,0,0,0.5), inset 0 0 80px rgba(56, 189, 248, 0.25); }}
    /* 🧊 异常卡片侧边条：左侧橙色装饰线 */
    .error-card {{ border-left: 5px solid rgba(245, 158, 11, 0.4); }}
    /* 🧊 异常卡片悬停反馈：向上移动 8 像素，增加橙色内发光 */
    .error-card:hover {{ transform: translateY(-8px); border-color: #f59e0b; box-shadow: 0 15px 35px rgba(0,0,0,0.5), inset 0 0 80px rgba(245, 158, 11, 0.25); }}

    /* 🏷️ SN 标签按钮：胶囊形状，去除下划线，设置点击跳转的过渡时间 */
    .sn-pill {{ padding: 6px 14px; border-radius: 40px; font-size: 0.8rem; font-weight: 800; text-decoration: none !important; transition: all 0.3s ease; border: 1px solid transparent; }}
    /* 🏷️ 正常 SN 标签：淡蓝色背景 + 蓝色文字 */
    .normal-sn {{ background: rgba(56, 189, 248, 0.08); color: #38bdf8 !important; border: 1px solid rgba(56, 189, 248, 0.3); }}
    /* 🏷️ 正常 SN 标签悬停：反转为蓝底黑字，增加发光感 */
    .normal-sn:hover {{ background: #38bdf8 !important; color: #000000 !important; box-shadow: 0 0 20px rgba(56, 189, 248, 0.6); transform: scale(1.05); }}
    /* 🏷️ 异常 SN 标签：淡橙色背景 + 橙色文字 */
    .error-sn-pill {{ background: rgba(245, 158, 11, 0.08); color: #f59e0b !important; border: 1px solid rgba(245, 158, 11, 0.3); }}
    /* 🏷️ 异常 SN 标签悬停：反转为橙底黑字，增加橙光 */
    .error-sn-pill:hover {{ background: #f59e0b !important; color: #000000 !important; box-shadow: 0 0 20px rgba(245, 158, 11, 0.6); transform: scale(1.05); }}

    /* 🚫 选项卡组件优化：允许溢出显示以展示发光效果，设置列表间距 */
    .stTabs {{ overflow: visible !important; }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 20px; background: transparent !important; padding: 30px 10px !important; margin-bottom: 10px; overflow: visible !important; }}
    /* 🚫 选项卡按钮：重塑为胶囊形状，添加细微边框，隐藏原始选中线条 */
    .stTabs [data-baseweb="tab"] {{ height: 42px !important; padding: 0 30px !important; font-size: 1rem !important; border-radius: 40px !important; border: 1.5px solid rgba(255, 255, 255, 0.1) !important; background: rgba(255, 255, 255, 0.02) !important; color: rgba(255, 255, 255, 0.5) !important; transition: all 0.4s ease !important; position: relative; z-index: 10; }}
    /* 🚫 选中第一个 Tab (汇总数据) 时的发光蓝样式 */
    .stTabs [data-baseweb="tab"][aria-selected="true"]:nth-child(1) {{ color: #38bdf8 !important; border-color: #38bdf8 !important; background: rgba(56, 189, 248, 0.15) !important; box-shadow: 0 0 35px 8px rgba(56, 189, 248, 0.5) !important; }}
    /* 🚫 选中第二个 Tab (异常拦截) 时的发光橙样式 */
    .stTabs [data-baseweb="tab"][aria-selected="true"]:nth-child(2) {{ color: #f59e0b !important; border-color: #f59e0b !important; background: rgba(245, 158, 11, 0.15) !important; box-shadow: 0 0 35px 8px rgba(245, 158, 11, 0.5) !important; }}
    /* 🚫 隐藏 Streamlit 原生选项卡底部的那根难看的白线 */
    .stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {{ display: none !important; }}

    /* 🔄 “重制系统”按钮：定义居中布局、蓝色描边、极粗字体 */
    div.stButton > button {{ 
        background: rgba(56, 189, 248, 0.08) !important; color: #38bdf8 !important; 
        border: 1.5px solid rgba(56, 189, 248, 0.4) !important; border-radius: 40px !important; 
        padding: 10px 45px !important; font-weight: 800 !important; font-size: 1rem !important; 
        transition: all 0.4s ease !important; margin: 50px auto !important; display: block !important; 
    }}
    /* 🔄 按钮悬停：全亮背景，增加按钮周围的蓝色光晕 */
    div.stButton > button:hover {{ background: #38bdf8 !important; color: #000000 !important; box-shadow: 0 0 30px 5px rgba(56, 189, 248, 0.5) !important; transform: scale(1.05); }}

    /* 📥 文件上传器：将其固定在屏幕底部中央，增加高强度模糊(毛玻璃)和呼吸边框动画 */
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
    /* 📥 上传器内按钮：加粗并微调圆角 */
    [data-testid="stFileUploader"] button {{ font-weight: 800 !important; border-radius: 12px !important; }}

    /* 🌟 主标题：利用渐变背景裁切出文字颜色，实现白到蓝的视觉渐变 */
    .grand-title {{ display: inline-block; font-size: 3.5rem !important; font-weight: 900; letter-spacing: 8px; background: linear-gradient(to bottom, #ffffff 40%, #38bdf8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    </style>

    <div class="user-profile">
        <img src="{AVATAR_URL}" class="avatar">
        <div class="user-name">{GITHUB_USERNAME}</div>
    </div>
    <div style="text-align:center; margin-bottom:100px;"><h1 class="grand-title">祝王哥天天爆单</h1></div>
""", unsafe_allow_html=True)

# --- 3. 核心提取逻辑 (处理 Excel 数据并将非结构化 SKU 拆解为属性) ---
def process_sku_logic(uploaded_file):
    # 正则规则：用于匹配文本中 Color: 后面的内容，以及 Size: 后面的内容
    COLOR_REG, SIZE_REG = r'(?i)Color[:：\s]*([a-zA-Z0-9\-_/]+)', r'(?i)Size[:：\s]*([a-zA-Z0-9\-\s/]+?)(?=\s*(?:Color|Size|$|[,;，；]))'
    # 映射字典：将 Excel 中冗长的尺码表述映射为简洁的 L/M 字符
    SIZE_MAP = {'HIGH ANKLE SOCKS': 'L', 'KNEE-HIGH SOCKS': 'M'}
    
    # 读取逻辑：使用 pandas 读取 Excel，并初始化结果存放列表
    df = pd.read_excel(uploaded_file, engine='openpyxl')
    cols = df.columns
    all_normal_data, all_error_rows = [], []
    
    # 逐行扫描：处理表格中的每一行记录
    for index, row in df.iterrows():
        # 分类清洗：提取 Category，并将 WZ 开头的各种子分类统一标记为 WZ
        c_raw = str(row[cols[2]]).strip()
        if not c_raw or c_raw == 'nan': continue
        cat = c_raw.split(' ')[0].upper()
        if cat.startswith('WZ'): cat = 'WZ'
        
        # 字段获取：提取 SKU 详情文本、计划数量文本及订单唯一标识 SN
        g_text, i_val, sn = str(row[cols[6]]), str(row[cols[8]]), str(row[cols[0]])
        # 数量清洗：从“10双”这类文本中只提取出数字 10
        i_qty = int(re.findall(r'\d+', i_val)[0]) if re.findall(r'\d+', i_val) else 0
        
        # 异常检测：如果分类里包含分号，代表该行可能混合了多类商品，记录异常
        if ';' in c_raw or '；' in c_raw:
            all_error_rows.append({'SN': sn, 'Line': index+2, 'Reason': "多个商品", 'Content': g_text})
            continue
            
        # SKU 拆分：按照分号将多组 Color/Size 文本切分为独立的块
        chunks = [c.strip() for c in re.split(r'[;；]', g_text) if c.strip()]
        data_pairs = []
        # 属性提取：遍历每个块，利用正则抓取颜色和尺码
        for chunk in chunks:
            c_m, s_m = re.search(COLOR_REG, chunk), re.search(SIZE_REG, chunk)
            if c_m: 
                clr = c_m.group(1).strip().upper()
                raw_s = s_m.group(1).strip().upper() if s_m else "FREE" # 默认 FREE
                data_pairs.append((clr, SIZE_MAP.get(raw_s, raw_s))) # 存入临时配对表
        
        # 准确性比对：如果提取出的 SKU 对数等于计划数量，则存入正常表，否则存入异常表
        if len(data_pairs) == i_qty and i_qty > 0:
            for c_val, s_val in data_pairs: 
                all_normal_data.append({'Category': cat, 'Color': c_val, 'Size': s_val, 'SN': sn})
        else:
            all_error_rows.append({'SN': sn, 'Line': index+2, 'Reason': f"数量异常({len(data_pairs)}/{i_qty})", 'Content': g_text})
            
    return pd.DataFrame(all_normal_data), pd.DataFrame(all_error_rows) # 返回两个整理好的 DataFrame

# --- 4. UI 渲染 (将分析后的结果展示到页面前端) ---
upload_zone = st.empty() # 创建占位槽位，用于动态隐藏上传器
uploaded_file = upload_zone.file_uploader("DROP FILE TO PARSE", type=["xlsx"]) # 文件上传入口

if uploaded_file:
    v_df, e_df = process_sku_logic(uploaded_file) # 调用处理逻辑获取结果
    upload_zone.empty() # 上传成功后清空上传器所在位置，腾出视觉空间
    
    t1, t2 = st.tabs(["汇总数据", "异常拦截"]) # 创建两个结果标签页
    
    with t1:
        if not v_df.empty:
            # 渲染逻辑：按 Category 循环，每个分类生成一个大卡片
            for cat in sorted(v_df['Category'].unique()):
                cat_group = v_df[v_df['Category'] == cat]
                attr_html_list = []
                # 颜色统计：在分类内部，按颜色进行分组汇总
                for clr in sorted(cat_group['Color'].unique()):
                    clr_group = cat_group[cat_group['Color'] == clr]
                    # 生成尺码徽章：计算该颜色下各尺码出现的频次，并生成带数量的 HTML 标签
                    size_badges = [f'<div style="display:inline-flex; align-items:center; background:rgba(255,255,255,0.05); border:1.5px solid rgba(255,255,255,0.12); border-radius:8px; padding:4px 12px; margin-right:8px;"><span style="color:#fff; font-size:0.9rem; font-weight:800;">{(s if s!="FREE" else "")}</span><span style="color:#38bdf8; font-weight:800; font-size:0.9rem; margin-left:5px;">{("×" if s!="FREE" else "")}{q}</span></div>' for s, q in clr_group['Size'].value_counts().sort_index().items()]
                    # 将颜色和对应的尺码徽章行封装成 HTML 块
                    attr_html_list.append(f'<div style="display:flex; align-items:center; gap:20px; padding:10px 0;"><div style="color:#38bdf8; font-weight:700; min-width:100px; font-size:1.1rem;">{clr}</div><div>{"".join(size_badges)}</div></div>')
                
                # 标签生成：将所有相关的 SN 订单号去重并生成可点击的跳转链接
                sn_html = "".join([f'<a href="{BASE_URL}{sn}" target="_blank" class="sn-pill normal-sn">{sn}</a>' for sn in sorted(list(set(cat_group['SN'].tolist())))])
                # 最终组合：渲染出带有分类名、详情列表、及侧边 SN 链接的大卡片
                st.markdown(f'<div class="wide-card normal-card"><div style="flex:1;"><div style="color:#38bdf8; font-weight:900; font-size:1.8rem; margin-bottom:15px; letter-spacing:1px;">{cat}</div>{"".join(attr_html_list)}</div><div style="display:flex; flex-wrap:wrap; gap:8px; justify-content:flex-end; max-width:400px;">{sn_html}</div></div>', unsafe_allow_html=True)
            
            # 操作逻辑：渲染底部的刷新按钮
            if st.button("↺ 重制系统"): st.rerun()

    with t2:
        # 异常渲染：如果存在识别错误的行，生成带橙色边框的警告卡片
        if not e_df.empty:
            for _, err in e_df.iterrows():
                sn_link = f'<a href="{BASE_URL}{err["SN"]}" target="_blank" class="sn-pill error-sn-pill">{err["SN"]}</a>'
                # 渲染：显示行号、错误原因以及导致错误的原始文本内容
                st.markdown(f'<div class="wide-card error-card"><div style="flex:1;"><div style="color:#f59e0b; font-weight:900; font-size:1.1rem;">LINE {err["Line"]} | {err["Reason"]}</div><div style="font-size:0.95rem; color:#cbd5e1; margin-top:8px; line-height:1.4;">{err["Content"]}</div></div><div>{sn_link}</div></div>', unsafe_allow_html=True)
