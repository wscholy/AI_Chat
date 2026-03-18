import streamlit as st
from anthropic import Anthropic

# ── 페이지 설정 ──────────────────────────────────────────────
st.set_page_config(
    page_title="수학 복습 챗봇 🔢",
    page_icon="📚",
    layout="centered",
)

# ── 시스템 프롬프트 ──────────────────────────────────────────
SYSTEM_PROMPT = """
당신은 초등학교 고학년(4~6학년) 학생들을 담당하는 친절하고 열정적인 기초학력 수학 강사입니다.

## 역할과 목표
- 학생이 틀린 수학 문제를 다시 이해하고 풀 수 있도록 도와주세요.
- 단순히 정답을 알려주는 것이 아니라, **왜 그렇게 되는지** 원리를 쉽게 설명해주세요.
- 학생이 스스로 생각하고 답을 찾을 수 있도록 **단계별 힌트**를 제공해주세요.

## 대화 방식
- 항상 따뜻하고 격려하는 말투를 사용하세요. (예: "잘했어!", "좋은 시도야!", "조금만 더 생각해볼까?")
- 어려운 수학 용어는 쉬운 말로 풀어서 설명하세요.
- 설명할 때는 구체적인 예시나 그림(이모지 활용)을 사용하세요.
- 한 번에 너무 많은 정보를 주지 말고, 작은 단계로 나누어 설명하세요.
- 학생이 이해했는지 확인하는 질문을 자주 하세요.

## 다루는 수학 영역 (초등 4~6학년)
- 큰 수와 자릿값
- 분수와 소수 (덧셈, 뺄셈, 곱셈, 나눗셈)
- 약수와 배수, 최대공약수, 최소공배수
- 도형 (넓이, 둘레, 부피)
- 비와 비율, 비례식
- 평균과 가능성
- 규칙과 대응
- 혼합 계산 (사칙연산 순서)

## 문제 복습 진행 순서
1. 학생이 어떤 문제를 틀렸는지 물어보세요.
2. 학생이 어떻게 풀었는지(오답 과정)를 물어보세요.
3. 어느 부분에서 헷갈렸는지 파악하세요.
4. 핵심 개념을 쉽게 다시 설명하세요.
5. 비슷한 예시 문제로 함께 연습하세요.
6. 학생 스스로 다시 풀어보도록 격려하세요.

## 주의사항
- 학생을 절대 무시하거나 답답해하는 표현을 사용하지 마세요.
- 틀려도 괜찮다는 것을 항상 강조하세요.
- 수학과 관련 없는 질문은 정중히 수학 공부로 돌아오도록 안내하세요.
- 정답을 바로 알려주기보다 학생이 스스로 발견하도록 유도하세요.

지금 바로 학생을 반갑게 맞이하고, 어떤 문제가 어려웠는지 물어보세요!
"""

# ── 초기 세션 상태 설정 ──────────────────────────────────────
def initialize_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "client" not in st.session_state:
        st.session_state.client = None
    if "api_key_confirmed" not in st.session_state:
        st.session_state.api_key_confirmed = False
    if "total_questions" not in st.session_state:
        st.session_state.total_questions = 0

initialize_session()

# ── 사이드바 ─────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ 설정")
    st.markdown("---")

    # API 키 입력
    st.subheader("🔑 API 키 입력")
    api_key = st.text_input(
        "Anthropic API Key",
        type="password",
        placeholder="sk-ant-...",
        help="Anthropic 콘솔에서 발급받은 API 키를 입력하세요.",
    )

    if api_key:
        if st.button("✅ API 키 확인", use_container_width=True):
            try:
                test_client = Anthropic(api_key=api_key)
                # 간단한 테스트 요청
                test_client.messages.create(
                    model="claude-sonnet-4-5",
                    max_tokens=10,
                    messages=[{"role": "user", "content": "안녕"}],
                )
                st.session_state.client = Anthropic(api_key=api_key)
                st.session_state.api_key_confirmed = True
                st.success("API 키가 확인되었습니다! 🎉")
            except Exception as e:
                st.error(f"API 키 오류: {str(e)}")
                st.session_state.api_key_confirmed = False

    st.markdown("---")

    # 학습 현황
    st.subheader("📊 오늘의 학습 현황")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("복습한 문제", f"{st.session_state.total_questions}개")
    with col2:
        st.metric("대화 수", f"{len(st.session_state.messages)}개")

    st.markdown("---")

    # 도움말
    st.subheader("💡 이렇게 사용하세요!")
    st.markdown("""
    1. 📝 **틀린 문제**를 입력하세요
    2. 🤔 **어떻게 풀었는지** 알려주세요
    3. 💬 선생님과 **함께 풀어봐요**
    4. ✅ **다시 도전**해보세요!
    """)

    st.markdown("---")

    # 대화 초기화
    if st.button("🔄 새로운 문제 시작", use_container_width=True):
        st.session_state.messages = []
        st.session_state.total_questions = 0
        st.rerun()

    # 다루는 영역
    with st.expander("📚 다룰 수 있는 수학 영역"):
        st.markdown("""
        - 분수 · 소수 계산
        - 약수 · 배수
        - 도형 (넓이, 부피)
        - 비와 비율
        - 혼합 계산
        - 규칙 찾기
        - 평균과 가능성
        """)

