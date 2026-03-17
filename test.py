import streamlit as st
import anthropic

# 페이지 설정
st.set_page_config(
    page_title="국어 선생님 봇",
    page_icon="📚",
    layout="centered"
)

# 스타일 설정
st.markdown("""
    <style>
    .teacher-message {
        background-color: #e8f4f8;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #2196F3;
        margin: 10px 0;
    }
    .student-message {
        background-color: #fff9e6;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #FFC107;
        margin: 10px 0;
    }
    .title-emoji {
        font-size: 40px;
    }
    </style>
""", unsafe_allow_html=True)

# 제목
col1, col2 = st.columns([1, 4])
with col1:
    st.markdown('<div class="title-emoji">📚</div>', unsafe_allow_html=True)
with col2:
    st.title("초등학교 1학년 국어 선생님")

st.markdown("**맞춤법을 재미있게 배워봅시다!**")
st.divider()

# API 키 입력
api_key = st.text_input(
    "Claude API 키를 입력하세요:",
    type="password",
    help="Anthropic 공식 웹사이트에서 발급받은 API 키를 입력합니다."
)

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "안녕하세요! 저는 여러분의 국어 선생님이에요. 😊\n\n"
                      "맞춤법이 틀린 문장을 알려주면, "
                      "제가 어떻게 고쳐야 하는지 친절하게 설명해드릴게요.\n\n"
                      "예를 들어 '고양이가 운동場'처럼 틀린 글을 말씀해 주세요!"
        }
    ]

if "api_key_valid" not in st.session_state:
    st.session_state.api_key_valid = False

# 메시지 표시
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(
            f'<div class="student-message"><b>학생:</b> {message["content"]}</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="teacher-message"><b>선생님:</b> {message["content"]}</div>',
            unsafe_allow_html=True
        )

st.divider()

# 사용자 입력
user_input = st.text_area(
    "여기에 맞춤법을 배우고 싶은 문장을 쓰세요:",
    placeholder="예: '나는 학교 갓어요'",
    height=80
)

# 전송 버튼
if st.button("선생님께 물어보기", type="primary", use_container_width=True):
    if not api_key:
        st.error("⚠️ API 키를 먼저 입력해주세요!")
    elif not user_input.strip():
        st.error("⚠️ 문장을 입력해주세요!")
    else:
        try:
            # 사용자 메시지 추가
            st.session_state.messages.append(
                {"role": "user", "content": user_input}
            )

            # Claude API 호출
            client = anthropic.Anthropic(api_key=api_key)

            system_prompt = """당신은 초등학교 1학년 국어 교사입니다.
학생들이 제시한 문장의 맞춤법을 친절하고 재미있게 가르칩니다.

지침:
1. 간단하고 쉬운 언어를 사용합니다
2. 틀린 부분을 명확히 표시합니다 (예: ❌ 틀린 말 → ✓ 올바른 말)
3. 왜 그렇게 고쳐야 하는지 짧게 설명합니다
4. 격려와 칭찬을 함께 합니다
5. 이모지를 적절히 사용하여 재미있게 만듭니다
6. 2-3문장의 짧은 설명을 제공합니다"""

            message = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=300,
                system=system_prompt,
                messages=st.session_state.messages
            )

            assistant_message = message.content[0].text

            # 어시스턴트 응답 추가
            st.session_state.messages.append(
                {"role": "assistant", "content": assistant_message}
            )

            # 페이지 새로고침
            st.rerun()

        except anthropic.APIError as e:
            st.error(f"❌ API 오류: {str(e)}")
        except Exception as e:
            st.error(f"❌ 오류 발생: {str(e)}")

# 사이드바 - 기능 설명
with st.sidebar:
    st.header("📖 사용법")
    st.markdown("""
    **이 봇의 역할:**
    - 맞춤법 검사 및 수정
    - 쉬운 설명 제공
    - 재미있는 학습 경험
    
    **예시:**
    - '우산을 들고 갔어요' → 올바른 표현
    - '학교 갔어요' → '학교에 갔어요'
    - '먹은음식' → '먹은 음식'
    
    **팁:**
    완전하지 않은 문장도 괜찮습니다.
    선생님이 이해하고 도와드릴게요! 😊
    """)
    
    st.divider()
    
    # 초기화 버튼
    if st.button("대화 초기화", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "안녕하세요! 저는 여러분의 국어 선생님이에요. 😊\n\n"
                          "맞춤법이 틀린 문장을 알려주면, "
                          "제가 어떻게 고쳐야 하는지 친절하게 설명해드릴게요!"
            }
        ]
        st.rerun()

st.divider()
st.caption("🌟 초등학교 1학년 국어 맞춤법 학습봇 | Powered by Claude Haiku")
