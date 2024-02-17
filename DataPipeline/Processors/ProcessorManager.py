from Processors.DataProcessors.Bills_DataProcessor import Bills_DataProcessor
from Processors.DataProcessors.Debates_DataProcessor import Debates_DataProcessor
from Processors.DataProcessors.Members_DataProcessor import Members_DataProcessor
from Processors.DataProcessors.News_DataProcessor import News_DataProcessor
from Processors.DataProcessors.Votes_DataProcessor import Votes_DataProcessor


class ProcessorManager:
    def __init__(self, batch_size):
        self.batch_size = batch_size
        
        self.collectors = [Debates_DataProcessor(),
                           Bills_DataProcessor(),
                           Members_DataProcessor(),
                           News_DataProcessor(),
                           Votes_DataProcessor()]

    
    def run_collectors(self):
        pass
