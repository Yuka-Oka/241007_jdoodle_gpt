# 2024/10/03
# cd Library/Mobile\ Documents/com~apple~CloudDocs/stream241003_jd

import openai
import os
import streamlit as st
import subprocess
from io import StringIO
import tempfile

import requests

st.title("⭕️ JDoodle")
st.title("⭕️ OpenAI")

JDoodle_Client_ID = st.secrets["client_id"]
JDoodle_Client_Secret = st.secrets["client_secret"]
openai.api_key = st.secrets["api_key"]

# session_satte "openai_model"作成
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4"

# ファイルアップロード（サイドバー）
uploaded_file = st.sidebar.file_uploader("Javaファイルをアップロードしてください", type=["java"])

# 関数response_generation：OpenAI APIを用いて応答生成
def response_generation(error_code):
    # プロンプト
    self_sys_prompt = "エラー文の解説を1行で簡単に説明してください"

    # 応答格納用変数
    full_response = ""
    message_placeholder = st.empty()

    for response in openai.ChatCompletion.create(
        model = st.session_state["openai_model"],
        messages = [
            {"role": "system", "content": self_sys_prompt},
            {"role": "user", "content": error_code}
        ],
        stream = True,
    ):
        full_response += response.choices[0].delta.get("content", "")
        message_placeholder.markdown(full_response + " ")
    message_placeholder.markdown(full_response)


if uploaded_file:
    java_code = uploaded_file.read().decode("utf-8")
    
    # JDoodle APIにリクエストを送信
    api_url = "https://api.jdoodle.com/v1/execute"
    data = {
        "script": java_code,
        "language": "java",
        "versionIndex": "3",  # Javaバージョン（例: 3 = JDK 1.8.0_66）
        "clientId": JDoodle_Client_ID,
        "clientSecret": JDoodle_Client_Secret
    }

    response = requests.post(api_url, json=data)
    
    if response.status_code == 200:
        result = response.json()
        
        output = result.get("output", "No output")
        st.code(output, language="text")

        # コンパイルエラーのチェック
        if "error" in result['output'].lower():
            st.write("コンパイルエラー発生！")
            content = java_code + result['output']
            print(content)
            response_generation(content)
        else:
            print("Compilation successful")
        
    else:
        st.write(f"Error: {response.status_code}")
