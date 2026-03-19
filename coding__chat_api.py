import streamlit as st
import anthropic

# ── 페이지 기본 설정
st.set_page_config(
    page_title="AI 융합전공 코딩 도우미",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 다크모드 CSS
DARK_CSS = """
<style>
html, body, [data-testid="stAppViewContainer"], .stApp {
    background-color: #0d1117 !important;
    color: #e6edf3 !important;
}
[data-testid="stSidebar"] {
    background-color: #161b22 !important;
    border-right: 1px solid #30363d !important;
}
[data-testid="stSidebar"] * {
    color: #e6edf3 !important;
}
[data-testid="stHeader"] {
    background-color: #0d1117 !important;
}
.block-container {
    background-color: #0d1117 !important;
    padding-top: 2rem !important;
}
h1, h2, h3, h4, h5, h6, p, span, div, label {
    color: #e6edf3 !important;
}
.header-banner {
    background: linear-gradient(135deg, #1c2e4a 0%, #1f4068 50%, #1565c0 100%);
    border-radius: 14px;
    padding: 26px 30px;
    margin-bottom: 22px;
    border: 1px solid #1f6feb;
    box-shadow: 0 4px 24px rgba(21,101,192,0.3);
}
.header-banner h1 {
    color: #f0f6fc !important;
    font-size: 1.7rem;
    font-weight: 700;
    margin: 0 0 6px 0;
}
.header-banner p {
    color: #8b949e !important;
    font-size: 0.92rem;
    margin: 0;
}
.info-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 12px 15px;
    margin-bottom: 10px;
}
.info-card h4 {
    color: #58a6ff !important;
    margin: 0 0 6px 0;
    font-size: 0.82rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.info-card p {
    color: #8b949e !important;
    margin: 0;
    font-size: 0.82rem;
    line-height: 1.55;
}
.model-badge {
    display: inline-block;
    background: #0d3b2e;
    color: #3fb950 !important;
    border: 1px solid #238636;
    border-radius: 20px;
    padding: 2px 11px;
    font-size: 0.76rem;
    font-weight: 600;
}
.status-online {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.82rem;
    color: #3fb950 !important;
}
.dot-online {
    width: 8px; height: 8px;
    background: #3fb950;
    border-radius: 50%;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%,100% { opacity:1; }
    50%      { opacity:0.35; }
}
@keyframes fadeInUp {
    from { opacity:0; transform:translateY(8px); }
    to   { opacity:1; transform:translateY(0); }
}
.msg-user {
    background: #1c2333;
    border: 1px solid #388bfd40;
    border-radius: 12px 4px 12px 12px;
    padding: 13px 16px;
    color: #cdd9e5 !important;
    line-height: 1.65;
    font-size: 0.92rem;
    animation: fadeInUp 0.25s ease;
    margin-bottom: 4px;
}
.msg-assistant {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 4px 12px 12px 12px;
    padding: 13px 16px;
    color: #e6edf3 !important;
    line-height: 1.65;
    font-size: 0.92rem;
    animation: fadeInUp 0.25s ease;
    margin-bottom: 4px;
}
.avatar-box {
    width: 38px; height: 38px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    flex-shrink: 0;
}
.av-user      { background: #1c2333; border: 1px solid #388bfd40; }
.av-assistant { background: #161b22; border: 1px solid #30363d; }
.stat-row { display: flex; gap: 8px; margin-top: 8px; }
.stat-box {
    flex: 1;
    background: #0d1117;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 9px;
    text-align: center;
}
.stat-num   { color: #58a6ff !important; font-size: 1.15rem; font-weight: 700; }
.stat-label { color: #484f58 !important; font-size: 0.7rem; margin-top: 2px; }
.stButton > button {
    background: linear-gradient(135deg, #1565c0, #1976d2) !important;
    color: #f0f6fc !important;
    border: none !important;
    border-radius: 7px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #1976d2, #1e88e5) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(21,101,192,0.45) !important;
}
.stTextArea textarea {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    color: #e6edf3 !important;
    border-radius: 8px !important;
    font-size: 0.92rem !important;
}
.stTextArea textarea::placeholder { color: #484f58 !important; }
.stTextArea textarea:focus {
    border-color: #388bfd !important;
    box-shadow: 0 0 0 3px rgba(56,139,253,0.15) !important;
}
.stTextInput input {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    color: #e6edf3 !important;
    border-radius: 8px !important;
}
.stTextInput input:focus {
    border-color: #388bfd !important;
    box-shadow: 0 0 0 3px rgba(56,139,253,0.15) !important;
}
.stSelectbox > div > div {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    color: #e6edf3 !important;
    border-radius: 8px !important;
}
div[data-baseweb="select"] > div {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    color: #e6edf3 !important;
}
div[data-baseweb="popover"] {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
}
div[data-baseweb="menu"] {
    background: #161b22 !important;
}
div[data-baseweb="option"] {
    background: #161b22 !important;
    color: #e6edf3 !important;
}
div[data-baseweb="option"]:hover {
    background: #1c2333 !important;
}
.stAlert {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    color: #e6edf3 !important;
    border-radius: 8px !important;
}
hr {
    border-color: #21262d !important;
    margin: 14px 0 !important;
}
.stSpinner > div {
    border-top-color: #388bfd !important;
}
.stForm {
    background: transparent !important;
    border: none !important;
}
.stFormSubmitButton > button {
    background: linear-gradient(135deg, #1565c0, #1976d2) !important;
    color: #f0f6fc !important;
    border: none !important;
    border-radius: 7px !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    height: 90px !important;
    width: 100% !important;
}
.footer-bar {
    text-align: center;
    color: #484f58 !important;
    font-size: 0.76rem;
    margin-top: 20px;
    padding: 10px;
    border-top: 1px solid #21262d;
}
.welcome-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 22px 16px;
    text-align: center;
    transition: border-color 0.2s;
}
.welcome-card:hover { border-color: #388bfd; }
.welcome-icon  { font-size: 2rem; margin-bottom: 10px; }
.welcome-title { color: #58a6ff !important; font-weight: 700; font-size: 0.93rem; margin-bottom: 7px; }
.welcome-desc  { color: #8b949e !important; font-size: 0.81rem; line-height: 1.5; }
</style>
"""
st.markdown(DARK_CSS, unsafe_allow_html=True)


# ── 세션 초기화
def init_session():
    defaults = {
        "messages"       : [],
        "api_key"        : "",
        "selected_model" : "claude-sonnet-4-5",
        "msg_count"      : 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()


# ── 모델 목록
MODELS = {
    "claude-sonnet-4-5"          : "Claude Sonnet 4.5  (권장)",
    "claude-opus-4-5"            : "Claude Opus 4.5    (최고 성능)",
    "claude-haiku-3-5"           : "Claude Haiku 3.5   (초고속)",
    "claude-opus-4-0"            : "Claude Opus 4.0    (고급)",
    "claude-3-7-sonnet-20250219" : "Claude Sonnet 3.7  (고급 추론)",
}


# ── 시스템 프롬프트 (백틱/특수문자 충돌 완전 회피)
def build_system_prompt():
    lines = [
        "당신은 AI 융합전공 교수입니다. 학생들의 프로그래밍 학습을 돕는 전문 코딩 멘토입니다.",
        "",
        "[전문 분야]",
        "- Python, JavaScript, Java, C/C++, SQL 등 주요 프로그래밍 언어",
        "- 머신러닝 및 딥러닝 (TensorFlow, PyTorch, scikit-learn)",
        "- 데이터 분석 (Pandas, NumPy, Matplotlib, Seaborn)",
        "- 웹 개발 (FastAPI, Flask, Streamlit, React)",
        "- 알고리즘 및 자료구조",
        "- AI/ML 파이프라인 설계 및 최적화",
        "- 클라우드 서비스 (AWS, GCP, Azure) 및 MLOps",
        "",
        "[응답 원칙]",
        "1. 명확하고 구조적인 설명: 개념을 단계별로 설명합니다.",
        "2. 실용적인 코드 예시: 항상 실행 가능한 코드를 제공합니다.",
        "3. 코드 품질 강조: 가독성, 효율성, 모범 사례를 함께 안내합니다.",
        "4. 학습 유도: 단순 정답보다 이해를 돕는 방향으로 설명합니다.",
        "5. 한국어 우선: 한국어로 답변하되 코드와 기술 용어는 영문 사용합니다.",
        "6. 오류 디버깅: 에러 메시지 분석 및 해결책을 체계적으로 제시합니다.",
        "",
        "[코드 응답 형식]",
        "- 코드는 마크다운 코드 펜스(언어명 명시)로 감쌉니다.",
        "- 복잡한 코드에는 주요 부분마다 주석을 추가합니다.",
        "- 필요시 개선된 버전과 원본을 함께 보여줍니다.",
        "",
        "항상 친절하고 격려하는 태도로 학생들의 성장을 응원하세요!",
    ]
    return "\n".join(lines)

SYSTEM_PROMPT = build_system_prompt()


# ── Claude API 호출
def call_claude(api_key: str, model: str, messages: list) -> str:
    try:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=messages,
        )
        return response.content[0].text
    except anthropic.AuthenticationError:
        return "오류: 유효하지 않은 API 키입니다. 사이드바에서 올바른 키를 입력해 주세요."
    except anthropic.RateLimitError:
        return "오류: 요청 한도를 초과했습니다. 잠시 후 다시 시도해 주세요."
    except anthropic.APIStatusError as e:
        return f"API 오류 ({e.status_code}): {e.message}"
    except Exception as e:
        return f"예상치 못한 오류: {str(e)}"


# ── 채팅 메시지 렌더링
def render_messages():
    for msg in st.session_state.messages:
        role    = msg["role"]
        content = msg["content"]

        if role == "user":
            c1, c2 = st.columns([0.91, 0.09])
            with c1:
                st.markdown(
                    '<div class="msg-user">' + content + '</div>',
                    unsafe_allow_html=True,
                )
            with c2:
                st.markdown(
                    '<div class="avatar-box av-user" style="margin-top:2px;">👨‍💻</div>',
                    unsafe_allow_html=True,
                )
        else:
            c1, c2 = st.columns([0.09, 0.91])
            with c1:
                st.markdown(
                    '<div class="avatar-box av-assistant" style="margin-top:2px;">🎓</div>',
                    unsafe_allow_html=True,
                )
            with c2:
                # st.markdown 으로 코드 하이라이팅 지원
                st.markdown(content)


# ══════════════════════════════════════════════════════════════════════
# 사이드바
# ══════════════════════════════════════════════════════════════════════
with st.sidebar:
    # 프로필
    st.markdown(
        '<div style="text-align:center;padding:14px 0 6px;">'
        '<div style="font-size:2.8rem;">🎓</div>'
        '<div style="color:#58a6ff;font-weight:700;font-size:1rem;margin-top:4px;">AI 융합전공</div>'
        '<div style="color:#8b949e;font-size:0.8rem;">코딩 도우미 교수</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # API 키
    st.markdown(
        '<div class="info-card"><h4>API 설정</h4></div>',
        unsafe_allow_html=True,
    )
    api_key_input = st.text_input(
        "Anthropic API Key",
        type="password",
        value=st.session_state.api_key,
        placeholder="sk-ant-...",
        help="Anthropic Console에서 발급받은 API 키를 입력하세요.",
    )
    if api_key_input:
        st.session_state.api_key = api_key_input
        st.markdown(
            '<div class="status-online">'
            '<div class="dot-online"></div>API 키 입력됨'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        st.warning("API 키를 입력해주세요.")

    st.markdown("---")

    # 모델 선택
    st.markdown(
        '<div class="info-card"><h4>모델 선택</h4></div>',
        unsafe_allow_html=True,
    )
    selected_model = st.selectbox(
        "Claude 모델",
        options=list(MODELS.keys()),
        format_func=lambda x: MODELS[x],
        index=list(MODELS.keys()).index(st.session_state.selected_model),
    )
    st.session_state.selected_model = selected_model
    st.markdown(
        '<div style="margin-top:5px;">'
        '<span class="model-badge">' + selected_model + '</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # 통계
    st.markdown(
        '<div class="info-card"><h4>대화 통계</h4></div>',
        unsafe_allow_html=True,
    )
    q_count = st.session_state.msg_count
    t_count = len(st.session_state.messages)
    st.markdown(
        '<div class="stat-row">'
        '<div class="stat-box">'
        '<div class="stat-num">' + str(q_count) + '</div>'
        '<div class="stat-label">질문 수</div>'
        '</div>'
        '<div class="stat-box">'
        '<div class="stat-num">' + str(t_count) + '</div>'
        '<div class="stat-label">전체 대화</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # 빠른 질문
    st.markdown(
        '<div class="info-card"><h4>빠른 질문</h4></div>',
        unsafe_allow_html=True,
    )
    quick_questions = [
        ("Python 기초 설명",
         "Python의 리스트 컴프리헨션과 일반 for 루프의 차이점과 각각의 적절한 사용 시기를 알려주세요."),
        ("ML 모델 구축 예시",
         "scikit-learn으로 간단한 분류 모델을 만드는 전체 코드를 작성해주세요. 데이터 전처리부터 모델 평가까지 포함해서요."),
        ("디버깅 방법 안내",
         "Python에서 자주 발생하는 에러 유형 5가지와 각 해결 방법을 예시 코드와 함께 설명해주세요."),
        ("데이터 시각화 코드",
         "Matplotlib과 Seaborn을 이용한 데이터 시각화 기본 코드 예시를 보여주세요."),
        ("REST API 연동 방법",
         "Python requests 라이브러리로 REST API를 호출하는 방법과 에러 처리 방법을 알려주세요."),
    ]
    for label, question in quick_questions:
        if st.button(label, use_container_width=True):
            st.session_state["quick_input"] = question
            st.rerun()

    st.markdown("---")

    if st.button("대화 초기화", use_container_width=True):
        st.session_state.messages  = []
        st.session_state.msg_count = 0
        st.rerun()

    st.markdown(
        '<div class="info-card" style="margin-top:10px;">'
        '<h4>사용 팁</h4>'
        '<p>'
        '에러 메시지 전체를 붙여넣으면 정확한 디버깅이 가능합니다.<br>'
        '코드의 목적과 맥락을 함께 설명해 주세요.<br>'
        '특정 언어/프레임워크를 명시하면 더 정확한 답변을 받을 수 있습니다.'
        '</p>'
        '</div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════
# 메인 영역
# ══════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="header-banner">'
    '<h1>🎓 AI 융합전공 코딩 도우미</h1>'
    '<p>AI 융합전공 교수가 코딩 학습을 도와드립니다. 언제든지 궁금한 점을 질문하세요!</p>'
    '</div>',
    unsafe_allow_html=True,
)

# 환영 카드 (대화 없을 때)
if not st.session_state.messages:
    c1, c2, c3 = st.columns(3)
    welcome_items = [
        ("💻", "코드 작성 도움",
         "새로운 기능 구현, 알고리즘 설계, 자료구조 선택 등 코드 작성의 모든 단계를 안내합니다."),
        ("🐞", "오류 디버깅",
         "에러 메시지 분석, 버그 원인 파악, 해결 방법 제시까지 체계적인 디버깅을 도와드립니다."),
        ("📚", "개념 학습",
         "프로그래밍 개념, AI/ML 이론, 최신 기술 트렌드를 쉽고 명확하게 설명해 드립니다."),
    ]
    for col, (icon, title, desc) in zip([c1, c2, c3], welcome_items):
        with col:
            st.markdown(
                '<div class="welcome-card">'
                '<div class="welcome-icon">' + icon + '</div>'
                '<div class="welcome-title">' + title + '</div>'
                '<div class="welcome-desc">'  + desc  + '</div>'
                '</div>',
                unsafe_allow_html=True,
            )
    st.markdown(
        '<div style="text-align:center;color:#484f58;font-size:0.86rem;margin:18px 0 6px;">'
        '아래 입력창에 질문을 입력하거나, 사이드바의 빠른 질문을 선택하세요.'
        '</div>',
        unsafe_allow_html=True,
    )

# 채팅 히스토리
with st.container():
    render_messages()

# ── 입력 영역
st.markdown("---")
default_text = st.session_state.pop("quick_input", "")

with st.form(key="chat_form", clear_on_submit=True):
    col_input, col_btn = st.columns([0.84, 0.16])
    with col_input:
        user_input = st.text_area(
            "입력",
            value=default_text,
            placeholder="코딩 관련 질문을 입력하세요...",
            height=90,
            label_visibility="collapsed",
        )
    with col_btn:
        submit = st.form_submit_button("전송 ✈️", use_container_width=True)

# 메시지 처리
if submit and user_input.strip():
    if not st.session_state.api_key:
        st.error("사이드바에서 Anthropic API 키를 먼저 입력해 주세요.")
    else:
        st.session_state.messages.append(
            {"role": "user", "content": user_input.strip()}
        )
        st.session_state.msg_count += 1

        with st.spinner("교수님이 답변을 작성 중입니다..."):
            reply = call_claude(
                st.session_state.api_key,
                st.session_state.selected_model,
                st.session_state.messages,
            )

        st.session_state.messages.append(
            {"role": "assistant", "content": reply}
        )
        st.rerun()

elif submit and not user_input.strip():
    st.warning("메시지를 입력해 주세요.")

# 하단 푸터
st.markdown(
    '<div class="footer-bar">'
    'AI 융합전공 코딩 도우미 &nbsp;|&nbsp; Powered by Anthropic Claude &nbsp;|&nbsp; 현재 모델: '
    + st.session_state.selected_model +
    '</div>',
    unsafe_allow_html=True,
)
