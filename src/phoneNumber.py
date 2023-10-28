def getMatches(data:tuple, csvFile:str) -> tuple:
    def getCsvData(filename:str) -> tuple:
        """
        Reads a CSV file and returns the email, name and phone number.

        Args:
            filename (str): The path to the CSV file.

        Returns:
            tuple: A tuple of data represented as a tuple of three strings:
                (email, name, phone_number).
        """
        import csv
        data = []
        with open(filename, 'r', encoding="cp1252") as csvFile:
            csvReader = csv.reader(csvFile)
            for line in csvReader:
                data += [[line[3].strip(), line[4].strip(), line[6].strip()]]
            data.pop(0)
        for i in range(len(data)):
            data[i][2] = data[i][2].replace(" ", "").replace("+351", "")
        return tuple(tuple(sub) for sub in data)

    return (0,)