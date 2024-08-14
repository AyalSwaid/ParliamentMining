from Processors.DataProcessors.DataProcessor import DataProcessor
import pickle
import os
from fuzzywuzzy import process
import json
import pandas as pd
from Data.GLOBAL import Data
# from docx.api import Document
import win32com.client # pip install pywin32
import Data.nlph_utils as nlph
from Data.GLOBAL import nlp
from collections import defaultdict
# from time import time
from datetime import datetime
import re
import spacy



class Debates_DataProcessor(DataProcessor):
    def __init__(self, batch_size):
        super(Debates_DataProcessor, self).__init__(batch_size)
        self.data_path = Data.processor_debates_dir
        self.table = "debates"
        self.word = None # used for IL

        self.members = None # for debates_members table processing



    def __del__(self):
        if self.word is not None:
            self.word.Quit()
    
    def to_csv(self):
        pass


    def process_data(self):
        pass
    

    def process_UK(self):

        file_path = os.listdir(self.data_path + '/UK')
        print(file_path)

        # if dir is empty then exit
        if len(file_path) > 0:
            file_path = file_path[0]
        else:
            print('processor (UK debates) did not find files to process')
            return
        # for file_path in os.listdir(self.data_path + '\\UK'):
        # NOTE: each pickle file is a single batch
        # load pickle file that contains all the debates_dates and files paths

        # load pickle file that is a list of dicts contains a date and txt file path of each debate
        debates = self.load_pkl(self.data_path + '/UK/'+file_path)

        # here we store new debates metadata for csv
        all_debates = []

        # iterate over the pkl and call extract_debate_data and split_members for each debate
        i = 0
        print(f"Processor (UK debates) started to process {len(debates)} debates")
        for debate in debates:
            # debate_title, members = self.extract_debate_data(debate['file_path'])
            # debate_title, speeches = self.UK_split_members(debate['file_path'])
            debate_title, speeches = self.test_UK_split_members(debate['content_file_path'])

            if len(speeches) < 2:
                # print(f"small debate: {debate['file_path']}")
                i += 1
                continue

            debate['debate_title'] = debate_title
            debate['country'] = 2

            # save speeches in json
            # slice file_path[24:] to remove the ".pkl" at the end
            speeches_file_path = f"{Data.speeches_files_dir}/UK/{debate['content_file_path'][24:34]}W{str(datetime.now()).replace(':', '-')}.json"

            Data.save_json(speeches_file_path, speeches)

            # with open(speeches_file_path, 'a+') as json_file:
            #     json.dump(speeches, json_file)

            # debate['file_path'] = speeches_file_path
            debate = {
                "date": debate["debate_date"],
                "debate_title": debate_title,
                "country": 2,
                "file_path": speeches_file_path
            }
            all_debates.append(debate)
        print(f"DONE, skipped {i} empty debates")
        # save debates in a csv table save
        # og_debates_table = pd.read_csv('debates.csv')
        new_debates = pd.DataFrame(all_debates)

        # og_debates_table = pd.concat([og_debates_table, new_debates], axis=0)
        new_debates.to_csv(f'{Data.csv_files_dir}/debates/{file_path}.csv')

        # delete pickle file
        os.remove(self.data_path + '/UK/'+file_path)




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

        # file_path = "tor_test.json" # TODO: delete this

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
                    filename = f"{i}m{datetime.now().strftime('%Y-%m-%d %H-%M-%S')}.json"
                    Data.save_json(f"{Data.speeches_files_dir}/IL/{filename}", debate['speeches'])# TODO: uncomment this


                    #
                    curr_debate['file_path'] = f"{Data.speeches_files_dir}/IL/{filename}"
                    all_debates.append(curr_debate)


            # save all debates in csv file as a batch
            new_debates = pd.DataFrame(all_debates)

            # og_debates_table = pd.concat([og_debates_table, new_debates], axis=0)
            new_debates.to_csv(f'{Data.csv_files_dir}/debates/{file_path.split("/")[-1]}.csv') # TODO: uncomment
            # new_debates.to_csv(f'testingSpeeches/{file_path.split("/")[-1]}.csv') # TODO: delete

            # TODO: remove file from collector

        # TODO: remove file fro to process dir
        os.remove(Data.processor_debates_dir + '/IL/' + file_path)
        if self.word is not None:
            self.word.Quit()
            self.word = None




    def process_TN(self):
        print("processor (TN debates) started")
        all_debates = []# this is saved as csv at the end
        file_path = os.listdir(self.data_path + '/TN')

        # TODO: put blacklist of files that cause errors
        # if dir is empty then exit
        if len(file_path) > 0:
            file_path = file_path[0]
        else:
            print('processor (IL debates) did not find files to process')
            return

        debates_files = Data.load_json(self.data_path + '/TN/' + file_path)

        for idx, debate_file in enumerate(debates_files):
            # print("TITLE:", debate_file['debate_title'])
            # check if the debate is of format after/before 2019
            if debate_file["periodID"] == 1: # before 2019
                speeches = self.__TN_get_speeches2014(debate_file['data'])
            elif debate_file['periodID'] == 2: # after 2019
                speeches = self.__TN_get_speeches2019(debate_file['data'])
            else:
                print("invalid periodID: ", debate_file["periodID"])
                continue

            if not speeches:
                continue

            speech_file_path = f"{Data.speeches_files_dir}/TN/{idx}om{datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%f')}.json"
            Data.save_json(speech_file_path, speeches)

            all_debates.append(
                {
                    "date": debate_file['date'],
                    "file_path": speech_file_path,
                    "debate_title": debate_file['debate_title'],
                    "country": Data.country2code['TN']
                }
            )

        csv_file_path = f"{Data.csv_files_dir}/debates/{datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%f')}.csv"
        pd.DataFrame(all_debates).to_csv(csv_file_path)
        os.remove(Data.processor_debates_dir + '/TN/' + file_path)


   


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

    def test_UK_split_members(self, file_path):
        # members = set()
        # speeches = defaultdict(str)  # format: {member_name: speech, member_name: speech}

        # the following list contains all speehes (larger than 5 words) in the same order.
        # it contains dicts of format {"name": member_name-str, "speech": member's speech}
        all_speeches_list = []


        # for file_path in files_path:
        curr_debate_speeches = {}
        rep_speakers = re.compile(r".+\n.+")
        rep_speech = re.compile(r".+")
        # r""

        with open(file_path, "r") as file:
            # lines = file.read().split('\n')
            lines = file.read()
            debate_title = lines.split("\n")[0].strip()

        # lines = ""
        # print(lines)
        matches = [match for match in rep_speakers.finditer(lines)] # put it in a list to use indexing
        speech_idx = 0
        for i in range(len(matches)):
            # print(f"\tspeech {i}")
            start, end = matches[i].start(), matches[i].end()
            match = lines[start:end]
            splitted_match = match.split("\n")
            speech_end_idx = matches[i+1].start() if i < (len(matches)-1) else len(lines)
            
            speaker = splitted_match[0].strip() # now speaker noctains name and party, position, etc. example: "Afzal Khan (Manchester, Gorton) (Lab)"
            speaker = self.__extract_uk_speaker_name(speaker)


            # note that match includes speaker name and his next first paragraph
            speech = lines[start+len(splitted_match[0]) : speech_end_idx]
            speech = " ".join(rep_speech.findall(speech))

            if len(speech) > 5:
                # speeches[speaker] += f"<{speech_idx}>{speech}"

                curr_speech = {
                    "name": speaker,
                    "speech": speech
                }
                all_speeches_list.append(curr_speech)
                speech_idx += 1

        return debate_title, all_speeches_list







    def UK_split_members(self, file_path):
        '''
        take debates text file and extract member name and speeches out of them
        :param file_path: path
        :return: debate_title: str, speeches: dict
        '''
        # files_path = os.listdir(txt_files_dir)

        members = set()
        speeches = {}  # format: {member_name: speech, member_name: speech}

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



    def __process_IL_files(self, files):
        """
        given files list related to a single plenum, extract all the debates data
        usually it is only one doc / docx file for each plenum
        :param files: list of format [file_type: str, file_path: str], this list is made by IL Collector
        :return: debates generator, for each file in plenum file return the debates it contains
        """
        for file_type, file_path in files:
            if file_type.lower() not in ["doc", "docx"]:
                print(f"debates processor (IL) cannot process file of type {file_type}, path: {file_path}")
                continue


            # convert word to text
            texts_lines = self.__word2text(file_path)

            # extract title and speeches from texts
            # tor files contains parts of debates so we deal with them differently
            if "_tor_" in file_path:
                debates = self.__parse_IL_TOR_plenum(texts_lines)
            else:
                debates = self.__parse_IL_plenum(texts_lines)

            yield debates


    def __init_wordApp(self):
        if self.word is None:
            # self.word = win32com.client.gencache.EnsureDispatch('Word.Application')
            self.word = win32com.client.dynamic.Dispatch('Word.Application')

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


    def __is_bold(self, paragraph):
        return paragraph.Range.Font.Bold != 0

    def __is_title(self, paragraph):
        return paragraph.Style.NameLocal.startswith("Heading")

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
            # if self.__is_title(p):
            #     tmp_txt = f"TT{tmp_txt}TT"
            if self.__is_paragraph_centered(p):
                if self.__is_bold(p):
                    tmp_txt = f"BB{tmp_txt}BB"
                if self.__is_underlined(p):
                    tmp_txt = f"UU{tmp_txt}UU"

                tmp_txt = f'**{tmp_txt}**'
            elif self.__is_underlined(p): # we check this only for MP speach
                tmp_txt = f"UU{tmp_txt}UU"

            if self.__filter_word_texts(tmp_txt):
                full_text.append(tmp_txt)
        lines = [t for t in full_text if len(t.strip()) > 0]
        doc.Close()
        # print(lines)
        return lines



    def __filter_word_texts(self, t):
        if (nlph.rep_title.search(t) is not None) and (nlph.rep_new_debate.search(t) is None): # any centered text that is not adebate title(not center underline bold)
            return False
        if (nlph.rep_new_debate.search(t) is not None) and (nlph.rep_bill_call.search(t.strip()) is not None):
            return False

        return True


    def __parse_IL_plenum(self, lines):
        """
        given lines of plenum doc file, extract all the debates speeches it contains
        :param lines: list of str lines (splitted by '\n')
        :return: dict of all debates from this files, format: [{debate_title: title, speeches: {speaker:speech, ...}, ...]
        """
        lines = '\n'.join(lines)
        # with open("curr_test666.txt", "a+") as f:
        #     f.write(lines)
        #     return
        matches = [match for match in nlph.rep_new_debate.finditer(lines)]
        plenum_started = False

        all_debates = []
        # curr_debate = defaultdict(dict)

        for i in range(len(matches)):
            start, end = matches[i].start(), matches[i].end()
            match = lines[start:end].strip()

            if plenum_started:

                if nlph.rep_title.search(
                        match):  # i know that this is always True but if the code works dont touch it XD

                    # check if match is new debate or table of contents or seder yom
                    if match.strip().strip("**").strip("UU").strip("BB") in nlph.re_bullshit_titles:
                        continue
                    else:  # if it is new debate
                        # get current debate title
                        curr_title = match.strip("**").strip("UU").strip("BB")
                        # if nlph.rep_first_two_bills.search(curr_title):
                        #     curr_title = lines[matches[i-1].start():matches[i-1].end()].strip()

                        if i != len(matches) - 1:
                            curr_debate_speeches = self.__get_IL_debate_speeches(lines, matches[i], matches[i + 1])
                        else: # last debate title in the docx file
                            curr_debate_speeches = self.__get_IL_debate_speeches(lines, matches[i], 0, last=True)

                        if len(curr_debate_speeches) < 2:
                            continue

                        curr_debate = {
                            "debate_title": curr_title.strip("**"),
                            "speeches": curr_debate_speeches
                        }

                        all_debates.append(curr_debate)
                else:
                    pass

                    # split it by '\n' and get speech of each member
            else:

                if nlph.rep_plenum_start.search(match):  # arrived to plenum intro title
                    print("plenum matched:", match)
                    plenum_started = True

        return all_debates


    def __get_IL_debate_speeches(self, all_text, idxs0, idxs1, last=False):
        """
        given indices of current and next debate, extract speeches of the current debate
        using regex
        :param all_text: all plenum file text
        :param idxs0: regex match index of curr debate
        :param idxs1: regex match index of next debate
        :return: dict of speeches, format {speaker: speech}
        """
        # print("getting speeches")
        if not last:
            lines = all_text[idxs0.end():idxs1.start()].strip()
        else:
            lines = all_text[idxs0.end()::].strip()
        all_speeches = defaultdict(str)
        all_speeches = []

        matches = [s for s in nlph.rep_is_speaker.finditer(lines)]

        for i in range(len(matches)):
            start, end = matches[i].start(), matches[i].end()
            speaker = lines[start:end].strip().strip('U')

            if i != len(matches) - 1:
                speech = lines[end:matches[i + 1].start()].strip()
            else:
                speech = lines[end:len(lines)].strip()

            if len(speech) > 5:
                # speeches[speaker] += f"<{speech_idx}>{speech}"

                curr_speech = {
                    "name": speaker,
                    "speech": speech
                }
                all_speeches.append(curr_speech)

        return all_speeches



    def load_pkl(self, file_path):
        with open(file_path, 'rb') as file:
            data = pickle.load(file)

        return data

    def __extract_uk_speaker_name(self, speaker):
        # rep_strings = re.compile(r"{\w\s}+")
        # reg_speaker = rep_strings.findall(speaker)
        if speaker in ["The Prime Minister", "Mr Speaker"]:
            return speaker

        doc = nlp(speaker)
        full_name = ""
        for ent in doc.ents:
            # print(ent, ent.label_)
            if ent.label_ == 'PERSON':
                full_name = ent.text
                break  # Assuming there is only one person entity in the text

        return full_name if full_name != "" else speaker


    def __TN_get_speeches2014(self, lines):
        """
        take text that conttains the full debate and return the speeches as list of dicts
        using regex.
        :param lines: text that includes the full debate with additional symbols like: BB, **.
        :return: list of dicts of format [{"name":name(str), "speech":speech(str)}]
        """
        person = re.compile("BB.+BB")
        centered = re.compile(r"\*\*.+\*\*")

        matches = [match for match in person.finditer(lines)] # include indices of MPs names
        all_speeches = [] # return later, format: [{"name":name(str), "speech":speech(str)}]

        # print(lines)
        for i in range(len(matches)):
            start, end = matches[i].start(), matches[i].end()
            match = lines[start:end].strip()

            match = match.strip("BB")
            if centered.search(match):
                continue

            if i < len(matches) -1:
                # print(len(lines), end, len(matches), i+1)
                speech = lines[end:matches[i + 1].start()].strip()
            else:
                speech = lines[end:len(lines)].strip()

            all_speeches.append(
                {
                    "name": match,
                    "speech": speech
                }
            )

        return all_speeches

    def __TN_get_speeches2019(self, data):
        """
        Function for 2019+ debates, get list of tuples that ordered according to
        the actual debate, and return it as the speeches format
        :param data: list of tuples of format [(name, party, speech)]
        :return: list of dicts of format [{"name":name(str), "speech":speech(str)}]
        """


        # return [{"name":name, "speech":speech} for name, party, speech in data]
        if len(data) == 0:
            return []
        res = []
        for bulk in data:
            if not bulk:
                continue
            try:
                res.extend([{"name": name, "speech": speech} for name, party, speech in bulk])
            except ValueError:
                continue
            # res.append({"name": name, "speech": speech})


            return res

    def __parse_IL_TOR_plenum(self, lines):
        lines = '\n'.join(lines)

        matches = [match for match in nlph.rep_new_debate.finditer(lines)]
        all_debates = []

        for i in range(len(matches)):
            start, end = matches[i].start(), matches[i].end()
            match = lines[start:end].strip()

            if nlph.rep_title.search(
                    match):  # i know that this is always True but if the code works dont touch it XD

                # check if match is new debate or table of contents or seder yom
                strippe_matchd = match.strip().strip("**").strip("UU").strip("BB")
                if strippe_matchd in nlph.re_bullshit_titles or strippe_matchd.startswith("הישיבה ה"):
                    continue
                else:  # if it is new debate
                    # get current debate title
                    curr_title = match.strip("**").strip("UU").strip("BB")
                    # if nlph.rep_first_two_bills.search(curr_title):
                    #     curr_title = lines[matches[i-1].start():matches[i-1].end()].strip()

                    if i != len(matches) - 1:
                        curr_debate_speeches = self.__get_IL_debate_speeches(lines, matches[i], matches[i + 1])
                    else: # last debate title in the docx file
                        curr_debate_speeches = self.__get_IL_debate_speeches(lines, matches[i], 0, last=True)

                    if len(curr_debate_speeches) < 2:
                        continue

                    curr_debate = {
                        "debate_title": curr_title.strip("**"),
                        "speeches": curr_debate_speeches
                    }

                    all_debates.append(curr_debate)
            else:
                continue

        return all_debates


    def UK_debate_members(self, debates_list):
        speeches_dir_path = Data.speeches_files_dir + "/UK"
        name2id = {}
        non_mp_members = set()

        # for csv_path in os.listdir(Data.csv_files_dir):
        #     df = pd.read_csv(csv_path)
        #     for row in df.itterrows():

        idx = 0 # used to save unique non_mp_members file name
        for file_path, debate_date in debates_list:
            self.members = pd.read_csv("Data/csv_files/members/UK_members_backup.csv")
            self.members['startDate'] = pd.to_datetime(self.members['startDate'])
            self.members['endDate'] = pd.to_datetime(self.members['endDate'])

            date = pd.to_datetime(debate_date)

            filtered_df = self.members[((self.members['startDate'] <= date) & (self.members['endDate'] >= date)) | ((self.members['startDate'] <= date) & (self.members['endDate'].isna()))]

            # TOOD: get period

            # debate_date = row["date"]
            # file_path = row["file_path"]
            print("\n\nfile path", file_path)
            unique_names = set()

            if not file_path.endswith(".json"):
                print("non json file detected by Abo Swaid:", file_path)
                continue

            speeches = Data.load_json(file_path)
            for speech in speeches:
                name = self.clean_UK_mp_name(speech["name"])

                if name is None:
                    speech["id"] = -1
                    non_mp_members.add(name)
                    continue

                name = self.__UK_get_real_name(name, unique_names)
                unique_names.add(name)
                # print(name)

                name_id = name2id.get((name, debate_date), self.__UK_get_name_id(name, debate_date, filtered_df))

                speech["id"] = name_id
                if name_id == -1:
                    non_mp_members.add(name)


            # overwrite the og json file path
            Data.save_json(file_path, speeches)

        # TODO: save the non_MP_members into json/pkl and then add it to uk_members.csv
        Data.save_pkl(non_mp_members, f"non_MP_members{idx}_{str(datetime.now()).replace(':', '-')}")
        idx += 1

        print("unique names:", unique_names)

    def clean_UK_mp_name(self, name):

        if name in ["Mr Speaker", "The Chair"]:
            return None

        contain_non_ascii = lambda s: len(s.encode('ascii', errors='ignore')) != len(s)

        ascii_name = []
        # clear non ascii chars
        for w in name.split():
            if not contain_non_ascii(w):
                ascii_name += [w]

        ascii_name = " ".join(ascii_name)
        # rep_mr = r'^\s*(MR\.?|MRS\.?|Dr\.?)\s+'

        rep_name = re.compile(r'\s*\(?((?:MR\.?|MRS\.?|MS\.?|Dr\.?)\s+)?((?:\w|-|\s)+)\)?', re.IGNORECASE)

        return rep_name.search(ascii_name).group(2)

    def __UK_get_real_name(self, name, names):
        if len(names) == 0 or name in names:
            return name.strip()

        name = name.split(" ")

        candidates = defaultdict(lambda: 0)

        # if len(name) == 1:
        for unique_name in names:
            for name_part in name:
                if name_part in unique_name.split():
                    candidates[unique_name] += 1

        if len(candidates) == 0:
            return " ".join(name).strip()

        return max(candidates, key=candidates.get).strip()


    def __UK_get_name_id(self, name, date, filtered_df):
        # if self.members is None:
        #     self.members = pd.read_csv("Data/csv_files/members/UK_members_backup.csv")
        #     self.members['startDate'] = pd.to_datetime(self.members['startDate'])
        #     self.members['endDate'] = pd.to_datetime(self.members['endDate'])
        #
        # date = pd.to_datetime(date)
        #
        # # filter by date
        # filtered_df =  self.members[( self.members['startDate'] <= date) & ( self.members['endDate'] >= date)]
        # print(filtered_df)
        filter_by_name = filtered_df[filtered_df["name"] == name]
        if len(filter_by_name) >= 1:
            return filter_by_name["member_id"].values[0]

        most_similar_name = process.extractOne(name, filtered_df['name'])
        print("sim", most_similar_name)
        if most_similar_name[1] < 90:
            return -1
        most_similar_row = filtered_df[filtered_df['name'] == most_similar_name[0]]

        most_similar_id = most_similar_row["member_id"].values[0] if len(most_similar_row) >= 1 else -1

        return most_similar_id

    def process_USA(self):
        DRIVER_PATH = r"C:\Users\Jiana\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"
        file_path = os.listdir(self.data_path + '/USA')

        if len(file_path) >= 1:
            data = Data.load_json(self.data_path + '/USA/' + file_path[0])
        else:
            print("No data to process")
            return

        start_idx = Data.get_progress()["USA_debates_processor_idx"]

        j = 0
        to_write = []
        counter = 0  # TODO save it somewhere
        for debate in data["results"][start_idx::]:
            date, title, country, speeches_file_path, members, speeches = "", "", 1, "", [], {}

            print(f"process {j+start_idx} from {len(data['results'])}")
            debate_id = counter
            counter += 1
            summary_link = debate['resultLink'] + "?api_key=21Q15esV5Oew1sJ9S8m9gKLaoMEe3rAYlMj4lRDn"
            try:
                summary_response = requests.get(summary_link)
            except Exception as e:
                print("blocked")
                time.sleep(60*15)
                pd.DataFrame(to_write, columns=["date", "debate_title", "country", "members", "file_path"]).to_csv(f"{Data.csv_files_dir}/debates/{file_path[0]}.csv")
                to_write = []
                summary_response = requests.get(summary_link)



            if summary_response.status_code == 200:
                summary_data = summary_response.json()
                if summary_data.get("members", False) and len(
                        summary_data["members"]) > 2:  # If at least there is two talking memberz
                    print("found deabate with 2")
                    details = summary_data[
                                  "detailsLink"] + "?api_key=21Q15esV5Oew1sJ9S8m9gKLaoMEe3rAYlMj4lRDn"

                    # options = Options()
                    # options.headless = True
                    # # block images and javascript requests
                    # # chrome_prefs = {
                    # #     "profile.default_content_setting_values": {
                    # #         "images": 2,
                    # #         "javascript": 2,
                    # #     }
                    # # }
                    # # options.experimental_options["prefs"] = chrome_prefs
                    # service = Service(executable_path=Data.chrome_driver_path)
                    # driver = webdriver.Chrome(options=options, service=service)
                    driver = self.init_driver()
                    print(details)
                    try:
                        driver.get(details)
                    except Exception as e:
                        print("ERRORED HERE: ", e)
                        driver.quit()
                        self.driver = None
                        continue
                    driver.implicitly_wait(2)
                    driver.refresh()
                    try:
                        driver.implicitly_wait(5)
                        print("done waiting")
                        element = driver.find_element(By.CSS_SELECTOR,
                            "#accMetadata > div:nth-child(11) > div.col-xs-12.col-sm-9 > p")
                        sub_type = element.text
                        driver.quit()
                        self.driver = None

                    except Exception as e:
                        print(e)
                        print("Element not found")
                        sub_type = None

                        # json_file_name = str(datetime.now()).replace(':', "-")
                        # with open(
                        #         fr'C:\Users\Jiana\OneDrive\Desktop\ParliamentMining\DataPipeline\Data\Failedlinksusa\{json_file_name}.json',
                        #         'w') as f:
                        #
                        #     json.dump(details, f)
                        #     continue

                    # TODO edit format to dict
                    if sub_type != "Honoring" and sub_type != "Celebrations" and sub_type != 'Recognitions':  # Not debates

                        date = summary_data["dateIssued"]

                        title = summary_data["title"]

                        record_link = summary_data["download"][
                                          "txtLink"] + "?api_key=21Q15esV5Oew1sJ9S8m9gKLaoMEe3rAYlMj4lRDn"
                        try:
                            txt_response = requests.get(record_link)
                        except:
                            print("Max retries exceeded with url:", record_link)
                            continue

                        # Check if the request was successful
                        if txt_response.status_code == 200:
                            # Parse the HTML content
                            soup = BeautifulSoup(txt_response.content, 'html.parser')
                            # Find and extract the text content
                            text_content = soup.get_text()
                        if text_content:
                            speeches = self.get_speech(text_content)  # this is generator

                            speeches = self.clean_speech(speeches)

                        members = summary_data[
                            "members"]  # example  'members': [{'role': 'SPEAKING',
                        # 'chamber': 'S',
                        # 'congress': '118',
                        # 'bioGuideId': 'S000033',
                        # 'memberName': 'Sanders, Bernard',
                        # 'state': 'VT',
                        # 'party': 'I'}]

                        members = self.get_members_USA(members)
                        country = 1
                        speeches_file_path = f"{Data.speeches_files_dir}/USA/{counter}_{file_path[0]}.json"
                        if speeches:
                            with open(speeches_file_path, 'a+') as json_file:
                                json.dump(speeches, json_file)
                            to_write.append(
                                [date, title, country, speeches_file_path,
                                 members])
                else:

                    counter -= 1
            else:
                print(summary_response.status_code)
                continue
            j += 1

        # exit driver, this line also exits all opened chrome instances
        os.system("taskkill /F /IM chrome.exe")
        self.driver = None

        csv_file_path = f"{Data.csv_files_dir}/debates/{file_path[0]}.csv"
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=["date", "debate_title", "country", "file_path", "members"])
            writer.writeheader()

            writer = csv.writer(csvfile)
            writer.writerows(to_write)

        if os.path.exists(self.data_path + '/USA/' + file_path[0]):
            os.remove(self.data_path + '/USA/' + file_path[0])


    def process_CA(self):

        file_path = os.listdir(self.data_path + '/CA')
        if len(file_path) >= 1:
            data = Data.load_json(self.data_path + '/CA/' + file_path[0])
        else:
            print("No data to process")
            return

        output = []
        out = {}
        i = 0
        members = set()
        for item in data:
            for debate in item:  # jalse w7de
                date = debate["date"]
                link = "https://api.openparliament.ca" + debate["url"]
                debate_data = CA_DataCollector.send_request(link)
                speeches = "https://api.openparliament.ca" + debate_data["related"]["speeches_url"]
                speeches = self.get_all(url=speeches)  # get all speeches for one jalse
                for x in speeches:  # all speeches in jalse w7de
                    for speech in x:  # all speeches in link wa7d
                        if speech.get("h1", None):
                            if speech["h1"]["en"] == "Government Orders":
                                speaker = self.get_member_CA(speech["politician_url"])
                                flag = speech.get("h2", "")
                                if flag:
                                    title = speech["h2"]["en"]
                                else:
                                    print(speech)
                                    title = ""
                                content = speech["content"]["en"]
                                content = re.sub(r'<[^>]*>|[\n\r]', '', content)
                                out[title] = out.get(title, [])
                                out[title].append(
                                    {"name": speaker, "speech": content})  # find for each debate ( title) the speeches
                # load to DB out( each item in out is debate) , members , date , counter
                # not out contains debates in jalse w7de ,  out is dict that has the
                # title of debate and all the speeches

                for title, speeches in out.items():
                    # print(speeches)
                    # print("stop")
                    for speech in speeches:
                        name = list(speech.keys())
                        if name[0] != "":
                            members.add(name[0])
                    speeches_file_path = f"{Data.speeches_files_dir}/CA/{str(datetime.now()).replace(':', '-')}_{file_path[0]}.json"
                    with open(speeches_file_path, 'a+') as json_file:
                        json.dump(speeches, json_file)
                    output.append([date, title, 4, members, speeches_file_path])
                    i += 1
                    out = {}
                    members = set()
        csv_file_path = f"{Data.csv_files_dir}/debates/{file_path[0]}_{str(datetime.now()).replace(':', '-')}.csv"
        # json_file_name = str(datetime.now()).replace(':', "-")
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=["date", "debate_title", "country", "members", "file_path"])
            writer.writeheader()

            writer = csv.writer(csvfile)
            writer.writerows(output)
        if os.path.exists(self.data_path + '/CA/' + file_path[0]):
            os.remove(self.data_path + '/CA/' + file_path[0])

        print("CSV file has been created successfully.")

    def get_member_CA(self, link):
        member_data = None
        if link:
            member_data = CA_DataCollector.send_request("https://api.openparliament.ca" + link)
        if member_data:
            return member_data["name"]
        return ""

    def get_all(self, url):
        all_data = []
        data = CA_DataCollector.send_request(url)
        curr_data = data["objects"]  # send curr in function to load data
        next_data = data["pagination"]["next_url"]
        all_data.append(curr_data)
        while True:
            if next_data:
                next_url = "https://api.openparliament.ca" + next_data
                new_data = CA_DataCollector.send_request(next_url)
                all_data.append(new_data["objects"])
                next_data = new_data["pagination"]["next_url"]
            else:
                break
        return all_data

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

    def get_speech(self, text):

        output = []

        # Correcting the regex pattern for speaker names
        SPEAKER_REGEX = re.compile(r"(?:^  +M[rs]\. [a-zA-Z-]+(?: |\.))|(?:^  +The [A-Z ]{2,}\.)", re.MULTILINE)
        current_speaker = None
        speech_start = None

        for m in re.finditer(SPEAKER_REGEX, text):
            name_start = m.start(0)
            name_end = m.end(0)

            if current_speaker is not None:
                speech_end = name_start
                output.append({"name": current_speaker, "speech": text[speech_start:speech_end].strip()})

            speech_start = name_end
            current_speaker = text[name_start:name_end].strip()[:-1]

        if current_speaker is not None:
            output.append({"name": current_speaker, "speech": text[speech_start:].strip()})

        return output

    def clean_speech(self, lst):
        new = []
        pattern = r'\[\[Page [SH]?\d*\]\]'

        for entry in lst:
            name = entry.get("name", "")
            text = entry.get("speech", "").replace("\n", "")
            text = re.sub(pattern, '', text)  # Remove page patterns
            text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
            text = re.sub(r"<[^>]*>", '', text)  # Remove HTML tags
            text = re.sub(r"_{2,}", ' ', text)  # Replace multiple underscores with a single space

            new.append({"name": name, "speech": text.strip()})  # Add cleaned entry to the new list

        return new

    def get_members_USA(self, members_lst):
        members = {}
        for i in members_lst:
            if i.get("memberName", None) and i.get("bioGuideId"):
                name = i["memberName"].replace(', ', ' ')
                members[i["bioGuideId"]] = name
            else:  # TODO sometimes output like this {'role': 'SPEAKING', 'chamber': 'H', 'congress': '111'}
                print(i)
        return members

if __name__ == "__main__":

    # fp1 = r"C:\Users\ayals\Downloads\Prime Minister 2024-03-13.txt"
    # fp2 = r"C:\Users\ayals\Downloads\Point of Order 2024-03-13.txt"
    x = Debates_DataProcessor(10)

    tester = [("Data/UK/usiness ofW2024-06-12 20-19-22.099870.json", "27/02/2020")]
    x.UK_debate_members(tester)
