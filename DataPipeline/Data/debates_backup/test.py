import os
import pandas as pd

sums = 0

def open_all_files(f_path):
    f_path = r"C:\Users\ayals\OneDrive\שולחן העבודה\parliamentMining\Data\speeches\UK" + "\\" + f_path.split('/')[-1]
    # print(f_path)
    try:
        open(f_path)
        True
    except FileNotFoundError:
        # print(2)
        return False
    

for i in os.listdir("."):
    if i.endswith(".csv"):
        df = pd.read_csv(i)
        false_sum = (df['file_path'].apply(open_all_files) == False).sum()
        if (false_sum) > 0:
            print(i, false_sum, len(df))
            sums +=1 
        # sums += len(df)


print(sums)