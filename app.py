import streamlit as st
import pdfplumber as pb
import pandas as pd
import matplotlib.pyplot as plt
import re
from datetime import datetime

st.set_page_config(page_title="AI Resume Analyzer", layout="wide")
st.title("📄 AI Resume Analyzer")
st.write(
    "Upload your resume to get an ATS-style skill score, role recommendations, "
    "section completeness check, and an optional match score against a job description."
)

uploaded_file = st.file_uploader("Upload Resume", type="pdf")


# ---------------------------------------------------------------------------
# Core extraction functions
# ---------------------------------------------------------------------------

def extract_text(pdf_file):
    """Extract and lowercase all text from a PDF file."""
    text = ""
    with pb.open(pdf_file) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + " "
    return text.lower()


@st.cache_data
def load_skills():
    skills_db = pd.read_csv("skills.csv")
    return skills_db["skills"].tolist()


def extract_skills(text, skill_list):
    found_skills = []
    not_found_skills = []
    for skill in skill_list:
        if skill.lower() in text:
            found_skills.append(skill)
        else:
            not_found_skills.append(skill)
    return found_skills, not_found_skills


def calculate_ats(found_skills, total_skills):
    if total_skills == 0:
        return 0
    return (len(found_skills) / total_skills) * 100


def extract_contact_info(text):
    email_match = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    phone_match = re.findall(r"(\+?\d{1,3}[\s-]?)?\d{10}", text)
    linkedin_match = re.findall(r"linkedin\.com/in/[a-zA-Z0-9\-_/]+", text)

    return {
        "email": email_match[0] if email_match else None,
        "phone": "".join(phone_match[0]).strip() if phone_match else None,
        "linkedin": linkedin_match[0] if linkedin_match else None,
    }


def check_resume_sections(text):
    sections = [
        "education",
        "experience",
        "projects",
        "skills",
        "certifications",
        "summary",
        "achievements",
    ]
    found = [s for s in sections if s in text]
    missing = [s for s in sections if s not in text]
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

    if "sql" in skills and (
        "excel" in skills or "power bi" in skills or "tableau" in skills
    ):
        recommend_roles.append("Data Analyst")

    if (
        "python" in skills
        and "machine learning" in skills
        and "pandas" in skills
        and "numpy" in skills
    ):
        recommend_roles.append("Data Scientist")

    if "opencv" in skills and "python" in skills:
        recommend_roles.append("Computer Vision Engineer")

    if "tensorflow" in skills or "deep learning" in skills:
        recommend_roles.append("Deep Learning Engineer")

    if "nltk" in skills or "spacy" in skills:
        recommend_roles.append("NLP Engineer")

    if "python" in skills and "streamlit" in skills:
        recommend_roles.append("Python Developer")

    if "excel" in skills and "power bi" in skills:
        recommend_roles.append("Business Analyst")

    if "html" in skills and "css" in skills and "javascript" in skills:
        recommend_roles.append("Web Developer")

    if "python" in skills and "sql" in skills:
        recommend_roles.append("Backend Developer")

    # Fallback only applies if NOTHING else matched (this was the bug before)
    if not recommend_roles:
        recommend_roles.append("General Tech Role")

    return recommend_roles


def jd_skill_match(found_skills, jd_text, skill_list):
    jd_text = jd_text.lower()
    jd_skills = [s for s in skill_list if s.lower() in jd_text]

    found_lower = [s.lower() for s in found_skills]
    matched = [s for s in jd_skills if s.lower() in found_lower]
    missing = [s for s in jd_skills if s.lower() not in found_lower]

    match_pct = (len(matched) / len(jd_skills) * 100) if jd_skills else 0
    return jd_skills, matched, missing, match_pct


# ---------------------------------------------------------------------------
# Main app
# ---------------------------------------------------------------------------

