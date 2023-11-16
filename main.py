from openai import OpenAI
import streamlit as st
import os

st.set_page_config(
    page_title="Yungu Highschool Chatbot",
    page_icon=":robot:",
    layout="wide"
)
st.title("Yungu Highschool Chatbot")

@st.cache_resource
def get_model():
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY")
    )

    with open("./prompt", 'r') as file:
        prompt = file.read()

    return client, prompt


client, prompt = get_model()
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "user",
        "content": prompt
    }]

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo-16k-0613"


col1, col2 = st.columns([0.3, 0.7])

with col1:
    pre_prompt = st.text_area("Setup", st.session_state.messages[0]["content"],height=500)
    st.session_state.messages[0]["content"] = pre_prompt

with col2:
    for message in st.session_state.messages[1:]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    with st.chat_message(name="user", avatar="user"):
        input_placeholder = st.empty()
    with st.chat_message(name="assistant", avatar="assistant"):
        message_placeholder = st.empty()

    if prompt_text := st.text_input("Chat:"):
        input_placeholder.markdown(prompt_text)
        past_key_values = st.session_state.past_key_values
        history = st.session_state.messages

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

