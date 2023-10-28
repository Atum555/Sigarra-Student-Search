import os, sys
import src.sigarra as sigarra
from src.bcolors import bcolors


def main_sigarra() -> None:
    # Invalid arguments or help
    if len(sys.argv) < 3 or sys.argv[2] in ["help", "-h"]:
        to_print =  f"{bcolors.OKBLUE}Usage:{bcolors.ENDC} {sys.argv[0]} sigarra "
        to_print += f"<{bcolors.OKGREEN}cookies_file{bcolors.ENDC}> [-y<years_to_search>] [-c<course_to_search>] [-t<max_threads>]"
        print(to_print)
        to_print =  f"{bcolors.OKBLUE}Example/Default:{bcolors.ENDC} {sys.argv[0]} sigarra "
        to_print += f"{bcolors.UNDERLINE}{bcolors.WARNING}cookies.txt{bcolors.ENDC} -y123 -c22841 -t50"
        print(to_print)
        to_print =  f"{bcolors.OKBLUE}Cookies file:{bcolors.ENDC} must be a text file with {bcolors.FAIL}SI_SESSION{bcolors.ENDC} on the first line and {bcolors.FAIL}SI_SECURITY{bcolors.ENDC} on the second line! "
        print(to_print)
        exit(1)

    # Define default values
    try:
        with open(sys.argv[2], 'r') as file:
            SI_SESSION  = file.readline().strip()
            SI_SECURITY = file.readline().strip()
    except: print(f"{bcolors.FAIL}ERROR{bcolors.ENDC} with cookies file!"); exit(1)
    YEARS_TO_SEARCH = ("1","2","3")
    COURSE_TO_SEARCH = "22841"
    MAX_THREADS = 50

    # Parse arguments
    for x in sys.argv[3:]:
        match x[:2]:
            case "-y":
                YEARS_TO_SEARCH = tuple(y for y in x[2:])
            case "-c":
                COURSE_TO_SEARCH = x[2:]
            case "-t":
                MAX_THREADS = int(x[2:])
            case _:
                print(f"{bcolors.FAIL}Invalid argument:{bcolors.ENDC} {bcolors.UNDERLINE}{x}{bcolors.ENDC}")
                exit(1)
    
    # Get Student Data
    studentData = sigarra.get_students_in(COURSE_TO_SEARCH, (SI_SESSION, SI_SECURITY), YEARS_TO_SEARCH, MAX_THREADS)
    
    # Save Data to a folder
    scriptDir = os.path.dirname(os.path.abspath(__file__))
    dataFolderDir = os.path.join(scriptDir, "data")
    if not os.path.exists(dataFolderDir): os.makedirs(dataFolderDir)
    dataDir = os.path.join(dataFolderDir, f"students_{COURSE_TO_SEARCH}_{''.join(sorted(YEARS_TO_SEARCH))}.txt")
    with open(dataDir, 'w') as file:
        for student in studentData: file.write("\t".join(x for x in student))
    print(f"Saved to {bcolors.WARNING}{dataDir}{bcolors.ENDC}")
    return None


def main_phone():
    pass

if __name__ == "__main__":
    # Invalid number of arguments or help
    def print_help() -> None:
        print(f"{bcolors.OKCYAN}Usage:{bcolors.ENDC} {sys.argv[0]} [ sigarra | phone ]")
        print(f"{bcolors.OKCYAN}For more help write:{bcolors.ENDC} {sys.argv[0]} [ sigarra | phone ] {bcolors.FAIL}-h{bcolors.ENDC}")
        exit(1)
    if len(sys.argv) < 2 or sys.argv[1] in ["help", "-h"]: print_help()

    match sys.argv[1]:
        case "sigarra": main_sigarra()
        case "phone": main_phone()
        case _: print_help()