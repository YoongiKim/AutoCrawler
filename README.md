# AutoCrawler
Google, Naver multiprocess image crawler (High Quality & Speed & Customizable)

![](docs/animation.gif)

# How to use

1. Install Chrome

2. pip install -r requirements.txt

3. Write search keywords in keywords.txt

4. **Run "main.py"**

5. Files will be downloaded to 'download' directory.


# Arguments
usage:
```
python3 main.py [--skip true] [--threads 4] [--google true] [--naver true] [--full false] [--face false] [--no_gui auto] [--limit 0]
```

```
--skip true        Skips keyword if downloaded directory already exists. This is needed when re-downloading.

--threads 4        Number of threads to download.

--google true      Download from google.com (boolean)

--naver true       Download from naver.com (boolean)

--full false       Download full resolution image instead of thumbnails (slow)

--face false       Face search mode

--no_gui auto      No GUI mode. (headless mode) Acceleration for full_resolution mode, but unstable on thumbnail mode.
                   Default: "auto" - false if full=false, true if full=true
                   (can be used for docker linux system)
                   
--limit 0          Maximum count of images to download per site. (0: infinite)
--proxy-list ''    The comma separated proxy list like: "socks://127.0.0.1:1080,http://127.0.0.1:1081".
                   Every thread will randomly choose one from the list.
```


# Full Resolution Mode

You can download full resolution image of JPG, GIF, PNG files by specifying --full true

![](docs/full.gif)



# Data Imbalance Detection

Detects data imbalance based on number of files.

When crawling ends, the message show you what directory has under 50% of average files.

I recommend you to remove those directories and re-download.


# Remote crawling through SSH on your server

```
sudo apt-get install xvfb <- This is virtual display

sudo apt-get install screen <- This will allow you to close SSH terminal while running.

screen -S s1

Xvfb :99 -ac & DISPLAY=:99 python3 main.py
```

# Customize

You can make your own crawler by changing collect_links.py

# How to fix issues

As google site consistently changes, you may need to fix ```collect_links.py```

1. Go to google image. [https://www.google.com/search?q=dog&source=lnms&tbm=isch](https://www.google.com/search?q=dog&source=lnms&tbm=isch)
2. Open devloper tools on Chrome. (CTRL+SHIFT+I, CMD+OPTION+I)
3. Designate an image to capture.
![CleanShot 2023-10-24 at 17 59 57@2x](https://github.com/YoongiKim/AutoCrawler/assets/38288705/6488d6df-1f01-4dfd-8691-6c0ac142fc04)
4. Checkout collect_links.py
![CleanShot 2023-10-24 at 18 02 35@2x](https://github.com/YoongiKim/AutoCrawler/assets/38288705/097c6c03-dd43-45d4-939e-2f677f595362)
5. Docs for XPATH usage: [https://www.w3schools.com/xml/xpath_syntax.asp](https://www.w3schools.com/xml/xpath_syntax.asp)
6. You can test XPATH using CTRL+F on your chrome developer tools.
![CleanShot 2023-10-24 at 18 05 14@2x](https://github.com/YoongiKim/AutoCrawler/assets/38288705/7ce2601f-9d53-48ff-a1cf-1a2befcc510f)
7. You need to find logic to crawling to work.

