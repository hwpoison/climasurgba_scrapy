import os
import requests
import threading
from threading import Thread

__author__ = 'hwpoison'

# Mini gestor de hilos
class ThreadPoolManager():
	def __init__(self):
		self.max_threads = False
		self.futures = []

	def addThread(self, name_, target_, args_):
		new_thread = Thread(name=name_, target=target_, args=args_)
		self.futures.append(new_thread)

	def checkActives(self):
		if actives:=threading.active_count() > 1:
			return actives
		else:
			return 0

	def startThreads(self):
		if not self.max_threads: 
			for thread in self.futures: #ejecuta todos los hilos disponibles
				thread.start()
		else:
			while self.futures: # mientras haya hilos por ejecutar
				if self.checkActives() < self.max_threads:  # si los hilos actuales son menores la maximo
					for nthread, thread in enumerate(self.futures): #iniciar los suficientes 
						self.futures.pop(nthread).start() # se extrae e inicializa

	def block(self):
		#while threading.active_count() > 1:
		while self.checkActives():
			# bloquea el hilo principal hasta que finalice todo
			pass
		return True

# Gestor de descargas multi hilo
class DownloadManager(ThreadPoolManager):
	def __init__(self, max_downloads=False):
		super().__init__()
		self.total_files = 0
		self.total_downloaded = 0
		self.omitteds = 0
		self.max_threads = max_downloads

	def downloadFile(self, link, location):
		if os.path.exists(location):
			#print(f"[!]{location} already exists!\n")
			self.total_files-=1
			self.omitteds+=1
			return False

		requestUrl = requests.get(link, stream=True)
		with open(location, 'wb') as f:
			for chunk in requestUrl.iter_content(1024):
				if chunk:
					f.write(chunk)
		self.total_downloaded+=1
		print(f'[+]{location} downloaded. {self.total_downloaded} of {self.total_files} ({self.omitteds} omitteds)')
		return True

	def addDownload(self, link, location):
		self.addThread("",  target_=self.downloadFile, args_=(link, location))
		self.total_files+=1

	def startDownloads(self):
		self.startThreads()

	def isDone(self):
		return self.block()