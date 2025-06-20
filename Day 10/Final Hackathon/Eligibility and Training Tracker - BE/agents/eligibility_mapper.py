# agents/eligibility_mapper.py
from pymongo import MongoClient
import traceback

def run(state):
    print("✅ Eligibility Mapper started...")
    
    try:
        # Get criteria from JD parser
        criteria = state.jd_criteria or {}
        min_cgpa = criteria.get("min_cgpa", 0.0)
        must_skills = criteria.get("must_have_skills", [])
        preferred_skills = criteria.get("preferred_skills", [])
        min_internships = criteria.get("min_internships", 0)
        min_projects = criteria.get("min_projects", 0)
        hackathon_required = criteria.get("hackathon_required", False)
        
        print(f"📋 Criteria: CGPA≥{min_cgpa}, Skills: {must_skills}, Internships≥{min_internships}, Projects≥{min_projects}, Hackathon: {hackathon_required}")
        
        # Connect to MongoDB
        client = MongoClient("mongodb://localhost:27017/")
        db = client.eligibility_tracker
        students_collection = db.students
        
        # Get all students
        students = list(students_collection.find({}, {"_id": 0}))
        print(f"👥 Processing {len(students)} students...")
        
        results = []
        
        for student in students:
            student_id = student.get("student_id", "Unknown")
            reasons = []
            status = "eligible"
            
            # Check CGPA
            student_cgpa = student.get("cgpa", 0.0)
            if student_cgpa < min_cgpa:
                status = "not_eligible"
                reasons.append(f"CGPA {student_cgpa} is below required {min_cgpa}")
            
            # Check must-have skills
            student_skills = [skill.lower().strip() for skill in student.get("skills", [])]
            missing_skills = []
            
            for required_skill in must_skills:
                skill_found = False
                required_skill_lower = required_skill.lower().strip()
                
                # Check for exact match or partial match
                for student_skill in student_skills:
                    if (required_skill_lower in student_skill or 
                        student_skill in required_skill_lower or
                        required_skill_lower == student_skill):
                        skill_found = True
                        break
                
                if not skill_found:
                    missing_skills.append(required_skill)
            
            if missing_skills:
                status = "not_eligible"
                reasons.append(f"Missing required skills: {', '.join(missing_skills)}")
            
            # Check internships
            student_internships = student.get("internships", 0)
            if student_internships < min_internships:
                status = "not_eligible"
                reasons.append(f"Has {student_internships} internship(s), requires {min_internships}")
            
            # Check projects
            student_projects = student.get("projects", 0)
            if student_projects < min_projects:
                status = "not_eligible"
                reasons.append(f"Has {student_projects} project(s), requires {min_projects}")
            
            # Check hackathons
            student_hackathons = student.get("hackathons", 0)
            if hackathon_required and student_hackathons == 0:
                status = "not_eligible"
                reasons.append("Hackathon participation required but not found")
            
            # Determine final status
            if status == "eligible" and not reasons:
                final_status = "eligible"
            elif len(reasons) <= 2:  # Allow partially eligible students
                final_status = "partially_eligible"
            else:
                final_status = "not_eligible"
            
            results.append({
                "student_id": student_id,
                "name": student.get("name", "Unknown"),
                "status": final_status,
                "reasons": reasons,
                "details": {
                    "cgpa": student_cgpa,
                    "skills": student.get("skills", []),
                    "internships": student_internships,
                    "projects": student_projects,
                    "hackathons": student_hackathons
                }
            })
        
        # Summary statistics
        eligible_count = len([r for r in results if r["status"] == "eligible"])
        partially_eligible_count = len([r for r in results if r["status"] == "partially_eligible"])
        not_eligible_count = len([r for r in results if r["status"] == "not_eligible"])
        
        print(f"📊 Results: {eligible_count} eligible, {partially_eligible_count} partially eligible, {not_eligible_count} not eligible")
        
        state.eligibility_results = results
        client.close()
        
    except Exception as e:
        print(f"❌ Error in Eligibility Mapper: {str(e)}")
        print(traceback.format_exc())
        state.eligibility_results = []
    
    return state