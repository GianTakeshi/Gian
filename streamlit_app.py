    /* --- 💊 药丸形状 Tabs 重制 --- */
    /* 1. 隐藏默认的红色/红色位移线条 */
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: transparent !important;
        display: none !important;
    }

    /* 2. Tab 容器间距调整 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        background-color: transparent !important;
        border-bottom: none !important; /* 去除底部整行边框 */
    }

    /* 3. 基础药丸样式 */
    .stTabs [data-baseweb="tab"] {
        height: 40px !important;
        padding: 0 30px !important;
        border-radius: 50px !important; /* 彻底药丸化 */
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        background: rgba(255, 255, 255, 0.03) !important;
        color: rgba(255, 255, 255, 0.4) !important;
        transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1) !important;
    }

    /* 4. 激活状态：汇总数据流 (药丸蓝) */
    .stTabs [data-baseweb="tab"]:nth-child(1)[aria-selected="true"] {
        color: #38bdf8 !important;
        background: rgba(56, 189, 248, 0.15) !important;
        border: 1.5px solid #38bdf8 !important;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.3);
        transform: scale(1.05);
    }

    /* 5. 激活状态：异常拦截 (药丸橙) */
    .stTabs [data-baseweb="tab"]:nth-child(2)[aria-selected="true"] {
        color: #f59e0b !important;
        background: rgba(245, 158, 11, 0.15) !important;
        border: 1.5px solid #f59e0b !important;
        box-shadow: 0 0 20px rgba(245, 158, 11, 0.3);
        transform: scale(1.05);
    }

    /* 6. 悬浮反馈 */
    .stTabs [data-baseweb="tab"]:hover {
        border-color: rgba(255, 255, 255, 0.4) !important;
        color: #fff !important;
    }
