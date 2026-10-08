import streamlit as st
import streamlit.components.v1 as components
from datetime import date
import time
from database import init_db, get_members, get_round_counts, save_result, get_history, reset_round
from gacha import draw_all

st.set_page_config(page_title="ヤマト トイレ掃除ガチャ", page_icon="🎰", layout="wide")

# DB初期化
init_db()

# カスタムCSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #ffe4ec 0%, #fff8d6 50%, #e8d5ff 100%);
    }
    h1 {
        text-align: center;
        background: linear-gradient(90deg, #ff6b9d, #feca57, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
    }
    .stButton>button {
        background: linear-gradient(90deg, #ff6b9d, #a855f7);
        color: white;
        font-weight: bold;
        border-radius: 25px;
        border: none;
        padding: 12px 30px;
        font-size: 18px;
        width: 100%;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #feca57, #ff6b9d);
        transform: scale(1.02);
    }
    .winner-card {
        background: white;
        border-radius: 20px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        margin: 10px 0;
        min-height: 160px;
    }
    .winner-card h2 {
        font-size: 24px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .role-men { border-top: 6px solid #4a90e2; }
    .role-guest { border-top: 6px solid #feca57; }
    .role-women { border-top: 6px solid #ff6b9d; }
        /* チェックボックスの文字を大きく */
    .stCheckbox label p {
        font-size: 20px !important;
        font-weight: bold !important;
    }
    .stCheckbox label {
        padding: 8px 0 !important;
    }

</style>
""", unsafe_allow_html=True)

st.title("🎰 ヤマト トイレ掃除ガチャ 🎰")
st.markdown(f"<p style='text-align:center; font-size:18px;'>📅 {date.today().strftime('%Y年%m月%d日')}</p>", unsafe_allow_html=True)

# 進捗表示
men_done, men_total = get_round_counts("Men")
guest_done, guest_total = get_round_counts("Guest")
women_done, women_total = get_round_counts("Women")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("🚹 男性", f"{men_done}/{men_total}")
with col2:
    st.metric("🚻 ゲスト", f"{guest_done}/{guest_total}")
with col3:
    st.metric("🚺 女子", f"{women_done}/{women_total}")

st.divider()

# セッション初期化
if "absent" not in st.session_state:
    st.session_state.absent = []
if "results" not in st.session_state:
    st.session_state.results = None
if "show_gacha" not in st.session_state:
    st.session_state.show_gacha = False

# 不在者チェック
with st.expander("👥 本日の不在者チェック", expanded=False):
    st.markdown("##### 🚹 男性")
    men = get_members("M")
    cols = st.columns(4)
    absent_men = []
    for i, name in enumerate(men):
        with cols[i % 4]:
            if st.checkbox(name, key=f"abs_m_{name}"):
                absent_men.append(name)

    st.markdown("##### 🚺 女子")
    women = get_members("F")
    cols = st.columns(4)
    absent_women = []
    for i, name in enumerate(women):
        with cols[i % 4]:
            if st.checkbox(name, key=f"abs_w_{name}"):
                absent_women.append(name)

    st.session_state.absent = absent_men + absent_women
    st.info(f"🍡 本日の不在者: {len(st.session_state.absent)}名")

st.divider()

# ガチャボタン
if st.button("🎁 ガチャを回す！ 🎰", key="gacha_btn"):
    results = draw_all(st.session_state.absent)
    st.session_state.results = results
    st.session_state.show_gacha = True
    st.rerun()

# ガチャ演出＆結果表示
if st.session_state.show_gacha and st.session_state.results:
    results = st.session_state.results
    men_name = results.get("Men") or "なし"
    guest_name = results.get("Guest") or "なし"
    women_name = results.get("Women") or "なし"

    gacha_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            font-family: 'Arial Black', sans-serif;
            overflow: hidden;
        }}
        .stage {{
            display: flex;
            justify-content: space-around;
            align-items: flex-end;
            min-height: 500px;
            position: relative;
        }}
        .machine {{
            position: relative;
            width: 220px;
            height: 340px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        .top-dome {{
            width: 180px;
            height: 180px;
            border-radius: 50% 50% 10% 10%;
            background: radial-gradient(circle at 30% 30%, rgba(255,255,255,0.6), rgba(255,255,255,0.1));
            border: 4px solid gold;
            position: relative;
            overflow: hidden;
            box-shadow: inset 0 0 30px rgba(255,255,255,0.3), 0 0 20px rgba(255,215,0,0.5);
        }}
        .machine.men .top-dome {{ border-color: #4a90e2; box-shadow: inset 0 0 30px rgba(74,144,226,0.3), 0 0 25px rgba(74,144,226,0.8); }}
        .machine.guest .top-dome {{ border-color: #feca57; box-shadow: inset 0 0 30px rgba(254,202,87,0.3), 0 0 25px rgba(254,202,87,0.8); }}
        .machine.women .top-dome {{ border-color: #ff6b9d; box-shadow: inset 0 0 30px rgba(255,107,157,0.3), 0 0 25px rgba(255,107,157,0.8); }}

        .capsules {{
            position: absolute;
            width: 100%;
            height: 100%;
            top: 0;
            left: 0;
        }}
        .mini-cap {{
            position: absolute;
            width: 28px;
            height: 28px;
            border-radius: 50%;
            animation: bounce 1.5s infinite ease-in-out;
        }}
        .mini-cap:nth-child(1) {{ top: 18%; left: 12%; background: #ff6b9d; animation-delay: 0s; }}
        .mini-cap:nth-child(2) {{ top: 38%; left: 55%; background: #feca57; animation-delay: 0.2s; }}
        .mini-cap:nth-child(3) {{ top: 58%; left: 20%; background: #4a90e2; animation-delay: 0.4s; }}
        .mini-cap:nth-child(4) {{ top: 28%; left: 65%; background: #a855f7; animation-delay: 0.6s; }}
        .mini-cap:nth-child(5) {{ top: 55%; left: 48%; background: #4ecdc4; animation-delay: 0.8s; }}

        @keyframes bounce {{
            0%, 100% {{ transform: translateY(0); }}
            50% {{ transform: translateY(-10px); }}
        }}

        .body {{
            width: 190px;
            height: 110px;
            background: linear-gradient(180deg, #e74c3c, #c0392b);
            margin-top: -5px;
            border-radius: 5px;
            position: relative;
            box-shadow: 0 5px 15px rgba(0,0,0,0.5);
        }}
        .machine.men .body {{ background: linear-gradient(180deg, #3498db, #2980b9); }}
        .machine.guest .body {{ background: linear-gradient(180deg, #f39c12, #e67e22); }}
        .machine.women .body {{ background: linear-gradient(180deg, #e91e63, #c2185b); }}

        .handle {{
            position: absolute;
            width: 50px;
            height: 50px;
            background: radial-gradient(circle, #ffd700, #b8860b);
            border-radius: 50%;
            top: 30px;
            left: 50%;
            transform: translateX(-50%);
            border: 3px solid #333;
            animation: spin 0.3s linear infinite;
            animation-play-state: paused;
        }}
        .handle::before {{
            content: '';
            position: absolute;
            width: 8px;
            height: 25px;
            background: #333;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            border-radius: 4px;
        }}
        .spinning .handle {{ animation-play-state: running; }}

        @keyframes spin {{
            0% {{ transform: translateX(-50%) rotate(0deg); }}
            100% {{ transform: translateX(-50%) rotate(360deg); }}
        }}

        .slot {{
            width: 70px;
            height: 22px;
            background: #000;
            margin: 10px auto;
            border-radius: 3px;
        }}

        .capsule {{
            position: absolute;
            width: 85px;
            height: 85px;
            border-radius: 50%;
            left: 50%;
            top: 240px;
            transform: translateX(-50%) scale(0);
            opacity: 0;
            z-index: 10;
            background: linear-gradient(180deg, #fff 0%, #fff 48%, #ff6b9d 52%, #ff6b9d 100%);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3), inset 0 -5px 10px rgba(0,0,0,0.2);
        }}
        .machine.men .capsule {{ background: linear-gradient(180deg, #fff 0%, #fff 48%, #4a90e2 52%, #4a90e2 100%); }}
        .machine.guest .capsule {{ background: linear-gradient(180deg, #fff 0%, #fff 48%, #feca57 52%, #feca57 100%); }}

        .dropping .capsule {{
            animation: drop 1s ease-out forwards;
        }}
        @keyframes drop {{
            0% {{ transform: translateX(-50%) translateY(-100px) scale(0.5); opacity: 0; }}
            60% {{ transform: translateX(-50%) translateY(20px) scale(1); opacity: 1; }}
            80% {{ transform: translateX(-50%) translateY(0) scale(1.1); opacity: 1; }}
            100% {{ transform: translateX(-50%) translateY(10px) scale(1); opacity: 1; }}
        }}

        .opened .capsule {{
            animation: open 0.5s ease-out forwards;
        }}
        @keyframes open {{
            0% {{ transform: translateX(-50%) scale(1); }}
            50% {{ transform: translateX(-50%) scale(1.6); }}
            100% {{ transform: translateX(-50%) scale(0); opacity: 0; }}
        }}

        .winner {{
            position: absolute;
            left: 50%;
            top: 180px;
            transform: translateX(-50%) scale(0);
            background: linear-gradient(135deg, #ffd700, #ff6b9d);
            color: white;
            padding: 15px 25px;
            border-radius: 15px;
            font-size: 22px;
            font-weight: 900;
            white-space: nowrap;
            box-shadow: 0 0 30px rgba(255,215,0,0.8);
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            z-index: 20;
            opacity: 0;
        }}
        .machine.men .winner {{ background: linear-gradient(135deg, #4a90e2, #2980b9); }}
        .machine.guest .winner {{ background: linear-gradient(135deg, #feca57, #e67e22); }}
        .machine.women .winner {{ background: linear-gradient(135deg, #ff6b9d, #c2185b); }}

        .reveal .winner {{
            animation: reveal 0.6s ease-out forwards;
        }}
        @keyframes reveal {{
            0% {{ transform: translateX(-50%) scale(0) rotate(-180deg); opacity: 0; }}
            60% {{ transform: translateX(-50%) scale(1.3) rotate(10deg); opacity: 1; }}
            100% {{ transform: translateX(-50%) scale(1) rotate(0deg); opacity: 1; }}
        }}

        .label {{
            color: white;
            font-size: 14px;
            margin-top: 10px;
            text-align: center;
            text-shadow: 0 2px 4px rgba(0,0,0,0.5);
        }}

        .confetti {{
            position: absolute;
            width: 10px;
            height: 10px;
            opacity: 0;
            top: 200px;
            left: 50%;
        }}
        .reveal .confetti {{
            animation: confetti-fall 1.5s ease-out forwards;
        }}
        @keyframes confetti-fall {{
            0% {{ transform: translate(0, 0) rotate(0deg); opacity: 1; }}
            100% {{ transform: translate(var(--x), var(--y)) rotate(720deg); opacity: 0; }}
        }}

        .sparkle {{
            position: absolute;
            width: 25px;
            height: 25px;
            background: radial-gradient(circle, #fff, transparent);
            border-radius: 50%;
            opacity: 0;
        }}
        .reveal .sparkle {{
            animation: sparkle 1s ease-out forwards;
        }}
        @keyframes sparkle {{
            0% {{ transform: scale(0); opacity: 1; }}
            100% {{ transform: scale(3); opacity: 0; }}
        }}

        .shake {{
            animation: shake 0.1s infinite;
        }}
        @keyframes shake {{
            0%, 100% {{ transform: translateX(0); }}
            25% {{ transform: translateX(-3px); }}
            75% {{ transform: translateX(3px); }}
        }}
    </style>
    </head>
    <body>
        <div class="stage">
            <div class="machine men" id="m1">
                <div class="top-dome">
                    <div class="capsules">
                        <div class="mini-cap"></div><div class="mini-cap"></div>
                        <div class="mini-cap"></div><div class="mini-cap"></div>
                        <div class="mini-cap"></div>
                    </div>
                </div>
                <div class="body">
                    <div class="handle"></div>
                    <div class="slot"></div>
                </div>
                <div class="capsule"></div>
                <div class="winner">🚹 {men_name}</div>
                <div class="label">男性トイレ</div>
                <div class="confetti" style="--x:-80px; --y:150px; background:#ff6b9d;"></div>
                <div class="confetti" style="--x:80px; --y:150px; background:#feca57;"></div>
                <div class="confetti" style="--x:-50px; --y:180px; background:#4ecdc4;"></div>
                <div class="confetti" style="--x:50px; --y:180px; background:#a855f7;"></div>
                <div class="sparkle" style="top:150px; left:30%;"></div>
                <div class="sparkle" style="top:150px; left:70%;"></div>
            </div>

            <div class="machine guest" id="m2">
                <div class="top-dome">
                    <div class="capsules">
                        <div class="mini-cap"></div><div class="mini-cap"></div>
                        <div class="mini-cap"></div><div class="mini-cap"></div>
                        <div class="mini-cap"></div>
                    </div>
                </div>
                <div class="body">
                    <div class="handle"></div>
                    <div class="slot"></div>
                </div>
                <div class="capsule"></div>
                <div class="winner">🚻 {guest_name}</div>
                <div class="label">ゲストトイレ</div>
                <div class="confetti" style="--x:-80px; --y:150px; background:#ff6b9d;"></div>
                <div class="confetti" style="--x:80px; --y:150px; background:#feca57;"></div>
                <div class="confetti" style="--x:-50px; --y:180px; background:#4ecdc4;"></div>
                <div class="confetti" style="--x:50px; --y:180px; background:#a855f7;"></div>
                <div class="sparkle" style="top:150px; left:30%;"></div>
                <div class="sparkle" style="top:150px; left:70%;"></div>
            </div>

            <div class="machine women" id="m3">
                <div class="top-dome">
                    <div class="capsules">
                        <div class="mini-cap"></div><div class="mini-cap"></div>
                        <div class="mini-cap"></div><div class="mini-cap"></div>
                        <div class="mini-cap"></div>
                    </div>
                </div>
                <div class="body">
                    <div class="handle"></div>
                    <div class="slot"></div>
                </div>
                <div class="capsule"></div>
                <div class="winner">🚺 {women_name}</div>
                <div class="label">女子トイレ</div>
                <div class="confetti" style="--x:-80px; --y:150px; background:#ff6b9d;"></div>
                <div class="confetti" style="--x:80px; --y:150px; background:#feca57;"></div>
                <div class="confetti" style="--x:-50px; --y:180px; background:#4ecdc4;"></div>
                <div class="confetti" style="--x:50px; --y:180px; background:#a855f7;"></div>
                <div class="sparkle" style="top:150px; left:30%;"></div>
                <div class="sparkle" style="top:150px; left:70%;"></div>
            </div>
        </div>

        <script>
            const machines = ['m1', 'm2', 'm3'];
            setTimeout(() => {{
                machines.forEach(id => document.getElementById(id).classList.add('spinning'));
            }}, 300);

            setTimeout(() => {{
                machines.forEach(id => document.getElementById(id).classList.add('shake'));
            }}, 3000);

            setTimeout(() => {{
                machines.forEach(id => {{
                    const m = document.getElementById(id);
                    m.classList.remove('spinning', 'shake');
                    m.classList.add('dropping');
                }});
            }}, 3800);

            setTimeout(() => {{
                machines.forEach(id => {{
                    const m = document.getElementById(id);
                    m.classList.remove('dropping');
                    m.classList.add('opened', 'reveal');
                }});
            }}, 5000);
        </script>
    </body>
    </html>
    """
    components.html(gacha_html, height=550)

    st.markdown("### 🏆 本日の勇者たち")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='winner-card role-men'><h4>🚹 男性</h4><h2>{men_name}</h2></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='winner-card role-guest'><h4>🚻 ゲスト</h4><h2>{guest_name}</h2></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='winner-card role-women'><h4>🚺 女子</h4><h2>{women_name}</h2></div>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🔄 引き直す"):
            results = draw_all(st.session_state.absent)
            st.session_state.results = results
            st.rerun()
    with col_b:
        if st.button("✅ この結果で確定！"):
            save_result(st.session_state.results)
            st.success("🎉 記録しました！今日もキレイにお願いします〜✨")
            st.session_state.results = None
            st.session_state.show_gacha = False
            time.sleep(2)
            st.rerun()

st.divider()

# 履歴表示
with st.expander("📋 直近7日の履歴"):
    history = get_history(7)
    if history:
        current_date = None
        for d, role, name in history:
            if d != current_date:
                st.markdown(f"**📅 {d}**")
                current_date = d
            emoji = {"Men": "🚹", "Guest": "🚻", "Women": "🚺"}
            st.markdown(f"　{emoji[role]} {role}: {name}")
    else:
        st.info("まだ履歴がありません")

# 管理メニュー
with st.expander("⚙️ 管理メニュー"):
    st.warning("⚠️ リセット操作は慎重に！")
    if st.button("🔄 全周リセット（当選済みを全部クリア）"):
        reset_round()
        st.success("リセットしました")
        st.rerun()
