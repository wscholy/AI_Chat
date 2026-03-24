import streamlit as st
import anthropic
import time
import random

# ── 페이지 설정 ──────────────────────────────────────────────
st.set_page_config(
    page_title="PCR 시뮬레이터",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS 스타일 ───────────────────────────────────────────────
st.markdown("""
<style>
    /* 전체 배경 */
    .main { background-color: #0a0e1a; }

    /* DNA 스트랜드 표시 */
    .dna-container {
        background: linear-gradient(135deg, #0d1b2a, #1b2838);
        border: 1px solid #00d4ff33;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        font-family: 'Courier New', monospace;
    }
    .dna-strand {
        font-size: 13px;
        letter-spacing: 3px;
        margin: 4px 0;
        word-break: break-all;
    }
    .strand-template { color: #00d4ff; }
    .strand-complement { color: #ff6b9d; }
    .strand-new { color: #00ff9f; }
    .strand-primer { color: #ffd700; }

    /* 단계 카드 */
    .step-card {
        background: linear-gradient(135deg, #111827, #1f2937);
        border-left: 4px solid;
        border-radius: 8px;
        padding: 16px 20px;
        margin: 8px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .step-denaturation { border-color: #ef4444; }
    .step-annealing    { border-color: #f59e0b; }
    .step-extension    { border-color: #10b981; }
    .step-complete     { border-color: #6366f1; }

    .step-title {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 8px;
    }
    .temp-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        margin-left: 8px;
    }
    .temp-high   { background: #ef444430; color: #fca5a5; border: 1px solid #ef444460; }
    .temp-mid    { background: #f59e0b30; color: #fcd34d; border: 1px solid #f59e0b60; }
    .temp-low    { background: #10b98130; color: #6ee7b7; border: 1px solid #10b98160; }

    /* 사이클 카운터 */
    .cycle-counter {
        background: linear-gradient(135deg, #1e1b4b, #312e81);
        border: 1px solid #6366f1;
        border-radius: 10px;
        padding: 12px 20px;
        text-align: center;
        color: #a5b4fc;
        font-size: 14px;
    }
    .cycle-number {
        font-size: 36px;
        font-weight: 900;
        color: #818cf8;
        display: block;
    }

    /* 증폭 결과 */
    .amplification-result {
        background: linear-gradient(135deg, #064e3b, #065f46);
        border: 1px solid #10b981;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        color: #a7f3d0;
    }
    .copy-number {
        font-size: 32px;
        font-weight: 900;
        color: #34d399;
    }

    /* 채팅 메시지 */
    .chat-message {
        padding: 12px 16px;
        border-radius: 10px;
        margin: 6px 0;
        line-height: 1.6;
    }
    .chat-user {
        background: #1e3a5f;
        border-left: 3px solid #3b82f6;
        color: #bfdbfe;
    }
    .chat-ai {
        background: #1a2e1a;
        border-left: 3px solid #10b981;
        color: #d1fae5;
    }

    /* 진행바 커스텀 */
    .stProgress > div > div { background-color: #10b981; }

    /* 버튼 */
    .stButton > button {
        background: linear-gradient(135deg, #065f46, #047857);
        color: #ecfdf5;
        border: 1px solid #10b981;
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #047857, #065f46);
        border-color: #34d399;
        box-shadow: 0 0 15px #10b98150;
    }

    /* 사이드바 */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1b2a, #111827);
    }
    section[data-testid="stSidebar"] .stMarkdown { color: #94a3b8; }

    /* 탭 */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background: #1f2937;
        border-radius: 8px 8px 0 0;
        color: #9ca3af;
    }
    .stTabs [aria-selected="true"] {
        background: #065f46 !important;
        color: #ecfdf5 !important;
    }
</style>
""", unsafe_allow_html=True)


# ── 유틸리티 함수 ────────────────────────────────────────────
def complement(base: str) -> str:
    """DNA 염기 보완 서열 반환"""
    mapping = {"A": "T", "T": "A", "G": "C", "C": "G"}
    return mapping.get(base.upper(), "N")

def complement_strand(seq: str) -> str:
    return "".join(complement(b) for b in seq)

def reverse_complement(seq: str) -> str:
    return complement_strand(seq)[::-1]

def format_dna(seq: str, chunk: int = 10) -> str:
    """DNA 서열을 보기 좋게 포맷"""
    return " ".join(seq[i:i+chunk] for i in range(0, len(seq), chunk))

def copies_after_n_cycles(n: int) -> int:
    """n 사이클 후 이론적 DNA 복사본 수"""
    return 2 ** n

def simulate_pcr_step(template: str, primer_f: str, primer_r: str, cycle: int, step: str):
    """PCR 단계별 시뮬레이션 데이터 반환"""
    comp = complement_strand(template)
    rc_primer_r = reverse_complement(primer_r)

    if step == "denaturation":
        return {
            "title": "🔥 변성(Denaturation)",
            "temp": "94–98°C",
            "temp_class": "temp-high",
            "step_class": "step-denaturation",
            "description": "고온으로 이중가닥 DNA의 수소결합이 끊어져 단일가닥으로 분리됩니다.",
            "strands": [
                ("5'→3' 주형 가닥", template[:40] + "...", "strand-template"),
                ("3'→5' 보완 가닥", comp[:40][::-1] + "...", "strand-complement"),
            ],
        }
    elif step == "annealing":
        return {
            "title": "🧲 결합(Annealing)",
            "temp": "50–65°C",
            "temp_class": "temp-mid",
            "step_class": "step-annealing",
            "description": "온도가 낮아지면 프라이머가 상보적 서열에 결합합니다.",
            "strands": [
                ("5'→3' 주형 가닥", template[:40] + "...", "strand-template"),
                ("정방향 프라이머 →", primer_f, "strand-primer"),
                ("← 역방향 프라이머", primer_r, "strand-primer"),
            ],
        }
    elif step == "extension":
        new_strand = primer_f + complement_strand(template[len(primer_f):len(template) - len(rc_primer_r)])
        return {
            "title": "🔬 신장(Extension)",
            "temp": "72°C",
            "temp_class": "temp-low",
            "step_class": "step-extension",
            "description": "DNA 중합효소(Taq)가 프라이머 3' 끝에서 뉴클레오타이드를 추가합니다.",
            "strands": [
                ("주형 가닥 (5'→3')", template[:50] + "...", "strand-template"),
                ("새 가닥 합성 중 →", new_strand[:50] + "...", "strand-new"),
            ],
        }
    return {}


# ── 세션 초기화 ──────────────────────────────────────────────
def init_session():
    defaults = {
        "api_key": "",
        "messages": [],
        "current_cycle": 0,
        "total_cycles": 30,
        "pcr_running": False,
        "pcr_complete": False,
        "current_step": None,
        "step_history": [],
        "template_dna": "ATGCGTACGATCGATCGATCGTAGCTAGCTAGCTAGCTAGCTAGCATGCGT",
        "primer_forward": "ATGCGTACG",
        "primer_reverse": "ACGCATGCT",
        "tm_forward": 54,
        "tm_reverse": 52,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()


# ── AI 응답 생성 ─────────────────────────────────────────────
def get_ai_response(user_message: str, context: str = "") -> str:
    """Claude API를 통해 PCR 전문가 응답 생성"""
    if not st.session_state.api_key:
        return "⚠️ API 키를 사이드바에 입력해주세요."

    client = anthropic.Anthropic(api_key=st.session_state.api_key)

    system_prompt = """당신은 분자생물학 전문가이자 PCR(Polymerase Chain Reaction) 교육 전문가입니다.
학생들에게 PCR의 원리, 과정, 응용을 명확하고 흥미롭게 설명합니다.

현재 시뮬레이션 컨텍스트:
""" + context + """

다음 지침을 따르세요:
- 전문 용어는 한국어로 설명하되 영어 원어도 병기
- 분자 수준의 정확한 설명 제공
- 실제 실험실 상황과 연결된 실용적 조언 포함
- 이모지를 적절히 활용해 가독성 향상
- 답변은 간결하되 핵심을 빠짐없이 포함
- 학생이 이해하기 쉬운 비유 활용"""

    messages = []
    for msg in st.session_state.messages[-6:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_message})

    try:
        with client.messages.stream(
            model="claude-sonnet-4-5",
            max_tokens=1024,
            system=system_prompt,
            messages=messages,
        ) as stream:
            return "".join(stream.text_stream)
    except Exception as e:
        return f"❌ API 오류: {str(e)}"


# ── 사이드바 ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🧬 PCR 시뮬레이터")
    st.markdown("---")

    # API 키
    st.markdown("#### 🔑 API 설정")
    api_key_input = st.text_input(
        "Anthropic API Key",
        type="password",
        placeholder="sk-ant-...",
        value=st.session_state.api_key,
    )
    if api_key_input:
        st.session_state.api_key = api_key_input
        st.success("✅ API 키 등록됨")

    st.markdown("---")
    st.markdown("#### ⚙️ PCR 파라미터 설정")

    # 주형 DNA
    template_input = st.text_area(
        "주형 DNA (5'→3')",
        value=st.session_state.template_dna,
        height=80,
        help="분석하려는 DNA 서열을 입력하세요 (A, T, G, C만 사용)",
    )
    if template_input:
        clean = "".join(c for c in template_input.upper() if c in "ATGC")
        st.session_state.template_dna = clean

    # 프라이머
    col1, col2 = st.columns(2)
    with col1:
        pf = st.text_input("정방향 프라이머", value=st.session_state.primer_forward)
        if pf:
            st.session_state.primer_forward = pf.upper()
    with col2:
        pr = st.text_input("역방향 프라이머", value=st.session_state.primer_reverse)
        if pr:
            st.session_state.primer_reverse = pr.upper()

    # 사이클 수
    st.session_state.total_cycles = st.slider(
        "사이클 수", min_value=10, max_value=40, value=st.session_state.total_cycles
    )

    # 온도 설정
    st.markdown("#### 🌡️ 온도 설정")
    denat_temp  = st.slider("변성 온도 (°C)", 90, 98, 95)
    anneal_temp = st.slider("결합 온도 (°C)", 45, 68, 58)
    extend_temp = st.slider("신장 온도 (°C)", 68, 75, 72)

    st.markdown("---")
    st.markdown("#### 📊 현재 상태")
    if st.session_state.pcr_complete:
        copies = copies_after_n_cycles(st.session_state.total_cycles)
        st.markdown(f"""
        <div class="amplification-result">
            <div>최종 복사본 수</div>
            <div class="copy-number">{copies:,}</div>
            <div>({st.session_state.total_cycles} 사이클 완료)</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="cycle-counter">
            <span class="cycle-number">{st.session_state.current_cycle}</span>
            현재 사이클 / {st.session_state.total_cycles}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🔄 시뮬레이션 초기화"):
        st.session_state.current_cycle = 0
        st.session_state.pcr_running   = False
        st.session_state.pcr_complete  = False
        st.session_state.current_step  = None
        st.session_state.step_history  = []
        st.rerun()


# ── 메인 영역 ────────────────────────────────────────────────
st.markdown("# 🧬 PCR 시뮬레이션 & AI 교육 플랫폼")
st.markdown("*Polymerase Chain Reaction — 분자생물학의 혁명적 기술을 단계별로 체험하세요*")

tab1, tab2, tab3, tab4 = st.tabs(
    ["🔬 시뮬레이션", "💬 AI 교육 챗봇", "📈 증폭 그래프", "📚 PCR 개요"]
)


# ══════════════════════════════════════════════════════════════
# 탭 1: 시뮬레이션
# ══════════════════════════════════════════════════════════════
with tab1:
    st.markdown("### PCR 단계별 시뮬레이션")

    # DNA 서열 정보
    template = st.session_state.template_dna
    primer_f = st.session_state.primer_forward
    primer_r = st.session_state.primer_reverse
    comp_template = complement_strand(template)

    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        st.metric("주형 DNA 길이", f"{len(template)} bp")
    with col_info2:
        st.metric("정방향 프라이머 Tm", f"~{st.session_state.tm_forward}°C")
    with col_info3:
        st.metric("역방향 프라이머 Tm", f"~{st.session_state.tm_reverse}°C")

    # DNA 서열 표시
    with st.expander("🧬 현재 DNA 서열 보기", expanded=False):
        st.markdown(f"""
        <div class="dna-container">
            <div class="dna-strand strand-template">
                5' {format_dna(template[:60])}... 3'
            </div>
            <div style="color:#4b5563; font-size:11px; margin:2px 0 2px 20px;">
                ||||||||||||||||||||||||||||
            </div>
            <div class="dna-strand strand-complement">
                3' {format_dna(comp_template[:60])}... 5'
            </div>
        </div>
        <div style="margin-top:8px;">
            <span style="color:#00d4ff; font-size:12px;">■ 주형(Template) &nbsp;</span>
            <span style="color:#ff6b9d; font-size:12px;">■ 보완(Complement) &nbsp;</span>
            <span style="color:#ffd700; font-size:12px;">■ 프라이머(Primer) &nbsp;</span>
            <span style="color:#00ff9f; font-size:12px;">■ 새 가닥(New strand)</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # 단계별 실행 버튼
    col_btn1, col_btn2, col_btn3, col_btn4, col_btn5 = st.columns(5)

    with col_btn1:
        if st.button("🔥 변성", use_container_width=True):
            st.session_state.current_step = "denaturation"
    with col_btn2:
        if st.button("🧲 결합", use_container_width=True):
            st.session_state.current_step = "annealing"
    with col_btn3:
        if st.button("🔬 신장", use_container_width=True):
            st.session_state.current_step = "extension"
            if st.session_state.current_cycle < st.session_state.total_cycles:
                st.session_state.current_cycle += 1
                st.session_state.step_history.append(st.session_state.current_cycle)
    with col_btn4:
        if st.button("▶ 전체 사이클", use_container_width=True):
            st.session_state.pcr_running = True
    with col_btn5:
        if st.button("⏩ 완료 처리", use_container_width=True):
            st.session_state.current_cycle = st.session_state.total_cycles
            st.session_state.pcr_complete = True
            st.session_state.current_step = "complete"

    # 전체 사이클 자동 실행
    if st.session_state.pcr_running and not st.session_state.pcr_complete:
        progress_bar = st.progress(0, text="PCR 진행 중...")
        status_placeholder = st.empty()

        for cycle in range(st.session_state.current_cycle + 1, st.session_state.total_cycles + 1):
            for step_name, step_label in [
                ("denaturation", f"사이클 {cycle} — 변성 중 🔥"),
                ("annealing",    f"사이클 {cycle} — 결합 중 🧲"),
                ("extension",    f"사이클 {cycle} — 신장 중 🔬"),
            ]:
                st.session_state.current_step = step_name
                status_placeholder.info(step_label)
                time.sleep(0.15)

            st.session_state.current_cycle = cycle
            st.session_state.step_history.append(cycle)
            progress = cycle / st.session_state.total_cycles
            progress_bar.progress(progress, text=f"사이클 {cycle}/{st.session_state.total_cycles} 완료")

        st.session_state.pcr_running  = False
        st.session_state.pcr_complete = True
        st.session_state.current_step = "complete"
        status_placeholder.success("✅ PCR 완료!")
        st.rerun()

    # 현재 단계 시각화
    if st.session_state.current_step:
        step = st.session_state.current_step

        if step == "complete":
            copies = copies_after_n_cycles(st.session_state.current_cycle)
            st.markdown(f"""
            <div class="step-card step-complete">
                <div class="step-title" style="color:#a5b4fc;">
                    ✅ PCR 완료!
                    <span class="temp-badge" style="background:#6366f130;color:#c7d2fe;border:1px solid #6366f1;">
                        {st.session_state.current_cycle} 사이클
                    </span>
                </div>
                <p style="color:#c7d2fe;">
                    PCR 증폭이 성공적으로 완료되었습니다.<br>
                    이론적으로 <strong style="color:#a5b4fc;">{copies:,}개</strong>의 DNA 복사본이 생성되었습니다.
                    (2<sup>{st.session_state.current_cycle}</sup> = {copies:,})
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            step_data = simulate_pcr_step(template, primer_f, primer_r, st.session_state.current_cycle, step)
            if step_data:
                st.markdown(f"""
                <div class="step-card {step_data['step_class']}">
                    <div class="step-title" style="color:#f1f5f9;">
                        {step_data['title']}
                        <span class="temp-badge {step_data['temp_class']}">{step_data['temp']}</span>
                    </div>
                    <p style="color:#cbd5e1; margin-bottom:12px;">{step_data['description']}</p>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("**🔍 DNA 서열 시각화:**")
                dna_html = '<div class="dna-container">'
                for label, seq, cls in step_data["strands"]:
                    dna_html += f"""
                    <div style="margin: 6px 0;">
                        <div style="color:#6b7280; font-size:11px; margin-bottom:2px;">{label}</div>
                        <div class="dna-strand {cls}">{format_dna(seq[:60])}</div>
                    </div>"""
                dna_html += "</div>"
                st.markdown(dna_html, unsafe_allow_html=True)

    # 사이클 진행 히스토리
    if st.session_state.step_history:
        st.markdown("---")
        st.markdown("**📋 사이클 진행 현황:**")
        completed = st.session_state.current_cycle
        total = st.session_state.total_cycles
        st.progress(completed / total if total > 0 else 0)

        cols = st.columns(6)
        for i, cycle_num in enumerate(st.session_state.step_history[-12:]):
            with cols[i % 6]:
                copies = copies_after_n_cycles(cycle_num)
                st.markdown(f"""
                <div style="background:#1f2937;border:1px solid #374151;border-radius:6px;
                            padding:8px;text-align:center;margin:2px;">
                    <div style="color:#60a5fa;font-weight:bold;">C{cycle_num}</div>
                    <div style="color:#34d399;font-size:11px;">{copies:,}개</div>
                </div>
                """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# 탭 2: AI 교육 챗봇
# ══════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### 💬 PCR 전문가 AI와 대화하기")

    # 빠른 질문 버튼
    st.markdown("**💡 빠른 질문:**")
    quick_cols = st.columns(4)
    quick_questions = [
        "PCR의 기본 원리를 설명해줘",
        "Taq 중합효소란 무엇인가요?",
        "프라이머 설계 방법을 알려줘",
        "PCR 실패 원인은 뭔가요?",
        "실시간 PCR(qPCR)이란?",
        "PCR의 의학적 응용 사례",
        "변성 온도가 중요한 이유",
        "GC 함량이 Tm에 미치는 영향",
    ]

    for i, (col, q) in enumerate(zip(quick_cols * 2, quick_questions)):
        if i < 4:
            with quick_cols[i]:
                if st.button(q, key=f"quick_{i}", use_container_width=True):
                    st.session_state.messages.append({"role": "user", "content": q})
                    context = f"현재 사이클: {st.session_state.current_cycle}/{st.session_state.total_cycles}, 현재 단계: {st.session_state.current_step}"
                    with st.spinner("AI 응답 생성 중..."):
                        resp = get_ai_response(q, context)
                    st.session_state.messages.append({"role": "assistant", "content": resp})
                    st.rerun()

    quick_cols2 = st.columns(4)
    for i in range(4, 8):
        with quick_cols2[i - 4]:
            q = quick_questions[i]
            if st.button(q, key=f"quick_{i}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": q})
                context = f"현재 사이클: {st.session_state.current_cycle}/{st.session_state.total_cycles}"
                with st.spinner("AI 응답 생성 중..."):
                    resp = get_ai_response(q, context)
                st.session_state.messages.append({"role": "assistant", "content": resp})
                st.rerun()

    st.markdown("---")

    # 채팅 히스토리
    chat_container = st.container()
    with chat_container:
        if not st.session_state.messages:
            st.markdown("""
            <div style="text-align:center; padding:40px; color:#4b5563;">
                <div style="font-size:48px;">🤖</div>
                <div style="font-size:18px; color:#6b7280; margin-top:12px;">
                    PCR 전문가 AI가 준비되었습니다
                </div>
                <div style="font-size:14px; color:#4b5563; margin-top:8px;">
                    위의 빠른 질문을 클릭하거나 아래에 직접 질문을 입력하세요
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    st.markdown(f"""
                    <div class="chat-message chat-user">
                        <strong>👤 나:</strong><br>{msg['content']}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message chat-ai">
                        <strong>🤖 PCR 전문가:</strong><br>{msg['content']}
                    </div>
                    """, unsafe_allow_html=True)

    # 입력창
    with st.form("chat_form", clear_on_submit=True):
        col_input, col_send = st.columns([5, 1])
        with col_input:
            user_input = st.text_input(
                "질문 입력",
                placeholder="PCR에 대해 궁금한 것을 물어보세요...",
                label_visibility="collapsed",
            )
        with col_send:
            submitted = st.form_submit_button("전송 →", use_container_width=True)

    if submitted and user_input.strip():
        st.session_state.messages.append({"role": "user", "content": user_input})
        context = (
            f"현재 시뮬레이션 사이클: {st.session_state.current_cycle}/{st.session_state.total_cycles}, "
            f"단계: {st.session_state.current_step}, "
            f"주형 DNA: {st.session_state.template_dna[:20]}..."
        )
        with st.spinner("🔬 분석 중..."):
            response = get_ai_response(user_input, context)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

    if st.session_state.messages:
        if st.button("🗑️ 대화 초기화", key="clear_chat"):
            st.session_state.messages = []
            st.rerun()


# ══════════════════════════════════════════════════════════════
# 탭 3: 증폭 그래프
# ══════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### 📈 DNA 증폭 곡선")

    import math

    total = st.session_state.total_cycles
    cycles_range = list(range(0, total + 1))
    copies_list  = [2 ** c for c in cycles_range]
    log_copies   = [math.log10(max(c, 1)) for c in copies_list]

    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.markdown("**지수 증폭 곡선 (이론값)**")
        chart_data_exp = {"사이클": cycles_range, "복사본 수": copies_list}
        import pandas as pd
        df_exp = pd.DataFrame(chart_data_exp)
        st.line_chart(df_exp.set_index("사이클"), color="#10b981")

    with col_g2:
        st.markdown("**로그 스케일 증폭 곡선**")
        df_log = pd.DataFrame({"사이클": cycles_range, "log10(복사본 수)": log_copies})
        st.line_chart(df_log.set_index("사이클"), color="#6366f1")

    st.markdown("---")
    st.markdown("**📊 주요 사이클 별 이론적 복사본 수:**")

    key_cycles = [1, 5, 10, 15, 20, 25, 30, 35, 40]
    key_cycles = [c for c in key_cycles if c <= total]

    metric_cols = st.columns(len(key_cycles))
    for col, c in zip(metric_cols, key_cycles):
        copies_val = 2 ** c
        with col:
            if copies_val >= 1_000_000:
                display = f"{copies_val / 1_000_000:.1f}M"
            elif copies_val >= 1_000:
                display = f"{copies_val / 1_000:.0f}K"
            else:
                display = str(copies_val)
            st.metric(f"사이클 {c}", display)

    st.markdown("---")
    st.markdown("**🔢 효율에 따른 실제 증폭량 비교:**")

    efficiencies = [0.90, 0.95, 0.98, 1.00]
    eff_data = {}
    sample_cycles = list(range(0, total + 1, max(1, total // 10)))

    for eff in efficiencies:
        eff_data[f"효율 {int(eff*100)}%"] = [(1 + eff) ** c for c in sample_cycles]

    df_eff = pd.DataFrame(eff_data, index=sample_cycles)
    df_eff.index.name = "사이클"
    st.line_chart(df_eff)

    st.info("""
    💡 **효율 설명**: 이상적인 PCR에서는 매 사이클마다 DNA가 정확히 2배로 증폭됩니다(효율 100%).
    실제 실험에서는 90~98% 효율이 일반적이며, 프라이머 특이성, 효소 활성, 반응 조건에 따라 달라집니다.
    """)


# ══════════════════════════════════════════════════════════════
# 탭 4: PCR 개요
# ══════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### 📚 PCR(중합효소 연쇄반응) 개요")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("""
        #### 🔬 PCR이란?
        PCR(Polymerase Chain Reaction, 중합효소 연쇄반응)은 **특정 DNA 서열을 시험관 내에서 
        기하급수적으로 증폭**시키는 분자생물학 기술입니다.

        1983년 **Kary Mullis**가 개발하여 1993년 노벨 화학상을 수상했습니다.

        ---
        #### 🧪 필수 구성 요소

        | 구성요소 | 역할 |
        |---------|------|
        | 주형 DNA | 증폭 대상 서열 |
        | DNA 중합효소 (Taq) | 새 가닥 합성 |
        | 프라이머 (×2) | 합성 시작점 제공 |
        | dNTPs | 뉴클레오타이드 재료 |
        | MgCl₂ | 효소 보조인자 |
        | 완충액 | 최적 pH 유지 |

        ---
        #### 🌡️ 3단계 과정
        """)

        steps_info = [
            ("🔥 변성 (Denaturation)", "94–98°C / 20–30초",
             "이중가닥 DNA의 수소결합이 끊어져 두 개의 단일가닥으로 분리"),
            ("🧲 결합 (Annealing)", "50–65°C / 20–40초",
             "프라이머가 상보적 서열에 결합하여 합성 시작점 형성"),
            ("🔬 신장 (Extension)", "72°C / 1분/kb",
             "Taq 중합효소가 프라이머 3' 끝에서 새 DNA 가닥 합성"),
        ]

        for title, temp, desc in steps_info:
            st.markdown(f"""
            <div class="step-card step-{'denaturation' if '변성' in title else 'annealing' if '결합' in title else 'extension'}">
                <div style="font-weight:bold; color:#f1f5f9; margin-bottom:4px;">
                    {title} <code style="font-size:11px;">{temp}</code>
                </div>
                <div style="color:#94a3b8; font-size:13px;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    with col_b:
        st.markdown("""
        #### 🏥 PCR의 응용 분야

        **의학 진단**
        - 감염병 진단 (COVID-19, HIV, 결핵 등)
        - 유전질환 검사
        - 암 유전자 분석

        **법의학**
        - DNA 지문 분석
        - 범죄 수사
        - 신원 확인

        **연구 분야**
        - 유전자 클로닝
        - 돌연변이 검출
        - 유전자 발현 분석 (RT-PCR)

        **농업/식품**
        - GMO 검출
        - 병원체 진단
        - 품종 판별

        ---
        #### 📐 프라이머 설계 원칙

        | 원칙 | 권장값 |
        |------|--------|
        | 길이 | 18–25 bp |
        | GC 함량 | 40–60% |
        | Tm 차이 | < 5°C |
        | 3' 말단 | G 또는 C |
        | 자기상보성 | 없어야 함 |
        | 이량체 형성 | 없어야 함 |

        ---
        #### ⚗️ PCR 변형 기술

        - **RT-PCR**: RNA → cDNA 변환 후 증폭
        - **qPCR**: 실시간 정량 분석
        - **Multiplex PCR**: 여러 표적 동시 증폭
        - **Nested PCR**: 민감도/특이도 향상
        - **LAMP**: 등온 증폭 (PCR 대안)
        """)

        st.markdown("---")
        st.markdown("#### ⚠️ PCR 실패 주요 원인")
        failure_data = {
            "원인": ["프라이머 이량체", "비특이 결합", "주형 오염", "효소 불활성화", "dNTP 고갈"],
            "해결책": ["프라이머 재설계", "결합 온도 상향", "음성 대조군 포함", "냉동 보관", "농도 최적화"],
        }
        import pandas as pd
        st.dataframe(pd.DataFrame(failure_data), hide_index=True, use_container_width=True)


# ── 푸터 ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#374151; font-size:12px; padding:10px;">
    🧬 PCR 시뮬레이션 플랫폼 | Claude claude-sonnet-4-5 기반 AI 교육 시스템<br>
    분자생물학 학습을 위한 인터랙티브 도구
</div>
""", unsafe_allow_html=True)
