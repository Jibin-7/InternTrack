from flask_login import UserMixin
from core import db, login_manager
from bson.objectid import ObjectId
import datetime

@login_manager.user_loader
def load_user(user_id):
    u = db.users.find_one({"_id": ObjectId(user_id)})
    if not u: return None
    return User(u)

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.name = user_data['name']
        self.email = user_data['email']
        self.role = user_data['role']
        self.skills = user_data.get('skills', '')
        self.github = user_data.get('github', '')
        self.linkedin = user_data.get('linkedin', '')
        
        # Profile Fields
        self.education = user_data.get('education', '')
        self.cgpa = user_data.get('cgpa', '')
        self.experience = user_data.get('experience', '')
        self.resume_link = user_data.get('resume_link', '')
        self.certificate_link = user_data.get('certificate_link', '')
        
        self.verification_status = user_data.get('verification_status', 'Pending')
        self.placement_status = user_data.get('placement_status', 'Open')
        self.notifications = user_data.get('notifications', [])

    # --- CRITICAL FIX: THIS WAS MISSING ---
    @property
    def unread_notifications_count(self):
        count = 0
        for n in self.notifications:
            # Check if notification is a Dictionary (New format) AND is_read is False
            if isinstance(n, dict) and not n.get('is_read', False):
                count += 1
        return count

    @staticmethod
    def create_user(name, email, password, role, skills):
        user_data = {
            "name": name, "email": email, "password": password, "role": role, "skills": skills,
            "verification_status": "Pending" if role == 'student' else "Verified",
            "placement_status": "Open", "notifications": [],
            "github": "", "linkedin": "", 
            "education": "", "cgpa": "", "experience": "", 
            "resume_link": "", "certificate_link": ""
        }
        return db.users.insert_one(user_data)

    @staticmethod
    def update_profile(user_id, data):
        db.users.update_one({"_id": ObjectId(user_id)}, {"$set": data})

class Job:
    @staticmethod
    def create_job(title, company, skills, description, posted_by, salary):
        return db.jobs.insert_one({
            "title": title, "company": company, "skills": skills,
            "description": description, "posted_by": posted_by, "salary": salary,
            "applicants": [],
            "posted_date": datetime.datetime.now()
        })
    
    @staticmethod
    def apply_to_job(job_id, user):
        applicant_entry = {
            "user_id": user.id, "name": user.name, "email": user.email, "skills": user.skills,
            "status": "Applied", "applied_date": datetime.datetime.now()
        }
        db.jobs.update_one(
            {"_id": ObjectId(job_id), "applicants.user_id": {"$ne": user.id}}, 
            {"$push": {"applicants": applicant_entry}}
        )

    @staticmethod
    def update_applicant_status(job_id, user_id, new_status):
        db.jobs.update_one(
            {"_id": ObjectId(job_id), "applicants.user_id": user_id},
            {"$set": {"applicants.$.status": new_status}}
        )
        if new_status == "Hired":
            db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"placement_status": "Placed"}})
        elif new_status == "Interviewing":
            db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"placement_status": "Interviewing"}})
        elif new_status == "Hold":
            db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"placement_status": "Hold"}})
        elif new_status == "Rejected":
             db.users.update_one(
                 {"_id": ObjectId(user_id), "placement_status": {"$nin": ["Placed", "Interviewing"]}}, 
                 {"$set": {"placement_status": "Rejected"}}
             )
    
    @staticmethod
    def delete_job(job_id):
        db.jobs.delete_one({"_id": ObjectId(job_id)})