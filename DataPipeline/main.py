import os

from Data.GLOBAL import Data
from Collectors.CollectorManager import CollectorManager
from Processors.ProcessorManager import  ProcessorManager
import json
from time import time


# import undetected_chromedriver as uc
#
# d_path = r'C:\Users\ayals\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe'
# uc.Chrome(version_main=120, driver_executable_path=d_path)

if __name__ == "__main__":
    # collector_m = CollectorManager(15)
    # processor_m = ProcessorManager(15)
    # #
    # since = time()
    # for i in range(5):# 1
    #     collector_m.run_collectors()
    #     processor_m.run_processors()
    #
    #     for p in os.listdir(Data.text_files_dir+'/UK'):
    #         os.remove(f'{Data.text_files_dir}/UK/{p}')
    #
    # print(f"elapsed: {time()-since}")




