def get_students_in(COURSE_TO_SEARCH:str, SI:tuple, YEARS_TO_SEARCH:tuple=("1", "2", "3"), MAX_THREADS:int=50, OUTPUT:bool=True) -> tuple:
    """
    This function uses multithreading to scrape Sigarra for students in a given course and years. The results are then parsed using BeautifulSoup and the student IDs are extracted from the HTML. The IDs are then sorted, filtered and information is retreved from the Sigarra website.


    Returns:
    - tuple: A tuple containing the student ID, name, year, and email address for each student found.
    """
    import time, subprocess, concurrent.futures
    from bs4 import BeautifulSoup
    from src.bcolors import bcolors

    SI_SESSION, SI_SECURITY = SI

    #def numberOfPagesToSearch(COURSE_TO_SEARCH:str, SI:tuple) -> int:
    def numberOfPagesToSearch() -> int:
        """
        Retrieves the number of pages to look for students in a given course.

        Returns:
        - int: The number of pages to search.
        """

        #SI_SESSION, SI_SECURITY = SI
        curlCommand = f'curl -b "SI_SESSION={SI_SESSION};SI_SECURITY={SI_SECURITY}" "https://sigarra.up.pt/feup/pt/fest_geral.fest_list?pv_estado=1&pv_curso_id={COURSE_TO_SEARCH}&pv_n_registos=50&pv_num_pag=1"'
        if OUTPUT: print(f"Retrieving number of pages: {bcolors.DARKGREY}{curlCommand}{bcolors.ENDC}")
        result = subprocess.run(curlCommand, shell=True, capture_output=True, text=True, encoding="iso-8859-15")
        page = BeautifulSoup(result.stdout, 'html.parser')
        paginar_registos = page.find('p', {'class': 'paginar-registos'})
        if paginar_registos is None: print(f"Error retrieving number of pages, possibly {bcolors.FAIL}invalid SI cookies{bcolors.ENDC}!"); exit()
        n = int(paginar_registos.text.strip().split(' ')[-1]) // 50 + 1 if paginar_registos is not None else 0
        if OUTPUT: print(f"Found {bcolors.OKCYAN}{n}{bcolors.ENDC} pages.")
        return n

    def search_students(page_number: int) -> tuple:
        """
        Searches for students in Sigarra on a specific page number using a curl command.

        Args:
            page_number (int): The page number to search for students on.

        Returns:
            tuple: A tuple containing the IDs of the students found on the specified page.
        """
        
        curlCommand = f'curl -b "SI_SESSION={SI_SESSION};SI_SECURITY={SI_SECURITY}" "https://sigarra.up.pt/feup/pt/fest_geral.fest_list?pv_estado=1&pv_curso_id={COURSE_TO_SEARCH}&pv_n_registos=50&pv_num_pag={page_number}"'

        if OUTPUT: print(f'Searching for students on page {bcolors.OKCYAN}{page_number}{bcolors.ENDC}: {bcolors.DARKGREY}"https://sigarra.up.pt/feup/pt/fest_geral.fest_list?pv_estado=1&pv_curso_id={COURSE_TO_SEARCH}&pv_n_registos=50&pv_num_pag={page_number}"{bcolors.ENDC}')

        curlOutput = subprocess.run(curlCommand, shell=True, capture_output=True, text=True, encoding="iso-8859-15")
        page = BeautifulSoup(curlOutput.stdout, 'html.parser')
        ids = ()
        for table in page.find_all('table', {'class': 'dados'}):
            for tr in table.find_all('tr', {'class': ['i', 'p']}):
                ids = ids + (tr.findChildren()[0].find('a', {'title': 'Visualizar estudante'}).text.strip(),)
        return ids

    def filter_student_id(student_id:str) -> tuple:
        """
        Retrieves information about a student from the FEUP website given their student ID.

        Args:
        - student_id (str): The student ID to search for.

        Returns:
        - tuple: A tuple containing the student ID, name, year, and email address if the student is found. Otherwise, an empty tuple is returned.
        """

        curlCommand = f'curl -b "SI_SESSION={SI_SESSION};SI_SECURITY={SI_SECURITY}" "https://sigarra.up.pt/feup/pt/fest_geral.cursos_list?pv_num_unico={student_id}"'

        if OUTPUT: print(f'Retrieving page for student ID {bcolors.OKCYAN}{student_id}{bcolors.ENDC}: {bcolors.DARKGREY}"https://sigarra.up.pt/feup/pt/fest_geral.cursos_list?pv_num_unico={student_id}"{bcolors.ENDC}')

        curlOutput = subprocess.run(curlCommand, shell=True, capture_output=True, text=True, encoding="iso-8859-15").stdout
        
        page = BeautifulSoup(curlOutput, 'html.parser')
        nome_div = page.find('div', {'class': 'estudante-info-nome'})
        if nome_div is None: print(f"Error on student ID {bcolors.FAIL}{student_id}{bcolors.ENDC}: {bcolors.DARKGREY}https://sigarra.up.pt/feup/pt/fest_geral.cursos_list?pv_num_unico={student_id}{bcolors.ENDC}"); return ()
        name = nome_div.text.strip()
        for i_curso, curso in enumerate(page.find_all('div', {'class': 'estudante-lista-curso-activo'})):
            try: 
                if str(curso.find('div', {'class': 'estudante-lista-curso-nome'}).find('a')).find(f"pv_curso_id={COURSE_TO_SEARCH}") != -1:
                    year = curso.find('table').findChildren()[0].findChildren()[1].text.strip()
                    if year in YEARS_TO_SEARCH: 
                        if OUTPUT: print(f"Found student {bcolors.OKCYAN}{student_id}{bcolors.ENDC} {bcolors.OKGREEN if year=='1' else bcolors.WARNING if year=='2' else bcolors.FAIL}{year}{bcolors.ENDC} {bcolors.LIGHTGREY}{name}{bcolors.ENDC}")
                        return (student_id, year, name, f"up{student_id}@up.pt")
            except: print(f"Error on student ID {bcolors.FAIL}{student_id}{bcolors.ENDC} on course {bcolors.FAIL}{i_curso}{bcolors.ENDC}: {bcolors.DARKGREY}https://sigarra.up.pt/feup/pt/fest_geral.cursos_list?pv_num_unico={student_id}{bcolors.ENDC}")
        return ()

    if OUTPUT: print(f"Searching for students in Course({bcolors.DARKGREY}{COURSE_TO_SEARCH}{bcolors.ENDC}) in Years({bcolors.DARKGREY}{','.join([x for x in YEARS_TO_SEARCH])}{bcolors.ENDC}) with {bcolors.DARKGREY}{MAX_THREADS}{bcolors.ENDC} threads.")
    studentIds = ()
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor: results = executor.map(search_students,range(1, numberOfPagesToSearch() +1))
    for result in results: studentIds += result
    studentIds = tuple(sorted(studentIds))
    if OUTPUT: print(f"Nº of Student IDs found: {bcolors.OKCYAN}{len(studentIds)}{bcolors.ENDC}")
    time.sleep(3)
    studentData = ()
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor: results = executor.map(filter_student_id, studentIds)
    for result in results: 
        if len(result)>0: studentData += (result,)
    
    print(f"Nº of Students found in Course({bcolors.DARKGREY}{COURSE_TO_SEARCH}{bcolors.ENDC}) in Years({bcolors.DARKGREY}{YEARS_TO_SEARCH}{bcolors.ENDC}): {bcolors.OKCYAN}{len(studentData)}{bcolors.ENDC}")
    return studentData