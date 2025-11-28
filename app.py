import streamlit as st
from datetime import datetime, timedelta
import pytz 
import time
import streamlit.components.v1 as components

# ===========================
# KST 시간 설정 (pytz 유지)
# ===========================
KST = pytz.timezone("Asia/Seoul")

st.set_page_config(page_title="인생 제어판", layout="wide")

# ===========================
# 세션 상태 초기화
# ===========================
if "page" not in st.session_state:
    st.session_state.page = "lobby"

if "goals" not in st.session_state:
    st.session_state.goals = []

if "balance" not in st.session_state:
    st.session_state.balance = 0
if "transactions" not in st.session_state:
    st.session_state.transactions = []

if "todos" not in st.session_state:
    st.session_state.todos = []

if "notes" not in st.session_state:
    st.session_state.notes = ""

if "timer_running" not in st.session_state:
    st.session_state.timer_running = False
    st.session_state.timer_end_time = None
if "timer_finished" not in st.session_state:
    st.session_state.timer_finished = False

# ===========================
# 페이지 이동 함수
# ===========================
def go_to(page_name):
    st.session_state.page = page_name

# 타이머 상태 초기화 함수
def reset_timer_state():
    st.session_state.timer_running = False
    st.session_state.timer_end_time = None
    st.session_state.timer_finished = False

# ===========================
# 로비 화면
# ===========================
if st.session_state.page == "lobby":
    st.title("인생 제어판")
    st.subheader("노력은 나를 배신하지 않는다")
    
    # Key 추가하여 위젯 충돌 방지
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("🎯 목표", key="btn_lobby_goals"): 
            go_to("goals")
    with col2:
        if st.button("📋 할 일", key="btn_lobby_todos"): 
            go_to("todos")
    with col3:
        if st.button("⏱ 타이머", key="btn_lobby_timer"): 
            go_to("timer")
    with col4:
        if st.button("💸 돈", key="btn_lobby_money"): 
            go_to("money")
    with col5:
        if st.button("📝 메모장", key="btn_lobby_notes"): 
            go_to("notes")

# ===========================
# 목표 관리
# ===========================
elif st.session_state.page == "goals":
    st.header("🎯 목표 관리")
    goal_input = st.text_input("목표 입력", key="goal_input") # Key 추가
    if st.button("추가", key="add_goal_btn"): # Key 추가
        if goal_input:
            st.session_state.goals.append({"goal": goal_input, "done": False})
    
    to_delete_goal = None
    for i, g in enumerate(st.session_state.goals):
        col1, col2, col3 = st.columns([0.1,0.7,0.2])
        with col1:
            g["done"] = st.checkbox("", key=f"goal_{i}", value=g["done"])
        with col2:
            st.write(("~~" if g["done"] else "") + g["goal"] + ("~~" if g["done"] else ""))
        with col3:
            if st.button("삭제", key=f"del_goal_{i}"):
                to_delete_goal = i
    if to_delete_goal is not None:
        st.session_state.goals.pop(to_delete_goal)
        st.rerun() # st.experimental_rerun() -> st.rerun() 변경
    
    if st.button("⬅ 로비로", key="go_lobby_goals"): # Key 추가
        go_to("lobby")

# ===========================
# 돈 관리
# ===========================
elif st.session_state.page == "money":
    st.header("💸 돈 관리")
    st.write(f"💰 현재 잔액: {st.session_state.balance:,}원")

    with st.form("money_form"):
        col1, col2 = st.columns(2)
        with col1:
            amount = st.number_input("금액", min_value=0, value=0, key="money_amount_input") # Key 추가
        with col2:
            type_ = st.radio("종류", ["지출", "수입"], key="money_type_radio") # Key 추가
        item = st.text_input("내용", key="money_item_input") # Key 추가
        submitted = st.form_submit_button("기록")

    if submitted and item and amount > 0:
        if type_ == "지출":
            st.session_state.balance -= amount
        else:
            st.session_state.balance += amount
        st.session_state.transactions.append({
            "item": item,
            "amount": amount,
            "type": type_,
            "time": datetime.now(KST).strftime("%Y-%m-%d %H:%M")
        })
        st.success("기록 완료!")

    st.subheader("거래 내역")
    for t in reversed(st.session_state.transactions):
        sign = "-" if t["type"]=="지출" else "+"
        st.write(f"{t['time']} | {t['item']} | {sign}{t['amount']:,}원")

    if st.button("⬅ 로비로", key="go_lobby_money"): # Key 추가
        go_to("lobby")

# ===========================
# 할 일 관리
# ===========================
elif st.session_state.page == "todos":
    st.header("📋 할 일 관리")

    todo_input = st.text_input("할 일 입력", key="todo_input") # Key 추가
    deadline = st.time_input("마감 시간 설정 (오늘)", value=datetime.now(KST).time(), key="todo_deadline_input") # Key 추가
    if st.button("추가", key="add_todo_btn"): # Key 추가
        if todo_input:
            st.session_state.todos.append({
                "task": todo_input,
                "deadline": deadline,
                "done": False
            })
    
    now = datetime.now(KST)
    to_delete_todo = None
    for i, t in enumerate(st.session_state.todos):
        col1, col2, col3 = st.columns([0.1,0.6,0.3])
        with col1:
            t["done"] = st.checkbox("", key=f"todo_{i}", value=t["done"])
        with col2:
            st.write(("~~" if t["done"] else "") + t["task"] + ("~~" if t["done"] else ""))
        with col3:
            deadline_dt = datetime.combine(now.date(), t["deadline"], tzinfo=KST) 
            if not t["done"]:
                if now > deadline_dt:
                    st.error("⛔ 마감 지남! 얼른 하자!")
                else:
                    remain = deadline_dt - now
                    if remain.total_seconds() > 0:
                         st.info(f"남은 시간: {int(remain.total_seconds()//3600)}시간 {int(remain.total_seconds()//60%60)}분")
                    else:
                        st.error("⛔ 마감 지남! 얼른 하자!")
            if st.button("삭제", key=f"del_todo_{i}"):
                to_delete_todo = i
    if to_delete_todo is not None:
        st.session_state.todos.pop(to_delete_todo)
        st.rerun() # st.experimental_rerun() -> st.rerun() 변경
    
    if st.button("⬅ 로비로", key="go_lobby_todos"): # Key 추가
        go_to("lobby")

