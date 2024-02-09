import os
import re
import time
from datetime import date, datetime, timedelta
import argparse
from calendar import monthrange


import imageio
import requests
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from bs4 import BeautifulSoup

from utils import DownloadManager, default_headers

__author__ = "hwpoison"
__description__ = """
Obtener imagenes en infrarrojos del satelite metereologico GOES-16 \
haciendo scrapping al sitio climasurgba.com.ar
El formato de las fechas a especificar sigue el formato AÑO/MES/DÍA
"""

URL_BASE = "https://climasurgba.com.ar"
URI_HISTORIAL = "/satelite/goes-topes-nubosos/historial/" 
TODAY_DATE = datetime.now()
TODAY_DATE_STR = TODAY_DATE.strftime("%Y/%m/%d")
DEFAULT_FPS = 12
SIMUL_LIMIT = 25
DEFAULT_QUALITY = 9
CROP_VIDEO = False

if os.sys.platform == 'linux':
    FONT_DIR = '/usr/share/fonts/TTF/Inconsolata-Bold.ttf'
else:
    FONT_DIR = 'ariblk.ttf'

def parseDate(strdate):
    return strdate.replace('/', '_')\
                  .replace(':', '_')

def view_file(file_name):
    print("[+] Opening for view...")
    os.system(f'start {file_name}')

# get url images of a specific day
def getImageUrls(date): # YYYY/M/D   
    images = {}
    url = URL_BASE + URI_HISTORIAL + date
    print('[+]Scraping images from:', url)
    html = BeautifulSoup(requests.get(url, headers=default_headers).text, 'html.parser')
    for link in html.find_all(href=re.compile("satelite/historial")):
        if image_link:=link.get('href'):
            images[date + '_' + link.text] = image_link
    if not images:
        print("[x]Not found.")
        return False
    return date, images # returns date and images

def downloadImages(images, folder_name=None, simul_limit=False, delay=False):
    date, images = images[0], images[1]
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

# animate images from folder
def generateAnimation(folders, format='mp4', fps=DEFAULT_FPS, crop=False):
    folders = [parseDate(fname) for fname in folders]
    if not [os.path.exists(f) for f in folders]:
        print('[-]Path does not exist')
    image_files = []
    for folder in folders:
        paths = [f'{folder}/{file}' for file in os.listdir(folder)]
        image_files.extend(paths)
    image_files.sort()
    print('[+]Loading and preparing images.')
    animation_frames = []
    for image_file in image_files:
        if image_file.endswith('.jpg'):
            try:
                #load and resize images
                image_loaded = Image.open(image_file)
                 
                # Setting rectangle to cut an image (center)
                if crop:
                    left, right = 260, 1047
                    top, bottom = 568, 942
                    image_loaded = image_loaded.crop((left, top, right, bottom))
                else:
                    image_loaded = image_loaded.resize((1488, 2064))

                #load font
                font = ImageFont.truetype(FONT_DIR, 25)
                draw = ImageDraw.Draw(image_loaded)
                date_text = image_file.split('/')[-1].split('_')
                #draw text
                date_text = f'{date_text[2]}/{date_text[1]} {date_text[3]}:00hs'
                draw.rectangle(((0,0),(210, 40)), fill ="#000000", outline ="red") 
                draw.text((10,0), date_text, (255,255,255), font=font)
                #add 
                animation_frames.append(image_loaded)
            except Exception as error:
                print('[x]Error to read ', image_file, error)

    print(f'[+]{len(animation_frames)} frames.')
    animation_frames.extend([animation_frames[-1] for i in range(fps*3)]) # add pause at the end
    if crop:
        file_path = f'{folder}/video_cropped.{format}'
    else:
        file_path = f'{folder}/video.{format}'
    print('[+]Generating the animation, please wait...')
    imageio.mimwrite(file_path , animation_frames, fps=fps, quality=DEFAULT_QUALITY)
    print('[+]Animation generated in ', file_path)
    return file_path

# download and animate a day
def getAndAnimateDay(date=TODAY_DATE_STR , delay=False, crop=False):
    print('[+]Getting images of the actual day.')
    images = getImageUrls(date)
    if images:
        print('[+]Preparing for download.')
        download = downloadImages(images, simul_limit=SIMUL_LIMIT, delay=delay)
        print('[+]Downloaded, now generating animation.')
        animation = generateAnimation([date], fps=DEFAULT_FPS, crop=CROP_VIDEO);
        print("[+]Finished.")
        return animation
    else:
        print("[x]Error to download! (No data found?).")
        return False

# get images from a entire month
def getAndAnimateFullMonth(month, year=2021):
    month_images = {}
    num_days = range(1, monthrange(year, month)[1]+1)
    print('[+]Collecting images...')
    for day in num_days:
        day_imgs = getImageUrls(f'{year}/{month}/{day}')[1]
        day_imgs = { f'{day}_{hour}':day_imgs[hour] for hour in day_imgs }
        month_images.update(day_imgs)

    folder_name = f'month_{month}_{year}'
    downloadImages((folder_name, month_images), simul_limit=SIMUL_LIMIT, delay=30)
    generateAnimation(folder_name, fps=DEFAULT_FPS)

def getAndAnimateFromYesterday():
    images = {}
    # get yesterday
    yesterday = TODAY_DATE - timedelta(days=1)
    yesterday_str = yesterday.strftime("%Y/%m/%d")
    images.update(getImageUrls(yesterday_str)[1])
    # get today  
    images.update(getImageUrls(TODAY_DATE_STR)[1])
    # download
    folder_name = yesterday_str+'_to_'+TODAY_DATE_STR
    downloadImages((folder_name, images), simul_limit=SIMUL_LIMIT)
    # animate
    animation_path = generateAnimation([folder_name], fps=DEFAULT_FPS)
    return animation_path

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('-t', '--today', help='Obtener y descargar imagenes del día.', action='store_true')
    parser.add_argument('-sy', '--sinceyesterday', help='Obtener y descargar imagenes Desde ayer hasta este momento.', action='store_true')
    parser.add_argument('-a', '--animate', help='Generar animación de una carpeta especifica. ex= --animate 2021-03-14,2021-03-15', type=str, nargs=1)
    parser.add_argument('-d', '--download', help='Descargar y anima las imagenes de un día en especifico (AÑO/MES/DÍA).', type=str, nargs=1)
    parser.add_argument('-m', '--month', help='Descarga y anima las imagenes de un mes entero en especifico.', type=int, nargs=1)
    parser.add_argument('--fps', help='Especificar los fps de la animación.', type=int, nargs=1)
    parser.add_argument('-v', '--visualize', help='Visualizar la animación luego de terminar de generarla.', action='store_true')
    parser.add_argument('-q', '--quality', help='Calidad de animación. (1-10 default=9)', type=int, nargs=1)
    parser.add_argument('-c', '--crop', help='Crop the image center', action='store_true')
    args = parser.parse_args()

    if args.fps:
        DEFAULT_FPS = args.fps[0]
    if args.crop:
        CROP_VIDEO = True
    if args.today:
        animation_path = getAndAnimateDay()
    if args.sinceyesterday:
        animation_path = getAndAnimateFromYesterday()
    if args.animate:
        animation_path = generateAnimation(args.animate[0].split(','), fps=DEFAULT_FPS)
    if args.quality:
        quality = args.quality[0]
    if args.download:
        getAndAnimateDay(date=args.download[0])
    if args.month:
        getAndAnimateFullMonth(month=args.month[0])
    if args.visualize:
        if animation_path:
            print('[+]Opening generated video.')
            view_file(animation_path)
    
    if not any(vars(args).values()):
        parser.print_help()