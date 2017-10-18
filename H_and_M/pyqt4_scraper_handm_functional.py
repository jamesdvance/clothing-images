import sys
from PyQt4.QtGui import * 
from PyQt4.QtCore import *
from PyQt4.QtWebKit import *
from urllib.request import urlretrieve
from urllib.error import URLError
import os
import re
from bs4 import BeautifulSoup #, SoupStrainer
import pandas as pd

img_path = 'C:/Users/J/MatchMyLook/Image_Files/Women/Tops/handm'
error_path = 'C:/Users/J/MatchMyLook/Scraping/Website_Scrapers/H_and_M/Bad_Urls'
data_path = 'C:/Users/J/MatchMyLook/Scraping/Data'

class Render(QWebPage):
	def __init__(self, url):
		self.app = QApplication(sys.argv) # from QTGUi package. Initializes a window system and constructs and application object with argv
		QWebPage.__init__(self)
		self.loadFinished.connect(self._loadFinished)
		self.mainFrame().load(QUrl(url))
		self.app.exec() 

	def _loadFinished(self, result):  
	    self.frame = self.mainFrame()  
	    self.app.quit()

# Render Page
def load_H_and_M(url_str):
	url = Render(url_str)
	html = url.frame.toHtml()
	bsjObj = BeautifulSoup(html, 'html.parser')
	return bsjObj

# Get Info,  Urls, Images HTML
def get_info_urls_images(bsjObj):
	product_info_html = bsjObj.findAll("", {"class":"product-info"})
	product_urls_html = bsjObj.findAll("",{"class":re.compile(r'product-url')})
	product_images_html = bsjObj.findAll("", {"class":re.compile(r'prio-one-image')})
	print(len(product_info_html))
	print(len(product_urls_html))
	print(len(product_images_html))
	return product_info_html, product_urls_html, product_images_html

def download_images(product_images_html, image_paths, img_path,error_path,iter):
	i = iter
	for image in product_images_html:
		try:
			img_url = image['data-src']
			i +=1
			img_url = img_url.replace(" ","%20")
			img_url = "http:"+img_url.replace("amp;","")
			try:
				urlretrieve(img_url, os.path.join(img_path, str(i)+'.jpg'))
				full_path = os.path.join(img_path, str(i)+'.jpg')
				image_paths.append(full_path)
			except URLError:
				file1 = open(os.path.join(error_path, str(i)+'.txt'),'w')
				bad_path = os.path.join(error_path, str(i)+'.txt')
				file1.write(img_url)
				image_paths.append(bad_path)
		except:
			print("skipped")
	return image_paths

def download_titles(product_info_html, titles):
	for info in product_info_html:
		product_titles = info.findAll("div",{ "class":"product-title"})
		for title in product_titles:
			titles.append(title.text)
	return titles

def download_prices(product_info_html, prices):
	for info in product_info_html:
		product_prices = info.findAll("span", {"class":"price"})
		for price in product_prices:
			prices.append(price.text)
	return prices

def download_urls(product_urls_html, urls):
	for url_iter in product_urls_html:
		urls.append(url_iter['href'])
	return urls

def process_single_page(bsjObj, img_path_str, error_path_str, iteration):
	img_path = img_path_str
	error_path = error_path_str

	titles = []
	prices = []
	urls = []
	image_paths = []

	product_info_html, product_urls_html, product_images_html = get_info_urls_images(bsjObj)
	image_paths = download_images(product_images_html, image_paths, img_path, error_path, iteration)
	titles = download_titles(product_info_html, titles)
	prices = download_prices(product_info_html, prices)
	urls = download_urls(product_urls_html, urls)
	return_df = pd.DataFrame({
		'Title':titles,
		'Price':prices,
		'Url':urls,
		'Image_Path':image_paths,},
		)
	return return_df

def scrape_full_site(img_path_str, error_path_str, csv_path):
	full_df = pd.DataFrame()
	url_str = 'http://www.hm.com/us/products/ladies/tops'
	bsjObj = load_H_and_M(url_str)
	df = process_single_page(bsjObj, img_path_str, error_path_str,0)
	full_df.append(df)
	product_counter_html = bsjObj.findAll("div", {"class":re.compile(r'sort-counter-text')})
	total_products = int(product_counter_html[0].text[0:3])
	pages = total_products/60
	iteration = 60
	for i in range(2,(int(pages)+2)):
		iteration = iteration*(i-1)
		url_str = 'http://www.hm.com/us/products/ladies/tops?page='+str(i)
		bsjObj = load_H_and_M(url_str)
		df = process_single_page(bsjObj, img_path_str, error_path_str,iteration)
		full_df.append(df)
			
	full_df.to_csv(csv_path)

scrape_full_site(img_path, error_path,data_path)