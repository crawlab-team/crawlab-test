import requests
from crawlab import save_item
import time
from random import randint
import json
import sys

for i in range(30):
  row = {}
  for j in range(10):
    row[f'field_{j+1}'] = randint(0, 100)
  save_item(row)
  print(f'saved {json.dumps(row)}')
  sys.stdout.flush()
  time.sleep(0.05)
