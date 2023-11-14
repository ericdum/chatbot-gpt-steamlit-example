from openai import OpenAI
import streamlit as st
import os

st.set_page_config(layout="wide")
st.title("Yungu Highschool Chatbot")

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo-16k-0613"

with open("./prompt", 'r') as file:
    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "user",
            "content": file.read()
        }]

col1, col2 = st.columns([0.3, 0.7])

with col1:
    pre_prompt = st.text_area("Setup", st.session_state.messages[0]["content"],height=500)
    st.session_state.messages[0]["content"] = pre_prompt

with col2:
    for message in st.session_state.messages[1:]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.text_input("Chat:"):
        if len(st.session_state.messages) < 2 or prompt != st.session_state.messages[-2]['content']:
            st.session_state.messages.append({"role": "user", "content": prompt})
            # with st.chat_message("user"):
            #     st.markdown(prompt)

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""

                for response in client.chat.completions.create(
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ],
                    model=st.session_state["openai_model"],
                    stream=True,
                    temperature=0.5
                ):
                    full_response += response.choices[0].delta.content or ""
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

