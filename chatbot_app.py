import streamlit as st
import anthropic
import time

st.set_page_config(page_title="챗봇 코드 생성기", page_icon="🛠️", layout="wide")

# ── 세션 초기화
for key, default in {
    "messages": [],
    "generated_codes": [],
    "current_code_idx": 0,
    "spec": {},
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ══════════════════════════════════════════════════════
# 사이드바 — 설정 패널
# ══════════════════════════════════════════════════════
with st.sidebar:
    st.title("🛠️ 챗봇 코드 생성기")
    st.caption("AI 융합 전공 실습")
    st.divider()

    api_key = st.text_input("🔑 Anthropic API 키", type="password", placeholder="sk-ant-...")

    st.subheader("⚙️ 모델 선택")
    model = st.radio(
        "사용할 모델",
        options=["claude-haiku-4-5-20251001", "claude-sonnet-4-6"],
        format_func=lambda x: "🚀 Claude Haiku  (빠름·저렴)" if "haiku" in x else "🧠 Claude Sonnet (강력·상세)",
        label_visibility="collapsed",
    )

    st.divider()
    st.subheader("📋 챗봇 사양 입력")

    role = st.text_area(
        "① 역할 부여 (시스템 프롬프트)",
        placeholder="예: 당신은 친절한 여행 도우미입니다. 한국어로 답변하세요.",
        height=90,
    )
    main_request = st.text_area(
        "② 주요 요청 사항",
        placeholder="예: 여행지 추천, 일정 작성, 숙소·항공 정보 안내 기능",
        height=90,
    )
    dev_env = st.selectbox(
        "③ 코드 개발 환경 및 언어",
        ["Python + Streamlit", "Python + Gradio", "Python (CLI)", "Node.js + Express"],
    )
    service_target = st.text_input(
        "④ 서비스 배포 환경",
        value="Streamlit Cloud (GitHub 연동)",
        disabled=True,
    )

    st.divider()
    gen_btn = st.button(
        "✨ 코드 생성하기",
        type="primary",
        use_container_width=True,
        disabled=not api_key,
    )
    clear_btn = st.button("🗑️ 대화 초기화", use_container_width=True)

# ══════════════════════════════════════════════════════
# 메인 영역 — 좌: 대화창 / 우: 코드 뷰어
# ══════════════════════════════════════════════════════
chat_col, code_col = st.columns([1, 1], gap="medium")

# ── 대화 초기화
if clear_btn:
    st.session_state.messages = []
    st.session_state.generated_codes = []
    st.session_state.current_code_idx = 0
    st.rerun()

# ── 코드 생성 시스템 프롬프트
SYSTEM_PROMPT = """당신은 Python Streamlit 챗봇 코드를 전문으로 생성하는 AI 개발자입니다.

규칙:
1. 요청에 맞는 완전하고 실행 가능한 코드를 작성합니다.
2. 코드는 반드시 ```python ... ``` 블록 안에 작성합니다.
3. 코드 블록 앞뒤로 간단한 설명을 한국어로 제공합니다.
4. requirements.txt 내용도 코드 블록 뒤에 별도로 제시합니다.
5. GitHub + Streamlit Cloud 배포를 전제로 합니다.
6. API 키는 st.text_input(type="password")로 입력받습니다.
7. 수정 요청 시 전체 코드를 다시 작성합니다."""

def extract_code(text):
    """응답에서 ```python 블록 추출"""
    import re
    pattern = r"```python\s*(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    return matches[0].strip() if matches else None

def build_spec_message():
    """사양 입력값을 첫 요청 메시지로 변환"""
    return f"""다음 사양으로 Streamlit 챗봇 코드를 작성해주세요.

- **역할 부여**: {role or '(미입력)'}
- **주요 기능**: {main_request or '(미입력)'}
- **개발 환경**: {dev_env}
- **배포 환경**: {service_target}
- **사용 모델**: {model}

위 사양을 반영한 완전한 실행 코드를 작성해주세요."""

def stream_response(client, messages):
    """스트리밍으로 응답 받기"""
    full_text = ""
    placeholder = st.empty()
    with client.messages.stream(
        model=model,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=messages,
    ) as stream:
        for text in stream.text_stream:
            full_text += text
            placeholder.markdown(full_text + "▌")
    placeholder.markdown(full_text)
    return full_text

# ══════════════════════════════════════
# 왼쪽: 대화창
# ══════════════════════════════════════
with chat_col:
    st.subheader("💬 대화창")
    st.caption("코드 생성 후 수정 요청을 이어서 입력하세요")

    # 대화 기록 표시
    chat_container = st.container(height=480)
    with chat_container:
        if not st.session_state.messages:
            st.info("왼쪽 패널에서 사양을 입력하고 **코드 생성하기**를 눌러주세요.")
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                # assistant 메시지에서 코드 블록은 접어서 표시
                if msg["role"] == "assistant":
                    import re
                    parts = re.split(r"(```python.*?```)", msg["content"], flags=re.DOTALL)
                    for part in parts:
                        if part.startswith("```python"):
                            with st.expander("📄 생성된 코드 보기", expanded=False):
                                st.code(part[9:-3].strip(), language="python")
                        else:
                            if part.strip():
                                st.markdown(part)
                else:
                    st.markdown(msg["content"])

    # 사양 기반 코드 생성
    if gen_btn:
        if not role and not main_request:
            st.warning("역할 부여 또는 주요 요청 사항을 입력해주세요.")
        else:
            user_msg = build_spec_message()
            st.session_state.messages.append({"role": "user", "content": user_msg})

            client = anthropic.Anthropic(api_key=api_key)
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(user_msg)
                with st.chat_message("assistant"):
                    response_text = stream_response(
                        client,
                        [{"role": m["role"], "content": m["content"]}
                         for m in st.session_state.messages],
                    )

            st.session_state.messages.append({"role": "assistant", "content": response_text})
            code = extract_code(response_text)
            if code:
                st.session_state.generated_codes.append(code)
                st.session_state.current_code_idx = len(st.session_state.generated_codes) - 1
            st.rerun()

    # 수정 요청 입력창
    if st.session_state.messages:
        user_input = st.chat_input("수정 요청을 입력하세요 (예: '버튼 색을 파란색으로 바꿔줘')")
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            client = anthropic.Anthropic(api_key=api_key)

            with chat_container:
                with st.chat_message("user"):
                    st.markdown(user_input)
                with st.chat_message("assistant"):
                    response_text = stream_response(
                        client,
                        [{"role": m["role"], "content": m["content"]}
                         for m in st.session_state.messages],
                    )

            st.session_state.messages.append({"role": "assistant", "content": response_text})
            code = extract_code(response_text)
            if code:
                st.session_state.generated_codes.append(code)
                st.session_state.current_code_idx = len(st.session_state.generated_codes) - 1
            st.rerun()

# ══════════════════════════════════════
# 오른쪽: 코드 뷰어
# ══════════════════════════════════════
with code_col:
    st.subheader("📄 생성된 코드")

    if not st.session_state.generated_codes:
        st.info("코드를 생성하면 여기에 표시됩니다.")
    else:
        total = len(st.session_state.generated_codes)

        # 버전 네비게이션
        nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
        with nav_col1:
            if st.button("◀ 이전", disabled=st.session_state.current_code_idx == 0, use_container_width=True):
                st.session_state.current_code_idx -= 1
                st.rerun()
        with nav_col2:
            idx = st.session_state.current_code_idx
            st.markdown(
                f"<div style='text-align:center;padding:6px;font-weight:600'>"
                f"버전 {idx + 1} / {total}</div>",
                unsafe_allow_html=True,
            )
        with nav_col3:
            if st.button("다음 ▶", disabled=st.session_state.current_code_idx == total - 1, use_container_width=True):
                st.session_state.current_code_idx += 1
                st.rerun()

        current_code = st.session_state.generated_codes[st.session_state.current_code_idx]

        # 복사 버튼 + 다운로드 버튼
        copy_col, dl_col = st.columns(2)
        with copy_col:
            # 클립보드 복사 (JavaScript)
            escaped = current_code.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
            copy_js = f"""
            <button onclick="
                navigator.clipboard.writeText(`{escaped}`).then(() => {{
                    this.innerText = '✅ 복사됨!';
                    setTimeout(() => this.innerText = '📋 코드 복사', 1500);
                }});
            " style="
                width:100%; padding:8px; border-radius:6px;
                background:#0D9488; color:white; border:none;
                font-size:14px; cursor:pointer; font-weight:600;
            ">📋 코드 복사</button>
            """
            st.components.v1.html(copy_js, height=44)

        with dl_col:
            st.download_button(
                "⬇️ .py 다운로드",
                data=current_code,
                file_name="chatbot_app.py",
                mime="text/x-python",
                use_container_width=True,
            )

        # 코드 표시
        st.code(current_code, language="python", line_numbers=True)

        # requirements.txt 힌트 + 다운로드
        with st.expander("📦 requirements.txt"):
            req_content = "anthropic\nstreamlit\n"
            st.code(req_content, language="text")
            st.download_button(
                label="⬇️ requirements.txt 다운로드",
                data=req_content,
                file_name="requirements.txt",
                mime="text/plain",
                use_container_width=True,
            )
            st.caption("GitHub 저장소 루트에 이 파일을 포함해야 Streamlit Cloud에서 자동 설치됩니다.")

        # GitHub 배포 안내
        with st.expander("🚀 배포 방법 (GitHub → Streamlit Cloud)"):
            st.markdown("""
1. GitHub 저장소에 `chatbot_app.py`, `requirements.txt` 업로드
2. [share.streamlit.io](https://share.streamlit.io) 접속 → GitHub 로그인
3. **New app** → 저장소 선택 → Main file: `chatbot_app.py`
4. **Deploy** 클릭 → 자동 빌드 (1~2분)
5. 생성된 URL 공유!

> ⚠️ API 키는 절대 코드에 넣지 마세요. 앱 화면에서 직접 입력하거나 Streamlit Secrets 사용.
""")
