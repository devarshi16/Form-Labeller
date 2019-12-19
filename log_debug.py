from config import LOGGING,DEBUGGING,LOG_FILE
from time import time,ctime

def logger(in_log):
    if LOGGING:
        curr_time = ctime(time())
        with open(LOG_FILE,'a') as f:
            f.write(curr_time+' '+in_log+'\n')

def debug(in_debug):
    if DEBUGGING:
        print("DEBUG: "+in_debug+"\n")
    
