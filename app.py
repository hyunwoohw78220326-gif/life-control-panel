import streamlit as st
from datetime import datetime, timedelta
import pytz
import streamlit.components.v1 as components

# ===========================
# KST 시간 설정
# ===========================
KST = pytz.timezone("Asia/Seoul")

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

# ===========================
# 페이지 이동 함수
# ===========================
def go_to(page_name):
    st.session_state.page = page_name

# ===========================
# 로비 화면
# ===========================
if st.session_state.page == "lobby":
    st.title("인생 제어판")
    st.subheader("노력은 나를 배신하지 않는다")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("🎯 목표"):
            go_to("goals")
    with col2:
        if st.button("📋 할 일"):
            go_to("todos")
    with col3:
        if st.button("⏱ 타이머"):
            go_to("timer")
    with col4:
        if st.button("💸 돈"):
            go_to("money")
    with col5:
        if st.button("📝 메모장"):
            go_to("notes")

# ===========================
# 목표 관리
# ===========================
elif st.session_state.page == "goals":
    st.header("🎯 목표 관리")
    goal_input = st.text_input("목표 입력")
    if st.button("추가"):
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
        st.experimental_rerun()
    
    if st.button("⬅ 로비로"):
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
            amount = st.number_input("금액", min_value=0, value=0)
        with col2:
            type_ = st.radio("종류", ["지출", "수입"])
        item = st.text_input("내용")
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

    if st.button("⬅ 로비로"):
        go_to("lobby")

# ===========================
# 할 일 관리
# ===========================
elif st.session_state.page == "todos":
    st.header("📋 할 일 관리")

    todo_input = st.text_input("할 일 입력")
    deadline = st.time_input("마감 시간 설정 (오늘)", value=datetime.now(KST).time())
    if st.button("추가"):
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
                    st.info(f"남은 시간: {remain.seconds//3600}시간 {remain.seconds//60%60}분")
            if st.button("삭제", key=f"del_todo_{i}"):
                to_delete_todo = i
    if to_delete_todo is not None:
        st.session_state.todos.pop(to_delete_todo)
        st.experimental_rerun()
    
    if st.button("⬅ 로비로"):
        go_to("lobby")

# ===========================
# 메모장
# ===========================
elif st.session_state.page == "notes":
    st.header("📝 메모장")
    if "notes" not in st.session_state:
        st.session_state.notes = ""
    new_notes = st.text_area("메모 입력", st.session_state.notes)
    st.session_state.notes = new_notes

    if st.button("⬅ 로비로"):
        go_to("lobby")

# ===========================
# 타이머
# ===========================
elif st.session_state.page == "timer":
    st.header("⏱ 집중 타이머")
    
    minutes = st.number_input("시간(분)", 1, 180, 25)
    if st.button("타이머 시작"):
        st.session_state.timer_running = True
        st.session_state.timer_end_time = datetime.now(KST) + timedelta(minutes=minutes)

    if st.session_state.timer_running and st.session_state.timer_end_time:
        now = datetime.now(KST)
        remaining = st.session_state.timer_end_time - now
        total_seconds = int(remaining.total_seconds())

        if total_seconds <= 0:
            st.session_state.timer_running = False
            st.success("⏰ 타이머 종료!")

            # 브라우저 소리 알람
            components.html("""
            <audio autoplay>
              <source src="https://www.soundjay.com/button/beep-07.mp3" type="audio/mpeg">
            </audio>
            """)
        else:
            minutes_left = total_seconds // 60
            seconds_left = total_seconds % 60
            st.warning(f"남은 시간: {minutes_left}분 {seconds_left}초")

    if st.button("⬅ 로비로"):
        st.session_state.timer_running = False
        go_to("lobby")

