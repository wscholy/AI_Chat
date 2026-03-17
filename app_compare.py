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

    btn_col1, btn_col2, btn_col3 = st.columns(3)
    with btn_col1:
        run_haiku  = st.button("🚀 Haiku만 실행",       disabled=not question, use_container_width=True)
    with btn_col2:
        run_sonnet = st.button("🧠 Sonnet만 실행",      disabled=not question, use_container_width=True)
    with btn_col3:
        run_both   = st.button("⚖️ 두 모델 동시 실행",  disabled=not question, use_container_width=True, type="primary")

    def call_api(model_name, client, system_prompt, question):
        t0 = time.time()
        try:
            response = client.messages.create(
                model=model_name,
                max_tokens=2048,
                system=system_prompt,
                messages=[{"role": "user", "content": question}]
            )
            return {
                "text": response.content[0].text,
                "elapsed": time.time() - t0,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "error": None,
            }
        except Exception as e:
            return {
                "text": None,
                "elapsed": time.time() - t0,
                "input_tokens": 0,
                "output_tokens": 0,
                "error": str(e),
            }

    def show_result(container, label, result):
        with container:
            if result["error"]:
                st.error("오류: " + result["error"])
            else:
                st.success(result["text"])
                elapsed_str = "{:.2f} 초".format(result["elapsed"])
                st.metric("⏱ " + label + " 응답 시간", elapsed_str)
                token_str = "토큰: 입력 {} / 출력 {}".format(
                    result["input_tokens"], result["output_tokens"]
                )
                st.caption(token_str)

    client = anthropic.Anthropic(api_key=api_key)
    col1, col2 = st.columns(2)

    # ── Haiku만 실행
    if run_haiku:
        with col1:
            with st.spinner("Haiku 실행 중..."):
                r = call_api("claude-haiku-4-5-20251001", client, system_prompt, question)
        show_result(col1, "Haiku", r)

    # ── Sonnet만 실행
    if run_sonnet:
        with col2:
            with st.spinner("Sonnet 실행 중..."):
                r = call_api("claude-sonnet-4-6", client, system_prompt, question)
        show_result(col2, "Sonnet", r)

    # ── 동시 실행 (병렬)
    if run_both:
        results = {}

        def threaded_call(key, model_name):
            results[key] = call_api(model_name, client, system_prompt, question)

        t_haiku  = threading.Thread(target=threaded_call, args=("haiku",  "claude-haiku-4-5-20251001"))
        t_sonnet = threading.Thread(target=threaded_call, args=("sonnet", "claude-sonnet-4-6"))
        t_haiku.start()
        t_sonnet.start()

        # 실시간 경과 시간 표시
        timer_col1, timer_col2 = st.columns(2)
        ph1 = timer_col1.empty()
        ph2 = timer_col2.empty()

        t_start = time.time()
        while t_haiku.is_alive() or t_sonnet.is_alive():
            elapsed = time.time() - t_start
            elapsed_str = "{:.1f}초 (실행 중...)".format(elapsed)

            if not t_haiku.is_alive() and "haiku" in results:
                haiku_val = "✅ {:.2f}초".format(results["haiku"]["elapsed"])
            else:
                haiku_val = elapsed_str

            if not t_sonnet.is_alive() and "sonnet" in results:
                sonnet_val = "✅ {:.2f}초".format(results["sonnet"]["elapsed"])
            else:
                sonnet_val = elapsed_str

            ph1.metric("⏱ Haiku",  haiku_val)
            ph2.metric("⏱ Sonnet", sonnet_val)
            time.sleep(0.1)

        t_haiku.join()
        t_sonnet.join()

        # 완료 후 최종 시간 고정
        ph1.metric("⏱ Haiku 응답 시간",  "{:.2f} 초".format(results["haiku"]["elapsed"]))
        ph2.metric("⏱ Sonnet 응답 시간", "{:.2f} 초".format(results["sonnet"]["elapsed"]))

        show_result(col1, "Haiku",  results["haiku"])
        show_result(col2, "Sonnet", results["sonnet"])

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
