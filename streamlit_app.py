import streamlit as st  # 导入 Streamlit 库：用于构建网页界面
import pandas as pd     # 导入 Pandas 库：用于处理 Excel 数据表格
import re               # 导入正则库：用于从 SKU 文本中精准提取颜色和尺码

# --- 1. 页面配置 (浏览器页签显示的信息) ---
st.set_page_config(
    page_title="爆单",      # 浏览器标签页显示的标题
    page_icon="🚀",         # 浏览器标签页显示的图标
    layout="wide"           # 页面布局：使用宽屏模式，利用屏幕横向空间
)

# 定义常量：方便后续统一修改
GITHUB_USERNAME = "GianTakeshi" 
# 基础链接：点击 SN 码时跳转到的订单详情页面地址
BASE_URL = "https://inflyway.com/kamelnet/#/kn/fly-link/orders/detail?id="
# 头像链接：通过 GitHub API 获取你的个人头像
AVATAR_URL = f"https://avatars.githubusercontent.com/{GITHUB_USERNAME}"

# --- 2. CSS 样式注入 (这部分决定了网页的“颜值”和“黑客帝国感”) ---
st.markdown(f"""
    <style>
    /* 整个 App 的背景底色：深蓝色到黑色的径向渐变 */
    .stApp {{ 
        background: radial-gradient(circle at 50% 50%, #0c1e3d 0%, #020617 60%, #000000 100%) !important; 
        color: #ffffff; 
        padding-top: 80px !important; 
    }}
    header {{visibility: hidden;}} /* 隐藏 Streamlit 默认的顶部横条 */

    /* [动画] 定义上传框的边框发光呼吸效果：从淡蓝到亮蓝循环 */
    @keyframes uploader-glow {{
        0% {{ border-color: rgba(56, 189, 248, 0.2); box-shadow: 0 0 10px rgba(56, 189, 248, 0.1); }}
        50% {{ border-color: rgba(56, 189, 248, 0.6); box-shadow: 0 0 25px rgba(56, 189, 248, 0.3); }}
        100% {{ border-color: rgba(56, 189, 248, 0.2); box-shadow: 0 0 10px rgba(56, 189, 248, 0.1); }}
    }}

    /* [样式] 左上角头像面板：毛玻璃质感 + 胶囊形状 */
    .user-profile {{
        position: fixed; top: 35px; left: 35px; display: flex; align-items: center; gap: 12px; z-index: 1000000; 
        background: rgba(255, 255, 255, 0.05); padding: 8px 20px 8px 8px; border-radius: 60px;
        border: 1.5px solid rgba(56, 189, 248, 0.2); backdrop-filter: blur(15px);
    }}
    /* [样式] 头像：圆形边框 + 呼吸动画 */
    .avatar {{ width: 38px; height: 38px; border-radius: 50%; border: 2px solid #38bdf8; animation: avatar-breathing 3s infinite ease-in-out; }}
    
    /* [样式] 数据卡片通用：半透明背景 + 悬浮位移特效 */
    .wide-card {{
        background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px; padding: 25px 30px; margin-bottom: 25px;
        display: flex; flex-direction: row; align-items: center; justify-content: space-between;
        backdrop-filter: blur(15px); transition: all 0.5s ease;
    }}
    /* [样式] 鼠标滑过卡片时的交互：向上浮动 8 像素 + 增加内发光 */
    .normal-card:hover {{ transform: translateY(-8px); border-color: #38bdf8; box-shadow: 0 15px 35px rgba(0,0,0,0.5), inset 0 0 80px rgba(56, 189, 248, 0.25); }}

    /* [样式] SN 标签链接：蓝色的胶囊按钮 */
    .sn-pill {{ padding: 6px 14px; border-radius: 40px; font-size: 0.8rem; font-weight: 800; text-decoration: none !important; transition: all 0.3s ease; }}
    .normal-sn {{ background: rgba(56, 189, 248, 0.08); color: #38bdf8 !important; border: 1px solid rgba(56, 189, 248, 0.3); }}
    
    /* [样式] 选项卡切换：去除默认样式，改为霓虹灯胶囊样式 */
    .stTabs [data-baseweb="tab"] {{ height: 42px !important; border-radius: 40px !important; border: 1.5px solid rgba(255, 255, 255, 0.1) !important; background: transparent !important; color: rgba(255, 255, 255, 0.5) !important; }}
    /* [样式] 当选项卡被选中时：增加亮蓝色光晕效果 */
    .stTabs [data-baseweb="tab"][aria-selected="true"] {{ color: #38bdf8 !important; border-color: #38bdf8 !important; box-shadow: 0 0 35px 8px rgba(56, 189, 248, 0.5) !important; }}

    /* [样式] 底部上传区域：固定在底部 + 较强的毛玻璃和发光动画 */
    [data-testid="stFileUploader"] {{
        position: fixed; bottom: 100px; left: 50%; transform: translateX(-50%); 
        width: 520px; z-index: 9999; background: rgba(12, 30, 61, 0.65) !important; 
        border-radius: 24px !important; animation: uploader-glow 4s infinite ease-in-out;
    }}

    /* [样式] 顶部大标题：文字渐变效果 (白到蓝) */
    .grand-title {{ font-size: 3.5rem !important; font-weight: 900; letter-spacing: 8px; background: linear-gradient(to bottom, #ffffff 40%, #38bdf8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    </style>

    <div class="user-profile">
        <img src="{AVATAR_URL}" class="avatar">
        <div class="user-name">{GITHUB_USERNAME}</div>
    </div>
    <div style="text-align:center; margin-bottom:100px;"><h1 class="grand-title">祝王哥天天爆单</h1></div>
""", unsafe_allow_html=True)

