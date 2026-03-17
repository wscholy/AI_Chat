import streamlit as st
import anthropic
from datetime import datetime

# 페이지 설정
st.set_page_config(
    page_title="중3 생물 선생님",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 다크 테마 CSS 적용
st.markdown("""
<style>
    /* 메인 배경색 */
    .stMainBlockContainer {
        background-color: #0e1117;
        color: #c9d1d9;
    }
    
    /* 채팅 메시지 스타일 */
    .stChatMessage {
        background-color: #161b22;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    
    /* 사용자 메시지 배경 */
    .stChatMessage.user {
        background-color: #1f6feb;
        color: #ffffff;
    }
    
    /* 어시스턴트 메시지 배경 */
    .stChatMessage.assistant {
        background-color: #21262d;
        color: #e6edf3;
    }
    
    /* 입력창 스타일 */
    .stChatInputContainer {
        background-color: #0e1117;
    }
    
    .stChatInput input {
        background-color: #161b22;
        color: #c9d1d9;
        border: 1px solid #30363d;
    }
    
    .stChatInput input::placeholder {
        color: #6e7681;
    }
    
    /* 텍스트 입력창 */
    .stTextInput input {
        background-color: #161b22;
        color: #c9d1d9;
        border: 1px solid #30363d;
    }
    
    .stTextInput input::placeholder {
        color: #6e7681;
    }
    
    /* 셀렉트박스 */
    .stSelectbox > div > div {
        background-color: #161b22;
        color: #c9d1d9;
    }
    
    /* 버튼 스타일 */
    .stButton > button {
        background-color: #238636;
        color: #ffffff;
        border: 1px solid #2ea043;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        background-color: #2ea043;
        border-color: #3fb950;
    }
    
    /* 사이드바 */
    .stSidebar {
        background-color: #0d1117;
    }
    
    .stSidebar .stTextInput input {
        background-color: #161b22;
        color: #c9d1d9;
    }
    
    .stSidebar .stSelectbox > div > div {
        background-color: #161b22;
        color: #c9d1d9;
    }
    
    /* 정보 박스 */
    .stInfo {
        background-color: #161b22;
        color: #79c0ff;
        border: 1px solid #1f6feb;
    }
    
    /* 에러 박스 */
    .stError {
        background-color: #161b22;
        color: #f85149;
        border: 1px solid #da3633;
    }
    
    /* 제목 스타일 */
    h1, h2, h3, h4, h5, h6 {
        color: #e6edf3;
    }
    
    /* 구분선 */
    hr {
        border-color: #30363d;
    }
    
    /* 마크다운 텍스트 */
    p, span, div {
        color: #c9d1d9;
    }
    
    /* 링크 색상 */
    a {
        color: #58a6ff;
    }
</style>
""", unsafe_allow_html=True)

# 사이드바 설정
with st.sidebar:
    st.title("⚙️ 설정")
    
    api_key = st.text_input(
        "Claude API 키 입력",
        type="password",
        help="https://console.anthropic.com 에서 발급받으세요"
    )
    
    st.divider()
    
    st.subheader("📚 학습 주제")
    topics = {
        "세포": "세포의 구조, 기능, 분열",
        "유전": "유전자, DNA, 유전의 법칙",
        "진화": "진화, 자연선택, 화석",
        "생태": "생태계, 식물, 먹이사슬",
        "신체": "소화, 순환, 호흡계",
        "자유 질문": "자유롭게 질문하기"
    }
    
    selected_topic = st.selectbox(
        "학습할 주제를 선택하세요",
        list(topics.keys()),
        help="주제를 선택하면 관련 학습 가이드를 받을 수 있습니다"
    )
    
    st.divider()
    
    st.subheader("💡 사용 팁")
    st.info(
        "- 개념이 어렵면 '쉽게 설명해줘'라고 말씀하세요\n"
        "- 예시를 원하면 '예시를 들어줘'라고 요청하세요\n"
        "- 문제 풀이를 원하면 문제를 복사해서 붙여넣으세요\n"
        "- 시험 대비를 원하면 '요점 정리'를 요청하세요"
    )

# 메인 영역
st.title("🧬 중3 생물 학습 가이드 챗봇")
st.markdown(f"**현재 선택된 주제**: {selected_topic} - {topics[selected_topic]}")

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

if "topic_history" not in st.session_state:
    st.session_state.topic_history = []

# 채팅 히스토리 표시
chat_container = st.container()

with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="🧑‍🏫" if message["role"] == "assistant" else "👨‍🎓"):
            st.markdown(message["content"])

