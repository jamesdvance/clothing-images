import re
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait	
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
import json
import pandas as pd
import datetime

from urllib.request import urlretrieve

def scrape_site(start_url):
	browser.webdriver.Firefox()
	browser.get(start_url)

def scrape_page(url):

	# Load page, click 'load more', reload page, until 'load more' isn't clickable
	# Can also try loading with page = 20
	# Get Items By XPath

	browser = webdriver.Firefox()
	browser.get(url)

	browser.wait = WebDriverWait(browser, 15)
	element = browser.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'product-info')))

	total_items_str = browser.find_element_by_xpath('/html/body/div[5]/div/div[3]/div/div[3]/div[2]/div[2]/div[2]/div').text

	total_items = int(total_items_str[0:3])

	titles = []
	prices = []
	urls = []
	image_urls = []
	image_refs = []

	def title_counter(num):
		if(num>1):
			return('['+str(num)+']')
		else:
			return("")

	def item_counter(num):
		if(num%60)==0:
			return(1)
		else:
			return num%60

	img_path = 'C:/Users/J/MatchMyLook/Image_Files/Women/Tops/handm'
	base_xpath = '/html/body/div[5]/div/div[3]/div/div[3]/div[2]/div[3]/'

	browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

	for i in range(1,(total_items+1)):

		item_cter = item_counter(i)
		pg_cter = int(i/60)+1
		title_ctr = title_counter(pg_cter)

		title = browser.find_element_by_xpath(base_xpath+'div'+title_ctr+'/div['+str(item_cter)+']/div/div[2]/div[1]').text
		titles.append(title)
		price = browser.find_element_by_xpath(base_xpath+'div['+str(pg_cter)+']/div['+str(item_cter)+']/div/div[2]/div[2]/span').text
		prices.append(price)
		url = browser.find_element_by_xpath(base_xpath+'div['+str(pg_cter)+']/div['+str(item_cter)+']/div/a').get_attribute('href')
		urls.append(url)
		img_url = browser.find_element_by_xpath(base_xpath+'div['+str(pg_cter)+']/div['+str(item_cter)+']/div/div[1]/img[1]').get_attribute('data-src')
		img_url = img_url.replace(" ","%20")
		img_url = "http:"+img_url.replace("amp;","")
		image_urls.append(img_url)
		urlretrieve(img_url, os.path.join(img_path, str(i)+'.jpg'))
		image_refs.append( os.path.join(img_path, str(i)+'.jpg'))

	return_df = pd.DataFrame({
		'Title':titles,
		'Price':prices,
		'Url':urls,
		'Image_Path':image_refs,},
		)

	return return_df

return_df = scrape_page('http://www.hm.com/us/products/ladies/tops?page=22')
return_df.to_csv("C:/Users/J/MatchMyLook/Scraping/Data/h_and_m_womens_tops.csv")