# ===========================
# 메모장
# ===========================
elif st.session_state.page == "notes":
    st.header("📝 메모장")
    new_notes = st.text_area("메모 입력", st.session_state.notes, key="notes_area") # Key 추가
    st.session_state.notes = new_notes

    if st.button("⬅ 로비로", key="go_lobby_notes"): # Key 추가
        go_to("lobby")

# ===========================
# ⏱ 타이머 (개선된 디자인 및 기능)
# ===========================
elif st.session_state.page == "timer":
    st.header("⏱ 집중 타이머")
    
    # ---------------------------
    # 1. 설정 및 시간 계산
    # ---------------------------
    
    # 타이머 설정 (시간(분) 입력)
    minutes = st.number_input(
        "타이머 설정 (분)", 
        min_value=1, 
        max_value=180, 
        value=st.session_state.get('timer_input_val', 25), 
        key="timer_input_val"
    )

    # 남은 시간 계산
    total_seconds = 0
    if st.session_state.timer_end_time is not None:
        now = datetime.now(KST)
        remaining = st.session_state.timer_end_time - now
        total_seconds = int(remaining.total_seconds())

    # 시간 종료 처리
    if total_seconds <= 0:
        total_seconds = 0
        if st.session_state.timer_running and not st.session_state.timer_finished:
            st.session_state.timer_running = False
            st.session_state.timer_finished = True
            st.success("⏰ 타이머 종료! 수고했어요!")
            components.html("""
                <audio autoplay>
                    <source src="https://www.soundjay.com/button/beep-07.mp3" type="audio/mpeg">
                </audio>
            """, height=0)

    hours_left = total_seconds // 3600
    minutes_left = (total_seconds % 3600) // 60
    seconds_left = total_seconds % 60
    
    # ---------------------------
    # 2. 타이머 디스플레이 (이미지 형태 구현)
    # ---------------------------

    display_time = f"{hours_left:02}:{minutes_left:02}:{seconds_left:02}"
    
    # 10초 미만일 때 빨간색으로 깜빡이도록 설정
    is_flashing = st.session_state.timer_running and total_seconds <= 10 and total_seconds > 0 and (total_seconds % 2 == 0)
    text_color = '#FF4B4B' if is_flashing else 'white'
    
    st.markdown(
        f"""
        <div style='
            background-color: black; 
            border-radius: 10px; 
            padding: 20px; 
            text-align: center;
            width: 80%;
            margin: 20px auto;
            box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
        '>
            <h1 style='
                color: {text_color}; 
                font-family: monospace; 
                font-size: 80px; 
                margin: 0;
            '>{display_time}</h1>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # ---------------------------
    # 3. 제어 버튼
    # ---------------------------

    col_reset, col_stsp = st.columns([1, 1])

    # 리셋 버튼
    with col_reset:
        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True) 
        if st.button("↩ RESET", key="reset_timer_btn_final", use_container_width=True):
            reset_timer_state()
            st.rerun() # st.experimental_rerun() -> st.rerun() 변경
            
    # START/STOP 버튼
    with col_stsp:
        # 실행 중일 때: STOP 버튼 표시
        if st.session_state.timer_running:
            if st.button("⏹ STOP", key="stop_timer_btn_final", type="secondary", use_container_width=True):
                st.session_state.timer_running = False
                st.session_state.last_paused_time = datetime.now(KST) 
                st.rerun() # st.experimental_rerun() -> st.rerun() 변경
        # 멈춤 상태일 때: START 버튼 표시
        else:
            if st.button("▶ START", key="start_timer_btn_final", type="primary", use_container_width=True, disabled=st.session_state.timer_finished):
                
                if st.session_state.timer_end_time is None or st.session_state.timer_finished:
                    # 새로 시작
                    st.session_state.timer_end_time = datetime.now(KST) + timedelta(minutes=minutes)
                else:
                    # 정지 상태에서 재개
                    remaining_paused_time = st.session_state.timer_end_time - st.session_state.last_paused_time
                    st.session_state.timer_end_time = datetime.now(KST) + remaining_paused_time
                    
                st.session_state.timer_running = True
                st.session_state.timer_finished = False
                st.rerun() # st.experimental_rerun() -> st.rerun() 변경
            
    # --- 타이머 업데이트 로직 ---
    # 타이머가 실행 중이라면 1초 후 페이지 새로고침 요청
    if st.session_state.timer_running and not st.session_state.timer_finished:
        time.sleep(1) 
        st.rerun() # st.experimental_rerun() -> st.rerun() 변경

    st.markdown("---")
    if st.button("⬅ 로비로", key="go_lobby_timer_final"): # Key 추가
        reset_timer_state()
        go_to("lobby")