if uploaded_file:
    st.success("Resume uploaded successfully!")

    resume_text = extract_text(uploaded_file)

    if not resume_text.strip():
        st.error(
            "No text could be extracted from this PDF. "
            "It may be a scanned image — try a text-based PDF instead."
        )
        st.stop()

    skill_list = load_skills()
    found_skills, missing_skills = extract_skills(resume_text, skill_list)
    ats_score = calculate_ats(found_skills, len(skill_list))
    contact_info = extract_contact_info(resume_text)
    found_sections, missing_sections = check_resume_sections(resume_text)
    roles = recommend_role(found_skills)

    tab1, tab2, tab3 = st.tabs(
        ["📊 Resume Analysis", "🎯 Job Description Match", "📥 Download Report"]
    )

    # -----------------------------------------------------------------
    # TAB 1: Resume Analysis
    # -----------------------------------------------------------------
    with tab1:
        with st.expander("View extracted resume text"):
            st.write(resume_text)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Contact Information")
            st.write(f"**Email:** {contact_info['email'] or '❌ Not found'}")
            st.write(f"**Phone:** {contact_info['phone'] or '❌ Not found'}")
            st.write(f"**LinkedIn:** {contact_info['linkedin'] or '❌ Not found'}")

            st.subheader("Resume Sections")
            for s in found_sections:
                st.success(f"✅ {s.title()}")
            for s in missing_sections:
                st.warning(f"⚠️ Missing section: {s.title()}")

        with col2:
            st.subheader("ATS Skill Score")
            st.metric(label="ATS Score", value=f"{ats_score:.2f}%")
            st.progress(int(ats_score))

            if ats_score < 40:
                st.error("Low ATS Score — consider adding more relevant skills.")
            elif ats_score < 70:
                st.warning("Average ATS Score — there's room to improve.")
            else:
                st.success("Excellent ATS Score!")

            st.subheader("Recommended Roles")
            for role in roles:
                st.info(role)

        st.subheader("Detected Skills")
        if found_skills:
            st.write(", ".join(found_skills))
        else:
            st.write("No matching skills found.")

        st.subheader("Skill Match Breakdown")
        fig, ax = plt.subplots()
        ax.pie(
            [len(found_skills), len(missing_skills)],
            labels=["Matched Skills", "Missing Skills"],
            autopct="%1.1f%%",
        )
        ax.axis("equal")
        st.pyplot(fig)

        st.subheader("Skills Not Found in Resume")
        if missing_skills:
            st.write(", ".join(missing_skills))
        else:
            st.success("🎉 No missing skills from our skill database!")

    # -----------------------------------------------------------------
    # TAB 2: Job Description Match
    # -----------------------------------------------------------------
    with tab2:
        st.write(
            "Paste a job description below to see how well your resume "
            "matches the skills it asks for."
        )
        jd_text = st.text_area("Job Description", height=200, key="jd_text")

        if jd_text.strip():
            jd_skills, jd_matched, jd_missing, jd_match_pct = jd_skill_match(
                found_skills, jd_text, skill_list
            )

            st.metric("Job Match Score", f"{jd_match_pct:.2f}%")
            st.progress(int(jd_match_pct))

            colA, colB = st.columns(2)
            with colA:
                st.subheader("✅ Skills You Have")
                if jd_matched:
                    for s in jd_matched:
                        st.success(s)
                else:
                    st.write("None matched yet.")

            with colB:
                st.subheader("❌ Skills to Add")
                if jd_missing:
                    for s in jd_missing:
                        st.error(s)
                else:
                    st.success("You cover everything detected in this JD!")

            if jd_skills:
                fig2, ax2 = plt.subplots()
                ax2.bar(
                    ["Matched", "Missing"],
                    [len(jd_matched), len(jd_missing)],
                    color=["#2ecc71", "#e74c3c"],
                )
                ax2.set_ylabel("Number of skills")
                ax2.set_title("Job Description Skill Match")
                st.pyplot(fig2)
        else:
            st.info("Paste a job description above to see your match score.")

    # -----------------------------------------------------------------
    # TAB 3: Download Report
    # -----------------------------------------------------------------
    with tab3:
        st.write("Generate a text summary of this analysis to save or share.")

        report_lines = [
            "AI RESUME ANALYZER REPORT",
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "--- Contact Information ---",
            f"Email: {contact_info['email'] or 'Not found'}",
            f"Phone: {contact_info['phone'] or 'Not found'}",
            f"LinkedIn: {contact_info['linkedin'] or 'Not found'}",
            "",
            "--- ATS Score ---",
            f"Score: {ats_score:.2f}%",
            "",
            "--- Detected Skills ---",
            ", ".join(found_skills) if found_skills else "None",
            "",
            "--- Missing Skills ---",
            ", ".join(missing_skills) if missing_skills else "None",
            "",
            "--- Resume Sections Found ---",
            ", ".join(found_sections) if found_sections else "None",
            "",
            "--- Resume Sections Missing ---",
            ", ".join(missing_sections) if missing_sections else "None",
            "",
            "--- Recommended Roles ---",
            ", ".join(roles),
        ]

        jd_text_value = st.session_state.get("jd_text", "")
        if jd_text_value.strip():
            jd_skills, jd_matched, jd_missing, jd_match_pct = jd_skill_match(
                found_skills, jd_text_value, skill_list
            )
            report_lines += [
                "",
                "--- Job Description Match ---",
                f"Match Score: {jd_match_pct:.2f}%",
                f"Matched Skills: {', '.join(jd_matched) if jd_matched else 'None'}",
                f"Missing Skills: {', '.join(jd_missing) if jd_missing else 'None'}",
            ]

        report_text = "\n".join(report_lines)
        st.text_area("Report Preview", report_text, height=300)

        st.download_button(
            label="Download Report (.txt)",
            data=report_text,
            file_name="resume_analysis_report.txt",
            mime="text/plain",
        )

else:
    st.info("Upload a PDF resume to get started.")
