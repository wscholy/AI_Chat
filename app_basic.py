import streamlit as st
import anthropic

st.set_page_config(page_title="Claude 챗봇", page_icon="🤖")
st.title("🤖 Claude AI 챗봇")
st.caption("Anthropic API 연결 실습 — AI 융합 전공")

# API 키 입력
api_key = st.text_input("Anthropic API 키를 입력하세요", type="password", placeholder="sk-ant-...")

if api_key:
    # 모델 선택
    model = st.selectbox(
        "모델 선택",
        ["claude-haiku-4-5-20251001", "claude-sonnet-4-6"],
        help="Haiku = 빠르고 저렴, Sonnet = 더 똑똑하고 강력"
    )

    # 시스템 프롬프트 (역할 부여)
    system_prompt = st.text_area(
        "AI 역할 설정 (시스템 프롬프트)",
        value="당신은 친절한 AI 조교입니다. 한국어로 간결하게 답변하세요.",
        height=80
    )

    # 대화 기록 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 대화 기록 표시
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # 사용자 입력
    if prompt := st.chat_input("메시지를 입력하세요..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # Claude API 호출
        with st.chat_message("assistant"):
            with st.spinner("생각 중..."):
                client = anthropic.Anthropic(api_key=api_key)
                response = client.messages.create(
                    model=model,
                    max_tokens=1024,
                    system=system_prompt,
                    messages=st.session_state.messages
                )
                reply = response.content[0].text
                st.write(reply)
                # 토큰 사용량 표시
                st.caption(f"토큰 사용: 입력 {response.usage.input_tokens} / 출력 {response.usage.output_tokens}")

        st.session_state.messages.append({"role": "assistant", "content": reply})

    # 대화 초기화 버튼
    if st.session_state.messages:
        if st.button("대화 초기화"):
            st.session_state.messages = []
            st.rerun()
else:
    st.info("👆 API 키를 입력하면 챗봇이 시작됩니다.")
    st.markdown("""
    **API 키가 없다면?**
    - [console.anthropic.com](https://console.anthropic.com) 에서 발급
    - 강사가 제공하는 키를 사용
    """)
