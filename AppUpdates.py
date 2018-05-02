import bs4
import requests
import os
import time
import datetime
import library



updateHistory = {}
appGenere = {}
apps = {}
month = {"Jan": 1, "Feb" : 2, "Mar": 3, "Apr" : 4, "May" : 5, "Jun" : 6, "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}


def checkUpdate(f):
	appf = open("appUrls.txt", "r")

	l = 7868

	# Start a new temp file to refresh the appUrls.txt
	tempFile = open("appUrlsTemp.txt", "w")


	# Start the checking update process
	library.printProgressBar(0, l, prefix = 'Check Update Progress:', suffix = 'Complete', length = 50)
	for i, line in enumerate(appf):

		#get the infos of an app
		appInfo = line.split(" || ")
		appName = appInfo[0]
		appurl = appInfo[1]
		latestUpdate = appInfo[2]
		appGe = appInfo[3].replace("\n", "")

		#now search the web page to see if there is a new update
		try:
			response = requests.get(appurl)
			page = bs4.BeautifulSoup(response.text, "html.parser")
			does_appUrls_has_latest_update = True

			#search through all the version history to see if there is a new update (There is some chance that it will miss some update if several updates is head of the latest update on file)
			for verHist in page.find_all('li'):
				if(verHist['class'] == ['version-history__item']):
					version = verHist.contents[1].string
					date = verHist.contents[3].string
					if library.compareDate(date, latestUpdate): #there is a new update
						updateHistory[appName] = date
						f.write(appName + " || " + date + " || " + appGe + " \n")

						#write the newest update to the tempfile
						tempFile.write(appName + " || " + appurl + " || " + latestUpdate + " || " + appGe)
						does_appUrls_has_latest_update = False
					break

			if does_appUrls_has_latest_update:
				tempFile.write(appName + " || " + appurl + " || " + latestUpdate + " || " + appGe)

		except requests.exceptions.RequestException as e:
			pass
		library.printProgressBar(i+1, l, prefix = 'Check Update Progress:', suffix = 'Complete', length = 50)

	appf.close()
	tempFile.close()

	lineCount = os.popen("wc -l appUrlsTemp.txt").read()
	if not "7793" in lineCount:
		print(lineCount)
	else:
		os.system("mv appUrls.txt appUrls_backup.txt")
		os.system("mv appUrlsTemp.txt appUrls.txt")



def main():

	########### The initialization part##########
	# #constructAppUrls()
	# f= open("initial.txt","a")
	# scrapeDates(f)
	# f.close()
	#library.reconfigureAppUrls()

	########### Actual Update starts #############
	base = "updates"
	postfix = ".txt"
	count = 1
	fileName = base + str(count) + postfix
	f = open(fileName, "w")
	f.close()

	while True:

		#check if the file size is too large, if yes, then create a new file
		statinfo = os.stat(fileName)
		size = statinfo.st_size
		if size > 1000000:
			count +=1
			fileName = base + str(count) + postfix
			f = open(fileName, "w")
			f.close()

		#open the file to write updates, the write method is append. (avoid overwrite existing data)
		f = open(fileName, "a")
		checkUpdate(f)
		f.close()
		for i in range(43200):
			library.printProgressBar(i+1, 43200, prefix = 'Waiting for next update:', suffix = 'Time to check!', length = 50)
			time.sleep(1)
main()
