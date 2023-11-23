from openai import OpenAI
import streamlit as st
import os

st.set_page_config(
    page_title="云谷学校“如何指导学生长期项目”面谈模拟器",
    page_icon=":robot:",
    layout="wide"
)
st.title("云谷学校“如何指导学生长期项目”面谈模拟器")


@st.cache_resource
def load_avatar():
  with open("./avatar/jerry", 'r') as file:
    jerry = file.read()
  with open("./avatar/spike", 'r') as file:
    spike = file.read()
  with open("./avatar/tom", 'r') as file:
    tom = file.read()

  user_data = {
    "Jerry": "data:image/jpeg;base64,"+jerry,
    "Spike": "data:image/jpeg;base64,"+spike,
    "Tom": "data:image/jpeg;base64,"+tom,
  }

  return user_data


@st.cache_resource
def get_model():
  client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY")
  )

  with open("./prompt", 'r') as file:
    prompt = file.read()

    return client, prompt


client, prompt = get_model()
user_data = load_avatar()

if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "user",
        "content": prompt
    }]

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo-16k-0613"


col1, col2 = st.columns([0.3, 0.7])
prompt_text = st.chat_input("Chat:")

with col1:
    query_params = st.experimental_get_query_params()
    if 'student' in query_params:
        selected_user = query_params['student'][0]
    else:
        selected_user = st.selectbox("Talk to:", list(user_data.keys()))
    st.image(user_data[selected_user], caption=selected_user, use_column_width=True)
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

    if prompt_text:
        input_placeholder.markdown(prompt_text)
        #if len(st.session_state.messages) < 2 or prompt != st.session_state.messages[-2]['content']:
        st.session_state.messages.append({"role": "user", "content": prompt_text})

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

