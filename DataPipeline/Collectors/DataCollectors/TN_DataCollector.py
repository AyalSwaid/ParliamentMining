from Collectors.DataCollectors.DataCollector import DataCollector
import requests as reqs
from bs4 import BeautifulSoup as bs
# from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


class TN_DataCollector(DataCollector):

    url = 'https://majles.marsad.tn/ar/chronicles?periodId=1&page=10&paginationId=0&between=2014-12-02%20-%202019-11-11'


    def __init__(self, batch_size):
        super(TN_DataCollector, self).__init__(batch_size)
    
    
    def get_debates(self):
        '''
        make fast example to get one page debates data
        '''
        my_xpath = '/html/body/div[2]/section[2]/div/div/div/div/div/*'
        links = self.__get_links(self.url)
        res = reqs.get('https://majles.marsad.tn' + links[0])
        soup = bs(res.content, "html.parser")


        root = soup.find()
        return self.try_sel('https://majles.marsad.tn' + links[0])
        return None
        for child in childs:
            # print(child.attrib)
            # cc = [x.tag for x in child.xpath("./")]
            try:
                par_name = child.xpath('./*/a')
                print(par_name.text)
                print()
            except:
                pass
            # if child.text is not None:
            print(child.text)
            # if 'strong' in cc:
            #     print([x.text for x in child.xpath("./*/*")])
        return None

    def get_tag_hierarchy(self, element):
        """
        Recursively builds a hierarchical list of tags.
        """
        tag_hierarchy = [element.name]
        for child in element.children:
            if child.name:
                tag_hierarchy.append(self.get_tag_hierarchy(child))
        return tag_hierarchy


    def try_sel(self, link):
        print(link)
        opt = webdriver.ChromeOptions()
        opt.add_argument("--headless")

        driver = webdriver.Chrome(options=opt, executable_path=r'C:\Users\ayals\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe')

        driver.get(link)
        content = driver.find_elements(By.XPATH, '/html/body/div[2]/section[2]/div/div/div/div/div/blockquote/*')

        # [print(x.tag_name) for x in content]

        # iterate over tags and collect what each member said
        speeches = {}
        curr_member =  None
        speech = ''
        # i = -1

        names = []
        for i in range(len(content)):
            tag = content[i]
            is_tit = self.is_title(tag)

            if not is_tit:
                is_mem = self.is_member(tag)

                # 1st condition is to check that we got a new member so we want to store the last member speech
                # 2nd condition is to get the last speech
                if is_mem is not None or ((curr_member is not None) and self.is_final_title(tag, i, len(content))):
                    if curr_member is not None:
                        speeches[curr_member] = speeches.get(curr_member, '') + speech
                    curr_member = is_mem
                    speech = ""
                    if ((curr_member is not None) and self.is_final_title(tag, i, len(content))):
                        break
                    continue
                #
                speech += self.get_text(driver, tag)
        return speeches

    def get_text(self, driver, tag):
        return driver.execute_script("return arguments[0].textContent;", tag)
    def is_title(self, tag):
        '''
        check if tag is in the center (is a title)
        :param tag: selenium element
        :return: Bool
        '''
        return tag.get_attribute('style') == "text-align: center;"


    def is_member(self, tag):
        # if tag.text is not None:
        #     return None
        # print(tag.value_of_css_property('color'))
        try:
            name_tag = tag.find_element(By.XPATH, './/strong')
            # print(name_tag)


            a_tag_path = './/strong//a'
            a_tag = tag.find_elements(By.XPATH, a_tag_path)
            if len(a_tag) == 1:
                return a_tag[0].get_attribute('href').split('/')[-1].replace('__', ' ')
            return name_tag.text if name_tag.text != '' else None
        except NoSuchElementException:
            return None

    def is_final_title(self, tag, i, n_tags):
        '''
        check if this title is at the end of the page, not necessirly the last title
        becuz sometimes they out some additional info at the end
        :param tag: selenium tag
        :param i: curr tag iteration index
        :param n_tags: num of tags at the parent tag
        :return: boolean
        '''
        return self.is_title(tag) and (i > (n_tags/2))


    def get_votes(self):
        pass


    def get_members(self):
        pass


    def get_bills(self):
        pass


    def __get_links(self, url):
        resp = reqs.get(self.url)
        soup = bs(resp.content, 'html.parser')
        all_links = soup.find_all('a')
        links = [link.get('href') for link in all_links if link.get('href').startswith('/ar/event/')]
        # if link.get('href').startswith('/ar/event/')

        return links[::2]




if __name__ == "__main__":
    a = TN_DataCollector(50)
    x = a.get_debates()
    print(x)
    # [print(i) for i in x]
    # print(x)
    # print(len(x))
