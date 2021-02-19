import os
import re
import time
import argparse
from calendar import monthrange


import imageio
import requests
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from bs4 import BeautifulSoup

from utils import DownloadManager

__author__ = "hwpoison"
__description__ = """
Obtener imagenes en infrarrojos del satelite metereologico GOES-16 \
haciendo scrapping al sitio climasurgba.com.ar
El formato de las fechas a especificar es del tipo AÑO/MES/DÍA
"""

URL_BASE = "https://climasurgba.com.ar"
URI_HISTORIAL = "/satelite/goes-topes-nubosos/historial/" 
ACTUAL_DATE = time.strftime("%Y/%m/%d")
DEFAULT_FPS = 12 # default fps

if os.sys.platform == 'linux':
    FONT_DIR = '/usr/share/fonts/TTF/Inconsolata-Bold.ttf'
else:
    FONT_DIR = 'ariblk.ttf'

def parseDate(strdate):
    return strdate.replace('/', '_')\
                  .replace(':', '_')

def scrapImages(date): # YYYY/M/D   
    images = {}
    url = URL_BASE + URI_HISTORIAL + date
    print('[+]Scraping images from:', url)
    html = BeautifulSoup(requests.get(url).text, 'html.parser')
    for link in html.find_all(href=re.compile("satelite/historial")):
        if image_link:=link.get('href'):
            images[date + '_' + link.text] = image_link
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
    downloadImages((folder_name, month_images), simul_limit=5, delay=30)
    makeAnimation(folder_name, fps=30)

def getDayImage(date=ACTUAL_DATE, delay=False):
    print('[+]Getting images of the actual day.')
    images = scrapImages(date)
    if images:
        print('[+]Preparing for download.')
        download = downloadImages(images, simul_limit=3, delay=delay)
        print('[+]Downloaded, now generating animation.')
        animation = makeAnimation([date], fps=DEFAULT_FPS);
        print("[+]Finished.")
        return True
    else:
        print("[x]Error to download! (No data found?).")
        return False

def downloadImages(images, folder_name=None, simul_limit=False, delay=False):
    date = images[0]
    images = images[1]
    pdate = parseDate(date)
    total_images = len(images)
    start = time.time()
    if not folder_name:
        folder_name = pdate 
        if not os.path.exists(folder_name):
            os.mkdir(folder_name)

    download_manager = DownloadManager(simul_limit=simul_limit, delay=delay)    

    for name in images:
        download_url = URL_BASE + images[name]
        file_name = parseDate(name)
        full_path = f"{folder_name}/{file_name}.jpg"
        download_manager.addDownload(download_url, full_path)

    print('[+]Download started, waiting.')
    print(f'[+]{download_manager.total_files} images founds.')
    download_manager.startDownloads()
    download_manager.isDone()
    print(f'[+]Finished in. {time.time()-start:.2f}')
    return True

def makeAnimation(folders, resolution=(608, 832), format='mp4', fps=DEFAULT_FPS):
    folders = [parseDate(fname) for fname in folders]
    if not [os.path.exists(f) for f in folders]:
        print('[-]Path does not exist')
    image_files = []
    for folder in folders:
        paths = [f'{folder}/{file}' for file in os.listdir(folder)]
        image_files.extend(paths)

    image_files.sort()
    print('[+]Loading and preparing images.')
    images = []

    for image_file in image_files:
        if image_file.endswith('.jpg'):
            try:
                #load images
                image_loaded = Image.open(image_file)
                image_loaded = image_loaded.resize(resolution)
                #load font
                font = ImageFont.truetype(FONT_DIR, 25)
                draw = ImageDraw.Draw(image_loaded)
                date_text = image_file.split('_')
                #draw
                date_text = f'{date_text[4]}/{date_text[1]} {date_text[5]}:00hs'
                draw.rectangle(((0,0),(175,40)), fill ="#000000", outline ="red") 
                draw.text((10,0), date_text, (255,255,255), font=font)
                #add 
                images.append(image_loaded)
            except Exception as error:
                print('[x]Error to read ', image_file, error)

    print(f'[+]{len(images)} frames.')
    images.extend([images[-1] for i in range(fps*3)]) # add pause at the end
    file_name = f'{folder}/video.{format}'
    imageio.mimwrite(file_name , images, fps=fps)
    print('[+]Animation generated in ', file_name)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('-t', '--today', help='Obtener y descargar imagenes del día.', action='store_true')
    parser.add_argument('-a', '--animate', help='Generar animación de una carpeta especifica. ex= --animate 2021-03-14,2021-03-15', type=str, nargs=1)
    parser.add_argument('-d', '--download', help='Descargar las imagenes de un día en especifico (AÑO/MES/DÍA).', type=str, nargs=1)
    parser.add_argument('-m', '--month', help='Descarga las imagenes de un mes entero en especifico.', type=int, nargs=1)
    parser.add_argument('--fps', help='Especificar los fps de la animación.', type=int, nargs=1)

    args = parser.parse_args()

    if args.fps:
        DEFAULT_FPS = args.fps[0]
    if args.today:
        getDayImage()
    if args.animate:
        makeAnimation(args.animate[0].split(','), fps=DEFAULT_FPS)
    if args.download:
        getDayImage(date=args.download[0])
    if args.month:
        getFullMonth(month=args.month[0])
