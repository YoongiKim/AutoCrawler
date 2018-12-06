"""
Copyright 2018 YoongiKim

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""


import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementNotVisibleException
import platform


class CollectLinks:
    def __init__(self):
        executable = ''

        if platform.system() == 'Windows':
            print('Detected OS : Windows')
            executable = './chromedriver/chromedriver_win.exe'
        elif platform.system() == 'Linux':
            print('Detected OS : Linux')
            executable = './chromedriver/chromedriver_linux'
        elif platform.system() == 'Darwin':
            print('Detected OS : Darwin')
            executable = './chromedriver/chromedriver_mac'
        else:
            assert False, 'Unknown OS Type'

        self.browser = webdriver.Chrome(executable)

    def google(self, keyword):
        self.browser.get("https://www.google.com/search?q={}&source=lnms&tbm=isch".format(keyword))

        time.sleep(1)

        print('Scrolling down')

        elem = self.browser.find_element_by_tag_name("body")

        for i in range(60):
            elem.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.2)

        try:
            # btn_more = self.browser.find_element(By.XPATH, '//input[@value="결과 더보기"]')
            btn_more = self.browser.find_element(By.XPATH, '//input[@id="smb"]')
            btn_more.click()

            for i in range(60):
                elem.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.2)

        except ElementNotVisibleException:
            pass

        photo_grid_boxes = self.browser.find_elements(By.XPATH, '//div[@class="rg_bx rg_di rg_el ivg-i"]')

        print('Scraping links')

        links = []

        for box in photo_grid_boxes:
            imgs = box.find_elements(By.TAG_NAME, 'img')

            for img in imgs:
                src = img.get_attribute("src")
                if src[0] != 'd':
                    links.append(src)

        print('Collect links done. Site: {}, Keyword: {}, Total: {}'.format('google', keyword, len(links)))
        self.browser.close()

        return links

    def naver(self, keyword):
        self.browser.get("https://search.naver.com/search.naver?where=image&sm=tab_jum&query={}".format(keyword))

        time.sleep(1)

        print('Scrolling down')

        elem = self.browser.find_element_by_tag_name("body")

        for i in range(60):
            elem.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.2)

        try:
            btn_more = self.browser.find_element(By.XPATH, '//a[@class="btn_more _more"]')
            btn_more.click()

            for i in range(60):
                elem.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.2)

        except ElementNotVisibleException:
            pass

        photo_grid_boxes = self.browser.find_elements(By.XPATH, '//div[@class="photo_grid _box"]')

        print('Scraping links')

        links = []

        for box in photo_grid_boxes:
            imgs = box.find_elements(By.CLASS_NAME, '_img')

            for img in imgs:
                src = img.get_attribute("src")
                if src[0] != 'd':
                    links.append(src)

        print('Collect links done. Site: {}, Keyword: {}, Total: {}'.format('naver', keyword, len(links)))
        self.browser.close()

        return links

    def google_full(self, keyword):
        self.browser.get("https://www.google.com/search?q={}&source=lnms&tbm=isch".format(keyword))

        time.sleep(2)

        first_photo_grid_boxes = self.browser.find_element(By.XPATH, '//img[@class="rg_ic rg_i"]')
        print(first_photo_grid_boxes.get_attribute('id'))

        first_photo_grid_boxes.click()

        time.sleep(1)

        container = self.browser.find_element(By.XPATH, '//div[@class="irc_land irc_bg"]')
        print(container.get_attribute('id'))

        img = container.find_element_by_id("irc-mi")
        print(img.get_attribute('src'))

        next_button = container.find_element(By.XPATH, '//div[@class="WPyac" and @id="irc-rac"]')
        print(next_button.get_attribute('id'))
        next_button.click()

        input()

        # print('Scraping links')
        #
        # links = []
        #
        # for box in photo_grid_boxes:
        #     imgs = box.find_elements(By.TAG_NAME, 'img')
        #
        #     for img in imgs:
        #         src = img.get_attribute("src")
        #         if src[0] != 'd':
        #             links.append(src)
        #
        # print('Collect links done. Site: {}, Keyword: {}, Total: {}'.format('google', keyword, len(links)))
        self.browser.close()

        return links


if __name__ == '__main__':
    collect = CollectLinks()
    links = collect.google_full('python')
    print(links)
