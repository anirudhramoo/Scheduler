import requests, os, json

import datetime as dt
from datetime import datetime, timedelta
from dotenv import load_dotenv, find_dotenv
import os
load_dotenv(find_dotenv())

class gcal_tool():
    def refresh(self, refresh_token):
        data = {
            'refresh_token': refresh_token,
            'client_id': os.environ["GOOGLE_CLIENT_ID"], 
            'client_secret': os.environ["GOOGLE_SECRET_KEY"], 
            'grant_type': 'refresh_token'
        }

        response = requests.post('https://oauth2.googleapis.com/token', data=data).json()
        self.access_token = response["access_token"]
       

        self.primary = [i for i in self.calendars() if 'mich' in i][0]
        cmeta = self.grequest("fhttps://www.googleapis.com/calendar/v3/calendars/{self.primary}")
        print(cmeta["timeZone"])

        self.tz = cmeta["timeZone"]

    def grequest(self, url, params = {}, data={}, type=requests.get):
        print("Acccess token")
        print(self.access_token)
        headers = {'Authorization': f'Bearer {self.access_token}'}
        return type(url, params=params, data=data, headers=headers).json()
    
    def calendars(self):
        cal_list = self.grequest("https://www.googleapis.com/calendar/v3/users/me/calendarList")
        print(cal_list)
        raws = [i['id'] for i in cal_list["items"]]
        print(raws)
        return raws
    
    def get_events(self, calid, mindate, maxdate):
        p = {"timeMin": mindate,
             "timeMax": maxdate}
        print(p)
        
        cal = self.grequest(
            f"https://www.googleapis.com/calendar/v3/calendars/{calid}/events", 
            params=p
        )

        return cal["items"]

    def __init__(self, access_token, cals = "mich"):
        self.access_token = access_token
        self.tz = 'America/New_York'

        self.cals = cals

    def getnextweek(self, calid, days=7):
        lower = datetime.now(dt.timezone.utc).replace(hour=0, minute=0, second=0,microsecond=0)

        upper = lower + timedelta(days=days)

        print(lower, upper)


        events = self.get_events(calid, 
                                 lower.replace(microsecond=0).isoformat(), 
                                 upper.replace(microsecond=0).isoformat())
        
        return events
    
    def totuple(self, event):
        if event.get("recurrence"):
            print(event.get("recurrence"))

        return (event["start"]["dateTime"], event["end"]["dateTime"],
                event.get("description") if event.get("description") else "",
                event["summary"], event["id"])
    
    def addevent(self, calid, start, end, desc, name, ii):
        p = {"end": {
                "dateTime": end,
                # "timeZone": self.tz                 
             },
             "start": {
                "dateTime": start,
                # "timeZone": self.tz
             },
             "description": desc,
             "summary": name}
        print(p)
        
        cal = self.grequest(
            f"https://www.googleapis.com/calendar/v3/calendars/{calid}/events", 
            data=json.dumps(p),
            type=requests.post
        )

        return cal
    
    def pushchange(self, args):
        return self.addevent(self.primary, *args)
       
    def patch_event(self, calid, start, end, desc, name, ii):
        headers = {'Authorization': f'Bearer {self.access_token}'}

        curr_url = f'https://www.googleapis.com/calendar/v3/calendars/{calid}/events/{ii}'

        curr = self.grequest(curr_url)
        curr["end"] = {"dateTime": end}
        curr["start"] = {"dateTime": start}
        curr["description"] = desc
        curr["summary"] = name

        return(requests.put(curr_url, headers=headers, data=json.dumps(curr)))
    
    def patchchange(self, args):
        return self.patch_event(self.primary, *args)
    
    def deleteevent(self, eventid):
        calid = self.primary
        headers = {'Authorization': f'Bearer {self.access_token}'}

        cal = requests.delete(
            f"https://www.googleapis.com/calendar/v3/calendars/{calid}/events/{eventid}",
            headers=headers)

        return cal

    def getevs(self, days = 8):
        lower = datetime.now(dt.timezone.utc).replace(hour=0, minute=0, second=0,microsecond=0)

        upper = lower + timedelta(days=days)
        
        return [self.totuple(i) for i in self.getnextweek(self.primary)]

    def runn(self):
        primary = [i for i in self.calendars() if self.cals in i][0]
        # print(primary)
        print([self.totuple(i) for i in self.getnextweek(primary)])
        # print(self.addevent(primary, "2024-02-19T11:00:00", "2024-02-19T11:30:00", "testing this will be deleted", "Heather wants to connect on Linkedin"))

        # print(self.deleteevent(primary,"6ikjlr9f3p6f1gm3g25dk16d5k"))
        # print(self.deleteevent(primary,"s6adcvdlcbh0do8rfp71hotqf0"))



        
    # 6ikjlr9f3p6f1gm3g25dk16d5k
    # s6adcvdlcbh0do8rfp71hotqf0


if __name__ == "__main__":
    access_token = "ya29.a0AfB_byAa-5XiF96eU8E9HweTJ2Ovqf4vKStLESJtbyrwjPtfmA-dKRqSUgrf0v_-XhkU0Sl3rAEOLcqq1n0S0QWDYtAqfWL89LvF0tnNgckREo3Qe3YAWpcVhqfX_wpBY2WRfvFEhbqwe8GM38gulaBMrN7TcB2yABfMjQaCgYKAU8SARMSFQHGX2MiQu6qaG6E-KhejZZ45dWgHA0173"
    test = gcal_tool(access_token)
    test.refresh("1//06WJTC4rzOVYyCgYIARAAGAYSNwF-L9Irt4Ebx3BK7nXgr27n6Wt1s4hzqxly72p7Y_xdSIsc1-v_L9Cksu2azZyNTJ033OCzH_E")

    print(test.getevs())
    print(test.patchchange(("2024-02-19T15:34:50-08:00", "2024-02-19T16:34:50-08:00", "new desc", "updatednev", '4epkp0o9mlf6ij5b6kvlsn5lo4')))


    # print(test.calendars())