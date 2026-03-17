import streamlit as st
import anthropic
from datetime import datetime

# 페이지 설정
st.set_page_config(
    page_title="중3 생물 단원퀴즈",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
    }
    .quiz-box {
        background-color: #f0f4ff;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 10px 0;
    }
    .answer-correct {
        background-color: #d4edda;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #28a745;
        margin: 10px 0;
    }
    .answer-incorrect {
        background-color: #f8d7da;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #dc3545;
        margin: 10px 0;
    }
    .stats-box {
        background-color: #e7f3ff;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
if "quiz_count" not in st.session_state:
    st.session_state.quiz_count = 0
if "correct_count" not in st.session_state:
    st.session_state.correct_count = 0
if "current_quiz" not in st.session_state:
    st.session_state.current_quiz = None
if "api_key" not in st.session_state:
    st.session_state.api_key = None

# 사이드바 설정
with st.sidebar:
    st.markdown("### ⚙️ 설정")
    
    api_key = st.text_input(
        "Claude API 키 입력",
        type="password",
        help="https://console.anthropic.com에서 발급받으세요"
    )
    
    if api_key:
        st.session_state.api_key = api_key
    
    st.markdown("---")
    
    units = {
        "🔬 세포의 구조와 기능": "세포의 구조, 세포막, 핵, 미토콘드리아, 엽록체",
        "🧬 유전자와 유전": "DNA, 염색체, 유전법칙, 멘델의 법칙",
        "🌱 생식과 발생": "감수분열, 유사분열, 배자발생, 성장",
        "🦠 생명의 다양성": "생물의 분류, 진화, 자연선택",
        "⚙️ 신경과 호르몬": "신경계, 뉴런, 호르몬, 항상성",
        "🫀 순환계와 호흡": "혈액순환, 심장, 폐호흡, 세포호흡",
        "🥗 소화와 영양": "소화기관, 소화효소, 영양소, 대사",
        "🛡️ 면역": "항원, 항체, 특이적 면역, 비특이적 면역"
    }
    
    selected_unit = st.selectbox(
        "📚 학습 단원 선택",
        options=list(units.keys()),
        help="퀴즈를 풀 단원을 선택하세요"
    )
    
    st.markdown("---")
    
    # 통계
    st.markdown("### 📊 학습 통계")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("총 풀이 수", st.session_state.quiz_count)
    with col2:
        if st.session_state.quiz_count > 0:
            accuracy = (st.session_state.correct_count / st.session_state.quiz_count) * 100
            st.metric("정답률", f"{accuracy:.1f}%")
        else:
            st.metric("정답률", "0%")
    
    if st.button("🔄 통계 초기화", use_container_width=True):
        st.session_state.quiz_count = 0
        st.session_state.correct_count = 0
        st.session_state.messages = []
        st.rerun()

# 메인 화면
st.markdown("""
    <div class="main-header">
        <h1>🧬 중학교 3학년 생물 단원퀴즈</h1>
        <p>Claude AI 선생님과 함께 생물 개념을 재미있게 학습해보세요!</p>
    </div>
""", unsafe_allow_html=True)

# API 키 확인
if not st.session_state.api_key:
    st.warning("⚠️ 사이드바에서 Claude API 키를 입력해주세요.")
    st.info("""
    **API 키 발급 방법:**
    1. [Anthropic Console](https://console.anthropic.com)에 접속
    2. 계정 생성 및 로그인
    3. API 키 발급
    4. 발급된 키를 위의 입력칸에 붙여넣기
    """)
    st.stop()

# Claude 클라이언트 초기화
client = anthropic.Anthropic(api_key=st.session_state.api_key)

# 퀴즈 생성 함수
def generate_quiz(unit_name: str, unit_content: str) -> str:
    """새로운 퀴즈를 생성합니다."""
    
    system_prompt = """당신은 중학교 3학년 생물 전담 교사입니다.
    
역할:
- 학생 수준에 맞는 퀴즈를 생성합니다.
- 한 번에 1개의 퀴즈만 제시합니다.
- 퀴즈는 객관식(4지선다형) 또는 단답형입니다.
- 교육적이고 재미있는 문제를 만듭니다.

퀴즈 생성 규칙:
1. 반드시 [퀴즈 시작] 마크로 시작
2. 문제를 명확하게 제시
3. 선택지 또는 답변 형식 표시
4. 한국어로 정확하게 표현
5. 반드시 [퀴즈 끝] 마크로 종료

예시:
[퀴즈 시작]
문제: 미토콘드리아의 주요 기능은?
① 광합성 수행
② ATP 생성을 통한 에너지 공급 ✓
③ 단백질 합성
④ 소화 효소 분비
[퀴즈 끝]"""

    user_message = f"""
다음 단원에서 새로운 퀴즈를 하나 생성해주세요:
단원: {unit_name}
내용: {unit_content}

이전에 출제한 퀴즈:
{chr(10).join([msg['content'][:100] + '...' if len(msg['content']) > 100 else msg['content'] for msg in st.session_state.messages[-6::2]])}

위 퀴즈들과 중복되지 않는 새로운 퀴즈를 만들어주세요."""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )
    
    return response.content[0].text

