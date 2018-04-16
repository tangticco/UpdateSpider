import bs4
import requests
import os
import time
from datetime import datetime



updateHistory = {}
apps = {}

#helper
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
	"""
	Call in a loop to create terminal progress bar
	@params:
		iteration   - Required  : current iteration (Int)
		total       - Required  : total iterations (Int)
		prefix      - Optional  : prefix string (Str)
		suffix      - Optional  : suffix string (Str)
		decimals    - Optional  : positive number of decimals in percent complete (Int)
		length      - Optional  : character length of bar (Int)
		fill        - Optional  : bar fill character (Str)
	"""
	percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
	filledLength = int(length * iteration // total)
	bar = fill * filledLength + '-' * (length - filledLength)
	print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
	# Print New Line on Complete
	if iteration == total:
		print()

#Scrape app store page for update dates
def scrapeDates(f):

	appf = open("appUrls.txt", "r")
	l = 7868
	printProgressBar(0, l, prefix = 'Initialize:', suffix = 'Complete', length = 50)
	for i, line in enumerate(appf):
		if i > -1: #a dirty shortcut since the file already has up to 4603
			appInfo = line.split(" XXXXXXXXXX ")
			appName = appInfo[0]
			appurl = appInfo[1]
			genre = "unknown"
			try:
				response = requests.get(appurl)
				page = bs4.BeautifulSoup(response.text, "html.parser")
				updates = {}
				count = 0

				for link in page.find_all('a'):
					if 'https://itunes.apple.com/us/genre' in link['href']:
						genre = link.string.extract()

				for verHist in page.find_all('li'):
					if(verHist['class'] == ['version-history__item']):
						version = verHist.contents[1].string
						date = verHist.contents[3].string
						if count == 0:
							updateHistory[appName] = date
							count+=1
						f.write(appName + " XXXXXXXXXX " + date + " XXXXXXXXXX " + genre + " \n")


			except requests.exceptions.RequestException as e:
				pass
		printProgressBar(i+1, l, prefix = 'Initialize:', suffix = 'Complete', length = 50)


	appf.close()


def constructupdateHistory():
	f = open("initial.txt", "r")
	for line in f:
		appInfo = line.split(" XXXXXXXXXX ")
		appName = appInfo[0]
		appdate = appInfo[1]

		if not appName in updateHistory:
			updateHistory[appName] = appdate

	f.close()



def checkUpdate(f):
	appf = open("appUrls.txt", "r")
	l = 7868
	printProgressBar(0, l, prefix = 'Update Progress:', suffix = 'Complete', length = 50)
	for i, line in enumerate(appf):
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
		printProgressBar(i+1, l, prefix = 'Update Progress:', suffix = 'Complete', length = 50)

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
	f= open("initial.txt","w+")
	scrapeDates(f)
	f.close()

	constructupdateHistory()

	print("Finish Initial Update History Construct")


	base = "updates"
	postfix = ".txt"
	count = 1
	fileName = base + str(count) + postfix
	f = open(fileName, "w")
	f.close()
	while True:
		statinfo = os.stat(fileName)
		size = statinfo.st_size
		if size > 1000000:
			count +=1
			fileName = base + str(count) + postfix
			f = open(fileName, "w")
			f.close()

		f = open(fileName, "w")
		checkUpdate(f)
		f.close()
		time.sleep(1200)
main()
