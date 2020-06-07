import threading, random, multiprocessing, time, queue
from queue import Queue
from timeit import default_timer as timer 
import sys, os
from subprocess import Popen, PIPE
from copy import copy

import asyncio

leng = 8
leng2 = 8

async def simple_loop():
    result = []
    for i in range(0, leng):
        for j in range(i, leng2):
            result.append([i,j])
    return result

async def simple_callback(item):
    print("done")
    print(item)

async def main():
    test = asyncio.create_task(simple_loop())
    

#loop = asyncio.get_event_loop()

# task = asyncio.ensure_future(simple_loop())
# task = future_callback(task, simple_callback)
