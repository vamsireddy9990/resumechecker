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
        background-color: #FF4B4B;
        color: white;
        border-radius: 10px;
        padding: 0.5rem 2rem;
        font-weight: bold;
    }
    .stTextArea textarea {
        border-radius: 10px;
        border: 2px solid #ccc;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Groq client
client = Groq(
    api_key=st.secrets["GROQ_API_KEY"]
)

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def analyze_resume(resume_text, job_description):
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
    """
    
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        model="llama-guard-3-8b",
        temperature=0.5,
        max_tokens=2048
    )
    
    return response.choices[0].message.content

# App header
st.title("🎯 Smart Resume Analyzer")
st.markdown("### Upload your resume and job description for detailed analysis")

# Create two columns
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 📄 Upload Resume (PDF)")
    uploaded_file = st.file_uploader("Choose your resume", type="pdf")

with col2:
    st.markdown("#### 💼 Job Description")
    job_description = st.text_area("Paste the job description here", height=200)

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
                
                # Create tabs for different sections
                tab1, tab2, tab3 = st.tabs(["Strengths", "Areas for Improvement", "Suggestions"])
                
                # Split the analysis into sections (assuming the API returns formatted text)
                sections = analysis.split("\n\n")
                
                with tab1:
                    st.markdown("### 💪 Key Strengths")
                    st.write(sections[0] if len(sections) > 0 else "No strengths identified")
                
                with tab2:
                    st.markdown("### 🎯 Areas for Improvement")
                    st.write(sections[1] if len(sections) > 1 else "No improvements suggested")
                
                with tab3:
                    st.markdown("### 💡 Suggestions")
                    st.write(sections[2] if len(sections) > 2 else "No specific suggestions")
                
                # Display match percentage if available
                if len(sections) > 3:
                    st.markdown("### 📈 Overall Match")
                    st.progress(float(sections[3].strip("%"))/100 if "%" in sections[3] else 0.5)
                    
            except Exception as e:
                st.error(f"An error occurred during analysis: {str(e)}")
    else:
        st.warning("Please upload a resume and provide a job description.")

# Footer
st.markdown("---")
st.markdown("### How it works")
st.write("""
1. Upload your resume in PDF format
2. Paste the job description you're interested in
3. Click 'Analyze Resume' to get detailed insights
4. Review the analysis to improve your application
""")
