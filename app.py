import streamlit as st
import pdfplumber as pb
import pandas as pd
import matplotlib.pyplot as plt
import re
from datetime import datetime

st.set_page_config(page_title="AI Resume Analyzer", layout="wide")
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


def calculate_ats(found_skills, total_skills):
    score = (len(found_skills) / total_skills) * 100
    return score


def get_contact_info(text):
    # basic regex, wont catch every format but good enough
    email = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    phone = re.findall(r"(\+?\d{1,3}[\s-]?)?\d{10}", text)
    linkedin = re.findall(r"linkedin\.com/in/[a-zA-Z0-9\-_/]+", text)

    email = email[0] if email else "Not found"
    phone = "".join(phone[0]).strip() if phone else "Not found"
    linkedin = linkedin[0] if linkedin else "Not found"

    return email, phone, linkedin


def check_sections(text):
    # checking if common resume sections are present
    sections = ["education", "experience", "projects", "skills", "certifications", "summary", "achievements"]
    found = []
    missing = []

    for sec in sections:
        if sec in text:
            found.append(sec)
        else:
            missing.append(sec)

    return found, missing


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

    # only add general role if nothing else matched
    if len(recommend_roles) == 0:
        recommend_roles.append("General Tech Role")

    return recommend_roles


def match_with_jd(found_skills, jd_text, total_skill_list):
    jd_text = jd_text.lower()

    # find which skills from our db are mentioned in the JD
    jd_skills = []
    for s in total_skill_list:
        if s.lower() in jd_text:
            jd_skills.append(s)

    found_lower = [s.lower() for s in found_skills]

    matched = []
    missing = []
    for s in jd_skills:
        if s.lower() in found_lower:
            matched.append(s)
        else:
            missing.append(s)

    if len(jd_skills) == 0:
        pct = 0
    else:
        pct = (len(matched) / len(jd_skills)) * 100

    return jd_skills, matched, missing, pct


if uploaded_file :
    st.success("Resume uploaded successfully!")

    resume_text = extract_text(uploaded_file)

    if not resume_text.strip():
        st.error("No text found in PDF")
        st.stop()

    skills, total_skills, no_skills = extract_skills(resume_text)
    email, phone, linkedin = get_contact_info(resume_text)
    found_sections, missing_sections = check_sections(resume_text)

    tab1, tab2, tab3 = st.tabs(["Resume Analysis", "Job Description Match", "Download Report"])

    with tab1:
        st.subheader("Resume Content")
        with st.expander("Show extracted text"):
            st.write(resume_text)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Contact Info")
            st.write("Email:", email)
            st.write("Phone:", phone)
            st.write("LinkedIn:", linkedin)

            st.subheader("Resume Sections")
            for sec in found_sections:
                st.success(sec.title() + " ✅")
            for sec in missing_sections:
                st.warning(sec.title() + " missing")

        with col2:
            score = calculate_ats(skills, total_skills)
            st.subheader('ATS Score')
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

            st.subheader('Recommended Role')
            roles = recommend_role(skills)
            for role in roles:
                st.info(role)

        st.subheader('Detected Skills')
        st.write(", ".join(skills) if skills else "No skills detected")

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

    with tab2:
        st.write("Paste a job description here to check how well your resume matches it")
        jd_text = st.text_area("Job Description", height=200, key="jd_text")

        if jd_text.strip() != "":
            skills_db = pd.read_csv('skills.csv')
            full_skill_list = skills_db["skills"].tolist()

            jd_skills, jd_matched, jd_missing, jd_pct = match_with_jd(skills, jd_text, full_skill_list)

            st.metric("Job Match Score", f"{jd_pct:.2f}%")
            st.progress(int(jd_pct))

            col_a, col_b = st.columns(2)
            with col_a:
                st.subheader("Skills you have")
                if jd_matched:
                    for s in jd_matched:
                        st.success(s)
                else:
                    st.write("None matched")

            with col_b:
                st.subheader("Skills to add")
                if jd_missing:
                    for s in jd_missing:
                        st.error(s)
                else:
                    st.success("Covered everything!")

            if jd_skills:
                fig2, ax2 = plt.subplots()
                ax2.bar(["Matched", "Missing"], [len(jd_matched), len(jd_missing)], color=["green", "red"])
                ax2.set_ylabel("Number of skills")
                st.pyplot(fig2)
        else:
            st.write("Paste a job description above to see your match score")

    with tab3:
        st.write("Download a summary of this analysis")

        report = []
        report.append("AI RESUME ANALYZER REPORT")
        report.append("Generated on: " + datetime.now().strftime('%Y-%m-%d %H:%M'))
        report.append("")
        report.append("Email: " + email)
        report.append("Phone: " + phone)
        report.append("LinkedIn: " + linkedin)
        report.append("")
        report.append("ATS Score: " + f"{score:.2f}%")
        report.append("")
        report.append("Detected Skills: " + (", ".join(skills) if skills else "None"))
        report.append("Missing Skills: " + (", ".join(no_skills) if no_skills else "None"))
        report.append("")
        report.append("Sections Found: " + (", ".join(found_sections) if found_sections else "None"))
        report.append("Sections Missing: " + (", ".join(missing_sections) if missing_sections else "None"))
        report.append("")
        report.append("Recommended Roles: " + ", ".join(roles))

        jd_val = st.session_state.get("jd_text", "")
        if jd_val.strip() != "":
            skills_db = pd.read_csv('skills.csv')
            full_skill_list = skills_db["skills"].tolist()
            jd_skills, jd_matched, jd_missing, jd_pct = match_with_jd(skills, jd_val, full_skill_list)
            report.append("")
            report.append("Job Match Score: " + f"{jd_pct:.2f}%")
            report.append("Matched: " + (", ".join(jd_matched) if jd_matched else "None"))
            report.append("Missing: " + (", ".join(jd_missing) if jd_missing else "None"))

        report_text = "\n".join(report)
        st.text_area("Report Preview", report_text, height=300)

        st.download_button(
            label="Download Report (.txt)",
            data=report_text,
            file_name="resume_analysis_report.txt",
            mime="text/plain",
        )

else:
    st.info("Upload a PDF resume to get started")
