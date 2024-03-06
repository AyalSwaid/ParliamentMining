from Collectors.DataCollectors.DataCollector import DataCollector
import requests as reqs
from bs4 import BeautifulSoup as bs
from Data.GLOBAL import Data
from datetime import datetime, timedelta

# Collected 25 plenum docs files in 49 seconds
# NOTE: EACH PLENUM CONTAINS MULTIPLE DEBATES
class IL_DataCollector(DataCollector):
    def __init__(self, batch_size):
        super(IL_DataCollector, self).__init__(batch_size)
    
    
    def get_debates(self):
        plenum_list = []

        # get dates range
        json_prog = Data.get_progress()
        start_date = json_prog['UK_debates_start_date']
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = start_date + timedelta(days=self.batch_size)


        for entries in self.get_plenum_bulks(start_date, end_date):
            # iterate ovcer all entries


            for entry in entries:
                is_special = entry.find('textIsSpecialMeeting')
                if is_special:
                    continue

                plenum_id = entry.find('PlenumSessionID').text
                plenum_date = entry.find('StartDate').text
                print("entry date: ", plenum_date)
                # TODO: convert date to relevant format


                # get all files for this debate
                # plenum_files format: (type, file_path)
                plenum_files = self.__get_plenum_files(plenum_id)
                if not plenum_files:
                    continue
                print("filesL",plenum_files)


                curr_plenum = {
                    "plenum_date": plenum_date,
                    "files": plenum_files
                }
                plenum_list.append(curr_plenum)


        # write batch data into disk (pass to processor)
        file_name = str(datetime.now()).replace(':', "-")
        batch_file_path = f"{Data.processor_debates_dir}/IL/{file_name}.json"
        Data.save_json(batch_file_path, plenum_list)

        # TODO: update start date for the next batch


            # print(first_element.find('properties'))
            # print(first_element.find_all('SessionUrl'))

    def get_votes(self):
        pass


    def get_members(self):
        pass


    def get_bills(self):
        pass


    def __get_plenum_files(self, plenum_id):
        """
        given plenum_id, query its related files from KNS_DocumentPlenumSession, download
        each file, save its path and type and return them as a list of tuples
        :param plenum_id:  int
        :return: donwloaded files: list of tuples of format [(file_type, file_path)]
        """
        file_types_blacklist = {"URL", "VDO"}
        files_url = 'https://knesset.gov.il/Odata/ParliamentInfo.svc/KNS_DocumentPlenumSession'
        url = f"{files_url}?$filter=PlenumSessionID eq {plenum_id}"


        files_resp = reqs.get(url)
        files_soup = bs(files_resp.content, 'xml')

        # first_element = soup.find('entry').find('properties')
        files_entries = files_soup.find_all('entry')

        # iterate over all related files
        files = []
        for file_entry in files_entries:
            file_type = file_entry.find("ApplicationDesc").text
            if file_type in file_types_blacklist:
                continue

            file_path_url = file_entry.find("FilePath").text
            print("file url:", file_path_url, file_type)
            response = reqs.get(file_path_url)

            file_path = f"{Data.text_files_dir}/IL/{file_path_url.split('/')[-1]}"
            if response.status_code == 200:
                #TODO: sometimes downloading the file raises exception
                # 1. check if file already exist
                # 2. sometimes status code is 200 but the page is error page
                # Open the file in binary write mode and write the content of the response
                with open(file_path, "wb") as f:
                    f.write(response.content)
            else:
                print("Failed to download file. Status code:", response.status_code)
                continue

            files.append((file_type, file_path))



        return files


    def get_plenum_bulks(self, start_date, end_date):
        # Define urls for the OData
        # TODO: SET CORRECT FILTER
        debates_url = f"""https://knesset.gov.il/Odata/ParliamentInfo.svc/KNS_PlenumSession?$filter=StartDate ge datetime'{start_date.strftime("%Y-%m-%d")}T00:00' and StartDate le datetime'{end_date.strftime("%Y-%m-%d")}T23:59'"""
        print(f"getting {debates_url}")

        skip_size = 100
        curr_bulk = 0

        # get OData output
        entries = ['tmp']
        while entries:
            resp = reqs.get(f"{debates_url}&$skip={skip_size*curr_bulk}")
            soup = bs(resp.content, 'xml')
            entries = soup.find_all('entry')
            print("LENS:",len(entries))
            yield entries
            curr_bulk += 1

if __name__ == "__main__":
    a = IL_DataCollector(20)
    a.get_debates()