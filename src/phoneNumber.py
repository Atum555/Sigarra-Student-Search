import csv
import sys

def getcsvdata(filename:str):
    data = []
    with open(filename, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        for line in csv_reader:
            data += [[line[3].strip(), line[4].strip(), line[6].strip()]]
        data.pop(0)
    for i in range(len(data)):
        data[i][2] = data[i][2].replace(" ", "").replace("+351", "")

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 script.py <filename>")
        sys.exit(1)
    getcsvdata(sys.argv[1])       


if __name__ == "__main__":
    main()
    