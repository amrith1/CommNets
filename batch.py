import argparse

import numpy.random as rand

from datastore import datastore

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
BATCH_TIME = args.parameter

# constant
BOY = 0
GIRL = 1
A_TIME = 0
SCORE = 1
GENDER = 2

data = datastore("batch", BATCH_TIME, HASTE, PICKY, RATE, MAX_TIME, time_store=int(MAX_TIME / BATCH_TIME))

boys = []
girls = []
dump = []
dump_gender = BOY


def arrival_generator():
    last_arrival_time = 0
    while True:
        last_arrival_time = last_arrival_time + rand.exponential(scale=1 / RATE)
        yield last_arrival_time, rand.uniform(), rand.randint(2)  # Atime, Score, Gender


arrival = arrival_generator()
next_batch_time = BATCH_TIME
current_time = 0


def get_score(x):
    return x[SCORE]


def get_atime(x):
    return x[A_TIME]


def opp_gender(x):
    return x ^ 1


# Equalize the boy girl arrays, load or save to dump as neccessary
def manage_dump(high_gender_list, low_gender_list, low_gender_int):
    global dump_gender, dump
    if dump_gender is low_gender_int and len(dump) > 0:
        num_retrieve = min(len(dump), len(high_gender_list) - len(low_gender_list))
        for x in range(num_retrieve):
            low_gender_list.append(dump.pop())
    num_dispose = len(high_gender_list) - len(low_gender_list)
    if num_dispose > 0:
        high_gender_list.sort(key=get_atime)
        for_the_dump = [high_gender_list.pop() for blah in range(num_dispose)]
        for_the_dump.reverse()
        dump_gender = opp_gender(low_gender_int)
        for person in for_the_dump:
            dump.append(person)


while current_time < MAX_TIME:
    #print(current_time, end="\r")
    candidate = next(arrival)
    current_time = candidate[A_TIME]
    if current_time < MAX_TIME:
        if dump_gender is BOY:
            data.add_time_stat(len(boys) + len(dump), len(girls), current_time)
        else:
            data.add_time_stat(len(boys), len(girls) + len(dump), current_time)

    if current_time > next_batch_time:
        # BATCH PROCESS
        if len(boys) > len(girls):
            manage_dump(high_gender_list=boys, low_gender_list=girls, low_gender_int=GIRL)
        else:
            manage_dump(high_gender_list=girls, low_gender_list=boys, low_gender_int=BOY)
        boys.sort(key=get_score)
        girls.sort(key=get_score)
        while len(boys) > 0:  # Pop the matches while they exist
            data.add_match(boys.pop(), girls.pop(), next_batch_time)

        next_batch_time += BATCH_TIME
    boys.append(candidate) if candidate[GENDER] is BOY else girls.append(candidate)

boy_scores = []
girl_scores = []
boy_atimes = []
girl_atimes = []
dump_scores = [entry[SCORE] for entry in dump]
dump_atimes = [entry[A_TIME] for entry in dump]
if dump_gender is BOY:
    boy_scores, boy_atimes = dump_scores, dump_atimes
else:
    girl_scores, girl_atimes = dump_scores, dump_atimes

data.save_stranglers(boy_scores, girl_scores, boy_atimes, girl_atimes)
print("Saving")
data.save_stats()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
