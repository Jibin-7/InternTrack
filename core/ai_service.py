from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def calculate_similarity(student_skills, jobs):
    """
    AI Engine: Matches student skills against Job Title + Skills + Description.
    """
    if not jobs: return []
    if not student_skills: return jobs # Return all if no skills to match against

    # 1. Prepare Data
    # We give more weight to "Skills" field by repeating it
    job_texts = [f"{j['title']} {j['skills']} {j['skills']} {j['description']}" for j in jobs]
    
    # Student profile is the query
    documents = [student_skills] + job_texts
    
    # 2. Vectorize (Convert text to numbers)
    tfidf = TfidfVectorizer(stop_words='english')
    matrix = tfidf.fit_transform(documents)
    
    # 3. Compute Similarity (Student vs All Jobs)
    cosine_sim = cosine_similarity(matrix[0:1], matrix[1:]).flatten()
    
    ranked_jobs = []
    for i, score in enumerate(cosine_sim):
        job = jobs[i]
        job['match_score'] = round(score * 100) # Percentage 0-100
        job['_id'] = str(job['_id'])
        
        # Only recommend if match > 5% to filter noise
        if job['match_score'] > 5:
            ranked_jobs.append(job)
    
    # 4. Sort by Highest Match
    return sorted(ranked_jobs, key=lambda x: x['match_score'], reverse=True)