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
        print("READING READING")
        
        for ids, (start, time, rs, ds, _, _) in events.items():
            # if start >= 0 and time >= 0 and rs >= 0 and ds >= 0:

            while start < 0:
                start += self.units
                rs += self.units
                ds += self.units

            
            if self.day[start] == -1:
                self.present.add(ids)
                self.events.append((time, rs, ds, ids))
                
                for x in range(start, start + time):
                    self.day[x] = ids

        self.n = len(events)

    def block(self, ts, rs, val, inday = False):
        day = inday if inday else self.day
        
        for i in range(rs, rs + ts):
            day[i] = val

    def earliest(self, ts, rs, inday = False):
        day = inday if inday else self.day
        for i in range(rs, rs + ts):
            if day[i] >= 0:
                ids = day[i]
                while day[i] == ids:
                    i += 1

                return i, ids

        return rs, -1

    def choose(self, ts, rs, ds, inday = False):
        day = inday if inday else self.day
        confs = []
        ers, c = self.earliest(ts, rs, day)


        while c >= 0:
            confs.append(c)
            ers, c = self.earliest(ts, ers, day)
                
            if ers + ts > ds:
                return -1, confs

        return ers, confs
    
    def __init__(self, events, units = 288):
        self.units = units
        self.day = [-1] * self.units
        self.present = set()
        
        self.n = 0
        self.events = []
        
        self.read(events)

    def addevent(self, event):
        ts, rs, ds = event
        neven = (ts, rs, ds, self.n)

        ers, conf = self.choose(ts, rs, ds)
        print(conf)

        if ers >= 0:
            self.block(ts, ers, self.n)
            self.events.append(neven)
            self.present.add(self.n)
            
            self.n += 1
            return self.n - 1, conf, False

        else:
            res, nd = self.resched(self.events + [neven])
            print("rescheding")
            
            if res >= 0:
                self.day = nd
                self.events.append(neven)
                self.present.add(self.n)
                self.n += 1
            
            return res, conf, True

    def resched(self, events):
        newday = [-1] * self.units
        events.sort(key = itemgetter(2))
        n = len(events)

        print(events)


        def find(ind, depth = n, retries = 3):
            if ind >= depth:
                return 0


            ts, rs, ds, ids = events[ind]
            print(ind, ids)
            #print("----", ind, depth, ids)
            #print(newday)
            
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

        if res >= 0:
            res = self.n

        return res, newday

    def whattime(self, ind):
        return self.day.index(ind)

if __name__ == "__main__":
    events = {0:(4, 7, 4, 50, 0, 0), 1:(11, 5, 11, 16, 0, 0)}
    event = (5, 4, 20)

    testing = timedperiod(events)
    #print(testing.day)

    res, confs, x = testing.addevent(event)
    print(testing.day)
