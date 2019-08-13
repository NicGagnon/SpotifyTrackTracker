# Scrape spotify website and log top song per country

from bs4 import BeautifulSoup
import requests
from openpyxl import load_workbook
import pandas as pd

from os.path import expanduser

home = expanduser("~")
path = "{}/Documents/Practice/SpotifyTrackTracker/SpotifyCharts.xlsx".format(home)

URL_front = "https://spotifycharts.com/regional/"
URL_back = "/daily/latest"
page = requests.get(URL_front)
soup = BeautifulSoup(page.text, "html.parser")

#Collect initial information
countries_list = soup.find("div", {"data-type": "country"})
country_names = [name.text for name in countries_list.select("li")]
country_abrvs = [abrv.get("data-value") for abrv in countries_list.select("li")]
date = [name.text for name in soup.find("div", {"data-type": "date"}).select("li")][0].replace('/', '-')

book = load_workbook(path)
writer = pd.ExcelWriter(path, engine = 'openpyxl')
writer.book = book

master_df = pd.DataFrame()

for country in country_abrvs:
  print(country)

  # Get URL for each country and collect soup
  URL = URL_front + country + URL_back
  country_page = requests.get(URL)
  country_soup = BeautifulSoup(country_page.text, "html.parser")

  # check for invalid countries, and then scrape top ten songs
  if country_soup.find("div", {"class": "chart-error"}): continue
  song_chart = country_soup.find("table", {"class": "chart-table"})
  songs = [song.text.strip('\n').replace('\n', ' ') for song in
           song_chart.find_all("td", {"class": "chart-table-track"})][0:10]
  song_df = pd.DataFrame([country_names[country_abrvs.index(country)]] + songs).transpose()
  master_df = master_df.append(song_df, sort=False)

master_df.to_excel(writer, date, index=False)
writer.save()
writer.close()
