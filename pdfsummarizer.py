import openai
import streamlit as st
import fitz  # PyMuPDF

st.title("PDF SUMMARIZER")

# Ensure to replace this with your actual OpenAI API key or manage secrets through Streamlit
openai.api_key = st.secrets ["OPENAI_API_KEY"]
st.write(f"Your OpenAI API key is: {"sk-proj-t9ekHJUPqQf6sOm1ZzVGT3BlbkFJUgPTCvZd9QjC7vR8XEth"}")

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

def extract_text_from_pdf(file):
    pdf_document = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    return text

def summarize_text(text):
    response = openai.ChatCompletion.create(
        model=st.session_state["openai_model"],
        messages=[
            {"role": "system", "content": "Summarize the following text."},
            {"role": "user", "content": text}
        ]
    )
    summary = response.choices[0].message["content"]
    return summary

uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file is not None:
    with st.spinner("Extracting text from PDF..."):
        extracted_text = extract_text_from_pdf(uploaded_file)
        st.session_state.messages.append({"role": "user", "content": extracted_text})
        st.success("Text extracted successfully!")

    if st.button("Summarize PDF"):
        with st.spinner("Generating summary..."):
            summary = summarize_text(extracted_text)
            st.session_state.messages.append({"role": "assistant", "content": summary})
            st.success("Summary generated successfully!")

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle new user input
if prompt := st.chat_input("Enter a new prompt"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        response = openai.ChatCompletion.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        
        for resp in response:
            if "content" in resp.choices[0].delta:
                content = resp.choices[0].delta["content"]
                full_response += content
                message_placeholder.markdown(full_response)
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})
