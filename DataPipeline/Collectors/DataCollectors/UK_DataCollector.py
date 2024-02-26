from DataCollector import DataCollector
import time
import selenium.webdriver.support.expected_conditions as EC
import undetected_chromedriver as uc
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import os
import pickle
from datetime import datetime
import pandas as pd
import json


class UK_DataCollector(DataCollector):
    def __init__(self, batch_size, txt_files_dir = "text_files"):
        super(UK_DataCollector, self).__init__(batch_size)

        # must give full path for download_dir !!!
        self.download_dir = r"C:\Users\ayals\OneDrive\שולחן העבודה\parliamentMining\Collectors\DataCollectors\test_downloads"
        self.txt_files_dir = txt_files_dir
        self.processor_files = r"C:\Users\ayals\OneDrive\שולחן העבודה\parliamentMining\Collectors\DataCollectors\to_process"



    def get_debates(self):
        print("collecting UK debates")
        driver = self.init_driver()
        links = self.get_debates_links(driver, "2015-04-01", "2015-05-31", 1)

        # files_path_gen = self.get_debates_files(driver, links)
        debates = []
        for (debate_file, debate_date) in self.get_debates_files(driver, links):
            debates.append({
                'date': debate_date,
                'file_path': debate_file
            })

        # save current batch data in pickle file for the processor
        pkl_file_name = str(datetime.now()).replace(':', "-")
        with open(f'{self.processor_files}\\debates\\UK\\{pkl_file_name}.pkl', 'wb') as f:
            pickle.dump(debates, f)
        driver.quit()
        #     # driver.command_executor.close()
        #     time.sleep(3)
        # except:
        #     pass

        print("DONE UK debates")

        return links




    def get_votes():
        pass


    def get_members():
        pass


    def get_bills():
        pass


    def init_driver(self):
        '''
        init chrome webdriver object and set options to start scraping.
        also creates the downloades & text files folders
        :return: webdriver object
        '''


        options  = uc.ChromeOptions()

        options.add_argument("--start-maximized")
        
        options.add_experimental_option("prefs", {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False, # Disable prompting for download
            "download.directory_upgrade": True})
        
        # create needed folders for downloads
        for dir_path in [self.download_dir, self.txt_files_dir]:
            try:
                os.mkdir(dir_path)
                print(f"Directory '{dir_path}' created successfully.")
            except FileExistsError:
                pass
        

        driver = uc.Chrome(options=options)

        return driver

    def get_debates_links(self, driver: uc.Chrome, start_date, end_date, start_page=1, final_page=0):
        '''
        get all the links for debates happened between start date - end date
        driver: selenium WebDriver
        the function iterates on the website pages, each page is 20 debates
        start_date: string of format "yyyy-mm-dd", example: "2000-01-01"
        end_date: string of format "yyyy-mm-dd", example: "2000-01-01"
        return: list of strings, including the links
        '''
        url = f"https://hansard.parliament.uk/search/Debates?endDate={end_date}&partial=False&sortOrder=1&startDate={start_date}"

        driver.get(url + f'&page={start_page}')

        try:
            n_pages = WebDriverWait(driver, 5).until( \
                EC.visibility_of_element_located((By.XPATH, '/html/body/main/div[2]/article/div/div[2]/div[2]/div/div[1]/div/strong[3]'))).text

            n_pages = int(n_pages)
        except TimeoutException:
            print("no debates for this period")
            return []

        if final_page == 0:
            final_page = n_pages + 1
        else:
            final_page = min(final_page, n_pages + 1)

        links = []
        for page in range(start_page, final_page):
            driver.get(url + f'&page={page}')
            search_results = WebDriverWait(driver, 30).until( \
                EC.visibility_of_any_elements_located((By.XPATH, "/html/body/main/div[2]/article/div/div[2]/div[3]/a")))

            links.extend([result.get_attribute("href") for result in search_results])

            # if page != final_page:
        # del driver

        return links


    def new_file_name(self):
        '''
        Checks if the file in download_dir is still downloading or finished.
        Note: the function assumes that there is only one file donwloading at a time.
        :return: None if file still didnt finish else return file name
        '''
        download_dir = self.download_dir

        filename = None
        for filename in os.listdir(download_dir):

            if filename.endswith(".tmp"):
                return None
        return filename


    def get_debates_files(self, driver, links):
        '''
        given the links of the debates in hansard website, get debate date and
        download its text file for each link in links list.
        the function moves the downloaded file from download_dir into text_files dir to get processed later
        :driver: webdriver object
        :links: list of string, containing debates links
        :return: generator:
                debate_file: txt file name
                deate date: string, presenting the date of the debate of format "yyyy-mm-dd"
        '''
        download_dir = self.download_dir
        txt_files_dir = self.txt_files_dir

        for link in links:
            link = link.split(r'/')
            debate_date = link[-4]
            text_file_url = "https://hansard.parliament.uk/debates/GetDebateAsText/" + link[-2]

            # download file by url GET
            driver.get(text_file_url)

            # wait untill file is downloaded
            debate_file = self.new_file_name()
            while debate_file is None:
                time.sleep(0.5)
                debate_file = self.new_file_name()

            # move file to the text files folder
            new_debate_file = str(datetime.now().microsecond) + debate_file
            new_debate_file = f"{txt_files_dir}\\UK\\{new_debate_file}"

            try:
                os.rename(f"{download_dir}\\{debate_file}", new_debate_file)
            except FileExistsError:
                print("Collector problem while copying donwloaded file from download dir to text dir")
            yield (new_debate_file, debate_date)

if __name__ == "__main__":
    a = UK_DataCollector(20, "test")
    links = a.get_debates()

    print(links, len(links))