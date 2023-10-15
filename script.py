import sys
import multiprocessing
import subprocess
from bs4 import BeautifulSoup


def search_students(page_number: int) -> str:
    """
    Searches for students in Sigarra on a specific page number using a curl command.

    Args:
        page_number (int): The page number to search for students on.

    Returns:
        str: The output of the curl command as a string.
    """
    global SI_SESSION, SI_SECURITY
    curl_command = f'curl -b "SI_SESSION={SI_SESSION};SI_SECURITY={SI_SECURITY}" "https://sigarra.up.pt/feup/pt/fest_geral.fest_list?pv_estado=1&pv_curso_id=22841&pv_ano_curr_max=1&pv_n_registos=10&pv_num_pag={page_number}"'

    print(f"Searching for students on page {page_number}: {curl_command}")

    result = subprocess.run(curl_command, shell=True, capture_output=True, text=True, encoding="iso-8859-15")
    return result.stdout

def get_student_ids():
    """
    Returns a tuple of sorted student IDs by scraping Sigarra using multiprocessing.

    Returns:
    tuple: A tuple of sorted student IDs (strings).
    """
    student_ids = []
    with multiprocessing.Pool() as pool: results = pool.map(search_students, range(1, 110))
    list_pages = tuple(BeautifulSoup(result, 'html.parser') for result in results)

    for page in list_pages:
        for table in page.find_all('table', {'class': 'dados'}):
            for tr in table.find_all('tr', {'class': ['i', 'p']}):
                student_ids.append(tr.findChildren()[0].find('a', {'title': 'Visualizar estudante'}).text.strip())
    return tuple(sorted(student_ids))

def is_first_yeat(student_id: str) -> str:
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
    student_list = get_student_ids()
    student_list = tuple(filter(is_first_yeat, student_list))
    print("Nº of Students in first year of computer science:", len(student_list))
    for x in student_list:
        print(x)
    for x in student_list:
        print(f"up{x}@up.pt")



if __name__ == "__main__":
    with open(sys.argv[1], 'r') as file:
        SI_SESSION  = file.readline().strip()
        SI_SECURITY = file.readline().strip()
    YEARS_TO_SEARCH = [x for x in sys.argv[2]]
    main()