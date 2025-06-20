import os
from typing import List, Dict
from collections import defaultdict
from langchain_google_genai import ChatGoogleGenerativeAI

from utils.vector_db import search, format_docs

GEMINI_KEY = "AIzaSyBP3m7WrltTLMueC3ikB9Yllls4JR8RQEU"

PROMPT_TEMPLATE = """
You are a career training advisor.
Suggest the best online resources and study plan for learning the skill: {skill}.
Here are some related resources:
{context}

Based on these, recommend:
- Online courses (e.g., Coursera, Udemy, YouTube)
- Project ideas or GitHub repos
- Certifications (if any)
- Timeline to complete (e.g., 4 weeks)

Output in a clear, readable format with links.
"""

def run(state):
    print("📚 Training Recommender (RAG) started...")

    if not state.gap_analysis:
        print("⚠️ No gap analysis available")
        state.training_recommendations = []
        return state

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GEMINI_KEY)
    training_responses = {}
    training_recommendations = []

    for gap in state.gap_analysis:
        student_id = gap["student_id"]
        student_plan = ""
        raw_skills = gap.get("gaps", [])

        # ✅ Filter skill-based gaps only
        skill_gaps = [s for s in raw_skills if s.lower() not in ["cgpa", "internships", "projects", "hackathons"]]
        non_skill_gaps = [s for s in raw_skills if s.lower() in ["cgpa", "internships", "projects", "hackathons"]]

        if non_skill_gaps:
            print(f"⚠️ Skipping non-skill gaps for student {student_id}: {non_skill_gaps}")

        all_skill_plans = []

        for skill in skill_gaps:
            skill_lower = skill.lower()

            if skill_lower in training_responses:
                print(f"✅ Using cached RAG result for: {skill}")
                plan = training_responses[skill_lower]
            else:
                try:
                    print(f"🔍 Retrieving documents for: {skill}")
                    docs = search(skill_lower, top_k=3)
                    context = format_docs(docs) if docs else "No relevant resources found."
                    prompt = PROMPT_TEMPLATE.format(skill=skill, context=context)

                    response = llm.invoke(prompt)
                    plan = response.content.strip() if hasattr(response, "content") else str(response)
                    training_responses[skill_lower] = plan

                except Exception as e:
                    print(f"❌ Error retrieving/generating for {skill}: {e}")
                    plan = "Training suggestion unavailable."

            all_skill_plans.append(f"🛠️ **{skill}**:\n{plan}")

        training_recommendations.append({
            "student_id": student_id,
            "training_plan": "\n\n".join(all_skill_plans) if all_skill_plans else "No skill gaps requiring training.",
            "resources": [],
            "gaps": skill_gaps
        })

    state.training_recommendations = training_recommendations
    print(f"✅ Generated training plans for {len(training_recommendations)} students")
    return state
