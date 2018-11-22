# AutoCrawler
Google, Naver multiprocess image crawler

![](img/animation.gif)

# How to use

1. Install Chrome

2. Extract chromedriver.zip

3. Add PATH where you extracted chromedriver.

4. pip install -r requirements.txt

5. Write search keywords in keywords.txt

6. Run auto_crawler.py

7. Files will be downloaded to 'download' directory.


# Arguments
usage: python3 auto_crawler.py [--skip true] [--threads 4] [--google true] [--naver true]

--skip SKIP        Skips keyword already downloaded before. This is needed when re-downloading.

--threads THREADS  Number of threads to download.

--google GOOGLE    Download from google.com (boolean)

--naver NAVER      Download from naver.com (boolean)


# Integrity Checking

Detects data imblance based on number of files.

When crawling ends, the message show you what directory has under 50% of average files.
