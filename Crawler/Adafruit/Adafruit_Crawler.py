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

visited = []
#vis_in = open("visited.txt","rb")
#visited = pickle.load(vis_in)
#vis_in.close()


#Creating an Empty Data Frame
df = pd.DataFrame(columns = ['URL', 'Name', 'Description', 'Image_URL', 'Image_Name', 'Price'])

#Creating the Directory
try: 
    os.mkdir(os.getcwd()+"//" + "Images" )
    os.mkdir(os.getcwd()+"//" + "Images" + "//" + "1")
except:
    try:
        os.mkdir(os.getcwd()+"//" + "Images" + "//" + "1")
    except Exception as e:
        print (e)

#Queue
q = set([])
#q_in = open("queue.txt","rb")
#q = pickle.load(q_in)
#q_in.close()
#q = set(q)

q.add("https://www.adafruit.com/product/4382")
q.add("https://www.adafruit.com/product/2771")
q.add("https://www.adafruit.com/product/products/3591")

#for i in range(10):
while (len(q)>0):
    url = q.pop()
    if url not in visited:
        try:
            print('Queue Size:', len(q))
            driver.get(url)  
            visited.append(url)
            time.sleep(15)

            #Description
            soup = BeautifulSoup(driver.page_source, 'html.parser') 
            content = soup.find_all('p')
            #print(content)
            if (len(content)>0):
                description = str(content[2].get_text())

                #Title
                title = soup.find_all('h1')
                Title = str(title[0].string)

                #Extracting Image URL's
                images = driver.find_elements_by_tag_name('img')
                for image in images:
                    iml = image.get_attribute('src').split('/')[-1]
                    urll= url.split('/')[-1]
                    #print (image.get_attribute('src'))
                    #print(iml)
                    #print(urll)
                    if urll in iml:
                        image_url = image.get_attribute('src')
                        image_name = str(image_url[-11:-7]) + r'.jpg'
                        #print(image_url)
                        break;

                #Extracting the Price
                price = soup.find_all('title')
                price = price[0].string.split()
                for i in price:
                    if '$' in i:
                        price = i
                #print(price)

                # Appending the Data to the DataFrame
                df= df.append({'URL': url, 'Name': Title, 'Description': description, 'Image_URL': image_url, 'Image_Name': image_name, 'Price': price}, ignore_index=True)

                # Extracting the Other Product Links
                links = soup.find_all('a')
                #print(links)
                for link in links:
                    u = link.get('href') 
                    #print(u)
                    if not is_absolute(u):            
                        u = urljoin(url, u)        
                    if "adafruit.com/product" in u:
                        if "verify.authorize.net" not in u:
                            if(u.count('product') == 1):
                                try:
                                    U = int(u.split('/')[-1])
                                    q.add(u)
                                except: 
                                    continue

                # Saving an Image
                #path = os.getcwd() + "//" + "Images" + "//" + "1//" + str(image_url[-11:-7]) + r'.jpg'
                #driver.get(image_url)
                #driver.get_screenshot_as_file(path)
        
        except KeyboardInterrupt:
            #Saving the DataFrame
            df.to_csv('Adafruit.csv', index = False)
            
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
df.to_csv('Adafruit.csv', index = False)

# Saving the Visited
vis = open("visited.txt","wb")
pickle.dump(visited, vis)
vis.close()

# Saving the Queue
que = open("queue.txt","wb")
pickle.dump(q, que)
que.close()
