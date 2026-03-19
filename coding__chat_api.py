import streamlit as st
import anthropic

# ── 페이지 기본 설정 ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI 융합전공 코딩 도우미",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 전역 CSS ─────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
        /* 전체 배경 */
        .stApp { background-color: #0f1117; }

        /* 사이드바 */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1a1f2e 0%, #16213e 100%);
            border-right: 1px solid #2d3561;
        }

        /* 헤더 배너 */
        .header-banner {
            background: linear-gradient(135deg, #1e3a5f 0%, #2d6a9f 50%, #1a8fe3 100%);
            border-radius: 16px;
            padding: 28px 32px;
            margin-bottom: 24px;
            box-shadow: 0 8px 32px rgba(26,143,227,0.25);
            border: 1px solid rgba(255,255,255,0.08);
        }
        .header-banner h1 {
            color: #ffffff;
            font-size: 1.85rem;
            font-weight: 700;
            margin: 0 0 6px 0;
        }
        .header-banner p {
            color: #a8d4f5;
            font-size: 0.95rem;
            margin: 0;
        }

        /* 채팅 메시지 */
        .chat-message {
            display: flex;
            gap: 14px;
            margin-bottom: 18px;
            animation: fadeIn 0.3s ease;
        }
        @keyframes fadeIn { from {opacity:0; transform:translateY(6px);} to {opacity:1; transform:translateY(0);} }

        .chat-avatar {
            width: 42px;
            height: 42px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
            flex-shrink: 0;
        }
        .avatar-assistant { background: linear-gradient(135deg, #1e3a5f, #1a8fe3); }
        .avatar-user      { background: linear-gradient(135deg, #2d1b69, #7c3aed); }

        .chat-bubble {
            max-width: 88%;
            padding: 14px 18px;
            border-radius: 16px;
            line-height: 1.65;
            font-size: 0.93rem;
        }
        .bubble-assistant {
            background: #1e2433;
            color: #e2e8f0;
            border: 1px solid #2d3561;
            border-top-left-radius: 4px;
        }
        .bubble-user {
            background: linear-gradient(135deg, #2d1b69, #4c1d95);
            color: #ede9fe;
            border: 1px solid #5b21b6;
            border-top-right-radius: 4px;
            margin-left: auto;
        }
        .chat-message.user-row { flex-direction: row-reverse; }

        /* 코드 블록 */
        .bubble-assistant pre, .bubble-assistant code {
            background: #0d1117 !important;
            border: 1px solid #30363d;
            border-radius: 8px;
        }

        /* 정보 카드 */
        .info-card {
            background: #1e2433;
            border: 1px solid #2d3561;
            border-radius: 12px;
            padding: 14px 16px;
            margin-bottom: 12px;
        }
        .info-card h4 { color: #60a5fa; margin: 0 0 8px 0; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; }
        .info-card p  { color: #94a3b8; margin: 0; font-size: 0.85rem; line-height: 1.5; }

        /* 모델 배지 */
        .model-badge {
            display: inline-block;
            background: linear-gradient(135deg, #064e3b, #065f46);
            color: #6ee7b7;
            border: 1px solid #059669;
            border-radius: 20px;
            padding: 3px 12px;
            font-size: 0.78rem;
            font-weight: 600;
        }

        /* 상태 표시 */
        .status-online {
            display: flex;
            align-items: center;
            gap: 6px;
            color: #6ee7b7;
            font-size: 0.82rem;
        }
        .dot-online {
            width: 8px; height: 8px;
            background: #10b981;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%,100% { opacity:1; }
            50%      { opacity:0.4; }
        }

        /* 버튼 */
        .stButton > button {
            background: linear-gradient(135deg, #1e3a5f, #1a8fe3) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            transition: all 0.2s !important;
        }
        .stButton > button:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 15px rgba(26,143,227,0.4) !important;
        }

        /* 입력창 */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {
            background: #1e2433 !important;
            border: 1px solid #2d3561 !important;
            color: #e2e8f0 !important;
            border-radius: 8px !important;
        }

        /* 선택박스 */
        .stSelectbox > div > div {
            background: #1e2433 !important;
            border: 1px solid #2d3561 !important;
            color: #e2e8f0 !important;
        }

        /* 구분선 */
        hr { border-color: #2d3561 !important; }

        /* 통계 */
        .stat-row { display: flex; gap: 10px; margin-top: 10px; }
        .stat-box {
            flex: 1;
            background: #151b2e;
            border: 1px solid #2d3561;
            border-radius: 8px;
            padding: 10px;
            text-align: center;
        }
        .stat-num  { color: #60a5fa; font-size: 1.2rem; font-weight: 700; }
        .stat-label{ color: #64748b; font-size: 0.73rem; margin-top: 2px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── 세션 초기화 ───────────────────────────────────────────────────────────────
def init_session():
    defaults = {
        "messages": [],
        "api_key": "",
        "selected_model": "claude-sonnet-4-5",
        "total_tokens": 0,
        "msg_count": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

# ── 지원 모델 목록 ────────────────────────────────────────────────────────────
MODELS = {
    "claude-sonnet-4-5"          : "Claude Sonnet 4.5  ⚡ 권장",
    "claude-opus-4-5"            : "Claude Opus 4.5    🧠 최고성능",
    "claude-haiku-3-5"           : "Claude Haiku 3.5   🚀 초고속",
    "claude-opus-4-0"            : "Claude Opus 4.0    💎 고급",
    "claude-3-7-sonnet-20250219" : "Claude Sonnet 3.7  🔬 고급추론",
}

# ── 시스템 프롬프트 ───────────────────────────────────────────────────────────
SYSTEM_PROMPT = """당신은 AI 융합전공 교수입니다. 학생들의 프로그래밍 학습을 돕는 전문 코딩 멘토 역할을 합니다.

## 전문 분야
- Python, JavaScript, Java, C/C++, SQL 등 주요 프로그래밍 언어
- 머신러닝 / 딥러닝 (TensorFlow, PyTorch, scikit-learn)
- 데이터 분석 (Pandas, NumPy, Matplotlib, Seaborn)
- 웹 개발 (FastAPI, Flask, Streamlit, React)
- 알고리즘 및 자료구조
- AI/ML 파이프라인 설계 및 최적화
- 클라우드 서비스 (AWS, GCP, Azure) 및 MLOps

## 응답 스타일
1. **명확하고 구조적인 설명**: 개념을 단계별로 설명합니다.
2. **실용적인 코드 예시**: 항상 실행 가능한 예시 코드를 제공합니다.
3. **코드 품질 강조**: 가독성, 효율성, 모범 사례를 함께 안내합니다.
4. **학습 유도**: 단순 정답 제공보다 이해를 돕는 방향으로 설명합니다.
5. **한국어 우선**: 기본적으로 한국어로 답변하되, 코드와 기술 용어는 영문을 사용합니다.
6. **오류 디버깅**: 에러 메시지 분석 및 해결책을 체계적으로 제시합니다.

## 코드 응답 형식
- 코드는 반드시 마크다운 코드 블록(
