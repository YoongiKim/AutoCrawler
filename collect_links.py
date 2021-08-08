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
from selenium.common.exceptions import ElementNotVisibleException, StaleElementReferenceException
import platform
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os.path as osp


class CollectLinks:
    def __init__(self, no_gui=False, proxy=None):
        executable = ''

        if platform.system() == 'Windows':
            print('Detected OS : Windows')
            executable = './chromedriver/chromedriver_win.exe'
        elif platform.system() == 'Linux':
            print('Detected OS : Linux')
            executable = './chromedriver/chromedriver_linux'
        elif platform.system() == 'Darwin':
            print('Detected OS : Mac')
            executable = './chromedriver/chromedriver_mac'
        else:
            raise OSError('Unknown OS Type')

        if not osp.exists(executable):
            raise FileNotFoundError('Chromedriver file should be placed at {}'.format(executable))

        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        if no_gui:
            chrome_options.add_argument('--headless')
        if proxy:
            chrome_options.add_argument("--proxy-server={}".format(proxy))
        self.browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)

        browser_version = 'Failed to detect version'
        chromedriver_version = 'Failed to detect version'
        major_version_different = False

        if 'browserVersion' in self.browser.capabilities:
            browser_version = str(self.browser.capabilities['browserVersion'])

        if 'chrome' in self.browser.capabilities:
            if 'chromedriverVersion' in self.browser.capabilities['chrome']:
                chromedriver_version = str(self.browser.capabilities['chrome']['chromedriverVersion']).split(' ')[0]

        if browser_version.split('.')[0] != chromedriver_version.split('.')[0]:
            major_version_different = True

        print('_________________________________')
        print('Current web-browser version:\t{}'.format(browser_version))
        print('Current chrome-driver version:\t{}'.format(chromedriver_version))
        if major_version_different:
            print('warning: Version different')
            print(
                'Download correct version at "http://chromedriver.chromium.org/downloads" and place in "./chromedriver"')
        print('_________________________________')

    def get_scroll(self):
        pos = self.browser.execute_script("return window.pageYOffset;")
        return pos

    def wait_and_click(self, xpath):
        #  Sometimes click fails unreasonably. So tries to click at all cost.
        try:
            w = WebDriverWait(self.browser, 15)
            elem = w.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            elem.click()
            self.highlight(elem)
        except Exception as e:
            print('Click time out - {}'.format(xpath))
            print('Refreshing browser...')
            self.browser.refresh()
            time.sleep(2)
            return self.wait_and_click(xpath)

        return elem

    def highlight(self, element):
        self.browser.execute_script("arguments[0].setAttribute('style', arguments[1]);", element,
                                    "background: yellow; border: 2px solid red;")

    @staticmethod
    def remove_duplicates(_list):
        return list(dict.fromkeys(_list))

    def google(self, keyword, add_url=""):
        self.browser.get("https://www.google.com/search?q={}&source=lnms&tbm=isch{}".format(keyword, add_url))

        time.sleep(1)

        print('Scrolling down')

        elem = self.browser.find_element_by_tag_name("body")

        for i in range(60):
            elem.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.2)

        try:
            # You may need to change this. Because google image changes rapidly.
            # btn_more = self.browser.find_element(By.XPATH, '//input[@value="결과 더보기"]')
            # self.wait_and_click('//input[@id="smb"]')
            self.wait_and_click('//input[@type="button"]')

            for i in range(60):
                elem.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.2)

        except ElementNotVisibleException:
            pass

        photo_grid_boxes = self.browser.find_elements(By.XPATH, '//div[@class="bRMDJf islir"]')

        print('Scraping links')

        links = []

        for box in photo_grid_boxes:
            try:
                imgs = box.find_elements(By.TAG_NAME, 'img')

                for img in imgs:
                    # self.highlight(img)
                    src = img.get_attribute("src")

                    # Google seems to preload 20 images as base64
                    if str(src).startswith('data:'):
                        src = img.get_attribute("data-iurl")
                    links.append(src)

            except Exception as e:
                print('[Exception occurred while collecting links from google] {}'.format(e))

        links = self.remove_duplicates(links)

        print('Collect links done. Site: {}, Keyword: {}, Total: {}'.format('google', keyword, len(links)))
        self.browser.close()

        return links

    def naver(self, keyword, add_url=""):
        self.browser.get(
            "https://search.naver.com/search.naver?where=image&sm=tab_jum&query={}{}".format(keyword, add_url))

        time.sleep(1)

        print('Scrolling down')

        elem = self.browser.find_element_by_tag_name("body")

        for i in range(60):
            elem.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.2)

        imgs = self.browser.find_elements(By.XPATH,
                                          '//div[@class="photo_bx api_ani_send _photoBox"]//img[@class="_image _listImage"]')

        print('Scraping links')

        links = []

        for img in imgs:
            try:
                src = img.get_attribute("src")
                if src[0] != 'd':
                    links.append(src)
            except Exception as e:
                print('[Exception occurred while collecting links from naver] {}'.format(e))

        links = self.remove_duplicates(links)

        print('Collect links done. Site: {}, Keyword: {}, Total: {}'.format('naver', keyword, len(links)))
        self.browser.close()

        return links

    def google_full(self, keyword, add_url=""):
        print('[Full Resolution Mode]')

        self.browser.get("https://www.google.com/search?q={}&tbm=isch{}".format(keyword, add_url))
        time.sleep(1)

        elem = self.browser.find_element_by_tag_name("body")

        print('Scraping links')

        self.wait_and_click('//div[@data-ri="0"]')
        time.sleep(1)

        links = []
        count = 1

        last_scroll = 0
        scroll_patience = 0

        while True:
            try:
                xpath = '//div[@id="islsp"]//div[@class="v4dQwb"]'
                div_box = self.browser.find_element(By.XPATH, xpath)
                self.highlight(div_box)

                xpath = '//img[@class="n3VNCb"]'
                img = div_box.find_element(By.XPATH, xpath)
                self.highlight(img)

                xpath = '//div[@class="k7O2sd"]'
                loading_bar = div_box.find_element(By.XPATH, xpath)

                # Wait for image to load. If not it will display base64 code.
                while str(loading_bar.get_attribute('style')) != 'display: none;':
                    time.sleep(0.1)

                src = img.get_attribute('src')

                if src is not None:
                    links.append(src)
                    print('%d: %s' % (count, src))
                    count += 1

            except StaleElementReferenceException:
                # print('[Expected Exception - StaleElementReferenceException]')
                pass
            except Exception as e:
                print('[Exception occurred while collecting links from google_full] {}'.format(e))

            scroll = self.get_scroll()
            if scroll == last_scroll:
                scroll_patience += 1
            else:
                scroll_patience = 0
                last_scroll = scroll

            if scroll_patience >= 30:
                break

            elem.send_keys(Keys.RIGHT)

        links = self.remove_duplicates(links)

        print('Collect links done. Site: {}, Keyword: {}, Total: {}'.format('google_full', keyword, len(links)))
        self.browser.close()

        return links

    def naver_full(self, keyword, add_url=""):
        print('[Full Resolution Mode]')

        self.browser.get(
            "https://search.naver.com/search.naver?where=image&sm=tab_jum&query={}{}".format(keyword, add_url))
        time.sleep(1)

        elem = self.browser.find_element_by_tag_name("body")

        print('Scraping links')

        self.wait_and_click('//div[@class="photo_bx api_ani_send _photoBox"]')
        time.sleep(1)

        links = []
        count = 1

        last_scroll = 0
        scroll_patience = 0

        while True:
            try:
                xpath = '//div[@class="image _imageBox"]/img[@class="_image"]'
                imgs = self.browser.find_elements(By.XPATH, xpath)

                for img in imgs:
                    self.highlight(img)
                    src = img.get_attribute('src')

                    if src not in links and src is not None:
                        links.append(src)
                        print('%d: %s' % (count, src))
                        count += 1

            except StaleElementReferenceException:
                # print('[Expected Exception - StaleElementReferenceException]')
                pass
            except Exception as e:
                print('[Exception occurred while collecting links from naver_full] {}'.format(e))

            scroll = self.get_scroll()
            if scroll == last_scroll:
                scroll_patience += 1
            else:
                scroll_patience = 0
                last_scroll = scroll

            if scroll_patience >= 100:
                break

            elem.send_keys(Keys.RIGHT)
            elem.send_keys(Keys.PAGE_DOWN)

        links = self.remove_duplicates(links)

        print('Collect links done. Site: {}, Keyword: {}, Total: {}'.format('naver_full', keyword, len(links)))
        self.browser.close()

        return links


if __name__ == '__main__':
    collect = CollectLinks()
    links = collect.naver_full('박보영')
    print(len(links), links)
