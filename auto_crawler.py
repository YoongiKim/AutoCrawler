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


import os
import requests
import shutil
from multiprocessing import Pool
import argparse
from collect_links import CollectLinks


class Sites:
    GOOGLE = 1
    NAVER = 2

    @staticmethod
    def get_text(code):
        if code == Sites.GOOGLE:
            return 'google'
        elif code == Sites.NAVER:
            return 'naver'


class AutoCrawler:
    def __init__(self, skip_already_exist=True, n_threads=4, do_google=True, do_naver=True, download_path='download'):
        """
        :param skip_already_exist: Skips keyword already downloaded before. This is needed when re-downloading.
        :param n_threads: Number of threads to download.
        :param do_google: Download from google.com (boolean)
        :param do_naver: Download from naver.com (boolean)
        """
        self.skip = skip_already_exist
        self.n_threads = n_threads
        self.do_google = do_google
        self.do_naver = do_naver
        self.download_path = download_path

        # If download_path doesn't exist -> make one
        if not os.path.exists('./{}'.format(self.download_path)):
            os.mkdir('./{}'.format(self.download_path))

    @staticmethod
    def all_dirs(path):
        paths = []
        for dir in os.listdir(path):
            if os.path.isdir(path + '/' + dir):
                paths.append(path + '/' + dir)

        return paths

    @staticmethod
    def all_files(path):
        paths = []
        for root, dirs, files in os.walk(path):
            for file in files:
                if os.path.isfile(path + '/' + file):
                    paths.append(path + '/' + file)

        return paths

    @staticmethod
    def make_dir(dirname):
        current_path = os.getcwd()
        path = os.path.join(current_path, dirname)
        if not os.path.exists(path):
            os.makedirs(path)

    @staticmethod
    def get_keywords(keywords_file='keywords.txt'):
        # read search keywords from file
        with open(keywords_file, 'r', encoding='utf-8-sig') as f:
            text = f.read()
            lines = text.split('\n')
            if '' in lines:
                lines.remove('')
            keywords = sorted(set(lines))

        print('{} keywords found: {}'.format(len(keywords), keywords))

        # re-save sorted keywords
        with open(keywords_file, 'w+', encoding='utf-8') as f:
            for keyword in keywords:
                f.write('{}\n'.format(keyword))

        return keywords

    def save_image_to_file(self, image, file_path):
        try:
            with open('{}'.format(file_path), 'wb') as file:
                shutil.copyfileobj(image.raw, file)
        except Exception as e:
            print('Save failed - {}'.format(e))

    def download_images(self, keyword, links, site_name):
        self.make_dir('{}/{}'.format(self.download_path, keyword))
        total = len(links)

        for index, link in enumerate(links):
            try:
                print('Downloading {} from {}: {} / {}'.format(keyword, site_name, index + 1, total))
                response = requests.get(link, stream=True)
                self.save_image_to_file(response, '{}/{}/{}_{}.jpg'.format(self.download_path, keyword, site_name, index))
                del response

            except Exception as e:
                print('Download failed - ', e)
                continue

    def download_from_site(self, keyword, site_code):
        site_name = Sites.get_text(site_code)
        collect = CollectLinks()  # initialize chrome driver

        try:
            dirname = '{}/{}'.format(self.download_path, keyword)

            if os.path.exists(os.path.join(os.getcwd(), dirname)) and self.skip:
                print('Skipping already existing directory {}'.format(dirname))
                return

            print('Collecting links... {} from {}'.format(keyword, site_name))

            if site_code == Sites.GOOGLE:
                links = collect.google(keyword)

            elif site_code == Sites.NAVER:
                links = collect.naver(keyword)

            else:
                print('Invalid Site Code')
                links = []

            print('Downloading images from collected links... {} from {}'.format(keyword, site_name))
            self.download_images(keyword, links, site_name)

            print('Done {} : {}'.format(site_name, keyword))

        except Exception as e:
            print('Exception {}:{} - {}'.format(site_name, keyword, e))

    def download(self, args):
        self.download_from_site(keyword=args[0], site_code=args[1])

    def do_crawling(self):
        keywords = self.get_keywords()

        tasks = []

        for keyword in keywords:
            if self.do_google:
                tasks.append([keyword, Sites.GOOGLE])

            if self.do_naver:
                tasks.append([keyword, Sites.NAVER])

        pool = Pool(self.n_threads)
        pool.map_async(self.download, tasks)
        pool.close()
        pool.join()
        print('pool join')

        self.imbalance_check()

        print('End Program')

    def imbalance_check(self):
        print('Data imbalance checking...')

        dict_num_files = {}

        for dir in self.all_dirs(self.download_path):
            n_files = len(self.all_files(dir))
            dict_num_files[dir] = n_files

        avg = 0
        for dir, n_files in dict_num_files.items():
            avg += n_files / len(dict_num_files)
            print('dir: {}, file_count: {}'.format(dir, n_files))

        dict_too_small = {}

        for dir, n_files in dict_num_files.items():
            if n_files < avg * 0.5:
                dict_too_small[dir] = n_files

        if len(dict_too_small) >= 1:
            for dir, n_files in dict_too_small.items():
                print('Data imbalance detected.')
                print('Below keywords have smaller than 50% of average file count.')
                print('I recommend you to remove these directories and re-download for that keyword.')
                print('_________________________________')
                print('Too small file count directories:')
                print('dir: {}, file_count: {}'.format(dir, n_files))

            print("Remove directories above? (y/n)")
            answer = input()

            if answer == 'y':
                # removing directories too small files
                print("Removing too small file count directories...")
                for dir, n_files in dict_too_small.items():
                    shutil.rmtree(dir)
                    print('Removed {}'.format(dir))

                print('Now re-run this program to re-download removed files. (with skip_already_exist=True)')
        else:
            print('Data imbalance not detected.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--skip', type=str, default='true',
                        help='Skips keyword already downloaded before. This is needed when re-downloading.')
    parser.add_argument('--threads', type=int, default=4, help='Number of threads to download.')
    parser.add_argument('--google', type=str, default='true', help='Download from google.com (boolean)')
    parser.add_argument('--naver', type=str, default='true', help='Download from naver.com (boolean)')
    args = parser.parse_args()

    _skip = False if str(args.skip).lower() == 'false' else True
    _threads = args.threads
    _google = False if str(args.google).lower() == 'false' else True
    _naver = False if str(args.naver).lower() == 'false' else True

    print('Options - skip:{}, threads:{}, google:{}, naver:{}'.format(_skip, _threads, _google, _naver))

    crawler = AutoCrawler(skip_already_exist=_skip, n_threads=_threads, do_google=_google, do_naver=_naver)
    crawler.do_crawling()
