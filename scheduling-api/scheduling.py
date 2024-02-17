### I PROMISE I WILL REFACTOR THIS
## THIS IS PURELY FOR TESTING

from itertools import accumulate
from functools import reduce

test = ([3, 4, 5], [0, 0, 3], [7, 4, 12])

def resched(times, releases, deads):
    day = [-1] * 288
    n = len(times)
    conflicts = []

    def block(ts, rs, val):
        for i in range(rs, rs + ts):
            day[i] = val        

    def earliest(ts, rs):
        for i in range(rs, rs + ts):
            if day[i] >= 0:
                return i + times[day[i]]

        return rs

    def choose(ts, rs, ds):
        ers = earliest(ts, rs)

        while rs != ers:
            rs = ers
            ers = earliest(ts, rs)
                
            if ers + ts > ds:
                return -1

        return ers
        

    def find(ind, depth = n, retries = 3):
        #print("----------", ind, depth)
        if ind >= depth:
            return 0
        
        else:
            ts = times[ind]
            rs = releases[ind]
            ds = deads[ind]

            ers = choose(ts, rs, ds)           

            #print(ind, ers)
            
            if ers < 0:
                return -1
            else:
                block(ts, ers, ind)
                
            recur = find(ind + 1, depth)

            if recur == 0:
                return 0

            elif -recur < retries:
                block(ts, ers, -1)
                nrec = find(ind + 1, ind + 1 - recur )
                    
                if nrec:
                    return recur + 1

                else:
                    ers = choose(ts, ers, ds)
                    
                   # print("--", ind, ers)
                    
                    if ers < 0:
                        return -1
                    else:
                        block(ts, ers, ind)
                        
                    recur = find(ind + 1 - recur)
                  
                                                            
            else:
                return recur
            
    res = find(0)
    return res, day


def inplace(day, time, start, end):
    conflicts = []  

    def earliest(ts, rs):
        for i in range(rs, rs + ts):
            if day[i] >= 0:
                conflicts.append(day[i])
                return i + times[day[i]]

        return rs

    def choose(ts, rs, ds):
        ers = earliest(ts, rs)

        while rs != ers:
            rs = ers
            ers = earliest(ts, rs)
                
            if ers + ts > ds:
                return -1, outs

        return ers

    return choose(time, start, end), conflicts


## INCOMPLETE
def addnewevent(day, time, start, end, ind):
    def block(ts, rs, val):
        for i in range(rs, rs + ts):
            day[i] = val     

    ers, confs = inplace(day, time, start, end)

    if ers >= 0:
        block(time, ers, ind)
        return 0, day

    else:
        return resched(params)
        
    
        

