import streamlit as st

st.title("GenAI Academic Mentor")

question = st.text_input("Ask your doubt:")

if st.button("Get Explanation"):
    if question != "":
        st.write("📘 Simple Explanation:")
        st.write("Let me explain this in an easy way...")

        # Simple confusion detection
        if "confuse" in question.lower() or "don't understand" in question.lower():
            st.warning("You seem confused 😟")
            st.write("Let me explain more slowly with an example.")
    else:
        st.write("Please enter a question")
