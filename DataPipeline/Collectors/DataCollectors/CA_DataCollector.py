from Collectors.DataCollectors.DataCollector import DataCollector
from datetime import datetime, date, timedelta
import requests
import json
from Data.GLOBAL import Data


class CA_DataCollector(DataCollector):
    def __init__(self, path, batch_size=65, url="https://api.openparliament.ca"):

        super().__init__(batch_size)
        self.path = path
        self.url = url

    # Get members only run once
    def get_members(self):
        """
        Retrieves information about Candian house of commons politicians and stores the data into JSON files.
        """

        data_url = self.url + "/politicians/?include=all"
        data = self.send_request(data_url)
        chmaber = "h"
        counter = 0
        if data:
            next_url = data["pagination"]["next_url"]

            while next_url is not None:

                members = data["objects"]
                to_write = {}

                for member in members:
                    name = member["name"]
                    data = self.send_request(self.url + member["url"])
                    if data:
                        membership = data["memberships"]

                        # get all information about politicians who have served in parliament more than once
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
                    else:
                        print("No data returned from request")
                # Write to files for the proccessor
                if to_write:

                    json_file_name = str(datetime.now()).replace(':', "-")
                    with open(f'{Data.processor_members_dir}/CA/{json_file_name}.json', 'wb') as f:
                        json.dump(to_write, f)
                    data = self.send_request(self.url +next_url)
                    next_url = data["pagination"]["next_url"]
                else:
                    print("Nothing to write")
        else:
            print("No data returned from request")
    def get_bills(self):
        """
        Retrieves information about bills introduced after a specified start date and stores the data into JSON files.

        """
        data = []
        # get start date
        json_prog = Data.get_progress()
        start_date = json_prog["CA_bills_start_date"]
        start_date = datetime.strptime(start_date, "%Y-%m-%d")

        api_url = self.url + f"/bills/?introduced={start_date.strftime('%Y-%m-%d')}"
        for i in range(self.batch_size):
            bill = self.send_request(api_url)
            if bill:
                if bill["objects"]:
                    data.append(bill)
            else:
                print("No data returned from request")
            start_date += timedelta(days=1)
        # write the data for the proccessor
        if data:
            json_file_name = str(datetime.now()).replace(':', "-")
            with open(f'{Data.processor_bills_dir}/CA/{json_file_name}.json', 'w') as f:
                json.dump(data, f)
        else:
            print("No data found")
        # update the start date
        last_date = start_date
        json_prog["CA_bills_start_date"] = last_date.strftime("%Y-%m-%d")
        Data.update_progress(json_prog)

    def get_debates(self):
        """
        Retrieves debates from a specified time range and stores the data into JSON files.
        """
        # get dates range
        print("HI")
        json_prog = Data.get_progress()
        start_date = json_prog["CA_debates_start_date"]
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = start_date + timedelta(days=self.batch_size)
        print(start_date.strftime('%Y-%m-%d'))
        print(end_date)

        data = []

        api_url = self.url + "/debates/?" + f"date__range={start_date.strftime('%Y-%m-%d')}%2C{end_date.strftime('%Y-%m-%d')}" + f"&limit=65"
        one_page = self.send_request(api_url)
        if one_page:

            curr_data = one_page["objects"]  # send curr in function to load data
            next_page = one_page["pagination"]["next_url"]
            data.append(curr_data)
            # get all debates for the wanted range
            while True:
                if next_page:
                    next_url = self.url + next_page
                    new_data = self.send_request(next_url)
                    data.append(new_data["objects"])
                    next_page = new_data["pagination"]["next_url"]
                else:
                    break
            if data:
                json_file_name = str(datetime.now()).replace(':', "-")
                with open(f'{Data.processor_debates_dir}/CA/{json_file_name}.json', 'w') as f:
                    print(data)
                    json.dump(data, f)
            else:
                print("No data to write")
        else:
            print("No data returned from request")
        # update the start date

        json_prog["CA_debates_start_date"] = end_date.strftime("%Y-%m-%d")
        Data.update_progress(json_prog)

    def send_request(self, api_url):
        """
        Helper function that sends a GET request to the specified API URL and retrieves JSON data.
        """
        data = []

        try:
            response = requests.get(api_url, headers={"Accept": "application/json"})
            if response.status_code == 200:
                data = response.json()
            else:
                print("Error:", response.status_code)
        except requests.exceptions.RequestException as e:
            print("Error:", e)
        return data
