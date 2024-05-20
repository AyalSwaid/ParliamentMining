p = r"C:\Users\ayals\OneDrive\שולחן העבודה\parliamentMining\Data\speeches\IL\1152024-03-03 05-10-33.json"
p = r"C:\Users\ayals\OneDrive\שולחן העבודה\parliamentMining\Data\speeches\IL\1202024-03-03 05-10-33.json"
p = r"C:\Users\ayals\OneDrive\שולחן העבודה\parliamentMining\Data\speeches\IL\12024-03-04 04-02-03.json"
import json

with open(p) as f:

  data = json.load(f)

  print(data.keys())