# 답변 평가 함수
def evaluate_answer(quiz: str, user_answer: str) -> tuple[bool, str]:
    """학생의 답변을 평가합니다."""
    
    system_prompt = """당신은 중학교 3학년 생물 전담 교사입니다.

역할:
- 학생의 퀴즈 답변을 평가합니다.
- 정답 여부를 판정합니다.
- 친절하고 격려적인 피드백을 제공합니다.
- 정답과 해설을 제시합니다.

평가 규칙:
1. 반드시 [평가 시작] 마크로 시작
2. 정답 여부: "정답입니다" 또는 "틀렸습니다"
3. 정답 제시
4. 간단한 해설 (2-3줄)
5. 격려 메시지
6. 반드시 [평가 끝] 마크로 종료"""

    user_message = f"""
다음 퀴즈에 대한 학생의 답변을 평가해주세요:

[퀴즈]
{quiz}

[학생 답변]
{user_answer}

답변을 평가하고 피드백을 제공해주세요."""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=400,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )
    
    response_text = response.content[0].text
    is_correct = "정답입니다" in response_text
    
    return is_correct, response_text

# 메인 콘텐츠
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown(f"### 📖 {selected_unit}")
    units = {
        "🔬 세포의 구조와 기능": "세포의 구조, 세포막, 핵, 미토콘드리아, 엽록체",
        "🧬 유전자와 유전": "DNA, 염색체, 유전법칙, 멘델의 법칙",
        "🌱 생식과 발생": "감수분열, 유사분열, 배자발생, 성장",
        "🦠 생명의 다양성": "생물의 분류, 진화, 자연선택",
        "⚙️ 신경과 호르몬": "신경계, 뉴런, 호르몬, 항상성",
        "🫀 순환계와 호흡": "혈액순환, 심장, 폐호흡, 세포호흡",
        "🥗 소화와 영양": "소화기관, 소화효소, 영양소, 대사",
        "🛡️ 면역": "항원, 항체, 특이적 면역, 비특이적 면역"
    }
    unit_content = units[selected_unit]

with col2:
    st.markdown("### 🎯 현재 상태")
    st.write(f"**문제 풀이**: {st.session_state.quiz_count}")
    st.write(f"**맞춘 문제**: {st.session_state.correct_count}")

# 퀴즈 영역
st.markdown("---")

if st.button("📝 새 퀴즈 생성", use_container_width=True, type="primary"):
    with st.spinner("퀴즈를 생성 중입니다..."):
        try:
            quiz = generate_quiz(selected_unit, unit_content)
            st.session_state.current_quiz = quiz
            st.session_state.messages.append({"role": "assistant", "content": quiz})
            st.rerun()
        except Exception as e:
            st.error(f"❌ 오류 발생: {str(e)}")

# 현재 퀴즈 표시
if st.session_state.current_quiz:
    st.markdown("""<div class="quiz-box">""", unsafe_allow_html=True)
    st.markdown("### 📋 현재 문제")
    st.markdown(st.session_state.current_quiz)
    st.markdown("""</div>""", unsafe_allow_html=True)
    
    # 답변 입력
    st.markdown("### ✍️ 당신의 답변")
    user_answer = st.text_area(
        "답변을 입력하세요",
        placeholder="예) ② 번 선택\n또는\n세포막은 인지질 이중층으로 구성되어 있습니다.",
        label_visibility="collapsed",
        height=80
    )
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("✅ 답변 제출", use_container_width=True, type="primary"):
            if user_answer.strip():
                with st.spinner("답변을 평가 중입니다..."):
                    try:
                        is_correct, feedback = evaluate_answer(
                            st.session_state.current_quiz,
                            user_answer
                        )
                        
                        # 통계 업데이트
                        st.session_state.quiz_count += 1
                        if is_correct:
                            st.session_state.correct_count += 1
                        
                        # 메시지 저장
                        st.session_state.messages.append({"role": "user", "content": user_answer})
                        st.session_state.messages.append({"role": "assistant", "content": feedback})
                        st.session_state.current_quiz = None
                        
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 오류 발생: {str(e)}")
            else:
                st.warning("답변을 입력해주세요.")
    
    with col2:
        if st.button("💡 힌트 요청", use_container_width=True):
            with st.spinner("힌트를 생성 중입니다..."):
                try:
                    hint_prompt = f"""다음 퀴즈에 대해 학생의 답변을 돕는 힌트를 간단히(2줄 이내) 제시해주세요:

[퀴즈]
{st.session_state.current_quiz}

학생이 스스로 답할 수 있도록 도움을 주는 힌트를 제시하세요."""

                    response = client.messages.create(
                        model="claude-haiku-4-5-20251001",
                        max_tokens=200,
                        messages=[{"role": "user", "content": hint_prompt}]
                    )
                    
                    st.info(f"💡 **힌트**: {response.content[0].text}")
                except Exception as e:
                    st.error(f"❌ 오류 발생: {str(e)}")
    
    with col3:
        if st.button("⏭️ 다음 문제", use_container_width=True):
            st.session_state.current_quiz = None
            st.rerun()

# 대화 히스토리 표시
if st.session_state.messages:
    st.markdown("---")
    st.markdown("### 📚 학습 기록")
    
    for i in range(len(st.session_state.messages) - 1, -1, -2):
        if i >= 1:
            quiz = st.session_state.messages[i-1]["content"]
            feedback = st.session_state.messages[i]["content"]
            
            with st.expander(f"📖 문제 {(len(st.session_state.messages) - i) // 2}"):
                st.markdown("**문제:**")
                st.markdown(quiz[:200] + ("..." if len(quiz) > 200 else ""))
                st.markdown("**피드백:**")
                
                if "정답입니다" in feedback:
                    st.markdown(f"""<div class="answer-correct">{feedback}</div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""<div class="answer-incorrect">{feedback}</div>""", unsafe_allow_html=True)

# 푸터
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; font-size: 12px; margin-top: 20px;">
    <p>🧬 중학교 3학년 생물 단원퀴즈 | Claude AI 교사</p>
    <p>Powered by Anthropic Claude Haiku</p>
</div>
""", unsafe_allow_html=True)
