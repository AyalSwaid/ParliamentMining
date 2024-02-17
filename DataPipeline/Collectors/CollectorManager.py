from Collectors.DataCollectors.CA_DataCollector import CA_DataCollector
from Collectors.DataCollectors.IL_DataCollector import IL_DataCollector
from Collectors.DataCollectors.TN_DataCollector import TN_DataCollector
from Collectors.DataCollectors.UK_DataCollector import UK_DataCollector
from Collectors.DataCollectors.USA_DataCollector import USA_DataCollector


class CollectorManager:
    def __init__(self, batch_size):
        self.batch_size = batch_size
        
        self.collectors = [UK_DataCollector(),
                           CA_DataCollector(),
                           IL_DataCollector(),
                           USA_DataCollector(),
                           TN_DataCollector()]

    
    def run_collectors(self):
        pass
