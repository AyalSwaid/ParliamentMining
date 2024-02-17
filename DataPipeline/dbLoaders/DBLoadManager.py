from dbLoaders.DBDataLoader import DBDataLoader


class DBLoadManager:
    def __init__(self, csv_paths) -> None:
        self.csv_paths = csv_paths
        self.data_loader = DBDataLoader()

    
    def init_db_tables(self):
        pass


    def fill_constant_tables(self):
        pass