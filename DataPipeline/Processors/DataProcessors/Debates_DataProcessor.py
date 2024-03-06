from Processors.DataProcessors.DataProcessor import DataProcessor
import pickle
import os
import json
import pandas as pd
from Data.GLOBAL import Data
from docx.api import Document
import win32com.client # pip install pywin32
import Data.nlph_utils as nlph
from collections import defaultdict
# from time import time
from datetime import datetime


"""
Statistics summary:
IL: 25 plenums -> 966 debates -> 15 minutes -> rate= 1 debate per second
"""
class Debates_DataProcessor(DataProcessor):
    def __init__(self, batch_size):
        super(Debates_DataProcessor, self).__init__(batch_size)
        self.data_path = Data.processor_debates_dir
        self.table = "debates"
        self.word = None # used for IL


    def __del__(self):
        if self.word is not None:
            self.word.Quit()
    
    def to_csv(self):
        pass


    def process_data(self):
        pass
    

    def process_UK(self):

        file_path = os.listdir(self.data_path + '/UK')

        # if dir is empty then exit
        if len(file_path) > 0:
            file_path = file_path[0]
        else:
            print('processor (UK debates) did not find files to process')
            return
        # for file_path in os.listdir(self.data_path + '\\UK'):
        # NOTE: each pickle file is a single batch
        # load pickle file that contains all the debates_dates and files paths
        debates = self.load_pkl(self.data_path + '/UK/'+file_path)

        # iterate over the pkl and call extract_debate_data and split_members for each debate
        for debate in debates:
            # debate_title, members = self.extract_debate_data(debate['file_path'])
            debate_title, speeches = self.UK_split_members(debate['file_path'])
            debate['debate_title'] = debate_title
            debate['country'] = 2

            # save speeches in json
            # slice file_path[24:] to remove the ".pkl" at the end
            speeches_file_path = f"{Data.speeches_files_dir}/UK/{debate['file_path'][24:-4]}.json"
            with open(speeches_file_path, 'a+') as json_file:
                json.dump(speeches, json_file)

            debate['file_path'] =  speeches_file_path

        # save debates in a csv table save
        # og_debates_table = pd.read_csv('debates.csv')
        new_debates = pd.DataFrame(debates)

        # og_debates_table = pd.concat([og_debates_table, new_debates], axis=0)
        new_debates.to_csv(f'{Data.csv_files_dir}/debates/{file_path}.csv')

        # delete pickle file
        os.remove(self.data_path + '\\UK\\'+file_path)




    def process_IL(self):
        print("processor (IL debates) started")
        file_path = os.listdir(self.data_path + '/IL')

        # TODO: put blacklist of files that cause errors
        # if dir is empty then exit
        if len(file_path) > 0:
            file_path = file_path[0]
        else:
            print('processor (IL debates) did not find files to process')
            return

        plenums = Data.load_json(f"{Data.processor_debates_dir}/IL/{file_path}")

        if self.word is None:
            self.__init_wordApp()

        all_debates = []
        p_num = 1
        for plenum in plenums:
            print(f"plenum {p_num}/{len(plenums)}")
            p_num += 1

            files = plenum['files']
            date = plenum['plenum_date']

            # debates = self.__process_IL_files(files)
            # iterate over generator returned from __process_IL_files(files)
            for debates in self.__process_IL_files(files):
                d_num = 1
                # print("<PROCESS_IL FUNCTION -> debates:\n", debates)

                # each generator step returns a list of debates of format [{"debate_title": title, "speeches": speeches}]
                for i, debate in enumerate(debates):
                    print(f"\tdebate {d_num}/{len(debates)}")
                    d_num += 1

                    curr_debate = {"date": date, "debate_title": debate['debate_title'], "country": 3}

                    # save speeches in json
                    filename = f"{i}{datetime.now().strftime('%Y-%m-%d %H-%M-%S')}.json"
                    Data.save_json(f"{Data.speeches_files_dir}/IL/{filename}", debate['speeches'])

                    #
                    curr_debate['file_path'] = f"{Data.speeches_files_dir}/IL/{filename}"
                    all_debates.append(curr_debate)


            # save all debates in csv file as a batch
            new_debates = pd.DataFrame(all_debates)

            # og_debates_table = pd.concat([og_debates_table, new_debates], axis=0)
            new_debates.to_csv(f'{Data.csv_files_dir}/debates/{file_path.split("/")[-1]}.csv')

            # TODO: remove file from collector

    def process_USA(self):
        pass


    def process_TN(self):
        pass


    def process_CA(self):
        pass


    def extract_UK_debate_data(self, file_path):
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


    def UK_split_members(self, file_path):
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



    def __process_IL_files(self, files):# Todo: this function is so slow, check how can we improve
        """
        given files list related to a single plenum, extract all the debates data from
        usually it is only one doc / docx file for each plenum
        this plenum
        :param files: list of format [file_type: str, file_path: str], this list is made by IL Collector
        :return: debates generator, for each file in plenum file return the debates it contains
        """
        for file_type, file_path in files:
            if file_type.lower() not in ["doc", "docx"]:
                print(f"debates processor (IL) cannot process file of type {file_type}, path: {file_path}")


            # convert word to text
            texts_lines = self.__word2text(file_path)

            # extract title and speeches from texts
            debates = self.__parse_IL_plenum(texts_lines)

            yield debates


    def __init_wordApp(self):
        if self.word is None:
            self.word = win32com.client.gencache.EnsureDispatch('Word.Application')

    def __is_paragraph_centered(self, paragraph):
        """
        This func is FUNC FOR IL WORD PROCESSING, check if given paragraph is positioned in the center
        :param paragraph: word document object paragraph
        :return: bool
        """
        alignment = paragraph.Format.Alignment
        return alignment == 1  # 1 corresponds to center alignment


    def __is_underlined(self, paragraph):
        return paragraph.Range.Font.Underline != 0


    def __word2text(self, file_path):
        """
        convert word (doc / docx) file into python string
        :param file_path: path to word file
        :return: lines, list of str, containing each line in the doc converted to str.
                to get full text in one string do '\n'.join(lines)
        """
        # print("old f path:",file_path)
        # print("working dir:", os.getcwd())
        file_path = os.path.join(os.getcwd(), file_path.replace('/', '\\'))
        # print("new f path:",file_path)

        doc = self.word.Documents.Open(file_path, ReadOnly=True)

        # todo: change the code
        full_text = []
        for p in doc.Paragraphs:
            tmp_txt = p.Range.Text.strip()
            if self.__is_paragraph_centered(p):
                tmp_txt = f'**{tmp_txt}**'
            elif self.__is_underlined(p): # we check this only for MP speach
                tmp_txt = f"UU{tmp_txt}UU"

            full_text.append(tmp_txt)
        lines = [t for t in full_text if len(t.strip()) > 0]
        # print(lines)
        return lines


    def __parse_IL_plenum(self, lines):
        """
        given lines of plenum doc file, extract all the debates speeches it contains
        :param lines: list of str lines (splitted by '\n')
        :return: dict of all debates from this files, format: [{debate_title: title, speeches: {speaker:speech, ...}, ...]
        """
        lines = '\n'.join(lines)
        # with open("curr_test.txt", "a+") as f:
        #     f.write(lines)
        matches = [match for match in nlph.rep_title.finditer(lines)]
        plenum_started = False

        all_debates = []
        # curr_debate = defaultdict(dict)

        for i in range(len(matches) - 1):
            start, end = matches[i].start(), matches[i].end()
            match = lines[start:end].strip()

            if plenum_started:

                if nlph.rep_title.search(
                        match):  # i know that this is always True but if the code works dont touch it XD

                    # check if match is new debate or table of contents or seder yom
                    if match.strip().strip("**") in nlph.re_bullshit_titles:
                        continue
                    else:  # if it is new debate
                        # get current debate title
                        curr_title = match
                        if nlph.rep_first_two_bills.search(curr_title):
                            curr_title = lines[matches[i-1].start():matches[i-1].end()].strip()
                        # all_speeches = defaultdict(str)

                        curr_debate_speeches = self.get_debate_speeches(lines, matches[i], matches[i + 1])
                        if len(curr_debate_speeches) < 2:
                            continue

                        curr_debate = {
                            "debate_title": curr_title.strip("**"),
                            "speeches": curr_debate_speeches
                        }
                        # curr_debate[curr_title] = curr_debate_speeches
                        all_debates.append(curr_debate)
                else:
                    pass  # TODO

                    # split it by '\n' and get speech of each member
            else:

                if nlph.rep_plenum_start.search(match):  # arrived to plenum intro title
                    # print("plenum matched:", match)
                    plenum_started = True
        return all_debates


    def __get_debate_speeches(self, all_text, idxs0, idxs1):
        """
        given indices of current and next debate, extract speeches of the current debate
        using regex
        :param all_text: all plenum file text
        :param idxs0: regex match index of curr debate
        :param idxs1: regex match index of next debate
        :return: dict of speeches, format {speaker: speech}
        """
        print("getting speeches")
        lines = all_text[idxs0.end():idxs1.start()].strip()

        all_speeches = defaultdict(str)

        matches = [s for s in nlph.rep_is_speaker.finditer(lines)]

        for i in range(len(matches)):
            start, end = matches[i].start(), matches[i].end()
            speaker = lines[start:end].strip().strip('U')

            if i != len(matches) - 1:
                all_speeches[speaker] += f"<{i}>" + lines[end:matches[i + 1].start()].strip()
            else:
                all_speeches[speaker] += f"<{i}>" + lines[end:len(lines)].strip()

        return all_speeches



    def load_pkl(self, file_path):
        with open(file_path, 'rb') as file:
            data = pickle.load(file)

        return data