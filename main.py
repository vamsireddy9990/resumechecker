import streamlit as st
import PyPDF2
import io
from groq import Groq

# Configure page settings
st.set_page_config(
    page_title="Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .stButton button {
        background-color: #4CAF50;
        color: white;
        padding: 15px 30px;
        font-size: 18px;
        border-radius: 10px;
        border: none;
        transition: all 0.3s;
    }
    .stButton button:hover {
        background-color: #45a049;
        transform: translateY(-2px);
    }
    .css-1d391kg {
        padding: 2rem 1rem;
    }
    </style>
""", unsafe_allow_html=True)

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def analyze_resume(resume_text, job_description):
    client = Groq(
        api_key='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'
    )
    
    prompt = f"""
    Analyze the following resume against the job description:
    
    Resume:
    {resume_text}
    
    Job Description:
    {job_description}
    
    Please provide:
    1. Key strengths matching the job requirements
    2. Areas of improvement or missing skills
    3. Specific suggestions to improve the resume
    4. Overall match percentage
    5. Recommendations for better alignment with the role
    """
    
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-guard-3-8b",
        temperature=0.7,
    )
    
    return chat_completion.choices[0].message.content

# Header
st.title("🎯 Smart Resume Analyzer")
st.markdown("### Match your resume against your dream job description")

# Create two columns
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📄 Upload Your Resume")
    uploaded_file = st.file_uploader("Choose your resume (PDF format)", type="pdf")

with col2:
    st.markdown("### 💼 Job Description")
    job_description = st.text_area("Paste the job description here", height=300)

# Analysis button
if st.button("🔍 Analyze Resume"):
    if uploaded_file is not None and job_description:
        with st.spinner("Analyzing your resume..."):
            try:
                # Extract text from PDF
                resume_text = extract_text_from_pdf(uploaded_file)
                
                # Get analysis from Groq
                analysis = analyze_resume(resume_text, job_description)
                
                # Display results in an organized manner
                st.markdown("## 📊 Analysis Results")
                st.markdown(analysis)
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please upload your resume and provide a job description.")

# Footer
st.markdown("---")
st.markdown("### 💡 Tips")
st.markdown("""
- Make sure your resume is in PDF format
- Provide a detailed job description for better analysis
- The analysis takes into account both technical skills and soft skills
""")
