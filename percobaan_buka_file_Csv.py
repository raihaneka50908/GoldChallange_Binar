import csv
with open("Asset Challenge/data.csv",'r') as f:
    ff=csv.reader(f)
    for row in ff:
        print(row)
