from ScheduleBuilder import ScheduleBuilder, Course, Student
import StudentJSONBuilder as json_builder
import sys

# 469 is end page

# JSON file locations
JSON_FILE_PREFIX = "Testing Data/Simple/[SIMPLE] "
STUDENT_JSON_LOCATION = JSON_FILE_PREFIX + "Students.json"
COURSES_JSON_LOCATION = JSON_FILE_PREFIX + "Courses.json"
FINAL_SCHEDULE_JSON_LOCATION = JSON_FILE_PREFIX + "Schedule.json"

# Constants
ID_RANGE = range(100_000000, 100_999999)
GRADE_LEVELS = ["9th", "10th", "11th", "12th"]
PERIODS = ["A1", "A2", "A3", "A4", "B1", "B2", "B3", "B4"]
TEACHERS = [
    "Aguayo", 
    "Shockey", 
    "Arrendondo", 
    "Bailey", 
    "Snyder",
    "Goodell",
    "Mueller",
    "Williams",
    "Brockhoff",
    "Garret",
    "Hernandez",
    "Nguyen",
    "Patel",
    "Kim",
    "Clark",
    "Lewis",
    "Robinson",
    "Walker",
    "Perez",
    "Hall",
    "Young",
    "Allen",
    "King",
    "Wright",
    "Scott",
    "Green",
    "Adams",
    "Baker",
    "Gonzalez",
    "Nelson",
    "Carter",
    "Mitchell",
    "Perez",
    "Roberts",
    "Turner",
    "Phillips",
    "Campbell",
    "Parker",
    "Evans",
    "Edwards",
]
COURSE_TITLES = [
    "Algebra I",
    "Geometry",
    "Algebra II",
    "Biology",
    "Chemistry",
    "Physics",
    "English I",
    "English II",
    "English III",
    "English IV",
    "World History",
    "U.S. History",
    "Government",
    "Economics",
    "Spanish I",
    "Spanish II",
    "French I",
    "French II",
    "Physical Education",
    "Health",
    "Art",
    "Music",
    "Computer Science",
    "Drama",
    "Journalism",
    "Psychology",
    "Sociology",
]

def run_special(arguments: list[str]) -> None:
    def run_tests(): 
        print("No tests implemented yet...")

    if arguments[1] == "test": run_tests() # Run Unit tests
    elif arguments[1] == "generate_s": json_builder.generate_student_json(
        filename =              JSON_FILE_PREFIX + "Students.json", 
        student_count =         int(arguments[2]), 
        teacher_json =          JSON_FILE_PREFIX + "Teachers.json", 
        grades =                GRADE_LEVELS,
        required_class_range =  range(2, 5),
        requested_class_range = range(1, 6),
        backup_count =          3,
        possibile_ids =         ID_RANGE,
    )
    elif arguments[1] == "generate_t": json_builder.generate_teacher_json(
        filename =              JSON_FILE_PREFIX + "Teachers.json",
        count =                 int(arguments[2]),
        teacher_names =         TEACHERS,
        course_count_range =    range(1, 3),
        working_periods_range = range(4, 8),
        allowed_periods =       PERIODS,
        room_json =             JSON_FILE_PREFIX + "Rooms.json",
        courses =               COURSE_TITLES,
    )
    elif arguments[1] == "generate_r": json_builder.generate_room_json(
        filename =              JSON_FILE_PREFIX + "Rooms.json",
        count =                 int(arguments[2]),
        capacity_range =        range(1500, 300000),
        room_number_range =     range(100, 900, 2)
    )
    elif arguments[1] == "compile_c": json_builder.compile_course_json(
        filename =              JSON_FILE_PREFIX + "Courses.json",
        teacher_json =          JSON_FILE_PREFIX + "Teachers.json",
        room_json =             JSON_FILE_PREFIX + "Rooms.json"
    )
    else: raise TypeError("Invalid argument.")

    sys.exit(0)

def log_time_info(time_logs: list[tuple[str, float, float]], student_count: int) -> None:
    def formatted_time(time: float) -> str:
        if time >= 3600:
            return f"{time / 3600:.2f} hours"
        elif time >= 60:
            return f"{time / 60:.2f} minutes"
        elif time >= 1:
            return f"{time:.2f} seconds"
        elif time >= 0.001:
            return f"{time * 1000:.2f} milliseconds"
        elif time >= 0.000001:
            return f"{time * 1000000:.2f} microseconds"
        else:
            return f"{time * 1000000000:.2f} nanoseconds"

    total_time = sum(time_taken for _, _, time_taken in time_logs)
    if total_time / 2 == time_logs[-1][2]: # If last row is a total row
        total_time -= time_logs[-1][2]
        time_logs = time_logs[:-1]
    
    titles = [
        (
            f"   {' ' * (2 - len(str(round((time / total_time) * 100))))}{(time / total_time) * 100:.0f}% {log}", 
            time, 
            time / total_time
        ) for log, _, time in time_logs
    ]
    titles.sort(key=lambda title: title[2], reverse=True)
    max_title_len = max(len(title) for title, _, _ in titles)

    print("\n---------------------------------------")
    print(f"T I M I N G   L O G S :")
    for title, time, _ in titles: print(f"{title}{" " * (max_title_len - len(title))}  {formatted_time(time)}")
    print(f"\nTook {formatted_time(total_time)} for {student_count} entries\nfor an average time of {formatted_time(total_time / student_count)}")
    print("---------------------------------------\n")

if __name__ == "__main__":
    # Bug testing options
    if len(sys.argv) > 1: run_special(sys.argv)
    
    # Solving the model
    results, student_count, (score, status), time_logs = ScheduleBuilder.solve_json(STUDENT_JSON_LOCATION, COURSES_JSON_LOCATION)

    print(f"Best solution found for {student_count} students:")
    print(f"  Status: '{status}'")
    print(f"  Score: {score}")
    
    if results != {}: json_builder.write_results(FINAL_SCHEDULE_JSON_LOCATION, results)
    log_time_info(time_logs, student_count)