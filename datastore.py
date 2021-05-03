import numpy as np
import pickle
import os
BOY = 0
GIRL = 1
A_TIME = 0
SCORE = 1
GENDER = 2

class datastore:
    def __init__(self, strategy, parameter, haste, pickiness, rate, max_time, time_store):
        self.strategy = strategy
        self.parameter = parameter
        self.haste = haste
        self.pickiness = pickiness
        self.rate = rate
        self.max_time = max_time
        store_size = int(max_time*rate)
        self.match_time = np.zeros(shape=(store_size,))
        self.boy_arrival = np.zeros(shape=(store_size,))
        self.girl_arrival = np.zeros(shape=(store_size,))
        self.boy_score = np.zeros(shape=(store_size,))
        self.girl_score = np.zeros(shape=(store_size,))
        self.time_step = max_time/time_store
        self.times = np.arange(0, max_time, self.time_step) + self.time_step

        self.num_boys = np.zeros(shape=(time_store,), dtype=np.uint16)
        self.num_girls = np.zeros(shape=(time_store,), dtype=np.uint16)

        self.match_counter = 0
        self.time_tracker = self.time_step
        self.time_counter = 0

        self.left_boys_arrival = np.array([])
        self.left_boys_score = np.array([])
        self.left_girls_arrival = np.array([])
        self.left_girls_score = np.array([])

    def add_match(self, person1, person2, time):
        (boy, girl) = (person1, person2) if person1[GENDER] is BOY else (person2, person1)
        self.match_time[self.match_counter] = time
        self.boy_arrival[self.match_counter] = boy[A_TIME]
        self.girl_arrival[self.match_counter] = girl[A_TIME]
        self.boy_score[self.match_counter] = boy[SCORE]
        self.girl_score[self.match_counter] = girl[SCORE]
        self.match_counter += 1

    def add_time_stat(self, boys, girls, time):
        while self.time_tracker < time:
            self.num_boys[self.time_counter] = boys
            self.num_girls[self.time_counter] = girls
            self.time_counter += 1
            self.time_tracker += self.time_step

    def save_stranglers(self, boy_scores, girl_scores, boy_arrivals, girl_arrivals):
        self.left_boys_score = np.array(boy_scores)
        self.left_girls_score = np.array(girl_scores)
        self.left_boys_arrival = np.array(boy_arrivals)
        self.left_girls_arrival = np.array(girl_arrivals)

    def save_stats(self):
        self.match_time = self.match_time[0:self.match_counter]
        self.boy_arrival = self.boy_arrival[0:self.match_counter]
        self.girl_arrival = self.girl_arrival[0:self.match_counter]
        self.boy_score = self.boy_score[0:self.match_counter]
        self.girl_score = self.girl_score[0:self.match_counter]

        path =f'results/{self.strategy}/picky_{self.pickiness}_haste_{self.haste}'
        try:
            os.mkdir(path)
        except:
            path
        file_name = path + f'/time_{self.max_time}_parameter_{self.parameter}.p'
        pickle.dump(self, open(file_name, "wb"))