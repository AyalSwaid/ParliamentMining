from Collectors.DataCollectors.DataCollector import DataCollector
from datetime import datetime,date,timedelta
import requests
import json

class CA_DataCollector(DataCollector):
    def __init__(self,path,batch_size=65,url="https://api.openparliament.ca"):

        super().__init__(batch_size)
        self.path = path
        self.url = url

    def get_members(self):

        data_url = self.url + "/politicians/?include=all"
        data = self.send_request(data_url)
        chmaber = "h"
        counter = 0 
        next_url = data["pagination"]["next_url"]
        while next_url is not None:
          members = data["objects"]
          to_write = {}
          for member in members:
            name = member["name"]
            data = self.send_request(self.url + member["url"])
            membership = data["memberships"]
            for i in membership :
              start_date = i["start_date"]
              start_date = datetime.strptime(start_date, "%Y-%m-%d")
              if start_date > datetime.strptime("2000-01-01", "%Y-%m-%d"):
                end_date = i["end_date"]
                db_id = counter
                counter +=1
                party = i["party"]["short_name"]["en"]
                country = 2
                member_id = i["riding"]["id"]
                to_write[db_id] = [member_id,name,start_date,end_date,party,chmaber,country]
            # Write to file
            json_file_name = str(datetime.now()).replace(':', "-")
            with open(f'{Data.processor_members_dir}/CA/{json_file_name}.json', 'wb') as f:
                json.dump(to_write, f)
            data = self.send_request(self.url +next_url)
            next_url = data["pagination"]["next_url"]

    def get_bills(self,start_date=date(2000, 1, 1)):
      data = []
      api_url = self.url + f"/bills/?introduced={start_date}"
      for i in range(self.batch_size):
        output = self.send_request(api_url)
        if output["objects"]:
          data.append(output)
        my_date += timedelta(days=1)
      last_date = my_date # TODO write it somewhere
      if data:
          json_file_name = str(datetime.now()).replace(':', "-")
          with open(f'{Data.processor_bills_dir}/CA/{json_file_name}.json', 'wb') as f:
              json.dump(data, f)


    def get_debates(self,url,start_date,end_date):
        all_debates = self.get_all(self.url +"/debates/?"+ f"date__range={start_date}%2C{end_date}" + f"&limit={self.batch_size}") 
        all_data = []
        data = self.send_request(url)
        curr_data = data["objects"]  #send curr in function to load data
        next = data["pagination"]["next_url"]
        all_data.append(curr_data)
        while True:
            if next:
                next_url = self.url + next
                new_data = self.send_request(next_url)
                all_data.append(new_data["objects"])
                next = new_data["pagination"]["next_url"]
            else:
                break
        json_file_name = str(datetime.now()).replace(':', "-")
        with open(f'{Data.processor_debates_dir}/CA/{json_file_name}.json', 'wb') as f:
          json.dump(all_data, f)
        return all_data

    def get_member(self,link):
        member_data = None
        if link:
          member_data = self.send_request(self.url+link)
        if member_data:
          # print(member_data)
          return member_data["name"]
        return ""
    
    def send_request(self,api_url):
    # Send GET request
        response = requests.get(api_url)
        try:
            response = requests.get(api_url, headers={"Accept": "application/json"})
            if response.status_code == 200:
                data = response.json()
            else:
                print("Error:", response.status_code)
        except requests.exceptions.RequestException as e:
            print("Error:", e)
        return data
