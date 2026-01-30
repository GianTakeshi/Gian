    <style>
    /* 🎨 全局背景：增加微弱噪声感以消除背景渐变的断层 */
    .stApp {{ 
        background: radial-gradient(circle at 50% 50%, #0c1e3d 0%, #020617 60%, #000000 100%) !important; 
        color: #ffffff; 
        padding-top: 80px !important; 
    }}
    header {{visibility: hidden;}}

    /* ✨ [平滑 HDR] 上传框动画：通过 5 层超细微阴影叠加消除断层 */
    @keyframes uploader-glow {{
        0% {{ border-color: rgba(56, 189, 248, 0.1); box-shadow: 0 0 10px rgba(56, 189, 248, 0.05); }}
        50% {{ 
            border-color: color(display-p3 0.3 0.8 1 / 0.8);
            /* 多层超浅阴影，每层透明度极低，模拟物理辉光渐散 */
            box-shadow: 
                0 0 10px #fff,
                0 0 20px color(display-p3 0.22 0.74 0.97 / 0.5),
                0 0 40px color(display-p3 0.22 0.74 0.97 / 0.3),
                0 0 60px color(display-p3 0.22 0.74 0.97 / 0.1),
                0 0 100px color(display-p3 0.22 0.74 0.97 / 0.05);
        }}
        100% {{ border-color: rgba(56, 189, 248, 0.1); box-shadow: 0 0 10px rgba(56, 189, 248, 0.05); }}
    }}

    /* 🛡️ 用户面板 */
    .user-profile {{
        position: fixed; top: 35px; left: 35px; display: flex; align-items: center; gap: 12px; z-index: 1000000; 
        background: rgba(255, 255, 255, 0.05); padding: 8px 20px 8px 8px; border-radius: 60px;
        border: 1.5px solid rgba(56, 189, 248, 0.2); backdrop-filter: blur(15px);
    }}
    .avatar {{ width: 38px; height: 38px; border-radius: 50%; border: 2px solid #38bdf8; }}

    /* 🧊 数据卡片：使用渐进式内阴影，防止边缘产生“硬杠” */
    .wide-card {{
        background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px; padding: 25px 30px; margin-bottom: 25px;
        display: flex; flex-direction: row; align-items: center; justify-content: space-between;
        backdrop-filter: blur(15px); transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    .normal-card {{ border-left: 5px solid rgba(56, 189, 248, 0.3); }}
    .normal-card:hover {{ 
        transform: translateY(-5px); 
        border-color: color(display-p3 0.4 0.85 1);
        /* 分散压力，避免色阶断层 */
        box-shadow: 0 15px 40px rgba(0,0,0,0.5), 
                    inset 0 0 30px color(display-p3 0.22 0.74 0.97 / 0.3),
                    inset 0 0 60px color(display-p3 0.22 0.74 0.97 / 0.1); 
    }}

    /* 🚫 Tabs 选中：极致平滑强光 */
    .stTabs [data-baseweb="tab"][aria-selected="true"]:nth-child(1) {{ 
        color: #fff !important; 
        border-color: color(display-p3 0.4 0.85 1) !important;
        background: rgba(56, 189, 248, 0.15) !important;
        box-shadow: 0 0 15px #fff, 
                    0 0 30px color(display-p3 0.22 0.74 0.97 / 0.8), 
                    0 0 60px color(display-p3 0.22 0.74 0.97 / 0.2) !important;
    }}

    /* 🏷️ 其他 UI 细节保持原样 */
    .sn-pill {{ padding: 6px 14px; border-radius: 40px; font-size: 0.8rem; font-weight: 800; text-decoration: none !important; transition: all 0.3s ease; }}
    .normal-sn {{ background: rgba(56, 189, 248, 0.08); color: #38bdf8 !important; border: 1px solid rgba(56, 189, 248, 0.3); }}
    .normal-sn:hover {{ background: color(display-p3 0.22 0.74 0.97) !important; color: #000000 !important; box-shadow: 0 0 15px color(display-p3 0.22 0.74 0.97); }}

    [data-testid="stFileUploader"] {{
        position: fixed; bottom: 100px; left: 50%; transform: translateX(-50%); 
        width: 520px; z-index: 9999;
        background: rgba(12, 30, 61, 0.7) !important; border-radius: 24px !important; 
        backdrop-filter: blur(40px) !important;
        border: 1.5px solid rgba(56, 189, 248, 0.3) !important;
        animation: uploader-glow 4s infinite ease-in-out;
    }}
    .grand-title {{ display: inline-block; font-size: 3.5rem !important; font-weight: 900; letter-spacing: 8px; background: linear-gradient(to bottom, #ffffff 40%, #38bdf8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    </style>
