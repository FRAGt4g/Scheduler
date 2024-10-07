import json
import random
import os
from typing import TypeVar
import pprint

T = TypeVar("T")

def rand_pop(list: list[T]) -> T:
    list.remove(x:= random.choice(list))
    return x

def rand_n_samples(original_list:list[T], n: int) -> list[list[T]]:
    if n > len(original_list):
        raise ValueError("Number of sublists cannot exceed the length of the original list.")
        
    # Shuffle the list to randomize element order
    random.shuffle(original_list)
    
    # Initialize variables
    remaining_elements = original_list[:]
    result = []
    
    # Distribute elements randomly among the specified number of sublists
    for i in range(n):
        if i == n - 1: result.append(remaining_elements) # The last sublist gets all the remaining elements
        
        else:
            # Calculate the max possible length for this sublist
            max_length = len(remaining_elements) - (n - len(result) - 1)
            sample_length = random.randint(1, max_length)
            
            # Get a random sample of the determined length
            result.append(remaining_elements[:sample_length])
            
            # Remove the sampled elements from the remaining list
            remaining_elements = remaining_elements[sample_length:]
    
    return result

def rand_samples(elements: list[T]) -> list[list[T]]:
    random.shuffle(elements)
    sub_lists: list[list[T]] = []

    while len(elements) > 0:
        sub_lists.append(elements[:(index:=random.randint(1, len(elements)))])
        elements = elements[index:]

    return sub_lists

def remove_all(list: list[T], removing: list[T]):
    for to_remove in removing: list.remove(to_remove)
def read(filename): return json.load(open(filename, "r"))
def write_into(filename, info):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f: json.dump(info, f, indent=2)

def generate_student_json(filename: str, student_count: int, teacher_json: str, grades: list[str], required_class_range: range, requested_class_range: range, backup_count: int, possibile_ids: range=range(100_00000, 100_99999)):
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
        f"{rand_pop(allowed_room_numbers)}": {
            "capacity": random.choice(capacity_range)
        }
        for _ in range(count)
    })

def generate_teacher_json(filename, count: int, teacher_names: list[str], course_count_range:range, working_periods_range: range, allowed_periods: list[str], room_json, courses: list[str]):
    rooms = [room for room in read(room_json)]
    teachers: dict = {}
    for _ in range(min(count, len(teacher_names))):
        room = rand_pop(rooms)
        courses_taught = random.sample(courses, random.choice(course_count_range))
        periods_per_class = rand_n_samples(random.sample(allowed_periods, random.choice(working_periods_range)), len(courses_taught))
        teachers[rand_pop(teacher_names)] = {
            rand_pop(courses_taught): {
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


def write_results(filename, results: dict[int, list[tuple[str, str, str]]]):
    write_into(filename, {
        student_id: [
            {
                "course": course,
                "period": period,
                "teacher": teacher
            } for course, period, teacher in results[student_id]
        ] for student_id in results
    })