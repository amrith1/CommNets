# import numpy as np
import numpy.random as rand
from bisect import bisect_left
from datastore import datastore
import argparse


# HASTE = 5
# PICKY = 20
# RATE = 100
# MAX_TIME = 10000.0
# THRESHOLD = 0.05

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--haste', help='', default=None, type=float)
parser.add_argument('--pickiness', help='', default=None, type=float)
parser.add_argument('--rate', help='', default=None, type=float)
parser.add_argument('--max_time', help='', default=None, type=float)
parser.add_argument('--parameter', help='', default=None, type=float)
args = parser.parse_args()

HASTE = args.haste
PICKY = args.pickiness
RATE = args.rate
MAX_TIME = args.max_time
THRESHOLD = args.parameter

# constant
BOY = 0
GIRL = 1
A_TIME = 0
SCORE = 1
GENDER = 2

asd;kaSDK

data = datastore("threshold", THRESHOLD, HASTE, PICKY, RATE, MAX_TIME, time_store=1000)

def arrival_generator():
    last_arrival_time = 0
    while True:
        last_arrival_time = last_arrival_time + rand.exponential(scale=1 / RATE)
        yield last_arrival_time, rand.uniform(), rand.randint(2)  # Atime, Score, Gender


arrival = arrival_generator()

boys = []
girls = []
boys_scores = []
girls_scores = []

current_time = 0
while current_time < MAX_TIME:
    print(current_time, end="\r")
    candidate = next(arrival)
    current_time = candidate[A_TIME]
    if current_time < MAX_TIME:
        data.add_time_stat(len(boys_scores), len(girls_scores), current_time)

    matches = boys if candidate[GENDER] is GIRL else girls
    match_scores = boys_scores if candidate[GENDER] is GIRL else girls_scores
    competitors = boys if candidate[GENDER] is BOY else girls
    competitor_scores = boys_scores if candidate[GENDER] is BOY else girls_scores
    match_index = bisect_left(match_scores, candidate[SCORE])

    def closeness(m_index):
        return abs(candidate[SCORE] - match_scores[m_index])

    def queue_candidate():
        insert_loc = bisect_left(competitor_scores, candidate[SCORE])
        competitors.insert(insert_loc, candidate)
        competitor_scores.insert(insert_loc, candidate[SCORE])

    if len(matches) > 0:
        if 0 < match_index < len(matches):
            match_index = (match_index - 1) if closeness(match_index - 1) < closeness(match_index) else match_index
        match_index = match_index - 1 if match_index == len(matches) else match_index
        if closeness(match_index) < THRESHOLD:
            match = matches.pop(match_index)
            match_scores.pop(match_index)
            data.add_match(candidate, match, current_time)
        else:
            queue_candidate()
    else:
        queue_candidate()
print("Saving")
data.save_stats()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
