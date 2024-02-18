import re
import datetime as dt

import pytz

from math import ceil

from utils.schedule import timedperiod as tp
from utils.calendarapi import gcal_tool as gct

# Define the Eastern Time Zone
eastern = pytz.timezone('US/Eastern')
# Convert to Eastern Time

def in_est(uttime):
    return uttime.astimezone(eastern)


class scheduler():
    def ttm(self, day, hr, mn):
        return (day*288) + (hr * 12) + (mn//5)

    def mtt(self, t):
        x = t%288
        return ((t//288), (x//12), (x%12) * 5)
    
    def parseevent(self, event):
        start, end, desc, name, ids = event

        cst = dt.datetime.fromisoformat(start)
        print("-----------", start)
        # print(cst, self.rn)
        cet = dt.datetime.fromisoformat(end)

        diff = (cst - self.rn)

        start = (diff.days*288) + diff.seconds//(300)
        duration = ceil((cet - cst).seconds/(300))


        lb, ub = self.parsedesc(desc)

        if not (lb or ub):
            lb, ub = start, start + duration

        return (start, duration, lb, ub, name, ids)
    
    def hmtom(self, val):
        h, m = val.split(':')
        return self.ttm(0, int(h), int(m))
    
    def parsenewevent(self, event):
        dur, rs, ds, days, name  = event

        return self.hmtom(dur), self.hmtom(rs), self.hmtom(ds), days, name

    
    def parsedesc(self, desc):
        ms = re.search("Heather's-Interval-is:([01]\d|2[0-3]):?([0-5]\d)-([01]\d|2[0-3]):?([0-5]\d)on-days-(\d+)", desc)

        if ms:
            return (self.ttm(int(ms.group(0)), int(ms.group(1))), self.ttm(int(ms.group(2)), int(ms.group(3))))
        
        else:
            return 0, 0

    def __init__(self, events, rtok):
        self.rn = dt.datetime.now(dt.timezone.utc).replace(hour=0, minute=0, second=0,microsecond=0)

        self.calapi = gct("")
        self.calapi.refresh(rtok)
        self.cal = self.calapi.getevs() # events

        print("THECALIS:", self.cal)

        self.ids = {i: self.parseevent(x) for i, x in enumerate(self.cal)}

        print(self.ids)

        self.sched = tp(self.ids, units=7*288)

    def torelutc(self, val):
        d, h, m = self.mtt(val)
        td = dt.timedelta(days=d, hours=h, minutes=m)
        return (self.rn + td).isoformat()

    def speak(self, ids):
        st, du, lb, ub, name, ii = self.ids[ids]

        d, h, m = self.mtt(du)
        d, h1, m1 = self.mtt(lb)
        d, h2, m2 = self.mtt(ub)

        return (self.torelutc(st), str(h) + ':' + str(m),
                str(h1) + ':' + str(m1), str(h2) + ':' + str(m2), name, ids)
    
    def togcal(self, ids):
        st, du, lb, ub, name, ii = self.ids[ids]

        d, h, m = self.mtt(du)
        d, h1, m1 = self.mtt(lb)
        d, h2, m2 = self.mtt(ub)

        ndes = str(h1) + ':' + str(m1) + '-' + str(h2) + ':' + str(m2)

        return (self.torelutc(st), self.torelutc(st + du),
                ndes, name, ii)
    
    def writetocal(self, ids):
        outs = []

        for i in ids:
            nst, net, ndes, name, ii = self.togcal(i)

            if i < len(self.cal):
                ndes = self.cal[i][2] + ndes

            outs.append((i, (nst, net, ndes, name, ii)))

        for i, x in outs:
            if x[-1] == 0:
                resp = self.calapi.pushchange(x)
                a, b, c, d, e, _ = self.ids[i]
                self.ids[i] = a, b, c, d, e, resp["id"]
                print(self.ids[i])
                print(resp)
            else:
                print(self.calapi.patchchange(x))


        return outs
    
    def giveallevents(self):
        return [(x[1][-2], x[0]) for x in self.ids.items()]

    def checkev(self, ids):
        return self.speak(ids)

    def remevent(self, ids):
        print(self.ids[ids])
        _, dur, _, _, _, ii = self.ids[ids]
        self.sched.delevent(ids, dur)

        self.ids.pop(ids)

        if ii != 0:
            self.calapi.deleteevent(ii)

    def addevent(self, event):
        dur, rs, ds, day, oname = self.parsenewevent(event)
        # print("OGNAME", name)
        tcon = []

        for day in day:
            diff = int(day) * 288

            res, confs, total = self.sched.addevent( (dur, diff + rs, diff + ds) )
            print(confs)

            if res >= 0:
                nstrt = self.sched.whattime(res)

                if total:
                    print("rescheded")
                    # print(self.sched.day)
                    for ids, (_, ndur, nrs, nds, nname, neid) in self.ids.items():
                        if ids in self.sched.present:
                            self.ids[ids] = (self.sched.whattime(ids), ndur, nrs, nds, nname, neid) 
                            self.writetocal([ids])

                
                self.ids[res] = (nstrt, dur, rs, ds, oname, 0)
                # print("THIS IS RES", res, oname)
                self.writetocal([res])

                print(event)
                return True, [self.speak(res)]

            else:
                tcon.extend(confs)
        
        return False, [self.speak(i) for i in tcon]
    

if __name__ == "__main__":
    tdata = [("2024-02-21T11:00:00", "2024-02-21T11:30:00", "", "test", 0)]

    #THIS IS THE FORMAT FOR EVENTS
    newev = [("2:00", "13:00", "18:00", "0", "newev"),
             ("1:00", "13:00", "14:00", "0", "newev2"),
             ("2:00", "13:00", "15:00", "0", "newev3")]
    
    ## INITIALIZE THE SCHEDULER LIKE THIS
    # THIS IS RAMUS REFRESH TOKEN
    rtok = "1//06WJTC4rzOVYyCgYIARAAGAYSNwF-L9Irt4Ebx3BK7nXgr27n6Wt1s4hzqxly72p7Y_xdSIsc1-v_L9Cksu2azZyNTJ033OCzH_E"
    damn = scheduler([], rtok)
    print(damn.ids, damn.sched.present)

    print("----------------")

    # THIS IS HOW YOU ADD AN EVENT
    # print(damn.addevent(newev[0]))
    # print(damn.ids)
    # print(damn.addevent(newev[1]))
    # print(damn.addevent(newev[2]))
    # print(damn.ids)

    # print(damn.writetocal([14, 15, 16, 17]))

    # print(damn.sched.day)
            
        
    
