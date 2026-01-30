import streamlit as st
import pandas as pd
import re

# --- 1. 页面配置 ---
st.set_page_config(page_title="SKU 属性解析中枢", page_icon="🚀", layout="wide")

GITHUB_USERNAME = "GianTakeshi" 
BASE_URL = "https://inflyway.com/kamelnet/#/kn/fly-link/orders/detail?id="
# 修正后的头像直链
AVATAR_URL = f"https://avatars.githubusercontent.com/{GITHUB_USERNAME}"

# --- 2. 注入核心 CSS ---
st.markdown(f"""
    <style>
    /* 🎭 背景 */
    .stApp {{ 
        background: radial-gradient(circle at 50% 50%, #0c1e3d 0%, #020617 60%, #000000 100%) !important; 
        color: #ffffff; 
    }}
    header {{visibility: hidden;}}

    /* 🛡️ 用户面板 - 确保头像显示并带有呼吸光晕 */
    @keyframes avatarPulse {{
        0%, 100% {{ box-shadow: 0 0 5px rgba(56, 189, 248, 0.3); border-color: rgba(56, 189, 248, 0.3); }}
        50% {{ box-shadow: 0 0 20px rgba(56, 189, 248, 0.7); border-color: rgba(56, 189, 248, 0.9); }}
    }}
    .user-profile {{
        position: fixed; top: 25px; left: 25px; display: flex; align-items: center; gap: 12px; z-index: 1000000; 
        background: rgba(255, 255, 255, 0.05); padding: 8px 20px 8px 8px; border-radius: 50px;
        border: 1px solid rgba(56, 189, 248, 0.2); backdrop-filter: blur(15px);
    }}
    .avatar {{ 
        width: 42px; height: 42px; border-radius: 50%; border: 2px solid #38bdf8; 
        object-fit: cover; animation: avatarPulse 2.5s infinite ease-in-out; 
    }}

    .grand-title {{
        text-align: center; font-family: 'Inter', sans-serif; font-size: 3.5rem !important; font-weight: 900; letter-spacing: 10px;
        background: linear-gradient(to bottom, #ffffff 40%, #38bdf8 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 40px 0;
    }}

    /* 💊 强效胶囊 Tab 锁定 (button 元素) */
    div[data-baseweb="tab-list"] {{ gap: 16px !important; background: transparent !important; }}
    div[data-baseweb="tab-highlight"] {{ display: none !important; }}
    
    button[data-baseweb="tab"] {{
        border-radius: 50px !important; 
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        background-color: rgba(255, 255, 255, 0.03) !important;
        padding: 8px 30px !important;
        height: 42px !important;
        transition: all 0.3s ease !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        background-color: rgba(56, 189, 248, 0.15) !important;
        border: 1.5px solid #38bdf8 !important;
        color: #38bdf8 !important;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.3) !important;
    }}

    /* 🧊 卡片浮动效果 */
    .wide-card {{
        background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px; padding: 25px 30px; margin-bottom: 25px;
        display: flex; flex-direction: row; align-items: center; justify-content: space-between;
        backdrop-filter: blur(15px);
        transition: all 0.4s cubic-bezier(0.2, 1, 0.3, 1) !important;
    }}
    .wide-card:hover {{
        transform: translateY(-12px) !important;
        border-color: rgba(56, 189, 248, 0.6) !important;
        box-shadow: 0 20px 40px rgba(0,0,0,0.5), 0 0 30px rgba(56, 189, 248, 0.25) !important;
    }}
    .normal-card {{ border-left: 5px solid rgba(56, 189, 248, 0.5); }}

    /* SN 药丸 */
    .sn-pill {{ 
        padding: 6px 18px; border-radius: 50px !important; 
        font-size: 0.75rem; font-weight: 600; text-decoration: none !important; transition: 0.2s; 
    }}
    .normal-sn {{ background: rgba(56, 189, 248, 0.1); color: #38bdf8 !important; border: 1px solid rgba(56, 189, 248, 0.2); }}

    /* 上传框固定 */
    [data-testid="stFileUploader"] {{
        position: fixed; bottom: 35px; left: 50%; transform: translateX(-50%); width: 450px; z-index: 9999;
        background: rgba(255, 255, 255, 0.08) !important; border: 1px solid rgba(56, 189, 248, 0.3) !important;
        border-radius: 50px !important; padding: 15px 35px !important; backdrop-filter: blur(25px) !important;
    }}
    </style>

    <div class="user-profile">
        < img src="{AVATAR_URL}" class="avatar">
        <div class="user-info">
            <div style="font-size: 0.9rem; font-weight: 900; color: #fff;">{GITHUB_USERNAME}</div>
            <div style="font-size: 0.6rem; color: #38bdf8; font-weight: bold;">● QUANTUM ANALYZER</div>
        </div>
    </div>
    <div class="grand-title">SKU 属性解析中枢</div>
""", unsafe_allow_html=True)

# --- [后续逻辑部分保持一致，直接运行即可] ---

uploaded_file = st.file_uploader("Upload", type=["xlsx"])

if uploaded_file:
    # ... (逻辑处理函数 process_sku_logic 略，同前文) ...
    # 此处假设逻辑已运行并返回 v_df, e_df
    t1, t2 = st.tabs(["💎 汇总数据流", "📡 异常拦截"])
    # ... (渲染内容略，同前文) ...
