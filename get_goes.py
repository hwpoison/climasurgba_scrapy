import os
import re
import time
import argparse
from calendar import monthrange


import imageio
import requests
from PIL import Image
from bs4 import BeautifulSoup
from utils import DownloadManager

__author__ = "hwpoison"
__description__ = """
Obtener imagenes en infrarrojos del satelite metereologico GOES-16 \
haciendo scrapping al sitio climasurgba.com.ar
"""

URL_BASE = "https://climasurgba.com.ar"
URI_HISTORIAL = "/satelite/goes-topes-nubosos/historial/" 
ACTUAL_DATE = time.strftime("%Y/%m/%d")

def scrapImages(date): # YYYY/M/D	
	images = {}
	url = URL_BASE + URI_HISTORIAL + date
	print('[+]Scraping images from:', url)
	html = BeautifulSoup(requests.get(url).text, 'html.parser')
	for link in html.find_all(href=re.compile("satelite/historial")):
		if image_link:=link.get('href'):
			images[link.text] = image_link
	if not images:
		print("[x]Not found.")
		return False

	return date, images

def getFullMonth(month, year=2021):
	month_images = {}
	num_days = range(1, monthrange(year, month)[1]+1)
	print('[+]Collecting images...')
	for day in num_days:
		day_imgs = scrapImages(f'{year}/{month}/{day}')[1]
		day_imgs = { f'{day}_{hour}':day_imgs[hour] for hour in day_imgs }
		month_images.update(day_imgs)

	folder_name = f'month_{month}_{year}'
	downloadImages((folder_name, month_images), download_limit=4)
	makeAnimation(folder_name, fps=30)

def getDayImage(date=ACTUAL_DATE):
	print('[+]Getting images of the actual day.')
	images = scrapImages(date)
	if images:
		print('[+]Preparing for download.')
		download = downloadImages(images)
		print('[+]Generating animation.')
		animation = makeAnimation(date, fps=12);
		print("[+]Finished.")
		return True
	else:
		print("[x]Error to download! (No data found?).")
		return False

def downloadImages(images, folder_name=None, download_limit=None):
	date = images[0]
	images = images[1]
	total_images = len(images)

	if not folder_name:
		folder_name = date.replace('/', '-')
		if not os.path.exists(folder_name):
			os.mkdir(folder_name)

	download_manager = DownloadManager(max_downloads=download_limit)	

	for hour in images:
		download_url = URL_BASE + images[hour]
		file_name = hour.replace(':','-')
		full_path = f"{folder_name}/{file_name}.jpg"

		download_manager.addDownload(download_url, full_path)

	download_manager.startDownloads()
	print(f'[+]{download_manager.total_files} images added to download.')
	print('[+]Download started, waiting.')
	download_manager.isDone()
	print('[+]Finished.')
	return True

def makeAnimation(folder, resolution=(594, 824), format='mp4', fps=15):
	folder = folder.replace('/', '-')
	if not os.path.exists(folder):
		print('[-]Path does not exist')
	files = [f"{folder}/{file}" for file in os.listdir(folder)]
	images = []
	print('[+]Loading and preparing images.')
	for image_file in files:
		if image_file.endswith('.jpg'):
			try:
				images.append(Image.open(image_file).resize(resolution))
			except Exception as error:
				print('[x]Error to read ', image_file, error)
	imageio.mimwrite(f'{folder}/video.{format}', images, fps=fps)
	print('[+]Animation generated.')

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description=__description__)
	parser.add_argument('-t', '--today', help='Obtener y descargar imagenes del día.', action='store_true')
	parser.add_argument('-a', '--animate', help='Generar animación de una carpeta especifica.', type=str, nargs=1)
	parser.add_argument('-d', '--download', help='Descargar las imagenes de un día en especifico (AÑO/MES/DÍA)', type=str, nargs=1)
	parser.add_argument('-m', '--month', help='Descarga las imagenes de un mes entero en especifico', type=int, nargs=1)
	args = parser.parse_args()

	if args.today:
		getDayImage()
	if args.animate:
		makeAnimation(args.animate[0])
	if args.download:
		getDayImage(date=args.download[0])
	if args.month:
		getFullMonth(month=args.month[0])
