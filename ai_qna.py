import streamlit as st
import openai
import pandas as pd

def show_ai_qna(df, api_key):
    st.markdown("#### 🤖 Ask AI About Your Data")
    question = st.text_input("Ask a question about the filtered data below (English only):")
    if not question:
        return

    preview = df.head(10).to_markdown(index=False)

    # Modern OpenAI API (for >=1.0.0)
    client = openai.OpenAI(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful business analytics assistant. Reply concisely."},
                {"role": "user", "content": f"Here is a preview of my table:\n{preview}\n\nMy question: {question}"}
            ],
            max_tokens=300,
            temperature=0.2,
        )
        answer = response.choices[0].message.content.strip()
        st.success(answer)
    except Exception as e:
        st.error(f"AI request failed: {e}")
