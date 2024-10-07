from ortools.sat.python.cp_model import IntVar, LiteralT
from ortools.sat.python import cp_model
import JSONManager as json_builder
import time

RESULTS = dict[int, list[tuple[str, str, str]]]
STUDENT_COUNT = int
STATS = tuple[float, str]
TIME_LOG = list[tuple[str, float, float]]
def solve_json(student_json: str, course_json: str, max_count: int | None) -> tuple[RESULTS, STUDENT_COUNT, STATS, TIME_LOG]:
    def check_data_validity(student_link, course_link):
        if not isinstance(student_link, str) or not student_link.endswith(".json"):
            raise TypeError("Student JSON file must be a string ending in '.json'")
        if not isinstance(course_link, str) or not course_link.endswith(".json"):
            raise TypeError("Course JSON file must be a string ending in '.json'")
        courses = json_builder.read(course_link)
        for course in courses:
            if not isinstance(courses[course], dict):
                raise TypeError("Course data must be a dictionary.")
            if "periods" not in courses[course]:
                raise ValueError("Course data must contain 'periods' key.")
            if not isinstance(courses[course]["periods"], dict):
                raise TypeError("Course periods must be a dictionary.")
            for period in courses[course]["periods"]:
                if not isinstance(courses[course]["periods"][period], list):
                    raise TypeError("Classrooms must be a list.")
                for classroom in courses[course]["periods"][period]:
                    if not isinstance(classroom, dict):
                        raise TypeError("Classroom data must be a dictionary.")
                    if "teacher" not in classroom:
                        raise ValueError("Classroom data must contain 'teacher' key.")
                    if not isinstance(classroom["teacher"], str):
                        raise TypeError("Teacher must be a string.")
                    if "capacity" not in classroom:
                        raise ValueError("Classroom data must contain 'capacity' key.")
                    if not isinstance(classroom["capacity"], int):
                        raise TypeError("Capacity must be an integer.")
    
    # time_logs: dict[str, tuple[float, tuple[float, float]]] = {} #Key: (Time at this step, (Start time, end time))
    time_logs: list[tuple[str, float, float]] = [] #Key: (Time at this step, (Start time, end time))
    start_time = time.time()
    check_data_validity(student_json, course_json)
    time_logs.append(("safety check(s)", time.time(), time.time() - start_time))
    # time_logs["safety check"] = (time.time() - list([time_logs[log] for log in time_logs])[-1], (time.time(), list([time_logs[log][1][1] for log in time_logs])[-1]))
    
    courses = json_builder.read(course_json)
    students = json_builder.read(student_json)
    if max_count is not None: students = dict(list(students.items())[:max_count])
    
    student_count = len(students)
    time_logs.append(("reading json", time.time(), time.time() - time_logs[-1][1]))
    # time_logs["reading json"] = (time.time() - list([time_logs[log][1][1] for log in time_logs])[-1], (time.time(), list([time_logs[log][1][1] for log in time_logs])[-1]))
    model = cp_model.CpModel()

    x = {
        (student, course, period, classroom["teacher"]): model.NewBoolVar(f"x_{student}_{course}_{period}_{classroom}") 
        for student in students 
        for course in courses 
        for period in courses[course]["periods"]
        for classroom in courses[course]["periods"][period]
    }
    
    # 1. Required Classes: Each student must be assigned to all required classes
    for student in students:
        for required_class in students[student]["required_classes"]:
            # Sum over all possible time slots for class j
            model.Add(
                sum(
                    x[(student, required_class, period, classroom["teacher"])] 
                    for period in courses[required_class]["periods"]
                    for classroom in courses[required_class]["periods"][period]
                ) == 1
            )
    
    # 2. Class Capacity: No class exceeds its capacity
    for required_class in courses:
        for period in courses[required_class]["periods"]:
            for classroom in courses[required_class]["periods"][period]:
                model.Add(
                    sum(
                        x[(s, required_class, period, classroom["teacher"])] for s in students
                    ) <= classroom["capacity"]
                )
    
    # 3. Time Slot Conflicts: A student cannot be in more than one class at the same time
    periods = set([
        period
        for course in courses
        for period in courses[course]["periods"]
    ])
    for student in students:
        for period in periods:
            # For all students, make sure that the sum of all classes at a given period is less than or equal to 1
            courses_at_t = [course for course in courses if period in courses[course]["periods"]]
            if len(courses_at_t) > 0:
                model.Add(
                    sum(
                        x[(student, course, period, classroom["teacher"])] 
                        for course in courses_at_t
                        for classroom in courses[course]["periods"][period]
                    ) <= 1
                )
    time_logs.append(("constraints", time.time(), time.time() - time_logs[-1][1]))
    
    solver = cp_model.CpSolver()
    model.Maximize(
        sum(
            x[(student, course, period, classroom["teacher"])] 
            for student in students 
            for course in courses 
            for period in courses[course]["periods"]
            for classroom in courses[course]["periods"][period]
        )
    )
    solver.Solve(model)
    time_logs.append(("solving", time.time(), time.time() - time_logs[-1][1]))
    
    
    if solver.StatusName() != "OPTIMAL" and solver.StatusName() != "FEASIBLE":
        return ({}, student_count, (solver.ObjectiveValue(), solver.StatusName()), time_logs)
    
    results: dict[int, list[tuple[str, str, str]]] = {student: [] for student in students}
    for (student, course, period, teacher), val in x.items():
        if solver.BooleanValue(val) is True:
            results[student].append((course, period, teacher))
    
    return (results, student_count, (solver.ObjectiveValue(), solver.StatusName()), time_logs)




