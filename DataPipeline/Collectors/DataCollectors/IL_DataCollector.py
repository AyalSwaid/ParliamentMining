from Collectors.DataCollectors.DataCollector import DataCollector
import requests as reqs
from bs4 import BeautifulSoup as bs


class IL_DataCollector(DataCollector):
    def __init__(self, batch_size):
        super(IL_DataCollector, self).__init__(batch_size)
    
    
    def get_debates(self):
        url = 'https://knesset.gov.il/Odata/ParliamentInfo.svc/KNS_CommitteeSession()/'
        url = 'https://knesset.gov.il/Odata/ParliamentInfo.svc/KNS_DocumentPlenumSession'
        resp = reqs.get(url)

        soup = bs(resp.content, 'xml')
        first_element = soup.find('entry').find('properties')

        print(first_element)
        print(first_element.find_all('SessionUrl'))

    def get_votes(self):
        pass


    def get_members(self):
        pass


    def get_bills(self):
        pass


if __name__ == "__main__":
    a = IL_DataCollector(20)
    a.get_debates()