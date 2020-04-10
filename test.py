import threading, random, multiprocessing, time, queue
from queue import Queue
from timeit import default_timer as timer 
import sys, os
from subprocess import Popen, PIPE
from copy import copy

length = 78897
for i in range(1, 5):
    print(int((length)*i/4)-int((length/4)))
    print(str( int((length)*i/4) ))

test = "del"
st = copy(test)
print(test)
# def Splitter(words, iter):
#     start = timer()
#     fileOut = os.path.join(os.path.dirname(os.path.realpath(__file__)), "engine", "f.txt") 
#     fileOut2 = os.path.join(os.path.dirname(os.path.realpath(__file__)), "engine", "f2.txt") 
#     enginePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "engine", "_score.exe")
#     print("Starting Thread  : "+words)
#     for iter in range(20000):        
#         # exceuting command
#         p = Popen([enginePath, fileOut, fileOut2], stdin=PIPE, stdout=PIPE, stderr=PIPE)
#         score = p.communicate()[0]
#         p.stdout.close()
#     elapsed = timer()-start
#     print (words+" exiting ... elapsed time "+str(elapsed)+" ms")

# def subThread(words):
#     start = timer()
#     numThreads = 4
#     threadList = []
#     queueThread = Queue()
#     for i in range(0,numThreads):
#         t = threading.Thread(
#             target=Splitter,
#             args=("this is thread "+str(i), iter)
#         )
#         threadList.append(t)
#     for t in threadList:    
#         t.start()
#         print("active thread : " + str(threading.activeCount()))
#     for t in threadList:
#         t.join()
#     elapsed = str(timer()-start)+" ms"
#     print("elapsed  "+ elapsed)

# if __name__ == "__main__":
#     start = timer()
#     t = threading.Thread(
#             target=subThread,
#             args=("this is thread sub thread",)
#         )
#     elapsed = str(timer()-start)+" ms"
#     print("elapsed  "+ elapsed)
#     start = timer()
#     subThread("subThread")
#     elapsed = str(timer()-start)+" ms"
#     print("elapsed  "+ elapsed)