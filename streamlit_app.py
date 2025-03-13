import streamlit as st

st.title("🎈 구본우에게 고해성사")
st.write(
    "익명으로 고해성사할 수 있는 절호의 기회! 지금 말하면 **모두 욘서~**"
)

with st.form("confession_form"):
    st.text_area(
        label="**👇요기에 작성해!**",
        placeholder="뭐든 작성해봐! Shift+Enter는 줄바꿈이지롱~"
    )
    submitted = st.form_submit_button(label="제출하기")

    if submitted:
        st.success("성공적으로 제출되었습니다! 모두 욘서~✨")