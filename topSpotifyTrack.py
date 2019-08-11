#Scrape spotify website and log top song per country 

from bs4 import BeautifulSoup
import requests
import xlsxwriter
import xlrd

from os.path import expanduser
home = expanduser("~")

URL_front = "https://spotifycharts.com/regional/"
URL_back = "/daily/latest"
page = requests.get(URL_front)
soup = 	BeautifulSoup(page.text, "html.parser")

countries_list = soup.find("div", {"data-type": "country"})
country_names = [name.text for name in countries_list.select("li")]
country_abrvs = [abrv.get("data-value") for abrv in countries_list.select("li")]
date = [name.text for name in soup.find("div", {"data-type": "date"}).select("li")][0].replace('/', '-')


# open the file for reading
wbRD = xlrd.open_workbook("{}/Documents/Practice/SpotifyTrackTracker/SpotifyCharts.xlsx".format(home))
sheets = wbRD.sheets()

## Extracting Top Songs from each country
workbook = xlsxwriter.Workbook("{}/Documents/Practice/SpotifyTrackTracker/SpotifyCharts.xlsx".format(home))

# run through the sheets and store sheets in workbook
# this still doesn't write to the file yet
for sheet in sheets: # write data from old file
    newSheet = workbook.add_worksheet(sheet.name)
    for row in range(sheet.nrows):
        for col in range(sheet.ncols):
            newSheet.write(row, col, sheet.cell(row, col).value)

## Write New Data
worksheet = workbook.add_worksheet(date)
bold = workbook.add_format({'bold': True})
row, column = 0, 0
worksheet.write(row, column, "Rank\\Country", bold)
for rank in range(1, 11):
	row += 1
	worksheet.write(row, column, rank, bold)
column += 1

for country in country_abrvs:
	print(country)

	#Get URL for each country and collect soup
	URL = URL_front + country + URL_back
	country_page = requests.get(URL)
	country_soup = BeautifulSoup(country_page.text, "html.parser")

	#check for invalid countries, and then scrape top ten songs
	if country_soup.find("div", {"class": "chart-error"}) : continue
	song_chart = country_soup.find("table", {"class":"chart-table"})
	songs = [song.text.strip('\n').replace('\n', ' ') for song in song_chart.find_all("td", {"class":"chart-table-track"})][0:10]
	
	#write songs to sheet
	row = 0
	worksheet.write(row, column, country_names[country_abrvs.index(country)])
	for song in songs:
		row += 1
		worksheet.write(row, column, song)
	column += 1  

workbook.close()




