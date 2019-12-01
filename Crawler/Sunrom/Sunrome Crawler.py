# -*- coding: utf-8 -*-
"""
Author: Darp Raithatha
"""

# Importing the Necessary Libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from selenium import webdriver
from urllib.parse import urlparse
from urllib.parse import urljoin
import pandas as pd
import os
import sys
import time
import pickle

# Checking the URL
def is_absolute(url):    
    """Determine whether URL is absolute."""    
    return bool(urlparse(url).netloc)

# Initialization 
options = webdriver.ChromeOptions()
options.add_argument("headless")
driver = webdriver.Chrome(chrome_options=options)

# Taking the Visited Input
visited = []
#vis_in = open("visited.txt","rb")
#visited = pickle.load(vis_in)
#vis_in.close()

#Creating an Empty Data Frame
df = pd.DataFrame(columns = ['URL', 'Name', 'Description', 'Image_URL', 'Image_Name', 'Price'])
df = pd.read_csv("Sunrome.csv")

#Creating the Directory
try: 
    os.mkdir(os.getcwd()+"//" + "Images" )
    os.mkdir(os.getcwd()+"//" + "Images" + "//" + "2")
except:
    try:
        os.mkdir(os.getcwd()+"//" + "Images" + "//" + "2")
    except Exception as e:
        print (e)
        #continue

#Queue
q = set([])
#q_in = open("queue.txt","rb")
#q = pickle.load(q_in)
#q_in.close()
#q = set(q)

q.add("https://www.sunrom.com/p/rj10-rj9-4p4c-black-socket-for-telephone-headset")
q.add("https://www.sunrom.com/p/wifi-module---esp8266---esp-12f-4mb")
q.add("https://www.sunrom.com/p/audio-player-wav-format-micro-sd-card")
q.add("https://www.sunrom.com/p/stm32f407vet6-m4-development-board")
q.add("https://www.sunrom.com/p/rj11-rj12-6p6c-gray-telephone-socket-for-landline")
q.add("https://www.sunrom.com/p/47uh-4r7-smd-7mm-inductor-28a")
q.add("https://www.sunrom.com/p/lm1117-18-sot223")
q.add("https://www.sunrom.com/p/tactile-switch-12x12x13mm")

z = 0
x = 0
while (len(q)>0):
    url = q.pop()
    if url not in visited:
        try:
            #print('Queue Size:', len(q))
            driver.get(url)  
            visited.append(url)
            
            # Extracting the Other Product Links
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            links = soup.find_all('a')
            #print(links)
            for link in links:
                u = link.get('href') 
                #print(u)
                if not is_absolute(u):            
                    u = urljoin(url, u)        
                if "sunrom.com" in u:
                    q.add(u)

            time.sleep(10)

            #Description
            if "sunrom.com/p" in url:
                print('Queue Size:', len(q))
                #soup = BeautifulSoup(driver.page_source, 'html.parser') 
                content = soup.find_all('p')
                #print(content)
                if (len(content)>0):
                    x += 1 
                    description = str(content[0].get_text()).strip()

                    #Title
                    title = soup.find_all('h1')
                    Title = str(title[0].string)

                    #Extracting Image URL's
                    i = 0
                    images = driver.find_elements_by_tag_name('img')
                    for image in images:
                        if i ==2:
                            image_url = image.get_attribute('src')
                            image_name = str(image_url[-12:-4]) + r'.jpg'
                            #print(image_url)
                            #print(image_name)
                            break;
                        i +=1

                    # Price
                    try:
                        price = soup.find_all('span')
                        for p in price:
                            if 'Rs.' in str(p.string):
                                price = str(p.string)
                                break;
                        #price = price.split(' ')
                        price = '$' + str(round(int(''.join(filter(str.isdigit, price)))/72, 2))
                    except:
                        try:
                            price = soup.find_all('div')
                            for p in price:
                                if 'Rs.' in str(p.string):
                                    price = str(p.string)
                                    break;
                            price = price.split(' ')
                            price = '$' + str(round(int(''.join(filter(str.isdigit, price[0])))/72, 2))
                        except:
                            price = '-'
                        #print(price)

                    # Appending the Data to the DataFrame
                    df= df.append({'URL': url, 'Name': Title, 'Description': description, 'Image_URL': image_url, 'Image_Name': image_name, 'Price': price}, ignore_index=True)
                    
                    # Saving an Image
                    #path = os.getcwd() + "//" + "Images" + "//" + "2//" + str(image_url[-12:-4]) + r'.jpg'
                    #driver.get(image_url)
                    #driver.get_screenshot_as_file(path)
                
        
        except KeyboardInterrupt:
            #Saving the DataFrame
            df.to_csv('Sunrome.csv', index = False)
            
            # Saving the Visited
            vis = open("visited.txt","wb")
            pickle.dump(visited, vis)
            vis.close()
                    
            # Saving the Queue
            que = open("queue.txt","wb")
            pickle.dump(q, que)
            que.close()
            print('KeyboardInterrupt')
            break;
            #pass
        
        except:
            continue

#Saving the DataFrame 
df.to_csv('Sunrome.csv', index = False)

# Saving the Visited
vis = open("visited.txt","wb")
pickle.dump(visited, vis)
vis.close()
        
# Saving the Queue
que = open("queue.txt","wb")
pickle.dump(q, que)
que.close()
