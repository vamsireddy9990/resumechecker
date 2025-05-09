# Import statements
import streamlit as st
import PyPDF2
import io
import anthropic
from dotenv import load_dotenv
import os
import pandas as pd
import plotly.graph_objects as go
import json

# Configure page - MUST be the first Streamlit command
st.set_page_config(
    page_title="Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables with robust error handling
print("Current working directory:", os.getcwd())
try:
    # Try to load from .env file
    load_dotenv(encoding='utf-8')
    api_key = os.getenv('ANTHROPIC_API_KEY')
    
    # If not found in .env, check if it's set directly in environment
    if not api_key:
        api_key = os.environ.get('ANTHROPIC_API_KEY')
    
    print("API Key found:", "Yes" if api_key else "No")
    print("API Key value:", api_key[:10] + "..." if api_key else "None")

except Exception as e:
    print("Error loading .env:", str(e))
    # Fallback to direct environment variable
    api_key = os.environ.get('ANTHROPIC_API_KEY')

if not api_key:
    st.error("Anthropic API key not found. Please check your .env file or environment variables.")
    st.info("Make sure your .env file exists and contains: ANTHROPIC_API_KEY=your_key_here")

# Custom CSS for better UI
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8eb 100%);
        padding: 2rem;
    }

    [data-testid="stHeader"] {
        background-color: transparent;
    }

    .main {
        background-color: transparent !important;
        max-width: 1200px;
        margin: 0 auto;
    }

    h1 {
        color: #2C3E50;
        text-align: center;
        font-size: 3.5rem !important;
        margin-bottom: 1.5rem !important;
        padding-bottom: 1rem;
        border-bottom: 4px solid #FF6B6B;
    }

    h3 {
        color: #2C3E50;
        font-size: 1.8rem !important;
        margin-bottom: 1.5rem !important;
    }

    p {
        font-size: 1.2rem !important;
        line-height: 1.6 !important;
    }

    /* File uploader container */
    [data-testid="stUploadedFileContainer"] {
        background-color: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1.5rem 0;
    }

    /* Text input/area styling */
    .stTextArea textarea {
        background-color: white;
        border: 2px solid #e0e0e0;
        border-radius: 15px;
        padding: 1.5rem;
        font-size: 1.2rem !important;
        min-height: 200px !important;
    }

    .stTextArea textarea:focus {
        border-color: #FF6B6B;
        box-shadow: 0 0 0 2px rgba(255, 107, 107, 0.2);
    }

    /* Button styling */
    .stButton > button {
        width: 100%;
        max-width: 500px;
        margin: 0 auto;
        background: linear-gradient(45deg, #FF6B6B, #FF8E8E);
        color: white;
        padding: 1rem 2rem;
        font-size: 1.4rem;
        font-weight: 600;
        border: none;
        border-radius: 15px;
        cursor: pointer;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.2);
        background: linear-gradient(45deg, #FF5252, #FF7676);
    }

    /* Success message */
    .success-message {
        padding: 1rem;
        background-color: #D4EDDA;
        color: #155724;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
        font-size: 1.2rem;
    }

    /* Error message */
    .stAlert {
        background-color: #FFF3CD;
        color: #856404;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #FF6B6B;
        font-size: 1.2rem !important;
    }

    /* Results styling */
    .results-container {
        background-color: white;
        padding: 3rem;
        border-radius: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 2rem 0;
    }

    .results-container h2 {
        font-size: 2.5rem !important;
        color: #2C3E50;
        margin-bottom: 2rem;
    }

    .results-container h3 {
        font-size: 1.8rem !important;
        margin-bottom: 1rem;
    }

    .match-score {
        font-size: 4rem !important;
        color: #FF6B6B;
        font-weight: bold;
        text-align: center;
        margin: 1rem 0;
    }

    .section-content {
        font-size: 1.1rem !important;
        padding: 0.8rem 0;
        border-bottom: 1px solid #eee;
    }

    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(45deg, #FF6B6B, #FF8E8E);
        height: 25px;
        border-radius: 12px;
    }
    </style>
""", unsafe_allow_html=True)

def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        return None

def analyze_resume(resume_text, job_description):
    """Analyze resume against job description using Anthropic API"""
    try:
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            st.error("Anthropic API key not found. Please check your .env file.")
            return None
            
        client = anthropic.Anthropic(api_key=api_key)
        
        prompt = f"""Analyze the following resume against the job description. 
        Provide a comprehensive analysis including:
        1. Key strengths and matches
        2. Missing skills or qualifications
        3. Specific suggestions for improvement
        4. Overall match score (percentage)
        5. ATS (Applicant Tracking System) compatibility score (percentage)
        6. Detailed skills breakdown with proficiency levels
        7. Missing important keywords from the job description
        8. Action verbs analysis
        9. Education and experience alignment
        10. Format and presentation score

        Resume:
        {resume_text}

        Job Description:
        {job_description}

        Format the response as a JSON with the following structure:
        {{
            "strengths": ["strength1", "strength2", ...],
            "weaknesses": ["weakness1", "weakness2", ...],
            "suggestions": ["suggestion1", "suggestion2", ...],
            "match_score": percentage,
            "ats_compatibility": percentage,
            "skill_matches": {{"skill1": percentage, "skill2": percentage, ...}},
            "missing_keywords": ["keyword1", "keyword2", ...],
            "action_verbs": {{
                "used": ["verb1", "verb2", ...],
                "recommended": ["verb1", "verb2", ...]
            }},
            "education_alignment": {{
                "score": percentage,
                "feedback": "detailed feedback"
            }},
            "experience_alignment": {{
                "score": percentage,
                "feedback": "detailed feedback"
            }},
            "format_score": {{
                "score": percentage,
                "issues": ["issue1", "issue2", ...],
                "positives": ["positive1", "positive2", ...]
            }}
        }}
        
        Ensure the analysis is thorough and actionable. For missing keywords, focus on technical skills, qualifications, and industry-specific terms that appear in the job description but are absent in the resume.
        """

        try:
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=4096,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            
            try:
                result = json.loads(response.content[0].text)
                return result
            except json.JSONDecodeError:
                st.error("Error parsing API response. Please try again.")
                return None
                
        except anthropic.APIError as api_error:
            st.error(f"API Error: {str(api_error)}")
            return None
            
    except Exception as e:
        st.error(f"Error during analysis: {str(e)}")
        return None

def create_radar_chart(skill_matches):
    """Create a radar chart for skill matches"""
    categories = list(skill_matches.keys())
    values = list(skill_matches.values())
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        line_color='#FF4B4B'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=False,
        title="Skills Match Analysis"
    )
    return fig

# Main UI
st.markdown("<h1>📄 Resume Analyzer</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.5rem !important; color: #666; margin-bottom: 3rem;'>Optimize your resume for your dream job</p>", unsafe_allow_html=True)

# Create two columns for inputs
col1, col2 = st.columns(2)

with col1:
    st.markdown("<h3>📎 Upload Resume</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #666;'>Upload your resume in PDF format</p>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type="pdf", label_visibility="collapsed")
    if uploaded_file:
        st.markdown("<div class='success-message'>✅ Resume uploaded successfully!</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<h3>📝 Job Description</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #666;'>Paste the job description you want to analyze against</p>", unsafe_allow_html=True)
    job_description = st.text_area("", height=200, placeholder="Paste the complete job description here...", label_visibility="collapsed")

# Analysis button
st.markdown("<div style='text-align: center; padding: 3rem 0;'>", unsafe_allow_html=True)
if st.button("🔍 Analyze Resume"):
    if uploaded_file is None:
        st.error("⚠️ Please upload a resume first!")
    elif not job_description:
        st.error("⚠️ Please provide a job description!")
    else:
        with st.spinner("🔄 Analyzing your resume... This may take a moment."):
            # Extract text from PDF
            resume_text = extract_text_from_pdf(uploaded_file)
            if resume_text:
                # Analyze resume
                analysis = analyze_resume(resume_text, job_description)
                
                if analysis:
                    st.markdown("<div class='results-container'>", unsafe_allow_html=True)
                    st.markdown("<h2 style='text-align: center;'>📊 Analysis Results</h2>", unsafe_allow_html=True)
                    
                    # Create three columns for the main scores
                    score_col1, score_col2, score_col3 = st.columns(3)
                    
                    with score_col1:
                        st.markdown("""
                            <div style='text-align: center;'>
                                <h3>Overall Match</h3>
                                <div class='match-score'>{0}%</div>
                            </div>
                        """.format(analysis['match_score']), unsafe_allow_html=True)
                        st.progress(analysis['match_score'] / 100)
                    
                    with score_col2:
                        st.markdown("""
                            <div style='text-align: center;'>
                                <h3>ATS Compatibility</h3>
                                <div class='match-score'>{0}%</div>
                            </div>
                        """.format(analysis['ats_compatibility']), unsafe_allow_html=True)
                        st.progress(analysis['ats_compatibility'] / 100)
                    
                    with score_col3:
                        st.markdown("""
                            <div style='text-align: center;'>
                                <h3>Format Score</h3>
                                <div class='match-score'>{0}%</div>
                            </div>
                        """.format(analysis['format_score']['score']), unsafe_allow_html=True)
                        st.progress(analysis['format_score']['score'] / 100)
                    
                    # Results in columns
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("<h3 style='color: #28A745;'>✅ Strengths</h3>", unsafe_allow_html=True)
                        for strength in analysis['strengths']:
                            st.markdown(f"<div class='section-content'>• {strength}</div>", unsafe_allow_html=True)
                    
                        st.markdown("<h3 style='color: #DC3545; margin-top: 20px;'>❌ Areas for Improvement</h3>", unsafe_allow_html=True)
                        for weakness in analysis['weaknesses']:
                            st.markdown(f"<div class='section-content'>• {weakness}</div>", unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown("<h3 style='color: #17A2B8;'>💡 Suggestions</h3>", unsafe_allow_html=True)
                        for suggestion in analysis['suggestions']:
                            st.markdown(f"<div class='section-content'>• {suggestion}</div>", unsafe_allow_html=True)
                    
                        st.markdown("<h3 style='color: #FD7E14; margin-top: 20px;'>🎯 Missing Keywords</h3>", unsafe_allow_html=True)
                        for keyword in analysis['missing_keywords']:
                            st.markdown(f"<div class='section-content'>• {keyword}</div>", unsafe_allow_html=True)
                    
                    # Action Verbs Analysis
                    st.markdown("<h3 style='text-align: center; margin: 2rem 0;'>📝 Action Verbs Analysis</h3>", unsafe_allow_html=True)
                    verb_col1, verb_col2 = st.columns(2)
                    
                    with verb_col1:
                        st.markdown("<h4 style='color: #28A745;'>Used in Your Resume</h4>", unsafe_allow_html=True)
                        for verb in analysis['action_verbs']['used']:
                            st.markdown(f"<div class='section-content'>• {verb}</div>", unsafe_allow_html=True)
                    
                    with verb_col2:
                        st.markdown("<h4 style='color: #17A2B8;'>Recommended Additions</h4>", unsafe_allow_html=True)
                        for verb in analysis['action_verbs']['recommended']:
                            st.markdown(f"<div class='section-content'>• {verb}</div>", unsafe_allow_html=True)
                    
                    # Education and Experience Alignment
                    st.markdown("<h3 style='text-align: center; margin: 2rem 0;'>🎓 Education & Experience Alignment</h3>", unsafe_allow_html=True)
                    edu_col1, edu_col2 = st.columns(2)
                    
                    with edu_col1:
                        st.markdown("""
                            <div style='text-align: center;'>
                                <h4>Education Match</h4>
                                <div class='match-score' style='font-size: 2.5rem !important;'>{0}%</div>
                                <p>{1}</p>
                            </div>
                        """.format(analysis['education_alignment']['score'], analysis['education_alignment']['feedback']), unsafe_allow_html=True)
                    
                    with edu_col2:
                        st.markdown("""
                            <div style='text-align: center;'>
                                <h4>Experience Match</h4>
                                <div class='match-score' style='font-size: 2.5rem !important;'>{0}%</div>
                                <p>{1}</p>
                            </div>
                        """.format(analysis['experience_alignment']['score'], analysis['experience_alignment']['feedback']), unsafe_allow_html=True)
                    
                    # Format Analysis
                    st.markdown("<h3 style='text-align: center; margin: 2rem 0;'>📋 Format Analysis</h3>", unsafe_allow_html=True)
                    format_col1, format_col2 = st.columns(2)
                    
                    with format_col1:
                        st.markdown("<h4 style='color: #28A745;'>Positive Aspects</h4>", unsafe_allow_html=True)
                        for positive in analysis['format_score']['positives']:
                            st.markdown(f"<div class='section-content'>• {positive}</div>", unsafe_allow_html=True)
                    
                    with format_col2:
                        st.markdown("<h4 style='color: #DC3545;'>Areas to Improve</h4>", unsafe_allow_html=True)
                        for issue in analysis['format_score']['issues']:
                            st.markdown(f"<div class='section-content'>• {issue}</div>", unsafe_allow_html=True)
                    
                    # Radar chart for skills
                    st.markdown("<h3 style='text-align: center; margin: 2rem 0;'>📊 Skills Match Analysis</h3>", unsafe_allow_html=True)
                    fig = create_radar_chart(analysis['skill_matches'])
                    fig.update_layout(
                        height=500,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                range=[0, 100],
                                tickfont=dict(size=12),
                                gridcolor="#e0e0e0"
                            ),
                            angularaxis=dict(
                                tickfont=dict(size=14),
                                gridcolor="#e0e0e0"
                            )
                        ),
                        font=dict(
                            family="Arial, sans-serif",
                            size=16,
                            color="#2C3E50"
                        )
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("""
    <div style='text-align: center; margin-top: 3rem; padding: 1rem; color: #666; border-top: 1px solid #eee;'>
        <p style='font-size: 1.1rem !important;'>Made with ❤️ for job seekers</p>
    </div>
""", unsafe_allow_html=True) 