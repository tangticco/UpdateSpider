import bs4
import requests
import os
import time
from datetime import datetime



updateHistory = {}
apps = {}

#Scrape app store page for update dates
def scrapeDates(f):

	appf = open("appUrls.txt", "r")

	for line in appf:
		appInfo = line.split(" XXXXXXXXXX ")
		appName = appInfo[0]
		appurl = appInfo[1]

		try:
			response = requests.get(appurl)
			page = bs4.BeautifulSoup(response.text)
			updates = {}
			count = 0
			for verHist in page.find_all('li'):
				if(verHist['class'] == ['version-history__item']):
					version = verHist.contents[1].string
					date = verHist.contents[3].string

					if count == 0:
						updateHistory[appName] = date
						count+=1

					f.write(appName + " " + date + " \n")



		except requests.exceptions.RequestException as e:
			pass

	appf.close()



def checkUpdate(f):
	appf = open("appUrls.txt", "r")

	for line in appf:
		appInfo = line.split(" XXXXXXXXXX ")
		appName = appInfo[0]
		appurl = appInfo[1]

		try:
			response = requests.get(appurl)
			page = bs4.BeautifulSoup(response.text, "html.parser")
			updates = {}
			count = 0
			for verHist in page.find_all('li'):
				if(verHist['class'] == ['version-history__item']):
					version = verHist.contents[1].string
					date = verHist.contents[3].string

					if count == 0 and date != updateHistory[appName]: #there is a new update
						updateHistory[appName] = date
						count+=1
						f.write(appName + " " + date + " \n")
						break



		except requests.exceptions.RequestException as e:
			pass

	appf.close()


def constructAppUrls():
	"""
	This is a method to intially construct the app's urls
	"""
	aurl = "https://itunes.apple.com/us/genre/ios/id36?mt=8"
	try:
		response = requests.get(aurl)
		page = bs4.BeautifulSoup(response.text, "html.parser")

		categories = []
		for urlItem in page.find_all("a"):

			if "https://itunes.apple.com/us/genre/" in urlItem['href']:
				categories.append(urlItem['href'])


		f = open("appUrls.txt", "w")


		for url in categories:
			try:
				response = requests.get(url)
				page = bs4.BeautifulSoup(response.text, "html.parser")

				for urlItem in page.find_all('a'):
					if "https://itunes.apple.com/us/app/" in urlItem['href']:
						appName = urlItem.string.extract()
						appUrl = urlItem['href']
						if appName not in apps:
							apps[appName] = appUrl
							updateHistory[appUrl] = 0
							f.write(appName + " XXXXXXXXXX " + appUrl + "\n")



			except requests.exceptions.RequestException as e:
				pass

		f.close()
	except requests.exceptions.RequestException as e:
		pass


def main():

	#constructAppUrls()
	# f= open("initial.txt","w+")
	# scrapeDates(f)
	# f.close()


	base = "updates"
	postfix = ".txt"
	fileName = base + str(datetime.now()) + postfix
	f = open(fileName, "w")
	f.close()
	while True:
		statinfo = os.stat(fileName)
		size = statinfo.st_size

		if size > 5000000:
			fileName = base + str(datetime.now()) + postfix
			f = open(fileName, "w")
			f.close()

		f = open(fileName, "w")
		checkUpdate(f)
		f.close()
		time.sleep(1200)
main()
