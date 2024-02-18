from operator import itemgetter

### Scheduling Logic-Algorithm
# init() - pass in a list of 5-TUPLES of scheduled events (start time, duration, release time, deadline, id), id < len(events)
#      - It assumes the existing schedule is VALID, this is not CHECKED, and will cause ERRORS if not

# addevent() - pass in a 3-TUPLE - of (duration, release time, deadline)
#              - returns a 2-TUPLE of (id, conflicts)
#              - id >= 0 -> it was a success and the new event has this id, no further action needed
#              - id < 0 -> it failed, conflicts is a list of events that conflict by their id (i.e. [2, 5, 6] means events 2, 5, 6 conflict with it)


class timedperiod():
    def read(self, events):
        
        for _, (start, time, rs, ds, ids) in enumerate(events):
            self.events.append(time, rs, ds, ids)
            
            for x in range(start, start + time):
                self.day[x] = ids

        self.n = len(events)

    def block(self, ts, rs, val, inday = False):
        day = inday if inday else self.day
        
        for i in range(rs, rs + ts):
            self.day[i] = val

    def earliest(self, ts, rs, inday = False):
        day = inday if inday else self.day
        for i in range(rs, rs + ts):
            if day[i] >= 0:
                return i + times[day[i]], day[i]

        return rs, -1

    def choose(self, ts, rs, ds, inday = False):
        day = inday if inday else self.day
        confs = []
        ers, c = self.earliest(ts, rs)

        while c >= 0:
            ers, c = self.earliest(ts, ers, day)
                
            if ers + ts > ds:
                return -1, confs

        return ers, confs
    
    def __init__(self, events = False, units = 288):
        self.units = units
        
        self.n = 0
        self.events = []
        self.day = [-1] * self.units
        
        if events:
            self.read(events)

    def addevent(self, event):
        ts, rs, ds = event

        ers, conf = self.choose(ts, rs, ds)

        if ers >= 0:
            self.block(ts, ers, self.n)
            self.events.append((ts, rs, ds, self.n))
            
            self.n += 1
            return self.n - 1, conf

        else:
            res, nd = self.resched(self.events + [event])
            
            if res >= 0:
                self.day = nd
                self.events.append((ts, rs, ds, self.n))
                self.n += 1
            
            return res, conf

    def resched(self, events):
        newday = [-1] * self.units
        events.sort(key = itemgetter(2))
        n = len(events)


        def find(ind, depth = n, retries = 3):
            if ind >= depth:
                return 0

            ts, rs, ds, ids = events[ind]
            ers, _ = self.choose(ts, rs, ds, newday)

            if ers < 0:
                return -1

            self.block(ts, ers, ids, newday)
            
            recur = find(ind + 1, depth)

            if recur == 0:
                return 0

            elif -recur < retries:
                self.block(ts, ers, -1, newday)
                nrec = find(ind + 1, ind + 1 - recur )
                    
                if nrec != 0:
                    return recur - 1

                ers, _ = self.choose(ts, rs, ds, newday)
                
                if ers < 0:
                    return -retries

                else:
                    self.block(ts, ers, ids, newday)
                    recur = find(ind + 1 - recur)


            return recur

        res = find(0)

        return res, newday


events = []
event = (5, 7, 20)

testing = timedperiod(events)
res, confs = testing.addevent(event)
