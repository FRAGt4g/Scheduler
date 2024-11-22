import JSONManager as json_builder
import Helpers as addons
import Scheduler
import Plotter
import sys


# JSON file locations
JSON_FILE_PREFIX = "../Testing Data/"
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



def ran_special_command(arguments: list[str]) -> bool:
    """
    Special Commands:
     - `generate_s` generates new fake student data
     - `generate_t` generates new fake teacher data
     - `generate_r` generates new fake room data
     - `time_comp` graphs time of the program against common big O functions 
     - `compile_c` uses teacher, student, and room data to compile course data
    """
    
    #Should add a unit test option
    if arguments[1] == "generate_s": 
        json_builder.generate_student_json(
            filename =              JSON_FILE_PREFIX + "Students.json", 
            student_count =         int(arguments[2]), 
            teacher_json =          JSON_FILE_PREFIX + "Teachers.json", 
            grades =                GRADE_LEVELS,
            required_class_range =  range(2, 5),
            requested_class_range = range(1, 6),
            backup_count =          3,
            possibile_ids =         ID_RANGE,
        )
        return True
    elif arguments[1] == "generate_t": 
        json_builder.generate_teacher_json(
            filename =              JSON_FILE_PREFIX + "Teachers.json",
            count =                 int(arguments[2]),
            teacher_names =         TEACHERS,
            course_count_range =    range(1, 3),
            working_periods_range = range(4, 8),
            allowed_periods =       PERIODS,
            room_json =             JSON_FILE_PREFIX + "Rooms.json",
            courses =               COURSE_TITLES,
        )
        return True
    elif arguments[1] == "generate_r": 
        json_builder.generate_room_json(
            filename =              JSON_FILE_PREFIX + "Rooms.json",
            count =                 int(arguments[2]),
            capacity_range =        range(1500, 300000),
            room_number_range =     range(100, 900, 2)
        )
        return True
    elif arguments[1] == "compile_c": 
        json_builder.compile_course_json(
            filename =              JSON_FILE_PREFIX + "Courses.json",
            teacher_json =          JSON_FILE_PREFIX + "Teachers.json",
            room_json =             JSON_FILE_PREFIX + "Rooms.json"
        )
        return True
    elif arguments[1] == "time_comp": 
        Plotter.graph_time_complexity(
            function =      lambda n: Scheduler.solve_json(STUDENT_JSON_LOCATION, COURSES_JSON_LOCATION, n), 
            input_range =   range(1, 1_000, 50)
        )
        return True

    return False

if __name__ == "__main__":

    if len(sys.argv) == 2 and ran_special_command(sys.argv): exit(0)

    # Solving the model
    try:
        artificial_student_count = int(sys.argv[1]) if len(sys.argv) > 1 else None
    except ValueError:
        print("Invalid input. Please provide a valid number for the artificial student count.")
        exit(1)

    print("Solving the students!")
    results, student_count, (score, status), time_logs = Scheduler.solve_json(
        STUDENT_JSON_LOCATION, COURSES_JSON_LOCATION, artificial_student_count
    )

    addons.long_print(f"""
    Solve has finised and here are the results:
        Status: '{status}'
        Score: {score}
    """)
    
    json_builder.write_results(FINAL_SCHEDULE_JSON_LOCATION, results)
    addons.log_time_info(time_logs, student_count)