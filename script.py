import sys
import subprocess
import concurrent.futures
from bs4 import BeautifulSoup


def search_students(page_number: int) -> str:
    """
    Searches for students in Sigarra on a specific page number using a curl command.

    Args:
        page_number (int): The page number to search for students on.

    Returns:
        str: The output of the curl command as a string.
    """
    global SI_SESSION, SI_SECURITY, YEARS_TO_SEARCH, COURSE_TO_SEARCH
    curl_command = f'curl -b "SI_SESSION={SI_SESSION};SI_SECURITY={SI_SECURITY}" "https://sigarra.up.pt/feup/pt/fest_geral.fest_list?pv_estado=1&pv_curso_id={COURSE_TO_SEARCH}&pv_n_registos=50&pv_num_pag={page_number}"'

    print(f"Searching for students on page {page_number}: {curl_command}")

    result = subprocess.run(curl_command, shell=True, capture_output=True, text=True, encoding="iso-8859-15")
    return result.stdout

def get_student_ids() -> tuple:
    """
    This function uses multithreading to scrape Sigarra for student IDs. It creates a thread pool of threads
    and maps the search_students function to a range of 1 to 1000. The results are then parsed using BeautifulSoup and the
    student IDs are extracted from the HTML. The IDs are then sorted and returned as a tuple.

    Returns:
    tuple: A tuple of sorted student IDs (strings).
    """
    global MAX_THREADS
    student_ids = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        results = executor.map(search_students, range(1, 1000))
    list_pages = tuple(BeautifulSoup(result, 'html.parser') for result in results)

    for page in list_pages:
        for table in page.find_all('table', {'class': 'dados'}):
            for tr in table.find_all('tr', {'class': ['i', 'p']}):
                student_ids.append(tr.findChildren()[0].find('a', {'title': 'Visualizar estudante'}).text.strip())
    return tuple(sorted(student_ids))

def filter_student_IDs(student_id: str) -> str:
    """
    Retrieves the HTML page for a student ID from the SIGARRA website.

    Args:
        student_id (str): The student ID to retrieve the page for.

    Returns:
        str: The HTML page for the student ID.
    """
    global SI_SESSION, SI_SECURITY
    curl_command = f'curl -b "SI_SESSION={SI_SESSION};SI_SECURITY={SI_SECURITY}" "https://sigarra.up.pt/feup/pt/fest_geral.cursos_list?pv_num_unico={student_id}"'

    print(f"Retrieving page for student ID {student_id}: {curl_command}")

    curl_output = subprocess.run(curl_command, shell=True, capture_output=True, text=True, encoding="iso-8859-15").stdout
    
    page = BeautifulSoup(curl_output, 'html.parser')
    for i_curso, curso in enumerate(page.find_all('div', {'class': 'estudante-lista-curso-activo'})):
        try:
            if curso.find('div', {'class': 'estudante-lista-curso-nome'}).find('a').text.strip() == "Licenciatura em Engenharia Informática e Computação":
                if curso.find('table').findChildren()[0].findChildren()[1].text.strip() == "1":
                    return True
        except:
            print(f"Error on student ID {student_id} on course {i_curso}: https://sigarra.up.pt/feup/pt/fest_geral.cursos_list?pv_num_unico={student_id}")
    return False

def main():
    global YEARS_TO_SEARCH, COURSE_TO_SEARCH
    student_IDs = get_student_ids()
    print(f"Nº of Student IDs found:", student_IDs)
    student_Data = tuple(filter(filter_student_IDs, student_IDs))
    print(f"Nº of Students found in Course({COURSE_TO_SEARCH}), in Years({YEARS_TO_SEARCH}):", len(student_Data))



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
                YEARS_TO_SEARCH = [y for y in x[:2]]
            case "-c":
                COURSE_TO_SEARCH = int(x[:2])
            case "-t":
                MAX_THREADS = int(x[:2])
            case _:
                print("Invalid argument: {x}")
                exit()
    main()