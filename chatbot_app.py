import streamlit as st
import anthropic

# 페이지 설정
st.set_page_config(
    page_title="중3 생물 선생님",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 스타일링
st.markdown("""
    <style>
    .teacher-message {
        background-color: #e8f5e9;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid #4caf50;
    }
    .student-message {
        background-color: #e3f2fd;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid #2196f3;
    }
    </style>
""", unsafe_allow_html=True)

# 제목
st.title("🧬 중3 생물 AI 선생님")
st.markdown("생물학의 신비로운 세계로 여러분을 초대합니다!")

# 사이드바 설정
with st.sidebar:
    st.header("⚙️ 설정")
    
    api_key = st.text_input(
        "Claude API 키 입력",
        type="password",
        help="Anthropic Claude API 키를 입력하세요"
    )
    
    st.markdown("---")
    st.subheader("📚 학습 주제")
    st.markdown("""
    - 세포의 구조와 기능
    - 생식과 발생
    - 유전과 진화
    - 생물의 다양성
    - 물질대사
    - 신경계와 내분비계
    - 항상성 유지
    """)
    
    st.markdown("---")
    st.info("💡 **팁**: 구체적인 질문일수록 더 좋은 답변을 받을 수 있습니다!")

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

if "api_key_set" not in st.session_state:
    st.session_state.api_key_set = False

# API 키 검증
if api_key:
    st.session_state.api_key_set = True
else:
    if st.session_state.messages:
        st.warning("⚠️ API 키를 입력해주세요")

# 채팅 히스토리 표시
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(
            f"""<div class="student-message">
            <strong>👤 학생:</strong> {message["content"]}
            </div>""",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""<div class="teacher-message">
            <strong>👨‍🏫 선생님:</strong> {message["content"]}
            </div>""",
            unsafe_allow_html=True
        )

# 사용자 입력
user_input = st.chat_input("생물에 대해 궁금한 점을 물어보세요...")

if user_input:
    if not st.session_state.api_key_set:
        st.error("❌ API 키를 먼저 입력해주세요")
    else:
        # 사용자 메시지 추가
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })
        
        # 메시지 표시
        st.markdown(
            f"""<div class="student-message">
            <strong>👤 학생:</strong> {user_input}
            </div>""",
            unsafe_allow_html=True
        )
        
        # Claude API 호출
        try:
            client = anthropic.Anthropic(api_key=api_key)
            
            # 시스템 프롬프트
            system_prompt = """당신은 중학교 3학년 생물 교과서를 전담하는 친절한 생물 선생님입니다.

역할 및 지침:
1. 학생의 질문에 정확하고 이해하기 쉽게 설명합니다
2. 중학교 수준의 생물학 개념을 정확히 다룹니다
3. 실제 예시나 그림 설명을 통해 개념을 명확하게 합니다
4. 학생이 이해하지 못한 부분이 있으면 다른 방식으로 설명합니다
5. 흥미로운 추가 정보나 실생활 응용 예시를 제공합니다
6. 존댓말을 사용하여 친근하게 대화합니다
7. 각 답변은 2-3개의 단락으로 적절히 구성합니다"""
            
            # API 호출
            with st.spinner("🤔 선생님이 생각중입니다..."):
                response = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=1024,
                    system=system_prompt,
                    messages=st.session_state.messages
                )
            
            # 응답 처리
            assistant_message = response.content[0].text
            
            # 어시스턴트 메시지 추가
            st.session_state.messages.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            # 응답 표시
            st.markdown(
                f"""<div class="teacher-message">
                <strong>👨‍🏫 선생님:</strong> {assistant_message}
                </div>""",
                unsafe_allow_html=True
            )
            
            # 추가 학습 제안
            st.success("✅ 답변이 완료되었습니다!")
            
        except anthropic.AuthenticationError:
            st.error("❌ API 키가 유효하지 않습니다. 다시 확인해주세요.")
        except anthropic.APIError as e:
            st.error(f"❌ API 오류: {str(e)}")

# 하단 정보
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("📝 질문 개수", len([m for m in st.session_state.messages if m["role"] == "user"]))

with col2:
    st.metric("💬 답변 개수", len([m for m in st.session_state.messages if m["role"] == "assistant"]))

with col3:
    if st.button("🔄 대화 초기화"):
        st.session_state.messages = []
        st.rerun()

st.caption("🧬 중3 생물 AI 선생님 v1.0 | Powered by Claude Haiku")