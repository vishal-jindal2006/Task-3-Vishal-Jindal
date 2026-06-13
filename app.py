from flask import Flask, render_template, request, send_file
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from reportlab.lib import colors

app = Flask(__name__)

df = pd.read_csv("data/careers.csv")
df["Skills"] = df["Skills"].str.lower()

latest_recommendations = []


# About Page
@app.route("/about")
def about():
    return render_template("about.html")


# Home Page
@app.route("/", methods=["GET", "POST"])
def home():

    global latest_recommendations
    recommendations = []

    if request.method == "POST":

        user_skills = request.form["skills"].lower().strip()

        user_skill_set = set(
            skill.strip()
            for skill in user_skills.split(",")
            if skill.strip()
        )

        documents = [user_skills] + df["Skills"].tolist()

        vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english"
        )

        tfidf_matrix = vectorizer.fit_transform(documents)

        user_vector = tfidf_matrix[0]
        career_vectors = tfidf_matrix[1:]

        similarity_scores = cosine_similarity(
            user_vector,
            career_vectors
        ).flatten()

        result_df = df.copy()
        result_df["Score"] = similarity_scores

        result_df = result_df.sort_values(
            by="Score",
            ascending=False
        )

        top_results = result_df.head(3)

        badges = [
            "🥇 BEST MATCH",
            "🥈 STRONG MATCH",
            "🥉 GOOD MATCH"
        ]

        for idx, (_, row) in enumerate(top_results.iterrows()):

            role_skills = set(
                skill.strip()
                for skill in row["Skills"].split(",")
            )

            matched_skills = list(
                user_skill_set.intersection(role_skills)
            )

            missing_skills = list(
                role_skills - user_skill_set
            )
            
            role = row["Role"]

            # Description Mapping
            descriptions = {
                "Data Scientist": "Analyzes data, builds predictive models and extracts business insights.",
                "Machine Learning Engineer": "Builds, trains and deploys machine learning systems and AI solutions.",
                "AI Engineer": "Develops AI-powered applications using NLP, deep learning and automation.",
                "Backend Developer": "Creates APIs, databases and server-side application logic.",
                "Frontend Developer": "Builds responsive and interactive user interfaces for websites.",
                "Full Stack Developer": "Works on both frontend and backend development.",
                "DevOps Engineer": "Manages CI/CD pipelines, deployment and infrastructure automation.",
                "Cloud Engineer": "Designs and manages cloud infrastructure.",
                "Cybersecurity Analyst": "Protects systems and networks from cyber threats.",
                "Data Analyst": "Analyzes data and creates reports for business decisions.",
                "Business Analyst": "Bridges business requirements with technology solutions.",
                "Software Engineer": "Designs and develops software applications.",
                "Mobile App Developer": "Creates mobile apps for Android and iOS.",
                "Android Developer": "Builds Android applications using Java and Kotlin.",
                "iOS Developer": "Develops iPhone and iPad applications using Swift.",
                "Database Administrator": "Manages databases, backups and performance.",
                "Cloud Architect": "Designs enterprise cloud solutions.",
                "Site Reliability Engineer": "Ensures reliability, monitoring and performance.",
                "Blockchain Developer": "Develops decentralized apps and smart contracts.",
                "Game Developer": "Creates games using modern game engines.",
                "UI UX Designer": "Designs intuitive user experiences and interfaces.",
                "QA Engineer": "Tests software quality and automation frameworks.",
                "Automation Engineer": "Builds automation systems and testing solutions.",
                "Network Engineer": "Designs and manages enterprise networks.",
                "System Administrator": "Maintains servers and IT infrastructure.",
                "Data Engineer": "Builds ETL pipelines and big-data systems.",
                "NLP Engineer": "Develops natural language processing systems.",
                "Computer Vision Engineer": "Creates AI systems that understand images and videos.",
                "AI Researcher": "Researches advanced AI models and deep learning technologies.",
                "Product Manager": "Leads product strategy and feature planning."
            }

            description = descriptions.get(
                role,
                "Technology Professional"
            )

            # Salary Mapping
            salary_map = {
                "AI Researcher":"₹15-35 LPA",
                "AI Engineer":"₹12-30 LPA",
                "Machine Learning Engineer":"₹10-25 LPA",
                "Data Scientist":"₹8-22 LPA",
                "NLP Engineer":"₹12-28 LPA",
                "Computer Vision Engineer":"₹12-28 LPA",
                "Backend Developer":"₹6-18 LPA",
                "Frontend Developer":"₹5-15 LPA",
                "Full Stack Developer":"₹8-22 LPA",
                "Cloud Engineer":"₹10-25 LPA",
                "Cloud Architect":"₹20-45 LPA",
                "DevOps Engineer":"₹10-25 LPA",
                "Cybersecurity Analyst":"₹8-25 LPA",
                "Data Engineer":"₹8-20 LPA",
                "Data Analyst":"₹5-12 LPA",
                "Business Analyst":"₹6-15 LPA",
                "QA Engineer":"₹4-12 LPA",
                "Automation Engineer":"₹6-16 LPA",
                "Product Manager":"₹15-40 LPA"
            }

            salary = salary_map.get(
                role,
                "₹5-15 LPA"
            )

            # Demand Mapping
            if role in [
                "AI Researcher",
                "AI Engineer",
                "Machine Learning Engineer",
                "Data Scientist",
                "NLP Engineer",
                "Computer Vision Engineer"
            ]:
                demand = "🔥 Very High"
                growth = "Excellent"

            elif role in [
                "Cloud Engineer",
                "Cloud Architect",
                "DevOps Engineer",
                "Cybersecurity Analyst",
                "Data Engineer"
            ]:
                demand = "🔥 High"
                growth = "Excellent"

            else:
                demand = "📈 Growing"
                growth = "Good"
                
            why_match = []

            for skill in matched_skills[:3]:
                why_match.append(
                    f"You already know {skill.title()}"
                )

            if len(matched_skills) >= 3:
                why_match.append(
                    "Strong overlap with required skills"
                )

            if demand == "🔥 Very High":
                why_match.append(
                    "High demand career in today's market"
                )

            recommendations.append({
                "badge": badges[idx],
                "role": row["Role"],
                "skills": row["Skills"],
                "score": round(row["Score"] * 100, 2),
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
                "roadmap": missing_skills[:3],
                
                "salary": salary,
                "demand": demand,
                "growth": growth,
                "description": description,
                "why_match": why_match,
            })
    latest_recommendations = recommendations

    return render_template(
        "index.html",
        total_roles=len(df),
        recommendations=recommendations
    )

