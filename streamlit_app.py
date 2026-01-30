import streamlit as st
import pandas as pd
import re

# --- 1. 页面配置 ---
st.set_page_config(page_title="爆单", page_icon="🚀", layout="wide")

# 配置常量
GITHUB_USERNAME = "GianTakeshi" 
BASE_URL = "https://inflyway.com/kamelnet/#/kn/fly-link/orders/detail?id="
AVATAR_URL = f"https://avatars.githubusercontent.com/{GITHUB_USERNAME}"

# --- 2. 注入 CSS (动态极光 HDR 背景版) ---
st.markdown(f"""
    <style>
    /* 🎨 [极光流体] 基础底色 */
    .stApp {{ 
        background: #000000 !important;
        color: #ffffff; 
        padding-top: 80px !important; 
    }}
    header {{visibility: hidden;}}

    /* 🌊 极光气泡层 - 使用双大括号转义 Python 语法 */
    .stApp::before, .stApp::after {{
        content: "";
        position: fixed;
        width: 100vw;
        height: 100vw;
        border-radius: 50%;
        z-index: -2;
        filter: blur(100px);
        opacity: 0.6;
        pointer-events: none;
    }}

    /* 深海蓝气泡 */
    .stApp::before {{
        background: radial-gradient(circle, color(display-p3 0.05 0.2 0.4) 0%, transparent 70%);
        top: -30%;
        left: -20%;
        animation: aurora-1 25s infinite alternate ease-in-out;
    }}

    /* 电磁蓝气泡 */
    .stApp::after {{
        background: radial-gradient(circle, color(display-p3 0.1 0.1 0.3) 0%, transparent 70%);
        bottom: -30%;
        right: -10%;
        animation: aurora-2 30s infinite alternate-reverse ease-in-out;
    }}

    /* 🕺 动力学动画定义 */
    @keyframes aurora-1 {{
        0% {{ transform: translate3d(0, 0, 0) scale(1); }}
        50% {{ transform: translate3d(20%, 15%, 0) scale(1.2); }}
        100% {{ transform: translate3d(-10%, 25%, 0) scale(0.9); }}
    }}

    @keyframes aurora-2 {{
        0% {{ transform: translate3d(0, 0, 0) scale(1.1); }}
        50% {{ transform: translate3d(-25%, -20%, 0) scale(0.8); }}
        100% {{ transform: translate3d(15%, -10%, 0) scale(1.3); }}
    }}

    /* ✨ 上传框呼吸：HDR 提亮 */
    @keyframes uploader-glow {{
        0% {{ border-color: rgba(56, 189, 248, 0.2); box-shadow: 0 0 10px rgba(56, 189, 248, 0.1); }}
        50% {{ border-color: color(display-p3 0.22 0.74 0.97); box-shadow: 0 0 25px color(display-p3 0.22 0.74 0.97 / 0.5); }}
        100% {{ border-color: rgba(56, 189, 248, 0.2); box-shadow: 0 0 10px rgba(56, 189, 248, 0.1); }}
    }}

    /* ✨ 头像呼吸 */
    @keyframes avatar-breathing {{
        0% {{ box-shadow: 0 0 0 0 rgba(56, 189, 248, 0.4); transform: scale(1); }}
        50% {{ box-shadow: 0 0 20px 4px color(display-p3 0.22 0.74 0.97 / 0.8); transform: scale(1.05); }}
        100% {{ box-shadow: 0 0 0 0 rgba(56, 189, 248, 0.4); transform: scale(1); }}
    }}

    .user-profile {{
        position: fixed; top: 35px; left: 35px; display: flex; align-items: center; gap: 12px; z-index: 1000000; 
        background: rgba(255, 255, 255, 0.05); padding: 8px 20px 8px 8px; border-radius: 60px;
        border: 1.5px solid rgba(56, 189, 248, 0.2); backdrop-filter: blur(15px);
    }}
    .avatar {{ width: 38px; height: 38px; border-radius: 50%; border: 2px solid #38bdf8; animation: avatar-breathing 3s infinite ease-in-out; }}
    .user-name {{ font-size: 0.95rem; font-weight: 600; color: #fff; letter-spacing: 0.5px; }}

    .wide-card {{
        background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px; padding: 25px 30px; margin-bottom: 25px;
        display: flex; flex-direction: row; align-items: center; justify-content: space-between;
        backdrop-filter: blur(25px); transition: all 0.5s cubic-bezier(0.165, 0.84, 0.44, 1);
    }}
    .normal-card {{ border-left: 5px solid rgba(56, 189, 248, 0.4); }}
    .normal-card:hover {{ 
        transform: translateY(-8px); 
        border-color: color(display-p3 0.22 0.74 0.97); 
        box-shadow: 0 15px 35px rgba(0,0,0,0.5), inset 0 0 80px color(display-p3 0.22 0.74 0.97 / 0.25); 
    }}

    .sn-pill {{ padding: 6px 14px; border-radius: 40px; font-size: 0.8rem; font-weight: 800; text-decoration: none !important; transition: all 0.3s ease; border: 1px solid transparent; }}
    .normal-sn {{ background: rgba(56, 189, 248, 0.08); color: #38bdf8 !important; border: 1px solid rgba(56, 189, 248, 0.3); }}
    .normal-sn:hover {{ background: color(display-p3 0.22 0.74 0.97) !important; color: #000000 !important; box-shadow: 0 0 20px color(display-p3 0.22 0.74 0.97 / 0.6); transform: scale(1.05); }}

    .stTabs [data-baseweb="tab-list"] {{ gap: 20px; background: transparent !important; padding: 30px 10px !important; }}
    .stTabs [data-baseweb="tab"] {{ height: 42px !important; border-radius: 40px !important; border: 1.5px solid rgba(255, 255, 255, 0.1) !important; color: rgba(255, 255, 255, 0.5) !important; }}
    .stTabs [data-baseweb="tab"][aria-selected="true"]:nth-child(1) {{ color: color(display-p3 0.22 0.74 0.97) !important; border-color: color(display-p3 0.22 0.74 0.97) !important; box-shadow: 0 0 35px 8px color(display-p3 0.22 0.74 0.97 / 0.5) !important; }}
    .stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {{ display: none !important; }}

    [data-testid="stFileUploader"] {{
        position: fixed; bottom: 100px; left: 50%; transform: translateX(-50%); 
        width: 520px; z-index: 9999;
        background: rgba(12, 30, 61, 0.65) !important; 
        border-radius: 24px !important; padding: 20px !important; 
        backdrop-filter: blur(30px) !important;
        border: 1.5px solid rgba(56, 189, 248, 0.3) !important;
        animation: uploader-glow 4s infinite ease-in-out;
    }}
    .grand-title {{ display: inline-block; font-size: 3.5rem !important; font-weight: 900; letter-spacing: 8px; background: linear-gradient(to bottom, #ffffff 40%, #38bdf8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    </style>

    <div class="user-profile">
        <img src="{AVATAR_URL}" class="avatar">
        <div class="user-name">{GITHUB_USERNAME}</div>
    </div>
    <div style="text-align:center; margin-bottom:100px;"><h1 class="grand-title">祝王哥天天爆单</h1></div>
""", unsafe_allow_html=True)

# 后续业务逻辑逻辑代码...
# [此处接你之前的 process_sku_logic 和 UI 渲染逻辑]
