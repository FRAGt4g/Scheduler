import sqlite3
import random
import os

def initialize_db(filename):
    conn = sqlite3.connect(filename)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            course_id INTEGER PRIMARY KEY, 
            course_title TEXT, 
            periods TEXT, 
            max_students INTEGER, 
            grade_levels TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id INTEGER PRIMARY KEY,
            grade_level TEXT, 
            required_classes TEXT, 
            requested_classes TEXT
        )
    """)
    conn.commit()
    conn.close()

def generate_student_json(filename, student_count, courses, grades, periods, required_class_count, requested_class_count, backup_count, id_range=(100_00000, 100_99999)):
    students = {}
    for _ in range(1, student_count + 1):
        while (student_id := random.randint(id_range[0], id_range[1])) in students: continue
        
        required = random.sample([course_title for course_title in courses], required_class_count)
        unchosen = [course_title for course_title in courses if course_title not in required]
        requests = {
            # intended: random.sample([course for course in courses], backup_count) for intended in random.sample([course for course in courses], requested_class_count)
        }
        top_choices = random.sample(unchosen, requested_class_count)
        left_overs = [course for course in unchosen if course not in top_choices]
        for course in top_choices:
            requests[course] = [left_overs.pop(random.randrange(len(left_overs))) for _ in range(backup_count)]

        students[student_id] = {
            "grade_level": random.choice(grades),
            "required_classes": required,
            "requested_classes": requests
        }
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(f"{filename}", "w") as f:
        json.dump(students, f, indent=2)

def read(filename): return json.load(open(filename, "r"))

def write_results(filename, results: dict[int, list[tuple[str, str, str]]]):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(f"{filename}", "w") as json_file:
        json.dump(
            {
                student_id: [
                    {
                        "course": course,
                        "period": period,
                        "teacher": teacher
                    } for course, period, teacher in results[student_id]
                ] for student_id in results
            }, 
            json_file,
            indent=2
        )