# 사용자 입력
user_input = st.chat_input(
    "생물 질문을 입력하세요...",
    disabled=not api_key,
    placeholder="예: 세포막의 기능이 뭐예요?" if api_key else "API 키를 입력해주세요"
)

if user_input and api_key:
    # 사용자 메시지 추가
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    
    # 화면에 사용자 메시지 표시
    with chat_container:
        with st.chat_message("user", avatar="👨‍🎓"):
            st.markdown(user_input)
    
    # Claude API 호출
    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        # 시스템 프롬프트 구성
        system_prompt = f"""당신은 친절하고 전문적인 중학교 3학년 생물 선생님입니다.

**역할:**
- 중3 생물 교과서 범위의 개념을 정확하고 쉽게 설명합니다.
- 학생의 이해도에 맞춰 설명을 조정합니다.
- 실생활 예시를 들어 개념을 명확히 합니다.
- 문제 풀이를 체계적으로 도와줍니다.

**현재 학습 주제: {selected_topic}**
({topics[selected_topic]})

**지침:**
1. 중3 수준의 언어를 사용합니다
2. 개념을 최대 3-4문장으로 간단히 설명합니다
3. 필요하면 그림이나 도표를 텍스트로 설명합니다
4. 암기해야 할 부분은 명확히 표시합니다
5. 학생이 어려워하면 더 쉬운 표현으로 다시 설명합니다
6. 마지막에 이해했는지 확인하는 질문을 합니다

**피해야 할 것:**
- 너무 복잡한 용어 사용
- 고등학교 이상의 내용
- 교과서 범위를 벗어난 설명"""

        # Claude와 대화
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=system_prompt,
            messages=[
                {
                    "role": "user" if msg["role"] == "user" else "assistant",
                    "content": msg["content"]
                }
                for msg in st.session_state.messages
            ]
        )
        
        assistant_message = response.content[0].text
        
        # 어시스턴트 메시지 저장
        st.session_state.messages.append({
            "role": "assistant",
            "content": assistant_message
        })
        
        # 어시스턴트 메시지 표시
        with chat_container:
            with st.chat_message("assistant", avatar="🧑‍🏫"):
                st.markdown(assistant_message)
        
        # 주제 히스토리 업데이트
        if selected_topic not in st.session_state.topic_history:
            st.session_state.topic_history.append(selected_topic)
    
    except anthropic.APIError as e:
        with chat_container:
            with st.chat_message("assistant", avatar="🧑‍🏫"):
                st.error(f"API 오류가 발생했습니다: {str(e)}")
    
    except Exception as e:
        with chat_container:
            with st.chat_message("assistant", avatar="🧑‍🏫"):
                st.error(f"오류가 발생했습니다: {str(e)}")

# 하단 기능 버튼
st.divider()

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🔄 대화 초기화", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

with col2:
    if st.button("📋 요점 정리", use_container_width=True, disabled=not api_key):
        st.session_state.messages.append({
            "role": "user",
            "content": f"{selected_topic}에 대해 시험 대비용 요점을 정리해줘. 핵심 개념 3-5개를 간단히 정리해주세요."
        })
        st.rerun()

with col3:
    if st.button("❓ 예시 문제", use_container_width=True, disabled=not api_key):
        st.session_state.messages.append({
            "role": "user",
            "content": f"{selected_topic}에 대한 중3 수준의 선택지 문제 2개를 만들어줄래?"
        })
        st.rerun()

with col4:
    if st.button("📚 학습 팁", use_container_width=True, disabled=not api_key):
        st.session_state.messages.append({
            "role": "user",
            "content": f"{selected_topic}을(를) 효과적으로 공부하는 방법을 알려줄래?"
        })
        st.rerun()

# 푸터
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: #6e7681; font-size: 12px;'>
    🧬 중3 생물 학습 가이드 챗봇 | Powered by Claude Haiku<br>
    생물 개념 이해, 문제 풀이, 시험 대비를 도와드립니다!
    </div>
    """,
    unsafe_allow_html=True
)
