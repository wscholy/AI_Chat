import streamlit as st
import anthropic

st.set_page_config(page_title="모델 비교 실습", page_icon="⚖️", layout="wide")
st.title("⚖️ Claude 모델 비교 실습")
st.caption("같은 질문 → 다른 모델 → 결과 비교 | AI 융합 전공")

api_key = st.text_input("Anthropic API 키", type="password", placeholder="sk-ant-...")

if api_key:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🚀 Claude Haiku")
        st.caption("빠르고 저렴 — 간단한 작업에 적합")
    with col2:
        st.subheader("🧠 Claude Sonnet")
        st.caption("더 강력 — 복잡한 추론에 적합")

    system_prompt = st.text_input(
        "역할 설정",
        value="당신은 대학교 AI 융합 전공 수업의 조교입니다. 학생 수준에 맞게 한국어로 답변하세요."
    )

    question = st.text_area("비교할 질문을 입력하세요", placeholder="예: 머신러닝과 딥러닝의 차이를 설명해줘", height=80)

    if st.button("🔍 두 모델 동시 실행", type="primary", disabled=not question):
        client = anthropic.Anthropic(api_key=api_key)
        col1, col2 = st.columns(2)

        import time

        with col1:
            with st.spinner("Haiku 생각 중..."):
                t0 = time.time()
                r1 = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=512,
                    system=system_prompt,
                    messages=[{"role": "user", "content": question}]
                )
                t1 = time.time()
            st.success(r1.content[0].text)
            st.metric("응답 시간", f"{t1-t0:.1f}초")
            st.caption(f"토큰: 입력 {r1.usage.input_tokens} / 출력 {r1.usage.output_tokens}")

        with col2:
            with st.spinner("Sonnet 생각 중..."):
                t0 = time.time()
                r2 = client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=512,
                    system=system_prompt,
                    messages=[{"role": "user", "content": question}]
                )
                t1 = time.time()
            st.success(r2.content[0].text)
            st.metric("응답 시간", f"{t1-t0:.1f}초")
            st.caption(f"토큰: 입력 {r2.usage.input_tokens} / 출력 {r2.usage.output_tokens}")

        st.divider()
        st.subheader("📊 토론: 어떤 모델이 더 나았나요?")
        st.markdown("""
        - **정확성**: 어느 쪽이 더 정확한가?
        - **깊이**: 어느 쪽이 더 상세한가?
        - **속도**: 체감 속도 차이는?
        - **활용 상황**: 각 모델이 적합한 상황은?
        """)
else:
    st.info("API 키를 입력하면 비교 실습을 시작할 수 있습니다.")
    with st.expander("💡 추천 비교 질문 예시"):
        st.markdown("""
        1. "파이썬이란 무엇인지 초보자에게 설명해줘"
        2. "기후 변화의 원인 3가지를 간단히 설명해줘"
        3. "시 한 편 써줘. 봄에 대한 내용으로."
        4. "피보나치 수열을 파이썬으로 구현하는 코드 작성해줘"
        5. "내가 오늘 점심으로 뭘 먹어야 할지 추천해줘"
        """)
