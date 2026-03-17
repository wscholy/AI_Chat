import streamlit as st
import anthropic
from datetime import datetime

# 페이지 설정
st.set_page_config(
    page_title="중3 생물 교사 챗봇",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS - 다크 테마
st.markdown("""
<style>
    body {
        background-color: #1a1a1a;
        color: #ffffff;
    }
    
    .teacher-message {
        background-color: #2d3f5f;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #4a90e2;
        margin: 10px 0;
        color: #e8f0fe;
    }
    
    .student-message {
        background-color: #3d3d3d;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #888;
        margin: 10px 0;
        color: #f0f0f0;
    }
    
    .header-title {
        color: #4a90e2;
        text-align: center;
        font-size: 2.5em;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    .info-box {
        background-color: #4d3d1f;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #ff9800;
        margin: 10px 0;
        color: #ffc966;
    }
    
    /* Streamlit 기본 요소 색상 조정 */
    .stTextInput > div > div > input {
        background-color: #2d2d2d;
        color: #ffffff;
        border: 1px solid #4a4a4a;
    }
    
    .stSelectbox > div > div > select {
        background-color: #2d2d2d;
        color: #ffffff;
    }
    
    .stButton > button {
        background-color: #4a90e2;
        color: #ffffff;
        border: none;
    }
    
    .stButton > button:hover {
        background-color: #3a7fd8;
    }
    
    .stExpander {
        background-color: #2d2d2d;
        border: 1px solid #4a4a4a;
    }
    
    .stExpander > div > div > p {
        color: #e8e8e8;
    }
    
    /* 사이드바 스타일 */
    [data-testid="stSidebar"] {
        background-color: #1f1f1f;
    }
    
    .stMarkdown, .stText {
        color: #ffffff;
    }
    
    hr {
        border-color: #4a4a4a;
    }
    
    .stCaption {
        color: #888888;
    }
    
    .stTabs [data-baseweb="tab-list"] button {
        color: #ffffff;
    }
    
    .stInfo {
        background-color: #2d3f5f;
        color: #e8f0fe;
    }
</style>
""", unsafe_allow_html=True)

# 헤더
st.markdown('<div class="header-title">🧬 중3 생물 교사 챗봇</div>', unsafe_allow_html=True)
st.markdown("---")

# 사이드바 설정
with st.sidebar:
    st.title("⚙️ 설정")
    
    # API 키 입력
    api_key = st.text_input(
        "Anthropic API 키 입력",
        type="password",
        help="https://console.anthropic.com에서 발급받으세요"
    )
    
    st.markdown("---")
    
    # 학습 주제 선택
    st.subheader("📚 학습 주제")
    topics = {
        "세포와 조직": "세포의 구조, 분열, 조직",
        "유전": "유전자, DNA, 상염색체 유전",
        "진화와 다양성": "진화, 자연선택, 생물 다양성",
        "생태계": "생산자, 소비자, 분해자, 에너지 흐름",
        "인체 기관계": "소화계, 순환계, 호흡계, 신경계",
        "자유 질문": "모든 생물 관련 질문 가능"
    }
    
    selected_topic = st.selectbox(
        "학습하고 싶은 주제를 선택하세요:",
        list(topics.keys()),
        help="주제 선택 후 질문하면 더 맞춤형 답변을 받을 수 있습니다"
    )
    
    st.markdown("---")
    
    # 학습 팁
    with st.expander("💡 학습 팁"):
        st.markdown("""
        - **단계별 학습**: 기초 개념부터 시작하세요
        - **예제 요청**: "~의 예를 들어줄 수 있나요?"
        - **개념 설명**: "~가 뭔가요?" 형태로 질문하세요
        - **문제 풀이**: 문제와 함께 풀이 과정을 설명해달라고 하세요
        - **정리 요청**: "요점을 정리해줄 수 있나요?"
        """)
    
    st.markdown("---")
    st.caption("🚀 Powered by Claude Haiku 4.5")

# 메인 콘텐츠
col1, col2 = st.columns([1, 4])

with col1:
    st.markdown("""
    <div class="info-box">
        <strong>📖 현재 주제:</strong><br>
        {topic}
    </div>
    """.format(topic=selected_topic), unsafe_allow_html=True)

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": f"안녕하세요! 👋 저는 중학교 생물 교사입니다.\n\n현재 **{selected_topic}** 주제로 학습 중이신 것 같네요.\n\n편하게 생물에 대해 질문해주세요. 저는 여러분의 궁금증을 명확하고 이해하기 쉽게 설명해드리겠습니다! 😊\n\n**어떤 질문이든 환영합니다:**\n- 개념 설명\n- 예제와 실생활 사례\n- 문제 풀이\n- 요점 정리"
        }
    ]

