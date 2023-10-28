def addPhoneNumbers(phoneData:list[list[str]], csvFile:str) -> list[list[str]]:
    from src.bcolors import bcolors

    def getCsvData(filename:str) -> list[list[str]]:
        """
        Reads a CSV file and returns the email, name and phone number.

        Args:
            filename (str): The path to the CSV file.

        Returns:
            tuple: A tuple of data represented as a tuple of three strings:
                (email, name, phone_number).
        """
        import csv
        data:list[list[str]] = []
        with open(filename, 'r', encoding="cp1252") as csvFile:
            csvReader = csv.reader(csvFile)
            for line in csvReader:
                data.append([line[3].strip(), line[6].strip()])
            data.pop(0)
        for i in range(len(data)):
            data[i][1] = data[i][1].replace(" ", "").replace("+351", "").replace("351", "")
        return data

    studentList = list(list(sub) for sub in phoneData)
    phoneData = getCsvData(csvFile)
    for i in range(len(studentList)):
        matCH = []
        for j in range(len(phoneData)):
            if studentList[i][3] == phoneData[j][0]:
                if len(matCH) and not studentList[i][-1] == phoneData[j][1]: print(f"{bcolors.FAIL}ERROR DOUBLE MATCH{bcolors.ENDC}: student number - {studentList[i][0]}")
                else: studentList[i].append(phoneData[j][1])
                matCH.append(j)
        if not len(matCH): studentList[i].append("")
        for j in list(reversed(sorted(matCH))):
            del phoneData[j]

    for i in range(len(phoneData)): print(f"{bcolors.FAIL}ERROR{bcolors.ENDC} no email match for: {phoneData[i]}")
    return studentList