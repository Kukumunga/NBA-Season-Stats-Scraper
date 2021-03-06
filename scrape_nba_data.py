# -*- coding: utf-8 -*-
"""scrape_nba_data.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1YniFut7MVp6sdkXmO1sHD4l7pYEXCyIT

# Imports
"""

#imports required to get selenium to work on Colabs
!pip install selenium
!apt-get update # to update ubuntu to correctly run apt install
!apt install chromium-chromedriver
!cp /usr/lib/chromium-browser/chromedriver /usr/bin
import sys
sys.path.insert(0,'/usr/lib/chromium-browser/chromedriver')
from selenium import webdriver
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

"""# Selenium
Use selenium to to get page source. Cannot use requests as it is blocked for that method.
"""

# a driver for total and advanced stats
driver_total = webdriver.Chrome('chromedriver',chrome_options=chrome_options)
driver_adv = webdriver.Chrome('chromedriver',chrome_options=chrome_options)

# Use selenium to to get source for page 
# cannot use requests as it is blocked for that method
# array of html pages sources from Basketball-Reference
total_source = []
advanced_source = []
# start and end dates for required years
start_year = 2018
end_year = 2020
years = list(range(start_year,end_year+1))
for i in years:
  driver_total.get('https://www.basketball-reference.com/leagues/NBA_%s_totals.html' % (i)) 
  driver_adv.get('https://www.basketball-reference.com/leagues/NBA_%s_advanced.html' % (i))
  total_source.append(driver_total.page_source)
  advanced_source.append(driver_adv.page_source)
driver_total.close()
driver_adv.close()

"""# Beautiful Soup
Use bs to sort through the HTML as it is a faster interface to that of selenium
"""

from bs4 import BeautifulSoup
import numpy as np
import pandas as pd

# returns a pandas DataFrame with all players data from a page source
def nba_parse_data(page_source):
  soup = BeautifulSoup(page_source, 'html.parser')
  print(soup.title)
  table = soup.find_all("table")[0]
  tbody = table.find('tbody')
  tr = tbody.find_all('tr')
  dataset = []
  for player in tr:
    data1 = []
    for col in player.find_all('td'):
      data1.append(col.text)
    dataset.append(data1)
  return pd.DataFrame(data=dataset)

# creates the tables for each NBA Player Total Season Stats table
data_per = [] 
for season in total_source:
  df = nba_parse_data(season)
  df.columns = ['PLAYER',	'POS'	,'AGE',	'TEAM',	'G'	,'GS',	'MP',	'FG'	
                ,'FGA','FG%',	'3P'	,'3PA',	'3P%',	'2P',	'2PA'	,'2P%','eFG%'
                ,	'FT',	'FTA',	'FT%',	'ORB',	'DRB',	'TRB',	'AST',	'STL'
                ,	'BLK',	'TOV'	,'PF'	,'PTS']
  df = df.drop_duplicates()
  df = df.drop('MP',axis=1)
  data_per.append(df)

# creates the tables for each NBA Player Per Game Advanced Stats table
data_adv = [] 
for season in advanced_source:
  df = nba_parse_data(season)
  df.columns = ['PLAYER',	'POS'	,'AGE',	'TEAM',	'G',	'MP',	'PER',	'TS%'
  ,'3PAr','FTr',	'ORB%',	'DRB%',	'TRB%',	'AST%',	'STL%',	'BLK%',	'TOV%',	'USG%'
  ,	'blank1','OWS',	'DWS',	'WS',	'WS/48'	,'blank2','OBPM',	'DBPM',	'BPM',	'VORP']
  df = df.drop_duplicates()
  df = df.drop(['blank1','blank2'],axis=1)
  data_adv.append(df)

# Merges the Per Game and Advanced stats for each year
frames = []
for i in range(len(years)):
  adv = data_adv[i]
  per = data_per[i]
  table = pd.merge(adv,per,on=['PLAYER',	'POS',	'AGE',	'TEAM','G'])
  # insert a YEAR column
  table.insert(loc=1,column='YEAR',value=years[i])
  frames.append(table)

data = pd.concat(frames)
data = data.dropna()

# #save DATA to csv
data.to_csv('season_stats_2018-2020.csv')
# !cp vote_mvp.csv "drive/My Drive/"

data

