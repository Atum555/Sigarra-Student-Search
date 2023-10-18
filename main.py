import os, sys
import src.sigarra as sigarra
from src.bcolors import bcolors


def main():
    global YEARS_TO_SEARCH, COURSE_TO_SEARCH, MAX_THREADS
    student_Data = sigarra.get_students_in(COURSE_TO_SEARCH, (SI_SESSION, SI_SECURITY), YEARS_TO_SEARCH, MAX_THREADS)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    with open(os.path.join(data_dir, f"students_{COURSE_TO_SEARCH}.txt"), 'w') as file:
        for student in student_Data: file.write(f"{student[0]}\t{student[1]}\t{student[2]}\t{student[3]}\n")
    print(f"Saved to {bcolors.WARNING}{os.path.join(data_dir, f'students_{COURSE_TO_SEARCH}.txt')}{bcolors.ENDC}")


if __name__ == "__main__":
    # Define default values
    with open(sys.argv[1], 'r') as file:
        SI_SESSION  = file.readline().strip()
        SI_SECURITY = file.readline().strip()
    YEARS_TO_SEARCH = ("1","2","3")
    COURSE_TO_SEARCH = "22841"
    MAX_THREADS = 50

    # Parse arguments
    for x in sys.argv[2:]:
        match x[:2]:
            case "-y":
                YEARS_TO_SEARCH = tuple(y for y in x[2:])
            case "-c":
                COURSE_TO_SEARCH = x[2:]
            case "-t":
                MAX_THREADS = int(x[2:])
            case _:
                print("Invalid argument: {x}")
                exit()

    #print(filter_student_IDs((202300600,)))
    #exit()

    main()