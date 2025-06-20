import fitz  # PyMuPDF
import re
import docx
import os

def extract_jd_text(file_path):
    text = ""
    file_ext = os.path.splitext(file_path)[1].lower()

    try:
        if file_ext == '.pdf':
            doc = fitz.open(file_path)  
            for page in doc:
                text += page.get_text()
            doc.close()
        elif file_ext == '.docx':
            doc = docx.Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        elif file_ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
    except Exception as e:
        print(f"❌ Error extracting text from {file_path}: {str(e)}")
        return ""

    return text.strip()

def parse_jd_criteria(jd_text):
    if not jd_text:
        return {
            "min_cgpa": 0.0,
            "must_have_skills": [],
            "preferred_skills": [],
            "min_internships": 0,
            "min_projects": 0,
            "hackathon_required": False,
            "coverage_percent": "0%"
        }

    jd_lower = jd_text.lower()
    criteria = {
        "min_cgpa": 0.0,
        "must_have_skills": [],
        "preferred_skills": [],
        "min_internships": 0,
        "min_projects": 0,
        "hackathon_required": False
    }

    # CGPA parsing
    cgpa_patterns = [
        r"cgpa.*?(\d+\.\d+)",
        r"gpa.*?(\d+\.\d+)",
        r"minimum.*?cgpa.*?(\d+\.\d+)",
        r"cgpa.*?above.*?(\d+\.\d+)",
        r"cgpa.*?minimum.*?(\d+\.\d+)",
        r"(\d+\.\d+).*?cgpa"
    ]
    for pattern in cgpa_patterns:
        match = re.search(pattern, jd_lower)
        if match:
            try:
                criteria["min_cgpa"] = float(match.group(1))
                break
            except:
                continue

    # Skill parsing
    common_skills = [
        'python', 'java', 'javascript', 'react', 'angular', 'node.js', 'mongodb', 
        'mysql', 'postgresql', 'spring', 'spring boot', 'django', 'flask',
        'html', 'css', 'git', 'docker', 'kubernetes', 'aws', 'azure',
        'machine learning', 'data science', 'tableau', 'power bi',
        'c++', 'c#', '.net', 'php', 'ruby', 'go', 'rust'
    ]

    skills_sections = []
    skills_keywords = ['skills', 'technical skills', 'requirements', 'technologies', 'tools']
    for keyword in skills_keywords:
        if keyword in jd_lower:
            start_idx = jd_lower.find(keyword)
            skills_sections.append(jd_lower[start_idx:start_idx + 200])
    if not skills_sections:
        skills_sections = [jd_lower]

    found_skills = []
    for section in skills_sections:
        for skill in common_skills:
            if skill in section and skill not in found_skills:
                found_skills.append(skill.title())

    if 'must' in jd_lower or 'required' in jd_lower:
        criteria["must_have_skills"] = found_skills[:5]
    else:
        criteria["must_have_skills"] = found_skills[:3]
        criteria["preferred_skills"] = found_skills[3:8]

    # Internship parsing
    internship_patterns = [
        r"(\d+).*?internship",
        r"internship.*?(\d+)",
        r"minimum.*?(\d+).*?internship",
        r"at least.*?(\d+).*?internship"
    ]
    for pattern in internship_patterns:
        match = re.search(pattern, jd_lower)
        if match:
            try:
                criteria["min_internships"] = int(match.group(1))
                break
            except:
                continue
    if 'internship' in jd_lower and criteria["min_internships"] == 0:
        criteria["min_internships"] = 1

    # Project parsing
    project_patterns = [
        r"(\d+).*?project",
        r"project.*?(\d+)",
        r"minimum.*?(\d+).*?project",
        r"at least.*?(\d+).*?project"
    ]
    for pattern in project_patterns:
        match = re.search(pattern, jd_lower)
        if match:
            try:
                criteria["min_projects"] = int(match.group(1))
                break
            except:
                continue
    if 'project' in jd_lower and criteria["min_projects"] == 0:
        criteria["min_projects"] = 1

    # Hackathon
    hackathon_indicators = ['hackathon', 'coding competition', 'programming contest']
    for indicator in hackathon_indicators:
        if indicator in jd_lower:
            criteria["hackathon_required"] = True
            break

    # Coverage estimation
    extracted = {
        "cgpa": criteria["min_cgpa"] > 0.0,
        "skills": len(criteria["must_have_skills"]) > 0,
        "internships": criteria["min_internships"] > 0,
        "projects": criteria["min_projects"] > 0,
        "hackathon": criteria["hackathon_required"]
    }
    coverage = round(100 * sum(extracted.values()) / len(extracted), 2)
    criteria["coverage_percent"] = f"{coverage}%"

    return criteria

def run(state):
    print("📄 JD Parser started...")
    if not state.file_path or not os.path.exists(state.file_path):
        print("❌ Invalid file path")
        state.jd_criteria = {}
        return state

    jd_text = extract_jd_text(state.file_path)
    print(f"🔍 Extracted JD text ({len(jd_text)} characters):")
    print(jd_text[:500] + "..." if len(jd_text) > 500 else jd_text)

    criteria = parse_jd_criteria(jd_text)
    print("✅ Parsed criteria:", criteria)

    state.jd_criteria = {
        "content": f"""
🧾 JD Criteria Extracted:
- CGPA ≥ {criteria['min_cgpa']}
- Must-Have Skills: {', '.join(criteria['must_have_skills'])}
- Preferred Skills: {', '.join(criteria['preferred_skills'])}
- Min Internships: {criteria['min_internships']}
- Min Projects: {criteria['min_projects']}
- Hackathon Required: {criteria['hackathon_required']}
- Coverage: {criteria['coverage_percent']}
""".strip(),
        **criteria
    }
    return state