"""
Old System. Saving incase new one has problems...

Courses = Dict[
    str,                    # Course Name 
    Dict[                   # Periods & Classrooms
        str,                # Period
        list[Dict[          # Classrooms
            str,        
            str | int       # Teacher / Capacity
        ]]
    ] | 
    Dict[str, list[str]] |  # Credits
    Dict[str, str] |        # Length of class
    Dict[str, Dict[         # Grade Weights
        str, int
    ]] | 
    Dict[str, List[str]]    # Prerequisites
]

class Student:
    def __init__(self, student_id: int, grade_level: str, required_classes: list[str], requested_classes: dict[str, list[str]]):
        self.id = student_id
        self.grade_level = grade_level
        self.required_classes = required_classes
        self.requested_classes = requested_classes
class Course:
    def __init__(self, name: str, time_slots: list[str], capacity: int, grade_weights: dict[str, int]):
        self.name = name
        self.time_slots = time_slots
        self.capacity = capacity
        self.grade_weight = grade_weights
class ScheduleBuilder:
    def __init__(self, courses: list[Course], periods: list[str], grade_levels: list[str], students: list[Student] = []):
        self.periods = periods
        self.grades = grade_levels
        self.courses = {courses.name: courses for courses in courses}
        self.students = {student.id: student for student in students}
        self.model = cp_model.CpModel()
        self.x: dict[tuple[int, str, str], LiteralT] = {}

    def populate_student_information(self, student_count: int, id_range: tuple[int, int] = (100_00000, 100_99999)) -> None:
        for _ in range(1, student_count + 1):
            while (id := random.randint(id_range[0], id_range[1])) in self.students: continue

            self.students[id] = Student(id, 
                grade_level=random.choice(self.grades), 
                required_classes=random.sample(list(self.courses.keys()), random.randint(3, 5)), 
                requested_classes= {
                    intended: random.sample(list(self.courses.keys()), 3) for intended in random.sample(list(self.courses.keys()), random.randint(3, 5))
                }
            )
    
    def build_model(self):
        # Decision Variables
        # x[(i, c, t)] = 1 if student s is assigned to class c at time t
        self.x = {
            (s, c, t): self.model.NewBoolVar(f"x_{s}_{c}_{t}") 
            for s in self.students for c in self.courses for t in self.courses[c].time_slots
        }
        
        # const
        
        # 1. Required Classes: Each student must be assigned to all required classes
        for s in self.students:
            for c in self.students[s].required_classes:
                # Sum over all possible time slots for class j
                self.model.Add(sum(self.x[(s, c, t)] for t in self.courses[c].time_slots) == 1)
        
        # 2. Class Capacity: No class exceeds its capacity
        for c in self.courses:
            for t in self.courses[c].time_slots:
                self.model.Add(
                    sum(self.x[(s, c, t)] for s in self.students) <= self.courses[c].capacity
                )
        
        # 3. Time Slot Conflicts: A student cannot be in more than one class at the same time
        for s in self.students:
            for t in self.periods:
                # If 
                courses_at_t = [course for course in self.courses if t in self.courses[course].time_slots]
                if len(courses_at_t) > 0:
                    self.model.Add(sum(self.x[(s, c, t)] for c in courses_at_t) <= 1)
    
    def solve_model(self) -> tuple[dict[int, list[tuple[str, str]]], float, str]:
        solver = cp_model.CpSolver()
        self.model.Maximize(sum(self.x[(s, c, t)] for s in self.students for c in self.courses for t in self.courses[c].time_slots))
        solver.Solve(self.model)
        if solver.StatusName() != "OPTIMAL" and solver.StatusName() != "FEASIBLE":
            return ({}, solver.ObjectiveValue(), solver.StatusName())
        
        results: dict[int, list[tuple[str, str]]] = {student: [] for student in self.students}
        for (student, course, time), val in self.x.items():
            if solver.BooleanValue(val):
                results[student].append((course, time))
        
        return (results, solver.ObjectiveValue(), solver.StatusName())


    def solve(students, courses, periods, grade_levels):
        scheduler = ScheduleBuilder(courses, periods, grade_levels, students)
        scheduler.build_model()
        return scheduler.solve_model()
        if solver.StatusName() != "OPTIMAL" and solver.StatusName() != "FEASIBLE":
            return ({}, solver.ObjectiveValue(), solver.StatusName())
        
        results: dict[int, list[tuple[str, str]]] = {student: [] for student in self.students}
        for (student, course, time), val in self.x.items():
            if solver.BooleanValue(val):
                results[student].append((course, time))
        return (results, solver.ObjectiveValue(), solver.StatusName())
        


    def solve(students, courses, periods, grade_levels):
        scheduler = ScheduleBuilder(courses, periods, grade_levels, students)
        scheduler.build_model()
        return scheduler.solve_model()
        if solver.StatusName() != "OPTIMAL" and solver.StatusName() != "FEASIBLE":
            return ({}, solver.ObjectiveValue(), solver.StatusName())
        
        results: dict[int, list[tuple[str, str]]] = {student: [] for student in self.students}
        for (student, course, time), val in self.x.items():
            if solver.BooleanValue(val):
                results[student].append((course, time))
        
        return (results, solver.ObjectiveValue(), solver.StatusName())


    def solve(students, courses, periods, grade_levels):
        scheduler = ScheduleBuilder(courses, periods, grade_levels, students)
        scheduler.build_model()
        return scheduler.solve_model()"""