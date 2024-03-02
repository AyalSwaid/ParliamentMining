from Collectors.DataCollectors.DataCollector import DataCollector
import requests
import json

class USA_DataCollector(DataCollector):
    def __init__(self, batch_size,start_date,end_date):
        super(USA_DataCollector, self).__init__(batch_size)
        self.url = 'https://api.govinfo.gov/search'
        self.api_key = 'c2mQmLAgAYvSIawOm9aPWLr2kYs277VUxqz6DS9L'
        self.start_date = start_date
        self.end_date = end_date
        self.search_query = {
            "query": f"Congressional Record -(daily and digest) publishdate:range({self.start_date},{self.end_date})",
            "pageSize": f"{batch_size}",
            "offsetMark": "*",
            "sorts": [
                {
                    "field": "score",
                    "sortOrder": "DESC"
                }
            ]
        }


    def get_debates(self):
        headers = {'X-Api-Key': self.api_key}
        query_response = requests.post(self.url, json=self.search_query, headers=headers)

        if query_response.status_code == 200:
            data = query_response.json()
            if data:
                json_file_name = str(datetime.now()).replace(':', "-")
                with open(f'{Data.processor_debates_dir}/USA/{json_file_name}.json', 'wb') as f:
                  json.dump(data, f)

    def get_members(self,congress,chamber):
          # Define the headers with the API key
          headers = {
              'X-API-Key': self.api_key
          }

          url = f"https://api.propublica.org/congress/v1/105/house/members.json"

          response = requests.get(url,headers = headers)


          if response.status_code == 200:
            data = response.json()
            if data:

                json_file_name = f"{congress}_{chamber}_{str(datetime.now()).replace(':', "-")}"
                with open(f'{Data.processor_members_dir}/USA/{json_file_name}.json', 'wb') as f:
                      json.dump(data, f) #TODO save the last date


    def get_bills(self,start_date,end_date):
        # Define the base URL and endpoint for bills
        api_url = f"https://api.govinfo.gov/published/{start_date}/{end_date}"  
        endpoint = 

        params = {
            "offset": 0,
            "pageSize": self.batch_size,  # Number of results per page
            "collection": "BILLS",
            "api_key": self.api_key
        }

        # Make the GET request
        response = requests.get(api_url, params=params)

        if response.status_code == 200:
            data = response.json()
            if data:
                json_file_name = str(datetime.now()).replace(':', "-")
                with open(f'{Data.processor_bills_dir}/USA/{json_file_name}.json', 'wb') as f:
                      json.dump(data, f) #TODO save the last date
