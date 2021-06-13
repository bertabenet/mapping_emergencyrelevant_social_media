import collector
import persister
import annotator

import multiprocessing as mp
import time
import os


if __name__ == '__main__':
    jobs = []
    
    for i in range(5):
        if i == 0: p = mp.Process(target = collector.collect)
        if i == 1: p = mp.Process(target = persister.persist)
        if i == 2: p = mp.Process(target = annotator.annotate, args = ("hour", ))
        if i == 3: p = mp.Process(target = annotator.annotate, args = ("day", ))
        if i == 4: p = mp.Process(target = annotator.annotate, args = ("week", ))
        
        jobs.append(p)
        p.start()
        
    for job in jobs:
        job.join()