# ── 메인 화면 ─────────────────────────────────────────────────
st.title("📚 수학 복습 챗봇")
st.markdown(
    """
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 16px 20px; border-radius: 12px; margin-bottom: 20px;'>
        <h4 style='color: white; margin: 0;'>🏫 기초학력 수학 선생님과 함께하는 복습 시간!</h4>
        <p style='color: #e8d5ff; margin: 6px 0 0 0; font-size: 14px;'>
            틀린 문제도 괜찮아요. 함께 이해하면 다음엔 꼭 맞출 수 있어요! 💪
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# API 키 미입력 안내
if not st.session_state.api_key_confirmed:
    st.info("👈 왼쪽 사이드바에서 **Anthropic API 키**를 입력하고 확인 버튼을 눌러주세요!", icon="🔑")

    # 예시 안내 카드
    st.markdown("### 🌟 이런 것들을 도와줄 수 있어요!")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style='background:#fff3cd; padding:16px; border-radius:10px; text-align:center;'>
            <div style='font-size:32px'>➗</div>
            <b>분수 나눗셈</b><br>
            <small>왜 뒤집어서 곱할까요?</small>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style='background:#d4edda; padding:16px; border-radius:10px; text-align:center;'>
            <div style='font-size:32px'>📐</div>
            <b>도형 넓이</b><br>
            <small>공식이 헷갈려요!</small>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style='background:#d1ecf1; padding:16px; border-radius:10px; text-align:center;'>
            <div style='font-size:32px'>🔢</div>
            <b>약수와 배수</b><br>
            <small>최대공약수 찾기</small>
        </div>
        """, unsafe_allow_html=True)
    st.stop()

# ── 초기 인사 메시지 생성 ────────────────────────────────────
if st.session_state.api_key_confirmed and len(st.session_state.messages) == 0:
    with st.spinner("선생님이 준비 중이에요... 잠깐만요! 🙋"):
        try:
            response = st.session_state.client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=500,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": "안녕하세요! 수업 시작해요."}],
            )
            greeting = response.content[0].text
            st.session_state.messages.append(
                {"role": "assistant", "content": greeting}
            )
        except Exception as e:
            st.error(f"초기화 오류: {e}")

# ── 채팅 메시지 표시 ─────────────────────────────────────────
chat_container = st.container()

with chat_container:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            with st.chat_message("user", avatar="🧒"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("assistant", avatar="👩‍🏫"):
                st.markdown(msg["content"])

# ── 퀵 버튼 ─────────────────────────────────────────────────
if st.session_state.api_key_confirmed and len(st.session_state.messages) > 0:
    st.markdown("##### 💬 빠른 입력")
    qcol1, qcol2, qcol3, qcol4 = st.columns(4)
    quick_prompts = {
        "🔁 다시 설명해줘": "조금 더 쉽게 다시 설명해 줄 수 있어요?",
        "✏️ 예시 보여줘": "비슷한 예시 문제를 하나 더 보여주세요!",
        "✅ 이해했어요!": "이제 이해했어요! 감사합니다 선생님!",
        "🆕 새 문제 복습": "다른 틀린 문제도 같이 풀어봐요!",
    }
    buttons = list(quick_prompts.items())
    cols = [qcol1, qcol2, qcol3, qcol4]
    for col, (label, prompt) in zip(cols, buttons):
        with col:
            if st.button(label, use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.spinner("선생님이 답변 중..."):
                    try:
                        resp = st.session_state.client.messages.create(
                            model="claude-sonnet-4-5",
                            max_tokens=1024,
                            system=SYSTEM_PROMPT,
                            messages=st.session_state.messages,
                        )
                        answer = resp.content[0].text
                        st.session_state.messages.append(
                            {"role": "assistant", "content": answer}
                        )
                        st.session_state.total_questions += 1
                    except Exception as e:
                        st.error(f"오류 발생: {e}")
                st.rerun()

# ── 사용자 입력 ──────────────────────────────────────────────
if user_input := st.chat_input(
    "틀린 문제를 입력하거나, 궁금한 점을 물어보세요! 😊",
    disabled=not st.session_state.api_key_confirmed,
):
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": user_input})

    # AI 응답 생성
    with st.chat_message("assistant", avatar="👩‍🏫"):
        with st.spinner("선생님이 생각 중이에요... 🤔"):
            try:
                response = st.session_state.client.messages.create(
                    model="claude-sonnet-4-5",
                    max_tokens=1500,
                    system=SYSTEM_PROMPT,
                    messages=st.session_state.messages,
                )
                assistant_reply = response.content[0].text
                st.session_state.messages.append(
                    {"role": "assistant", "content": assistant_reply}
                )
                st.session_state.total_questions += 1
                st.markdown(assistant_reply)
            except Exception as e:
                err_msg = f"❌ 오류가 발생했어요: {str(e)}"
                st.error(err_msg)

    st.rerun()

# ── 푸터 ────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#888; font-size:13px;'>"
    "📚 기초학력 수학 복습 챗봇 | Powered by Claude claude-sonnet-4-5 | "
    "틀려도 괜찮아요, 함께 배워요! 💙"
    "</div>",
    unsafe_allow_html=True,
)
