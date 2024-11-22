import json
import random
import os
import Helpers as addons
from typing import List, Tuple, Dict

def read(filename): return json.load(open(filename, "r"))
def write_into(filename, info):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f: json.dump(info, f, indent=2)

def generate_student_json(filename: str, student_count: int, teacher_json: str, grades: List[str], required_class_range: range, requested_class_range: range, backup_count: int, possibile_ids: range=range(100_00000, 100_99999)):
    students = {}
    teacher_info = read(teacher_json)
    courses = []
    for teacher in teacher_info:
        for course in teacher_info[teacher]:
            if course not in courses: courses.append(course)
    for _ in range(1, student_count + 1):
        while (student_id := random.choice(possibile_ids)) in students: continue
        
        required_courses = random.sample(courses, random.choice(required_class_range))
        unchosen = list(set(courses) - set(required_courses))
        requests = {
            # intended: random.sample([course for course in courses], backup_count) for intended in random.sample([course for course in courses], requested_class_count)
        }
        top_choices = random.sample(unchosen, random.choice(requested_class_range))
        left_overs = [course for course in unchosen if course not in top_choices]
        for course in top_choices:
            requests[course] = [left_overs.pop(random.randrange(len(left_overs))) for _ in range(backup_count)]

        students[student_id] = {
            "grade_level": random.choice(grades),
            "required_classes": required_courses,
            "requested_classes": requests
        }
    
    write_into(filename, students)

def generate_room_json(filename, count, capacity_range: range, room_number_range: range):
    allowed_room_numbers = list(room_number_range)
    write_into(filename, {
        f"{addons.rand_pop(allowed_room_numbers)}": {
            "capacity": random.choice(capacity_range)
        }
        for _ in range(count)
    })

def generate_teacher_json(filename, count: int, teacher_names: List[str], course_count_range:range, working_periods_range: range, allowed_periods: List[str], room_json, courses: List[str]):
    rooms = [room for room in read(room_json)]
    teachers: dict = {}
    for _ in range(min(count, len(teacher_names))):
        room = addons.rand_pop(rooms)
        courses_taught = random.sample(courses, random.choice(course_count_range))
        periods_per_class = addons.rand_n_samples(random.sample(allowed_periods, random.choice(working_periods_range)), len(courses_taught))
        teachers[addons.rand_pop(teacher_names)] = {
            addons.rand_pop(courses_taught): {
                period: room
                for period in periods_in_class
            }
            for periods_in_class in periods_per_class
        }
    write_into(filename, teachers)

def compile_course_json(filename, teacher_json, room_json):
    rooms = read(room_json)
    teachers = read(teacher_json)
    courses = { }
    for teacher in teachers:
        for subject in teachers[teacher]:
            if subject not in courses: courses[subject] = {
                "periods": { },
                "prerequisites": []
            }
            for period in teachers[teacher][subject]:
                if period not in courses[subject]["periods"]: courses[subject]["periods"][period] = []
                courses[subject]["periods"][period].append({
                    "teacher": teacher,
                    "capacity": rooms[teachers[teacher][subject][period]]["capacity"]
                })
    write_into(filename, courses)


def write_results(filename, results: Dict[int, List[Tuple[str, str, str]]]):
    write_into(filename, {
        student_id: [
            {
                "course": course,
                "period": period,
                "teacher": teacher
            } for course, period, teacher in results[student_id]
        ] for student_id in results
    })