# --- 3. 核心数据处理逻辑 (这里是“大脑”，负责算账) ---
def process_sku_logic(uploaded_file):
    # 正则规则：(?i)表示忽略大小写，提取 Color 和 Size 后面的关键词
    COLOR_REG, SIZE_REG = r'(?i)Color[:：\s]*([a-zA-Z0-9\-_/]+)', r'(?i)Size[:：\s]*([a-zA-Z0-9\-\s/]+?)(?=\s*(?:Color|Size|$|[,;，；]))'
    # 尺码转换：如果 Excel 里是全称，自动转为单个字母
    SIZE_MAP = {'HIGH ANKLE SOCKS': 'L', 'KNEE-HIGH SOCKS': 'M'}
    
    df = pd.read_excel(uploaded_file, engine='openpyxl') # 读取上传的文件
    cols = df.columns # 获取所有列名
    all_normal_data, all_error_rows = [], [] # 定义容器，分别存放“正常”和“异常”的数据
    
    for index, row in df.iterrows(): # 遍历 Excel 的每一行
        c_raw = str(row[cols[2]]).strip() # 获取第 3 列 (分类)
        if not c_raw or c_raw == 'nan': continue # 如果分类为空则跳过
        cat = c_raw.split(' ')[0].upper() # 提取分类的第一个单词 (如 WZ)
        if cat.startswith('WZ'): cat = 'WZ' # 统一处理 WZ 打头的分类
        
        g_text = str(row[cols[6]]) # 获取第 7 列 (包含 Color/Size 的原始文本)
        i_val = str(row[cols[8]])  # 获取第 9 列 (计划数量)
        sn = str(row[cols[0]])     # 获取第 1 列 (SN 码)
        
        # 提取数字：从计划数量文本中找出整数 (如 "10双" -> 10)
        i_qty = int(re.findall(r'\d+', i_val)[0]) if re.findall(r'\d+', i_val) else 0
        
        # 分割文本：用分号拆分包含多个 SKU 的字符串
        chunks = [c.strip() for c in re.split(r'[;；]', g_text) if c.strip()]
        data_pairs = []
        
        for chunk in chunks: # 遍历拆分出来的每一个 SKU 块
            c_m = re.search(COLOR_REG, chunk) # 找颜色
            s_m = re.search(SIZE_REG, chunk)  # 找尺码
            if c_m: 
                clr = c_m.group(1).strip().upper() # 存颜色
                raw_s = s_m.group(1).strip().upper() if s_m else "FREE" # 没尺码默认为 FREE
                data_pairs.append((clr, SIZE_MAP.get(raw_s, raw_s))) # 存入临时列表
        
        # 判断：如果识别到的对数 == Excel 标注的数量，则认为正常
        if len(data_pairs) == i_qty and i_qty > 0:
            for c_val, s_val in data_pairs: 
                all_normal_data.append({'Category': cat, 'Color': c_val, 'Size': s_val, 'SN': sn})
        else: # 否则：计入异常列表
            all_error_rows.append({'SN': sn, 'Line': index+2, 'Reason': f"数量异常({len(data_pairs)}/{i_qty})", 'Content': g_text})
            
    return pd.DataFrame(all_normal_data), pd.DataFrame(all_error_rows) # 返回两个处理好的结果表

