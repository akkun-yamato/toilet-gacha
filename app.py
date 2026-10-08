import streamlit as st
import streamlit.components.v1 as components
from datetime import date
import time
from database import init_db, get_members, get_round_counts, save_result, get_history, reset_round
from gacha import draw_all

st.set_page_config(
    page_title="ヤマト トイレ掃除ガチャ",
    page_icon="🎰",
    layout="wide"
)

init_db()

# カスタムCSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #ffe4ec 0%, #fff8d6 50%, #e8d5ff 100%);
    }
    h1 {
        text-align: center;
        color: #ff6b9d;
        font-size: 2.5em;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .date-display {
        text-align: center;
        font-size: 1.2em;
        color: #666;
        margin-bottom: 20px;
    }
    .stButton>button {
        background: linear-gradient(45deg, #ff6b9d, #c86dd7);
        color: white;
        font-size: 1.3em;
        font-weight: bold;
        padding: 15px 40px;
        border-radius: 30px;
        border: none;
        box-shadow: 0 4px 15px rgba(255,107,157,0.4);
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 20px rgba(255,107,157,0.6);
    }
    .winner-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        text-align: center;
        margin: 10px 0;
        min-height: 140px;
    }
    .winner-card h2 {
        font-size: 1.8em;
        margin: 10px 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .role-men { border-top: 6px solid #4a90e2; }
    .role-guest { border-top: 6px solid #feca57; }
    .role-women { border-top: 6px solid #ff6b9d; }
    .stCheckbox label p {
        font-size: 20px !important;
        font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)

# タイトル
st.markdown("<h1>🎰 ヤマト トイレ掃除ガチャ 🎰</h1>", unsafe_allow_html=True)
st.markdown(f"<div class='date-display'>📅 {date.today().strftime('%Y年%m月%d日')}</div>", unsafe_allow_html=True)

st.markdown("---")

# セッション初期化
if "absent" not in st.session_state:
    st.session_state.absent = []
if "results" not in st.session_state:
    st.session_state.results = None
if "show_gacha" not in st.session_state:
    st.session_state.show_gacha = False

# 不在者チェック
with st.expander("👥 本日の不在者チェック", expanded=False):
    st.markdown("**出張・休暇の人にチェック**")
    absent = []
    men = get_members("M")
    women = get_members("F")

    st.markdown("### 🚹 男性")
    cols = st.columns(4)
    for i, name in enumerate(men):
        if cols[i % 4].checkbox(name, key=f"abs_m_{name}"):
            absent.append(name)

    st.markdown("### 🚺 女子")
    cols = st.columns(4)
    for i, name in enumerate(women):
        if cols[i % 4].checkbox(name, key=f"abs_w_{name}"):
            absent.append(name)

    st.session_state.absent = absent
    if absent:
        st.info(f"本日の不在者: {len(absent)}名")

# ガチャボタン
if st.button("🎁 ガチャを回す！ 🎰", use_container_width=True):
    results = draw_all(st.session_state.absent)
    st.session_state.results = results
    st.session_state.show_gacha = True
    st.rerun()

# ガチャ演出
if st.session_state.show_gacha and st.session_state.results:
    results = st.session_state.results
    men_name = results.get("Men", "該当者なし")
    guest_name = results.get("Guest", "該当者なし")
    women_name = results.get("Women", "該当者なし")

    gacha_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{
            margin: 0;
            padding: 10px;
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            font-family: 'Hiragino Sans', 'Meiryo', sans-serif;
            overflow: hidden;
        }}
        .gacha-container {{
            display: flex;
            justify-content: center;
            align-items: flex-start;
            gap: 20px;
            padding: 10px;
            flex-wrap: nowrap;
        }}
        .machine {{
            width: 180px;
            text-align: center;
            position: relative;
        }}
        .dome {{
            width: 160px;
            height: 160px;
            margin: 0 auto;
            background: radial-gradient(circle at 30% 30%, rgba(255,255,255,0.4), rgba(255,255,255,0.1));
            border-radius: 50% 50% 10px 10px;
            position: relative;
            overflow: hidden;
            border: 3px solid rgba(255,255,255,0.3);
            box-shadow: 0 0 30px rgba(100,200,255,0.3), inset 0 0 20px rgba(255,255,255,0.2);
        }}
        .machine.men .dome {{ box-shadow: 0 0 30px #4a90e2, inset 0 0 20px rgba(255,255,255,0.2); border-color: #4a90e2; }}
        .machine.guest .dome {{ box-shadow: 0 0 30px #feca57, inset 0 0 20px rgba(255,255,255,0.2); border-color: #feca57; }}
        .machine.women .dome {{ box-shadow: 0 0 30px #ff6b9d, inset 0 0 20px rgba(255,255,255,0.2); border-color: #ff6b9d; }}
        .mini-cap {{
            width: 32px;
            height: 32px;
            border-radius: 50%;
            position: absolute;
            animation: shake 0.5s infinite;
        }}
        .mini-cap:nth-child(1) {{ background: #ff6b9d; top: 15px; left: 20px; animation-delay: 0s; }}
        .mini-cap:nth-child(2) {{ background: #c86dd7; top: 30px; right: 15px; animation-delay: 0.1s; }}
        .mini-cap:nth-child(3) {{ background: #feca57; bottom: 20px; left: 50px; animation-delay: 0.2s; }}
        .mini-cap:nth-child(4) {{ background: #48dbfb; bottom: 30px; right: 30px; animation-delay: 0.15s; }}
        .mini-cap:nth-child(5) {{ background: #1dd1a1; top: 60px; left: 60px; animation-delay: 0.25s; }}
        @keyframes shake {{
            0%, 100% {{ transform: translate(0,0); }}
            25% {{ transform: translate(5px,-5px); }}
            50% {{ transform: translate(-3px,3px); }}
            75% {{ transform: translate(3px,-3px); }}
        }}
        .body {{
            width: 160px;
            height: 100px;
            margin: 0 auto;
            border-radius: 10px;
            position: relative;
            margin-top: -5px;
        }}
        .machine.men .body {{ background: linear-gradient(145deg, #4a90e2, #2e5c99); }}
        .machine.guest .body {{ background: linear-gradient(145deg, #feca57, #c99830); }}
        .machine.women .body {{ background: linear-gradient(145deg, #ff6b9d, #c84177); }}
        .slot {{
            width: 60px;
            height: 20px;
            background: #222;
            border-radius: 5px;
            position: absolute;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
        }}
        .handle {{
            width: 40px;
            height: 40px;
            background: radial-gradient(circle at 30% 30%, #fff568, #d4a800);
            border-radius: 50%;
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            box-shadow: 0 2px 5px rgba(0,0,0,0.3);
            animation: rotate 1s linear infinite;
            animation-play-state: paused;
        }}
        .handle::after {{
            content: '';
            width: 4px;
            height: 20px;
            background: #333;
            position: absolute;
            top: 10px;
            left: 50%;
            transform: translateX(-50%);
            border-radius: 2px;
        }}
        .machine.rotating .handle {{ animation-play-state: running; }}
        .machine.shaking {{ animation: machine-shake 0.2s infinite; }}
        @keyframes rotate {{
            from {{ transform: translateX(-50%) rotate(0deg); }}
            to {{ transform: translateX(-50%) rotate(360deg); }}
        }}
        @keyframes machine-shake {{
            0%, 100% {{ transform: translate(0,0); }}
            25% {{ transform: translate(-3px, 2px); }}
            75% {{ transform: translate(3px, -2px); }}
        }}
        .capsule {{
            width: 55px;
            height: 55px;
            border-radius: 50%;
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) scale(0);
            opacity: 0;
            z-index: 10;
            box-shadow: 0 0 30px gold, inset -5px -8px 15px rgba(0,0,0,0.3), inset 8px 8px 15px rgba(255,255,255,0.4);
        }}
        .machine.men .capsule {{
            background: linear-gradient(to bottom, rgba(255,255,255,0.5) 0%, rgba(255,255,255,0.3) 48%, #4a90e2 52%, #2e5c99 100%);
            border: 2px solid rgba(255,255,255,0.6);
        }}
        .machine.guest .capsule {{
            background: linear-gradient(to bottom, rgba(255,255,255,0.5) 0%, rgba(255,255,255,0.3) 48%, #feca57 52%, #c99830 100%);
            border: 2px solid rgba(255,255,255,0.6);
        }}
        .machine.women .capsule {{
            background: linear-gradient(to bottom, rgba(255,255,255,0.5) 0%, rgba(255,255,255,0.3) 48%, #ff6b9d 52%, #c84177 100%);
            border: 2px solid rgba(255,255,255,0.6);
        }}
        .machine.drop .capsule {{
            animation: drop 1s ease-in forwards;
        }}
        @keyframes drop {{
            0% {{ transform: translate(-50%, -200px) scale(1); opacity: 1; }}
            70% {{ transform: translate(-50%, 65px) scale(1); opacity: 1; }}
            85% {{ transform: translate(-50%, 50px) scale(1); opacity: 1; }}
            100% {{ transform: translate(-50%, 65px) scale(1.05); opacity: 1; }}
        }}
        .winner {{
            margin-top: 95px;
            background: white;
            border-radius: 10px;
            padding: 10px 8px;
            font-weight: bold;
            opacity: 0;
            transform: scale(0.5);
            transition: all 0.5s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            position: relative;
            z-index: 5;
        }}
        .machine.show-winner .winner {{
            opacity: 1;
            transform: scale(1);
        }}
        .role-label {{
            font-size: 0.9em;
            color: #666;
            margin-bottom: 5px;
        }}
        .winner-name {{
            font-size: 1.4em;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .machine.men .winner-name {{ color: #4a90e2; }}
        .machine.guest .winner-name {{ color: #c99830; }}
        .machine.women .winner-name {{ color: #ff6b9d; }}

        /* ========== スマホ対応 ========== */
        @media (max-width: 600px) {{
            body {{ padding: 2px; }}
            .gacha-container {{
                gap: 5px;
                padding: 2px;
            }}
            .machine {{ width: 110px; }}
            .dome {{
                width: 95px;
                height: 95px;
            }}
            .mini-cap {{ width: 20px; height: 20px; }}
            .mini-cap:nth-child(1) {{ top: 10px; left: 10px; }}
            .mini-cap:nth-child(2) {{ top: 20px; right: 8px; }}
            .mini-cap:nth-child(3) {{ bottom: 12px; left: 30px; }}
            .mini-cap:nth-child(4) {{ bottom: 18px; right: 18px; }}
            .mini-cap:nth-child(5) {{ top: 40px; left: 40px; }}
            .body {{
                width: 95px;
                height: 65px;
            }}
            .slot {{
                width: 40px;
                height: 14px;
                top: 12px;
            }}
            .handle {{
                width: 26px;
                height: 26px;
                bottom: 12px;
            }}
            .handle::after {{
                width: 3px;
                height: 13px;
                top: 6px;
            }}
            .capsule {{
                width: 38px;
                height: 38px;
            }}
            @keyframes drop {{
                0% {{ transform: translate(-50%, -120px) scale(1); opacity: 1; }}
                70% {{ transform: translate(-50%, 40px) scale(1); opacity: 1; }}
                85% {{ transform: translate(-50%, 32px) scale(1); opacity: 1; }}
                100% {{ transform: translate(-50%, 40px) scale(1.05); opacity: 1; }}
            }}
            .winner {{
                margin-top: 65px;
                padding: 6px 4px;
            }}
            .role-label {{ font-size: 0.7em; }}
            .winner-name {{ font-size: 1em; }}
        }}
    </style>
    </head>
    <body>
        <div class="gacha-container">
            <div class="machine men" id="m-men">
                <div class="dome">
                    <div class="mini-cap"></div>
                    <div class="mini-cap"></div>
                    <div class="mini-cap"></div>
                    <div class="mini-cap"></div>
                    <div class="mini-cap"></div>
                </div>
                <div class="body">
                    <div class="slot"></div>
                    <div class="handle"></div>
                    <div class="capsule"></div>
                </div>
                <div class="winner">
                    <div class="role-label">🚹 男性トイレ</div>
                    <div class="winner-name">{men_name}</div>
                </div>
            </div>
            <div class="machine guest" id="m-guest">
                <div class="dome">
                    <div class="mini-cap"></div>
                    <div class="mini-cap"></div>
                    <div class="mini-cap"></div>
                    <div class="mini-cap"></div>
                    <div class="mini-cap"></div>
                </div>
                <div class="body">
                    <div class="slot"></div>
                    <div class="handle"></div>
                    <div class="capsule"></div>
                </div>
                <div class="winner">
                    <div class="role-label">🚻 ゲストトイレ</div>
                    <div class="winner-name">{guest_name}</div>
                </div>
            </div>
            <div class="machine women" id="m-women">
                <div class="dome">
                    <div class="mini-cap"></div>
                    <div class="mini-cap"></div>
                    <div class="mini-cap"></div>
                    <div class="mini-cap"></div>
                    <div class="mini-cap"></div>
                </div>
                <div class="body">
                    <div class="slot"></div>
                    <div class="handle"></div>
                    <div class="capsule"></div>
                </div>
                <div class="winner">
                    <div class="role-label">🚺 女子トイレ</div>
                    <div class="winner-name">{women_name}</div>
                </div>
            </div>
        </div>
        <script>
            const machines = ['m-men', 'm-guest', 'm-women'];
            setTimeout(() => {{
                machines.forEach(id => document.getElementById(id).classList.add('rotating', 'shaking'));
            }}, 300);
            setTimeout(() => {{
                machines.forEach(id => {{
                    const m = document.getElementById(id);
                    m.classList.remove('rotating', 'shaking');
                    m.classList.add('drop');
                }});
            }}, 3000);
            setTimeout(() => {{
                machines.forEach(id => document.getElementById(id).classList.add('show-winner'));
            }}, 4200);
        </script>
    </body>
    </html>
    """
    components.html(gacha_html, height=450)

    # 結果カード
    st.markdown("### 🎉 本日の掃除担当")
    c1, c2, c3 = st.columns(3)
    c1.markdown(f"<div class='winner-card role-men'><div>🚹 男性トイレ</div><h2>{men_name}</h2></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='winner-card role-guest'><div>🚻 ゲストトイレ</div><h2>{guest_name}</h2></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='winner-card role-women'><div>🚺 女子トイレ</div><h2>{women_name}</h2></div>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🔄 引き直す", use_container_width=True):
            results = draw_all(st.session_state.absent)
            st.session_state.results = results
            st.rerun()
    with col_b:
        if st.button("✅ この結果で確定！", use_container_width=True):
            for role, name in results.items():
                save_result(role, name)
            st.success("保存しました！お疲れさまでした🎉")
            st.session_state.show_gacha = False
            st.session_state.results = None
            time.sleep(2)
            st.rerun()

st.markdown("---")

# 履歴
with st.expander("📋 直近7日の履歴"):
    history = get_history(7)
    if history:
        for h in history:
            st.write(f"**{h['date']}** 🚹{h.get('Men','-')} / 🚻{h.get('Guest','-')} / 🚺{h.get('Women','-')}")
    else:
        st.write("履歴なし")

# 管理メニュー
with st.expander("⚙️ 管理メニュー"):
    if st.button("🔄 全周リセット"):
        reset_round()
        st.success("リセット完了！")
        st.rerun()
