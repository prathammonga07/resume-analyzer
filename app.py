import streamlit as st
import pdfplumber as pb
import pandas as pd
import matplotlib.pyplot as plt

st.title("AI RESUME ANALYZER")

uploaded_file = st.file_uploader(
    'Upload Resume', type = "pdf"
)

def extract_text(pdf_read):
    text = ""

    with pb.open(pdf_read) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()

            if extracted:  
                text += extracted + " "
    return text.lower()


def extract_skills(text):
    skills_db = pd.read_csv('skills.csv')
    skill_list = skills_db["skills"].tolist()
    found_skills = []
    not_found_skills = []

    for skill in skill_list:
        if skill.lower() in text:
            found_skills.append(skill)

        if skill.lower() not in text:
            not_found_skills.append(skill)
            

    return found_skills, len(skill_list), not_found_skills

def calculate_ast(found_skills, total_skills):
    score = (len(found_skills) / total_skills) * 100
    return score

def recommend_role(skills):

    skills = [skill.lower() for skill in skills]
    recommend_roles = []

    if (
        "machine learning" in skills
        or "tensorflow" in skills
        or "deep learning" in skills
        or "scikit-learn" in skills
    ):

        recommend_roles.append("Machine Learning Engineer")

    if (
        "sql" in skills
        and (
            "excel" in skills
            or "power bi" in skills
            or "tableau" in skills
        )
    ):

        recommend_roles.append("Data Analyst")

    if (
        "python" in skills
        and "machine learning" in skills
        and "pandas" in skills
        and "numpy" in skills
    ):

        recommend_roles.append("Data Scientist")

    if (
        "opencv" in skills
        and "python" in skills
    ):

        recommend_roles.append("Computer Vision Engineer")

    if (
        "tensorflow" in skills
        or "deep learning" in skills
    ):

        recommend_roles.append("Deep Learning Engineer")

    if (
        "nltk" in skills
        or "spacy" in skills
    ):

        recommend_roles.append("NLP Engineer")

    if (
        "python" in skills
        and "streamlit" in skills
    ):

        recommend_roles.append("Python Developer")

    if (
        "excel" in skills
        and "power bi" in skills
    ):

        recommend_roles.append("Business Analyst")

    if (
        "html" in skills
        and "css" in skills
        and "javascript" in skills
    ):

        recommend_roles.append("Web Developer")

    if (
        "python" in skills
        and "sql" in skills
    ):

        recommend_roles.append("Backend Developer")

    else:

        recommend_roles.append("General Tech Role")

    return recommend_roles

if uploaded_file :
    st.success("Resume uploaded successfully!")

    resume_text = extract_text(uploaded_file)

    if not resume_text.strip():
        st.error("No text found in PDF")
        st.stop()
    
    skills, total_skills, no_skills = extract_skills(resume_text)

    st.subheader("Resume Content")
    st.write(resume_text)
    
    st.subheader('Detected Skills')
    for skill in skills:
        st.success(skill) 

    score = calculate_ast(skills, total_skills)
    st.metric(
        label = "ATS Score",
        value=f"{score:.2f}%"
    )
    st.progress(int(score))
    if score < 40:
        st.error("Low ATS Score")
    elif score < 70:
        st.warning("Average ATS Score")
    else:
        st.success("Excellent ATS Score")

    matched = len(skills)
    missing = len(no_skills)
    
    labels = ['Matched Skills', 'Missing Skills']
    sizes = [matched, missing]
    
    fig, ax = plt.subplots()

    ax.pie(
        sizes,
        labels=labels,
        autopct='%1.1f%%'
    )
    
    ax.axis('equal')
    
    st.subheader("Skill Match Analysis")

    st.pyplot(fig)
    

    st.subheader('Top Missing Skills')
    if len(no_skills) == 0:
            st.success("🎉 No missing skills found!")
    else:
        for skill in no_skills:
            st.write('❌', skill)
        
    st.subheader('Recommended Role')
    roles = recommend_role(skills)
    for role in roles:
        st.success(role)

    



    