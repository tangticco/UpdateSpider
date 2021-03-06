import bs4
import requests
import os
import time
import datetime

updateHistory = {}
appGenere = {}

############   Helpers   ###############


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

def compareDate(date1, date2):
	"""
	This method takes two dates in the format like Jul 2, 2015 and parse it into a datetime in order to compare them
	rtype: bool
	return: if date1 is later then date2 then return True, if not return false
	"""
	da1 = datetime.datetime.strptime(date1, "%b %d, %Y")
	da2 = datetime.datetime.strptime(date2, "%b %d, %Y")

	return True if da1 > da2 else False






############Old initialization functions and deprecated functions ##########

def constructupdateHistory():
	"""
	deprecated function
	"""
	f = open("initial.txt", "r")
	for line in f:
		appInfo = line.split(" XXXXXXXXXX ")
		appName = appInfo[0]
		appdate = appInfo[1]
		appGe = appInfo[2]
		#ensure that updateHistory contains the latest update
		if not appName in updateHistory:
			updateHistory[appName] = appdate
			appGenere[appName] = appGe
		else:
			if compareDate(appdate, updateHistory[appName]):
				updateHistory[appName] = appdate
	f.close()


def reconfigureAppUrls():
	"""
	part of the initialization process. Not used later
	"""

	constructupdateHistory()

	appf = open("appUrls.txt", "r")
	tempFile = open("appUrlsTemp.txt", "w")
	l = 7868
	printProgressBar(0, l, prefix = 'Reconfigure Update Progress:', suffix = 'Complete', length = 50)
	for i, line in enumerate(appf):
		appInfo = line.split(" XXXXXXXXXX ")
		appName = appInfo[0]
		appurl = appInfo[1].replace("\n", "")
		if appName in updateHistory:
			latestUpdate = updateHistory[appName]
			appGe = appGenere[appName]
			tempFile.write(appName + " || " + appurl + " || " + latestUpdate + " || " + appGe)
		else:
			try:
				response = requests.get(appurl)
				page = bs4.BeautifulSoup(response.text, "html.parser")
				updates = {}
				for verHist in page.find_all('li'):
					if(verHist['class'] == ['version-history__item']):
						version = verHist.contents[1].string
						date = verHist.contents[3].string

						if not appName in updateHistory:
							updateHistory[appName] = date
							appGenere[appName] = "unknown"
						else:
							if compareDate(date, updateHistory[appName]):
								updateHistory[appName] = appdate
			except requests.exceptions.RequestException as e:
				pass
		printProgressBar(i+1, l, prefix = 'Reconfigure Update Progress:', suffix = 'Complete', length = 50)

	appf.close()
	tempFile.close()

	os.system("mv appUrls.txt appUrls_backup.txt")
	os.system("mv appUrlsTemp.txt appUrls.txt")

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

def scrapeDates(f):
	"""
	The initialization function of the initial data
	"""
	appf = open("appUrls.txt", "r")
	l = 7868
	printProgressBar(0, l, prefix = 'Initialize:', suffix = 'Complete', length = 50)
	for i, line in enumerate(appf):
		if i > 6367:
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
