import requests, os, json

import datetime as dt
from datetime import datetime, timedelta

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
        print(self.access_token)

    def grequest(self, url, params = {}, data={}, type=requests.get):
        headers = {'Authorization': f'Bearer {self.access_token}'}
        return type(url, params=params, data=data, headers=headers).json()
    
    def calendars(self):
        cal_list = self.grequest("https://www.googleapis.com/calendar/v3/users/me/calendarList")
        return [i['id'] for i in cal_list["items"]]
    
    def get_events(self, calid, mindate, maxdate):
        p = {"timeMin": mindate,
             "timeMax": maxdate}
        # print(p)
        
        cal = self.grequest(
            f"https://www.googleapis.com/calendar/v3/calendars/{calid}/events", 
            params=p
        )

        return cal["items"]

    def __init__(self, access_token):
        self.access_token = access_token
        self.tz = 'America/New_York'

    def getnextweek(self, calid, days=7):
        lower = datetime.now(dt.timezone.utc)
        upper = lower + timedelta(days=days)


        events = self.get_events(calid, 
                                 lower.replace(microsecond=0).isoformat(), 
                                 upper.replace(microsecond=0).isoformat())
        
        return events
    
    def totuple(self, event):
        return (event["start"], event["end"], 
                event.get("description") if event.get("description") else "",
                event["summary"])
    
    def addevent(self, calid, start, end, desc, name):
        p = {"end": {
                "dateTime": end,
                "timeZone": self.tz                 
             },
             "start": {
                "dateTime": start,
                "timeZone": self.tz
             },
             "description": desc,
             "summary": name}
        # print(p)
        
        cal = self.grequest(
            f"https://www.googleapis.com/calendar/v3/calendars/{calid}/events", 
            data=json.dumps(p),
            type=requests.post
        )

        return cal
    
    def deleteevent(self, calid, eventid):
        headers = {'Authorization': f'Bearer {self.access_token}'}

        cal = requests.delete(
            f"https://www.googleapis.com/calendar/v3/calendars/{calid}/events/{eventid}",
            headers=headers)

        return cal


    def runn(self):
        primary = [i for i in self.calendars() if 'mich' in i][0]
        # print(primary)
        print([self.totuple(i) for i in self.getnextweek(primary)])
        # print(self.addevent(primary, "2024-02-19T11:00:00", "2024-02-19T11:30:00", "testing this will be deleted", "Heather wants to connect on Linkedin"))

        # print(self.deleteevent(primary,"6ikjlr9f3p6f1gm3g25dk16d5k"))
        # print(self.deleteevent(primary,"s6adcvdlcbh0do8rfp71hotqf0"))



        
    # 6ikjlr9f3p6f1gm3g25dk16d5k
    # s6adcvdlcbh0do8rfp71hotqf0


if __name__ == "__main__":
    access_token = "ya29.a0AfB_byAqBgLdo8cwydIUYij81w2IUuQQ23h_xE02n1INkeK65VDBDErpAmoaQpwZl_vaSQOwMQpxaMlBy60d5-igplqc804QR-5R0wCzZey7yMHNSAV_4uT5VrUIa6ObpzV0Iya-TLabZqqkDjPebdGTgQi-Bha3vZ3oaCgYKAWQSARMSFQHGX2Mi7r9ae0NA8o7rYX5Qo8W0zg0171"
    test = gcal_tool(access_token)
    # test.refresh("1//06WJTC4rzOVYyCgYIARAAGAYSNwF-L9Irt4Ebx3BK7nXgr27n6Wt1s4hzqxly72p7Y_xdSIsc1-v_L9Cksu2azZyNTJ033OCzH_E")

    test.runn()


    # print(test.calendars())