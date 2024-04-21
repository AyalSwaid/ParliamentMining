import mysql.connector
from  Exceptions.dbException import DatabaseException
import pandas as pd


class dbManager:

    def test(self):
        mydb = self.connect()

        cur = mydb.cursor()
        # self.drop_tables(cur)
        # return
        # self.create_tables(mydb, cur)
        # mydb.commit()

        # cur.execute("SHOW TABLES")

        for i in range(30):
            self.insert_debate(cur,
                                 None,
                                 "hellow parlioametn",
                                 "hi hello hey",
                                 "hh.txt",
                                 "2024-03-18",
                                 0,
                                 None)

        self.insert_topic(cur, "corona")



        self.insert_country(cur, "brazil")

        self.insert_debate_member(cur, 5, 25, False)



        # self.__insert_debate(cur, "kalola")

        mydb.commit()

        # cur.fe
        # for i in cur:
        #     print(i)

        # cur.execute("CREATE DATABASE mytestdbpython")
        # cur.execute("SHOW DATABASES")
        #
        #
        # for db in cur:
        #     print(db)
        # print(mydb)

    def test_get(self):
        mydb = self.connect()
        # mydb2 = self.connect()
        cur = mydb.cursor()

        for i in self.get_batches(cur, query="select * from countries", batch_size=9):
            print(i)


    def connect(self):
        """
        connect to the db, username: admin, pwd: admin
        :return: database instance
        """
        mydb = mysql.connector.connect(
            host="localhost",
            user="admin",
            passwd="admin",
            database="dbv2"
        )

        self.db = mydb
        return mydb


    def read_sql_file(self, file_name):
        """
        return content of sql file
        :param file_name: str
        :return: content str
        """
        if not file_name.endswith(".sql"):
            file_name = f"{file_name}.sql"

        with open(f"{file_name}") as f:
            return f.read()


    def drop_tables(self, cur):
        """
        drop all tables in db.
        Note: u have to consider foriegn keys relations
        :param cur: cursor instance
        :return: None
        """

        tables = ["debates", "debates_members", "topics", "countries"]

        # for table in

        for i in tables:
            cur.execute(F"DROP TABLE {i}")


    def create_tables(self,mydb, cur):
        """
        execute sql file test_create_tables.sql that creates needed tables
        :param mydb:
        :param cur:
        :return: None
        """
        # query = self.read_sql_file("test_create_tables.sql")
        query = self.read_sql_file("Data/sql_queries/create_tables.sql")
        cur.execute(query)
        return
        for q in query.split(";"):
            print(q)
            cur.execute(q)
            # mydb.commit()


    def insert_topic(self, cur, topic):
        """
        insert topic in topics table
        :param cur:
        :param topic:
        :return:
        """
        try:
            cur.execute("INSERT INTO topics (topic) VALUES(%s)", (topic,))
        except Exception as e:
            raise DatabaseException("error while inserting", "insert_topic", "")

    def insert_country(self, cur, country):
        """
        insert country into countries table
        :param cur:
        :param country:
        :return: None
        """
        cur.execute("INSERT INTO countries (name) VALUES(%s)", (country,))


    def insert_debate_member(self, cur, debate_id, member_id, is_sponsor):
        cur.execute("INSERT INTO debates_members (debate_id, member_id, is_sponsor) VALUES(%s, %s, %s)", (debate_id, member_id, is_sponsor))

    def insert_debate(self, cur, topic, title, summary, content_file_path, debate_date, is_issue, country):

        # (topic, title, summary, content_file_path, debate_date, is_issue, country)
        cur.execute("INSERT INTO debates (topic, title, summary, content_file_path, debate_date, is_issue, country) VALUES (%s, %s, %s, %s, %s, %s, %s)", (topic, title, summary, content_file_path, debate_date, is_issue, country))



    def insert_to_table(self, cur, table, data_dict):
        cur.execute(f"INSERT INTO {table} ({','.join(data_dict.keys())}) VALUES (%s, %s, %s, %s, %s, %s, %s)",tuple(data_dict.values()))


    def insert_from_df(self, cur, table, df):
        num_params = len(df.columns)
        params_str = ",".join(["%s"] * num_params)

        for row in df.iterrows():
            query = f"INSERT INTO {table} ({df.columns}) VALUES ({params_str})"
            cur.execute(query, tuple(row))


    def get_debates(self, cur, start=0, end = None, batch_size = None):
        assert isinstance(start, int)
        assert isinstance(end,int) or end is None
        assert isinstance(batch_size,int) or batch_size is None

        sql = f"SELECT * FROM debates"

        if end is None:
            sql += f" WHERE debate_id >= {start}"
        else:
            sql +=  f" WHERE debate_id >= {start} AND debate_id < {end}"
        print(sql)
        cur.execute(sql)

        if batch_size is None:
            return cur.fetchall()

        else:
            rows = cur.fetchmany(batch_size)
            while rows:
                yield rows
                rows = cur.fetchmany(batch_size)


    def get_batches(self, cur,query, params=None, batch_size=10, return_df=True):
        """
        execute select query and return its output by batches
        :param query: any full sql query
        :param batch_size:
        :return:
        """
        # cur = self.connect().cursor()
        if params is not None:
            cur.execute(query, params)
        else:
            cur.execute(query)

        columns = [column[0] for column in cur.description]
        rows = cur.fetchmany(batch_size)
        while rows:
            if return_df:
                yield pd.DataFrame(rows, columns=columns)
            else:
                yield rows
            rows = cur.fetchmany(batch_size)


    def get_all(self, cur, query, return_df = True):
        cur.execute(query)

        data = cur.fetchall()
        columns = [column[0] for column in cur.description]

        return pd.DataFrame(data, columns=columns)if return_df else data

    def get_table(self, table):
        cur = self.db.cursor()
        query = f"SELECT * FROM {table}"

        data = self.get_all(cur, query, return_df = True)
        return data



    def get_table_batches(self, table, batch_size=10):
        """
        get table data from db and return it as dataframe
        :param table: str
        :param int - specify batch size0
        :return: dataframe
        """
        cur = self.db.cursor()
        query = f"SELECT * FROM {table}"
        # print("555")
        # if batch_size is None:
        #

        # else:
        data_batches = self.get_batches(cur, query, batch_size=batch_size, return_df=True)
        # columns = [column[0] for column in cur.description]
        return data_batches
        # for batch in data_batches:
        #     yield pd.DataFrame(batch, columns=columns)



    def test_df(self):
        self.connect()
        # print("555")
        df = self.get_table("debates")
        dfs = self.get_table_batches("debates", batch_size=10)

        # print(next(iter(df)))
        for df in dfs:
            print((df.info()))
            print(df.head())

        print((df.info()))
        print(df.head())










if __name__ == "__main__":
    db = dbManager()
    # db.test()
    # db.test_get()
    db.test_df()