import sys
import subprocess
import concurrent.futures
from bs4 import BeautifulSoup

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    LIGHTGREY = '\033[37m'
    DARKGREY = '\033[90m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def get_student_ids() -> tuple:
    """
    This function uses multithreading to scrape Sigarra for student IDs. It creates a thread pool of threads
    and maps the search_students function to a range of 1 to 1000. The results are then parsed using BeautifulSoup and the
    student IDs are extracted from the HTML. The IDs are then sorted and returned as a tuple.

    Returns:
    tuple: A tuple of sorted student IDs (strings).
    """

    def page_number_to_search() -> int:
        """
        Retrieves the number of pages to search for a given course.

        Returns:
        int: The number of pages to search.
        """

        global SI_SESSION, SI_SECURITY, YEARS_TO_SEARCH, COURSE_TO_SEARCH
        curl_command = f'curl -b "SI_SESSION={SI_SESSION};SI_SECURITY={SI_SECURITY}" "https://sigarra.up.pt/feup/pt/fest_geral.fest_list?pv_estado=1&pv_curso_id={COURSE_TO_SEARCH}&pv_n_registos=50&pv_num_pag=1"'
        print(f"Retrieving number of pages: {bcolors.DARKGREY}{curl_command}{bcolors.ENDC}")
        result = subprocess.run(curl_command, shell=True, capture_output=True, text=True, encoding="iso-8859-15")
        page = BeautifulSoup(result.stdout, 'html.parser')
        n = int(page.find('p', {'class': 'paginar-registos'}).text.strip().split(' ')[-1]) // 50 + 1
        print(f"Found {bcolors.OKCYAN}{n}{bcolors.ENDC} pages.")
        return n

    def search_students(page_number: int) -> tuple:
        """
        Searches for students in Sigarra on a specific page number using a curl command.

        Args:
            page_number (int): The page number to search for students on.

        Returns:
            tuple: A tuple containing the IDs of the students found on the specified page.
        """
        
        global SI_SESSION, SI_SECURITY, YEARS_TO_SEARCH, COURSE_TO_SEARCH
        curl_command = f'curl -b "SI_SESSION={SI_SESSION};SI_SECURITY={SI_SECURITY}" "https://sigarra.up.pt/feup/pt/fest_geral.fest_list?pv_estado=1&pv_curso_id={COURSE_TO_SEARCH}&pv_n_registos=50&pv_num_pag={page_number}"'

        print(f'Searching for students on page {bcolors.OKCYAN}{page_number}{bcolors.ENDC}: {bcolors.DARKGREY}"https://sigarra.up.pt/feup/pt/fest_geral.fest_list?pv_estado=1&pv_curso_id={COURSE_TO_SEARCH}&pv_n_registos=50&pv_num_pag={page_number}"{bcolors.ENDC}')

        result = subprocess.run(curl_command, shell=True, capture_output=True, text=True, encoding="iso-8859-15")
        page = BeautifulSoup(result.stdout, 'html.parser')
        ids = ()
        for table in page.find_all('table', {'class': 'dados'}):
            for tr in table.find_all('tr', {'class': ['i', 'p']}):
                ids = ids + (tr.findChildren()[0].find('a', {'title': 'Visualizar estudante'}).text.strip(),)
        return ids

    global MAX_THREADS
    student_ids = ()
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor: results = executor.map(search_students, range(1, page_number_to_search() +1))
    for result in results: student_ids += result
    return tuple(sorted(student_ids))


