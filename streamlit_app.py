import streamlit as st
import requests
import json
import time

# API 기본 설정
BASE_API_URL = "https://flow.wowza.co.kr"
FLOW_ID = "cb503cb0-2661-4050-b3cf-09a162e4b463"
# 기본 엔드포인트로 FLOW_ID 사용 (필요시 엔드포인트 이름으로 교체)
ENDPOINT = FLOW_ID

# Streamlit secrets에서 API 키 값을 불러옴
openai_api_key = st.secrets["openai"]["api_key"]
google_search_api_key = st.secrets["google"]["search_api_key"]
google_cse_id = st.secrets["google"]["cse_id"]

# Langflow 구성요소 튜닝 옵션에 API 키들을 포함시킴
TWEAKS = {
    "ChatInput-2B4W6": {},      # Langflow Chat Input 컴포넌트
    "ChatOutput-W1EYG": {},     # Langflow Chat Output 컴포넌트
    "Agent-a0lR8": {"api_key": openai_api_key},  # 예시로 OpenAI API 키 전달
    "GoogleSearchAPICore-cXunR": {
         "api_key": google_search_api_key,
         "cse_id": google_cse_id
    }
}

def run_flow(message: str,
             endpoint: str = ENDPOINT,
             tweaks: dict = TWEAKS,
             output_type: str = "chat",
             input_type: str = "chat",
             api_key: str = None) -> dict:
    """
    Langflow API에 메시지를 보내어 응답을 받아옵니다.
    튜닝 옵션에 ChatInput, ChatOutput 및 기타 구성요소의 API 키를 포함시킵니다.
    """
    api_url = f"{BASE_API_URL}/api/v1/run/{endpoint}"
    payload = {
        "input_value": message,
        "output_type": output_type,
        "input_type": input_type,
        "tweaks": tweaks
    }
    # 필요시 API 키를 헤더에 추가 (예: Langflow에서 별도의 인증을 요구하는 경우)
    headers = {"x-api-key": api_key} if api_key else None
    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()

# 세션 상태에 채팅 내역을 저장 (최초 실행 시 초기화)
if "messages" not in st.session_state:
    st.session_state["messages"] = []

st.title("Langflow 기반 AI 채팅")

# 기존 채팅 내역을 화면에 표시
for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

# 사용자의 채팅 입력 (Streamlit chat input)
user_input = st.chat_input("메시지를 입력하세요:")

if user_input:
    # 사용자의 메시지를 세션에 저장 및 표시
    st.session_state["messages"].append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)
    
    # Langflow ChatInput에 메시지를 전달하고 ChatOutput 응답 받기
    with st.status("AI가 응답 중입니다..."):
        response = run_flow(user_input)
        # 응답에서 Langflow ChatOutput 컴포넌트 값을 추출 (API 응답 구조에 따라 키 이름 조정)
        output_data = response.get("ChatOutput-W1EYG", {})
        ai_response = output_data.get("content")
        if not ai_response:
            # fallback: 기본 응답 키 사용
            ai_response = response.get("response") or response.get("output") or json.dumps(response)
        
        # st.write_stream을 사용해 실시간 스트리밍 효과로 출력 (단어 단위 업데이트)
        stream_text = ""
        for word in ai_response.split():
            stream_text += word + " "
            st.write_stream(stream_text)
            time.sleep(0.1)
    
    # AI의 응답을 세션에 저장 및 최종 표시
    st.session_state["messages"].append({"role": "assistant", "content": stream_text})
    st.chat_message("assistant").write(stream_text)
