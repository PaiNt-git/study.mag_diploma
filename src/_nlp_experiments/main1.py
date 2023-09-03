from corus import load_russe_rt
from pprint import pprint
import random

path = 'datasets/raw.githubusercontent.com_nlpub_russe-evaluation_master_russe_evaluation_rt.csv'
records = load_russe_rt(path)

for record in random.sample(list(records), 200):
    pprint(record)