@app.route("/download-report")
def download_report():

    pdf_file = "Career_Report.pdf"

    def add_background(canvas, doc):

        canvas.saveState()

        # Dark Gradient Style Background
        canvas.setFillColor(colors.HexColor("#0F172A"))
        canvas.rect(0, 0, 600, 900, fill=1)

        # Top Blue Bar
        canvas.setFillColor(colors.HexColor("#2563EB"))
        canvas.rect(0, 780, 600, 20, fill=1)

        # Bottom Cyan Bar
        canvas.setFillColor(colors.HexColor("#06B6D4"))
        canvas.rect(0, 0, 600, 20, fill=1)

        canvas.restoreState()

    doc = SimpleDocTemplate(pdf_file)

    styles = getSampleStyleSheet()
    
    styles["BodyText"].textColor = colors.white
    styles["Heading2"].textColor = colors.white

    content = []

    content.append(
        Paragraph(
            "<font color='white'><b>🚀 AI Career Matchmaker Report</b></font>",
            styles["Title"]
        )
    )

    content.append(Spacer(1, 20))

    for career in latest_recommendations:

        content.append(
            Paragraph(
                f"<font color='#38BDF8'><b>{career['role']}</b></font>",
                styles["Heading2"]
            )
        )

        content.append(
            Paragraph(
                f"Match Score: {career['score']}%",
                styles["BodyText"]
            )
        )

        content.append(
            Paragraph(
                f"Salary: {career['salary']}",
                styles["BodyText"]
            )
        )

        content.append(
            Paragraph(
                f"Demand: {career['demand']}",
                styles["BodyText"]
            )
        )

        content.append(
            Paragraph(
                f"Growth: {career['growth']}",
                styles["BodyText"]
            )
        )

        content.append(
            Paragraph(
                career["description"],
                styles["BodyText"]
            )
        )

        content.append(
            Paragraph(
                "<font color='#38BDF8'>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</font>",
                styles["BodyText"]
            )
        )

        content.append(Spacer(1, 20))

        content.append(Spacer(1, 20))

        content.append(
            Paragraph(
                "<font color='#64748B'>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</font>",
                styles["BodyText"]
            )
        )

    content.append(
        Paragraph(
            "<font color='#94A3B8'>Generated using AI Career Matchmaker</font>",
            styles["BodyText"]
        )
    )

    content.append(
        Paragraph(
            "<font color='#38BDF8'><b>Developed By Vishal Jindal</b></font>",
            styles["BodyText"]
        )
    )
    
    doc.build(
        content,
        onFirstPage=add_background,
        onLaterPages=add_background
    )

    return send_file(
        pdf_file,
        as_attachment=True
    )


if __name__ == "__main__":
    app.run(debug=True)