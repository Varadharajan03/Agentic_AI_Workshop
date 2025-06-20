# agents/gap_analyzer.py
from pymongo import MongoClient
import traceback

def run(state):
    print("🔍 Gap Analyzer started...")
    
    try:
        if not state.eligibility_results:
            print("⚠️ No eligibility results available")
            state.gap_analysis = []
            return state
        
        if not state.jd_criteria:
            print("⚠️ No JD criteria available")
            state.gap_analysis = []
            return state
        
        # Get student data from MongoDB
        client = MongoClient("mongodb://localhost:27017/")
        db = client.eligibility_tracker
        students_collection = db.students
        
        # Create student lookup dictionary
        students_data = {}
        for student in students_collection.find({}, {"_id": 0}):
            students_data[student["student_id"]] = student
        
        client.close()
        
        # Get criteria
        jd_criteria = state.jd_criteria
        required_skills = jd_criteria.get("must_have_skills", [])
        min_cgpa = jd_criteria.get("min_cgpa", 0.0)
        min_internships = jd_criteria.get("min_internships", 0)
        min_projects = jd_criteria.get("min_projects", 0)
        hackathon_required = jd_criteria.get("hackathon_required", False)
        
        gaps_analysis = []
        
        for eligibility_result in state.eligibility_results:
            student_id = eligibility_result["student_id"]
            
            if student_id not in students_data:
                print(f"⚠️ Student {student_id} not found in database")
                continue
            
            student = students_data[student_id]
            student_gaps = []
            gap_reasons = []
            recommendations = []
            
            # Analyze skill gaps
            student_skills = [skill.lower().strip() for skill in student.get("skills", [])]
            missing_skills = []
            
            for required_skill in required_skills:
                skill_found = False
                required_skill_lower = required_skill.lower().strip()
                
                for student_skill in student_skills:
                    if (required_skill_lower in student_skill or 
                        student_skill in required_skill_lower or
                        required_skill_lower == student_skill):
                        skill_found = True
                        break
                
                if not skill_found:
                    missing_skills.append(required_skill)
            
            if missing_skills:
                student_gaps.extend(missing_skills)
                gap_reasons.append(f"Missing technical skills: {', '.join(missing_skills)}")
                recommendations.append(f"Learn {', '.join(missing_skills)} through online courses and projects")
            
            # Analyze CGPA gap
            student_cgpa = student.get("cgpa", 0.0)
            if student_cgpa < min_cgpa:
                student_gaps.append("cgpa")
                gap_reasons.append(f"CGPA {student_cgpa} is below required {min_cgpa}")
                recommendations.append("Focus on improving academic performance")
            
            # Analyze internship gap
            student_internships = student.get("internships", 0)
            if student_internships < min_internships:
                gap_count = min_internships - student_internships
                student_gaps.append("internships")
                gap_reasons.append(f"Need {gap_count} more internship(s)")
                recommendations.append("Apply for internships to gain practical experience")
            
            # Analyze project gap
            student_projects = student.get("projects", 0)
            if student_projects < min_projects:
                gap_count = min_projects - student_projects
                student_gaps.append("projects")
                gap_reasons.append(f"Need {gap_count} more project(s)")
                recommendations.append("Build portfolio projects to demonstrate skills")
            
            # Analyze hackathon gap
            student_hackathons = student.get("hackathons", 0)
            if hackathon_required and student_hackathons == 0:
                student_gaps.append("hackathons")
                gap_reasons.append("Hackathon participation required")
                recommendations.append("Participate in coding competitions and hackathons")
            
            # Priority classification
            priority = "high" if len(student_gaps) > 3 else "medium" if len(student_gaps) > 1 else "low"
            
            gaps_analysis.append({
                "student_id": student_id,
                "name": student.get("name", "Unknown"),
                "gaps": student_gaps,
                "reasons": gap_reasons,
                "recommendations": recommendations,
                "priority": priority,
                "current_status": eligibility_result["status"],
                "gap_count": len(student_gaps)
            })
        
        # Summary statistics
        high_priority = len([g for g in gaps_analysis if g["priority"] == "high"])
        medium_priority = len([g for g in gaps_analysis if g["priority"] == "medium"])
        low_priority = len([g for g in gaps_analysis if g["priority"] == "low"])
        
        print(f"📊 Gap Analysis Complete: {high_priority} high priority, {medium_priority} medium priority, {low_priority} low priority")
        
        state.gap_analysis = gaps_analysis
        
    except Exception as e:
        print(f"❌ Error in Gap Analyzer: {str(e)}")
        print(traceback.format_exc())
        state.gap_analysis = []
    
    return state