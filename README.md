# scrapy-reddit

This is a scrapy script that scrapes your saved, upvoated, ... posts. By default the script stores the results
in a xlsx file, but it can be easily changed to store them anywhere you want. For interacting with xlsx this program uses 
this library: https://github.com/jurgonaut/simple-python-xlsx.git. 

## Usage

- install requirements.txt
- first you must create an app in https://www.reddit.com/prefs/apps/
- add the client id and secret in settings.py
- add your reddit credentials in settings.py or with env variables
- run the command "scrapy crawl reddit" while inside the project
- check the results in path XLSX_PATH (settings.py)

## Extending the script

If you wish to do something else with the scraped items you can easily create a new middleware 
for the script, for more info on scrapy middleware check: https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
