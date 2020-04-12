import threading, random, multiprocessing, time, queue
from queue import Queue
from timeit import default_timer as timer 
import sys, os
from subprocess import Popen, PIPE
from copy import copy

leng = 10
leng2 = 100

for i in range(0, leng):
    for j in range(i, leng2):
        print(i,j)

