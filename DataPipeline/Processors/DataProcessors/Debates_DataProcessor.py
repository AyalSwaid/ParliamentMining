from Processors.DataProcessors.DataProcessor import DataProcessor
import pickle
import os
import json
import pandas as pd


class Debates_DataProcessor(DataProcessor):
    def __init__(self, batch_size, data_path):
        super(Debates_DataProcessor, self).__init__(batch_size)
        self.data_path = data_path
        self.table = "debates"

    
    def to_csv(self):
        pass


    def process_data(self):
        pass
    

    def process_UK(self):
        for file_path in os.listdir(self.data_path + '\\UK'):
            # NOTE: each pickle file is a single batch
            # load pickle file that contains all the debates_dates and files paths
            debates = self.load_pkl(self.data_path + '\\UK\\'+file_path)

            # iterate over the pkl and call extract_debate_data and split_members for each debate
            for debate in debates:
                # debate_title, members = self.extract_debate_data(debate['file_path'])
                debate_title, speeches = self.split_members(debate['file_path'])
                debate['debate_title'] = debate_title

                # save speeches in json
                with open(f"speeches\\UK\\{debate_title}.json", 'a+') as json_file:
                    json.dump(speeches, json_file)


            # save debates in a csv table save
            og_debates_table = pd.read_csv('debates.csv')
            new_debates = pd.DataFrame(debates)

            og_debates_table = pd.concat([og_debates_table, new_debates], axis=0)
            og_debates_table.to_csv('debates.csv')






        # save the result of each iteration in a csv row


    def process_IL(self):
        pass


    def process_USA(self):
        pass


    def process_TN(self):
        pass


    def process_CA(self):
        pass


    def extract_debate_data(self, file_path):
        '''
        given debate txt file path, process and extract data like debate title, members,
        :file_path: string, full path of the debate txt file
        :return: debate_title: string
                members: list
        '''
        members = set()

        with open(file_path, "r") as file:
            lines = file.read().split('\n')
            debate_title = lines[0].strip()

            for i in range(1, len(lines)):
                # print(lines[i])
                # according to the txt files format, when new member speaks the next line is not '\n'
                if (lines[i] != '') and (lines[i - 1] != ''):  # New member is taling
                    members |= set([lines[i - 1]])

            return debate_title, list(members)


    def split_members(self, file_path):
        '''
        take debates text file and extract member name and speeches out of them
        :param files_path:
        :return:
        '''
        # files_path = os.listdir(txt_files_dir)

        members = set()
        speeches = {}

        # for file_path in files_path:
        curr_debate_speeches = {}

        with open(file_path, "r") as file:
            lines = file.read().split('\n')
            debate_title = lines[0].strip()
            speech = ''
            member_name = None
            for i in range(1, len(lines)):

                # print(lines[i])
                # according to the txt files format, when new member speaks the next line is not '\n'
                if (lines[i] != '') and (lines[i - 1] != ''):  # New member is talking
                    if member_name is not None:
                        curr_debate_speeches[member_name] = curr_debate_speeches.get(member_name, '') + speech
                    member_name = lines[i - 1]
                    members |= set([member_name])
                    speech = lines[i]
                else:
                    speech += lines[i] + ' '
            speeches[debate_title] = curr_debate_speeches

        return debate_title, speeches



    def load_pkl(self, file_path):
        with open(file_path, 'rb') as file:
            data = pickle.load(file)

        return data