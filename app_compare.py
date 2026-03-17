import streamlit as st
import anthropic
import time
import threading

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
    question = st.text_area(
        "비교할 질문을 입력하세요",
        placeholder="예: 머신러닝과 딥러닝의 차이를 설명해줘",
        height=80
    )

    if st.button("🔍 두 모델 동시 실행", type="primary", disabled=not question):
        client = anthropic.Anthropic(api_key=api_key)

        # 결과를 담을 딕셔너리 (스레드 간 공유)
        results = {}

        def call_model(model_key, model_name):
            t0 = time.time()
            try:
                response = client.messages.create(
                    model=model_name,
                    max_tokens=2048,   # ← 512 → 2048으로 수정 (Sonnet 응답 잘림 방지)
                    system=system_prompt,
                    messages=[{"role": "user", "content": question}]
                )
                results[model_key] = {
                    "text": response.content[0].text,
                    "elapsed": time.time() - t0,
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "error": None,
                }
            except Exception as e:
                results[model_key] = {
                    "text": None,
                    "elapsed": time.time() - t0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "error": str(e),
                }

        # 두 모델을 병렬 실행 → 실제 응답 시간을 정확히 비교할 수 있음
        with st.spinner("두 모델 동시 실행 중..."):
            t_haiku  = threading.Thread(target=call_model, args=("haiku",  "claude-haiku-4-5-20251001"))
            t_sonnet = threading.Thread(target=call_model, args=("sonnet", "claude-sonnet-4-6"))
            t_haiku.start()
            t_sonnet.start()
            t_haiku.join()
            t_sonnet.join()

        # 결과 표시
        col1, col2 = st.columns(2)

        with col1:
            r = results["haiku"]
            if r["error"]:
                st.error(f"오류: {r['error']}")
            else:
                st.success(r["text"])
                st.metric("응답 시간", f"{r['elapsed']:.1f}초")
                st.caption(f"토큰: 입력 {r['input_tokens']} / 출력 {r['output_tokens']}")

        with col2:
            r = results["sonnet"]
            if r["error"]:
                st.error(f"오류: {r['error']}")
            else:
                st.success(r["text"])
                st.metric("응답 시간", f"{r['elapsed']:.1f}초")
                st.caption(f"토큰: 입력 {r['input_tokens']} / 출력 {r['output_tokens']}")

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
