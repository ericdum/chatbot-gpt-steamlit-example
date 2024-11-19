from openai import OpenAI
import streamlit as st
import streamlit.components.v1 as components
import os

query_params = st.query_params
if 'student' in query_params:
    selected_user = query_params['student'].lower()
else:
    #selected_user = st.selectbox("Talk to:", list(user_data.keys()))
    selected_user = "jerry"

st.set_page_config(
    page_title="云谷学校“如何指导学生长期项目”面谈模拟器",
    page_icon="https://yungu.org/favicon.ico",
    layout="wide"
)

custom_style = """
<style>
.block-container {
  padding-top: 2rem;
}
iframe {
display:none;
}
</style>
"""
st.markdown(custom_style, unsafe_allow_html=True)
#st.markdown('<div style="position:absolute;width:100%;top:0;left:0;">this is a logo</div>', unsafe_allow_html=True)
st.title("云谷学校“如何指导学生长期项目”面谈模拟器")


@st.cache_resource
def get_model():
  client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY")
  )

  prompts = {}
  avatars = {}
  for name in os.listdir('./prompts'):
    with open("./prompts/"+name, 'r') as file:
      prompts[name] = file.read()

  for name in os.listdir('./avatar'):
    with open("./avatar/"+name, 'r') as file:
      avatars[name] = "data:image/jpeg;base64,"+file.read()
  
  return client, prompts, avatars


client, prompts, avatars = get_model()
prompt = prompts[selected_user]
avatar = avatars[selected_user]

if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "user",
        "content": prompt
    }]

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o"


col1, col2 = st.columns([0.3, 0.7])
prompt_text = st.chat_input("Chat:")


with col1:
    st.image(avatar, caption=selected_user, use_container_width=True)
    #pre_prompt = st.text_area("Setup", st.session_state.messages[0]["content"],height=500)
    #st.session_state.messages[0]["content"] = pre_prompt

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
            temperature=0.5,
            max_tokens=8192
        ):
            full_response += response.choices[0].delta.content or ""
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})


components.html( """
<script>
window.addEventListener('beforeunload', function (e) {
alert("请勿关闭页面，请联系指导老师")
    // 取消事件的默认动作
    e.preventDefault();
    // Chrome 需要设置 returnValue
    e.returnValue = "您是否想要关闭网页？请联系指导老师";
});
</script>
""")