if "current_topic" not in st.session_state:
    st.session_state.current_topic = selected_topic

# 주제 변경 감지
if selected_topic != st.session_state.current_topic:
    st.session_state.current_topic = selected_topic
    st.session_state.messages.append({
        "role": "user",
        "content": f"주제를 {selected_topic}로 변경했습니다."
    })
    st.session_state.messages.append({
        "role": "assistant",
        "content": f"좋아요! 이제 **{selected_topic}** 주제로 함께 학습하겠습니다. 궁금한 점을 편하게 물어봐주세요! 📚"
    })

# 대화 표시
st.subheader("💬 대화")
chat_container = st.container()

with chat_container:
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(
                f'<div class="student-message"><strong>👤 학생:</strong><br>{message["content"]}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="teacher-message"><strong>👨‍🏫 생물 선생님:</strong><br>{message["content"]}</div>',
                unsafe_allow_html=True
            )

# 입력 영역
st.markdown("---")
col1, col2 = st.columns([20, 1])

with col1:
    user_input = st.text_input(
        "질문을 입력하세요:",
        placeholder="예: 세포의 구조를 설명해줄 수 있나요? / 광합성이 뭔가요?",
        label_visibility="collapsed"
    )

# 메시지 처리
if user_input:
    if not api_key:
        st.error("⚠️ API 키를 입력해주세요!")
    else:
        try:
            # 메시지 추가
            st.session_state.messages.append({
                "role": "user",
                "content": user_input
            })
            
            # Claude API 호출
            client = anthropic.Anthropic(api_key=api_key)
            
            system_prompt = f"""당신은 중학교 3학년 생물 담당 선생님입니다.

다음 원칙을 따르세요:
1. 학생의 수준에 맞게 설명하세요 (쉽고 명확하게)
2. 현재 학습 주제: {selected_topic}
3. 예제와 실생활 사례를 포함하세요
4. 학생을 격려하고 긍정적인 태도를 유지하세요
5. 복잡한 개념은 단계별로 설명하세요
6. 비유나 그림으로 설명할 수 있다면 텍스트로 표현하세요
7. 마크다운 형식을 사용해 답변을 보기 좋게 구성하세요
8. 답변 끝에 "더 궁금한 점이 있나요?" 같은 격려 문구를 추가하세요

학생들의 학습을 돕는 친절한 선생님이 되세요!"""
            
            with st.spinner("선생님이 답변을 준비 중입니다... 🤔"):
                message = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=1024,
                    system=system_prompt,
                    messages=[
                        {
                            "role": msg["role"],
                            "content": msg["content"]
                        }
                        for msg in st.session_state.messages
                    ]
                )
                
                assistant_message = message.content[0].text
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_message
                })
                
                # 페이지 새로고침
                st.rerun()
                
        except anthropic.AuthenticationError:
            st.error("❌ API 키가 올바르지 않습니다. https://console.anthropic.com 에서 API 키를 확인해주세요.")
        except anthropic.NotFoundError as e:
            st.error("❌ 모델을 찾을 수 없습니다. API 키와 모델명을 확인해주세요.")
            st.info("현재 사용 중인 모델: `claude-haiku-4-5-20251001`")
        except anthropic.RateLimitError:
            st.error("⏱️ 요청이 너무 많습니다. 잠시 후 다시 시도해주세요.")
        except anthropic.APIError as e:
            st.error(f"❌ API 오류가 발생했습니다: {str(e)}")
        except Exception as e:
            st.error(f"❌ 예상치 못한 오류가 발생했습니다: {str(e)}")

# 초기화 버튼
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔄 대화 초기화", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": f"대화를 초기화했습니다. 다시 시작해볼까요? 😊\n\n**{selected_topic}** 주제로 궁금한 점을 물어봐주세요!"
            }
        ]
        st.rerun()

with col2:
    if st.button("💾 대화 저장 (준비 중)", use_container_width=True):
        st.info("💡 대화 저장 기능은 준비 중입니다.")

with col3:
    if st.button("❓ 도움말", use_container_width=True):
        st.info("""
        **이 챗봇 사용법:**
        1. 사이드바에서 학습하고 싶은 주제를 선택하세요
        2. 생물에 대한 질문을 자유롭게 입력하세요
        3. 선생님(AI)이 친절하게 설명해줄 거예요
        4. 복잡한 개념은 여러 번 물어봐도 괜찮아요
        5. 언제든지 대화를 초기화하고 새로 시작할 수 있습니다
        """)

st.markdown("---")
st.caption("© 2024 생물 학습 챗봇 | Streamlit + Claude Haiku 4.5")
