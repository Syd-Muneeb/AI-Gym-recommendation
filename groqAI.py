import streamlit as st
from groq import Groq

def get_groq_client():
    # Groq API key - HARDCODED
    api_key = "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" # Replace with your actual Groq API key if you want it to work
    if not api_key:
        st.error("Groq API key not found. Please set it in the .env file or hardcode it.") # Adjusted message
        return None
    return Groq(api_key=api_key)

def analyze_routine_with_groq(routine_df):
    client = get_groq_client()
    if not client:
        return "Error: Groq client not initialized due to missing API key."

    routine_summary = "\n".join([f"{row['Title']} - {row['Type']} - {row['BodyPart']}" for _, row in routine_df.iterrows()])
    prompt = f"""
You are a professional fitness coach. Analyze the following gym workout routine:

{routine_summary}

Please provide feedback on:
- Tell the benefits of the routine
- The effectiveness for general fitness
- Tips for progression or safety
"""
    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "You are a helpful fitness expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error analyzing routine: {e}"