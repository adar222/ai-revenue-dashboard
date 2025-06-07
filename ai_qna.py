import streamlit as st
import openai
import pandas as pd

def show_ai_qna(df, api_key):
    st.markdown("### 🤖 Ask AI About Your Data")
    user_question = st.text_input(
        "Ask a question about the filtered data below (English only):",
        key="ai_qna_input"
    )
    if not user_question:
        return

    if not api_key:
        st.warning("Enter your OpenAI API key above to enable AI Q&A.")
        return

    # Show a small sample of the filtered data for the model to reference
    # (Do not send too many rows! Tokens are expensive/limited.)
    preview = df.head(10).to_markdown(index=False)
    prompt = (
        "You are an expert business data analyst. "
        "Given the following data sample and user question, answer as clearly as possible, referencing numbers from the data. "
        f"\n\nDATA SAMPLE:\n{preview}\n\n"
        f"QUESTION: {user_question}"
    )

    try:
        # New OpenAI v1.x client and call
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # You can set this to gpt-4 or gpt-4o if you have access!
            messages=[
                {"role": "system", "content": "You are a business data analyst assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=300,
            temperature=0.2,
        )
        answer = response.choices[0].message.content
        st.success(answer)
    except Exception as e:
        st.error(f"AI request failed:\n\n{e}")