# --- 4. 界面渲染 (把计算结果变回漂亮网页) ---
upload_zone = st.empty() # 创建一个空容器，方便后续用 empty() 清空
uploaded_file = upload_zone.file_uploader("DROP FILE TO PARSE", type=["xlsx"]) # 显示上传控件

if uploaded_file: # 一旦用户上传了文件
    v_df, e_df = process_sku_logic(uploaded_file) # 调用上面的大脑进行计算
    upload_zone.empty() # 计算完了，把屏幕底部的上传控件藏起来，腾位置给数据
    
    t1, t2 = st.tabs(["汇总数据", "异常拦截"]) # 创建两个切换标签
    
    with t1: # 在“汇总数据”标签下
        if not v_df.empty:
            for cat in sorted(v_df['Category'].unique()): # 按分类(WZ等)循环
                cat_group = v_df[v_df['Category'] == cat]
                attr_html_list = []
                for clr in sorted(cat_group['Color'].unique()): # 按颜色循环
                    clr_group = cat_group[cat_group['Color'] == clr]
                    # 生成尺码徽章：包含 Size 名字和频率计数 (Value Counts)
                    size_badges = [f'<div class="size-box"><b>{s}</b> ×{q}</div>' for s, q in clr_group['Size'].value_counts().sort_index().items()]
                    # 将颜色和对应的尺码徽章拼成 HTML
                    attr_html_list.append(f'<div class="row">{clr} : {" ".join(size_badges)}</div>')
                
                # 生成右侧的 SN 跳转胶囊
                sn_html = "".join([f'<a href="{BASE_URL}{sn}" target="_blank" class="sn-pill normal-sn">{sn}</a>' for sn in sorted(list(set(cat_group['SN'].tolist())))])
                # 最终渲染成一个大卡片
                st.markdown(f'<div class="wide-card normal-card"><div><h2>{cat}</h2>{"".join(attr_html_list)}</div><div>{sn_html}</div></div>', unsafe_allow_html=True)
            
            if st.button("↺ 重制系统"): st.rerun() # 底部的重置按钮

    with t2: # 在“异常拦截”标签下
        if not e_df.empty:
            for _, err in e_df.iterrows(): # 循环显示所有错误的行
                sn_link = f'<a href="{BASE_URL}{err["SN"]}" target="_blank" class="sn-pill error-sn-pill">{err["SN"]}</a>'
                # 渲染橙色警告样式的卡片
                st.markdown(f'<div class="wide-card error-card"><div><b>LINE {err["Line"]}</b> | {err["Reason"]}<p>{err["Content"]}</p></div><div>{sn_link}</div></div>', unsafe_allow_html=True)