def filter_student_IDs(student_ids: tuple) -> tuple:
    """
    Filters a list of student IDs and retrieves information about each student from the Sigarra website.

    Args:
    - student_ids (tuple): A tuple containing the student IDs to search for.

    Returns:
    - tuple: A tuple containing the student ID, name, year, and email address for each student found.
    """
    
    def filter_student_id(student_id:str) -> tuple:
        """
        Retrieves information about a student from the FEUP website given their student ID.

        Args:
        - student_id (str): The student ID to search for.

        Returns:
        - tuple: A tuple containing the student ID, name, year, and email address if the student is found. Otherwise, an empty tuple is returned.
        """
        global SI_SESSION, SI_SECURITY, COURSE_TO_SEARCH, YEARS_TO_SEARCH
        curl_command = f'curl -b "SI_SESSION={SI_SESSION};SI_SECURITY={SI_SECURITY}" "https://sigarra.up.pt/feup/pt/fest_geral.cursos_list?pv_num_unico={student_id}"'

        print(f'Retrieving page for student ID {bcolors.OKCYAN}{student_id}{bcolors.ENDC}: {bcolors.DARKGREY}"https://sigarra.up.pt/feup/pt/fest_geral.cursos_list?pv_num_unico={student_id}"{bcolors.ENDC}')

        curl_output = subprocess.run(curl_command, shell=True, capture_output=True, text=True, encoding="iso-8859-15").stdout
        
        page = BeautifulSoup(curl_output, 'html.parser')
        try: name = page.find('div', {'class': 'estudante-info-nome'}).text.strip()
        except: print(f"Error on student ID {bcolors.FAIL}{student_id}{bcolors.ENDC}: {bcolors.DARKGREY}https://sigarra.up.pt/feup/pt/fest_geral.cursos_list?pv_num_unico={student_id}{bcolors.ENDC}"); return ()
        for i_curso, curso in enumerate(page.find_all('div', {'class': 'estudante-lista-curso-activo'})):
            try:
                if str(curso.find('div', {'class': 'estudante-lista-curso-nome'}).find('a')).find(f"pv_curso_id={COURSE_TO_SEARCH}") != -1:
                    year = curso.find('table').findChildren()[0].findChildren()[1].text.strip()
                    if year in YEARS_TO_SEARCH: 
                        print(f"Found student {bcolors.OKCYAN}{student_id}{bcolors.ENDC} {bcolors.OKGREEN if year=='1' else bcolors.WARNING if year=='2' else bcolors.FAIL}{year}{bcolors.ENDC} {bcolors.LIGHTGREY}{name}{bcolors.ENDC}")
                        return (student_id, year, name, f"up{student_id}@up.pt")
            except:
                print(f"Error on student ID {bcolors.FAIL}{student_id}{bcolors.ENDC} on course {bcolors.FAIL}{i_curso}{bcolors.ENDC}: {bcolors.DARKGREY}https://sigarra.up.pt/feup/pt/fest_geral.cursos_list?pv_num_unico={student_id}{bcolors.ENDC}")
        return ()
    
    global MAX_THREADS
    student_data = ()
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor: results = executor.map(filter_student_id, student_ids)
    for result in results: 
        if len(result)>0: student_data += (result,)
    return student_data


def main():
    global YEARS_TO_SEARCH, COURSE_TO_SEARCH
    student_IDs = get_student_ids()
    print(f"Nº of Student IDs found: {bcolors.OKCYAN}{len(student_IDs)}{bcolors.ENDC}")
    student_Data = filter_student_IDs(student_IDs)
    print(f"Nº of Students found in Course({bcolors.DARKGREY}{COURSE_TO_SEARCH}{bcolors.ENDC}), in Years({bcolors.DARKGREY}{YEARS_TO_SEARCH}{bcolors.ENDC}): {bcolors.OKCYAN}{len(student_Data)}{bcolors.ENDC}")
    with open(f"students_{COURSE_TO_SEARCH}.txt", 'w') as file:
        for student in student_Data: file.write(f"{student[0]}\t{student[1]}\t{student[2]}\t{student[3]}\n")
    print(f"Saved to {bcolors.WARNING}students_{COURSE_TO_SEARCH}.txt{bcolors.ENDC}")


if __name__ == "__main__":
    # Define default values
    with open(sys.argv[1], 'r') as file:
        SI_SESSION  = file.readline().strip()
        SI_SECURITY = file.readline().strip()
    YEARS_TO_SEARCH = ["1"]
    COURSE_TO_SEARCH = 22841
    MAX_THREADS = 50

    # Parse arguments
    for x in sys.argv[2:]:
        match x[:2]:
            case "-y":
                YEARS_TO_SEARCH = [y for y in x[2:]]
            case "-c":
                COURSE_TO_SEARCH = int(x[2:])
            case "-t":
                MAX_THREADS = int(x[2:])
            case _:
                print("Invalid argument: {x}")
                exit()

    #print(f"Searching for students in course {COURSE_TO_SEARCH} in years {YEARS_TO_SEARCH} with {MAX_THREADS} threads.")
    main()