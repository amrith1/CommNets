import numpy as np
import numpy.random as rand
from bisect import bisect_left
from datastore import datastore
import argparse


def main():
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

    data = datastore("time_threshold", THRESHOLD, HASTE, PICKY, RATE, MAX_TIME, time_store=1000)

    def arrival_generator():
        last_arrival_time = 0
        while True:
            last_arrival_time = last_arrival_time + rand.exponential(scale=1 / RATE)
            yield last_arrival_time, rand.uniform(), rand.randint(2)  # Atime, Score, Gender

    arrival = arrival_generator()
    boys_scores = []
    girls_scores = []
    boys_atime = []
    girls_atime = []

    current_time = 0
    while current_time < MAX_TIME:
        #print(current_time, end="\r")
        candidate = next(arrival)
        current_time = candidate[A_TIME]
        if current_time < MAX_TIME:
            data.add_time_stat(len(boys_scores), len(girls_scores), current_time)

        match_atime = boys_atime if candidate[GENDER] is GIRL else girls_atime
        match_scores = boys_scores if candidate[GENDER] is GIRL else girls_scores
        competitors_atime = boys_atime if candidate[GENDER] is BOY else girls_atime
        competitor_scores = boys_scores if candidate[GENDER] is BOY else girls_scores

        low_index = bisect_left(match_scores, candidate[SCORE] - THRESHOLD)
        high_index = bisect_left(match_scores, candidate[SCORE] + THRESHOLD)

        def queue_candidate():
            insert_loc = bisect_left(competitor_scores, candidate[SCORE])
            competitors_atime.insert(insert_loc, candidate[A_TIME])
            competitor_scores.insert(insert_loc, candidate[SCORE])

        if high_index - low_index > 0 and high_index != 0:
            potential_match_atime = np.array(match_atime[low_index:high_index])
            match_index = low_index + np.argmax(potential_match_atime)
            match = (match_atime.pop(match_index), match_scores.pop(match_index), 1 ^ candidate[GENDER])
            data.add_match(candidate, match, current_time)
        else:
            queue_candidate()
    print("Saving")
    data.save_stranglers(boys_scores, girls_scores, boys_atime, girls_atime)
    data.save_stats()


if __name__ == '__main__':
    main()
