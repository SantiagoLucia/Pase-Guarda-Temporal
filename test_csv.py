import csv
from pathlib import Path

FILE_PATH = Path('data.csv')

with FILE_PATH.open(mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        print(row['numero_expediente'])
        
