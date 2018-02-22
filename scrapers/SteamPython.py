import urllib
import requests
import time
import re
import numpy as np
import pandas as pd
import json
from selenium import webdriver
from bs4 import BeautifulSoup as bs
steamAPIKey=""
browser = webdriver.Chrome()
maxpages = 100
url_base = "http://store.steampowered.com/search/?sort_by=Name_ASC&tags=21978&page="
url_details_base = "http://store.steampowered.com/api/appdetails?appids="
url_playercount_base = "https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?key="
string_ignore = ["353370","353380","358040"]
totallinkcount=0

list_appid=[]
list_name=[]
list_price=[]
list_playercount=[]
list_earlyaccess=[]

with open("pagedata.txt","w+") as file:
    for pagenumber in range(maxpages):
        linkcount = 0
        url_final = url_base + str(pagenumber)
        browser.get(url_final)
        res = browser.page_source
        res_bs = bs(res)
        for link in res_bs.find_all('a'):
            if "http://store.steampowered.com/app/" in link.get("href"):
                if any(ignored_string in link.get("href") for ignored_string in string_ignore):
                    continue
                item = link.get("href")
                item_list = item.split("/")
                appid = item_list[4]
                name = item_list[5]
                list_appid.append(appid)
                list_name.append(name)
                
                url_details_final = url_details_base+appid
                response_details=requests.get(url_details_final)
                
                #price = re.compile("\$\d+")
                print(appid)
                try:
                    price = (re.search("\$\d+(?:\.\d+)?",response_details.text)).group()[1:]
                except AttributeError:
                    price = 0
                print(price)
                list_price.append(price)
                
                url_playercount_final = url_playercount_base+steamAPIKey+"&format=json&appid="+appid
                response_playercount = requests.get(url_playercount_final)
                playercount_dict = json.loads(response_playercount.text)
                #print(playercount_dict)
                #print(appid)
                try:
                    list_playercount.append(playercount_dict["response"]["player_count"])
                except KeyError:
                    list_playercount.append(np.nan)
                    
                
                if "Early Access" in response_details.text:
                    list_earlyaccess.append(True)
                else:
                    list_earlyaccess.append(False)
                
                
                linkcount+=1
                totallinkcount+=1
            #time.sleep(.2)
        if (linkcount <= 3) == True: 
            break
    browser.close()
    
df = pd.DataFrame({"AppID":list_appid,"Name":list_name,"PlayerCount":list_playercount,"PriceUSD":list_price,"EarlyAccess":list_earlyaccess})
print(df)
df.to_csv("Data.csv")
    
#soup.find("meta", {"name":"City"})['content']

#with open("pagedata_details.txt","w+") as file:
    #response_details = requests.get("http://store.steampowered.com/api/appdetails?appids=607190")
    #response_players = requests.get("https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?key="+steamAPIKey+"&format=json&appid=607190")
    #response_players_bs = bs(response_players.text)
    #info = json.loads(str(response_players_bs))
    #file.write(str(info))
    #file.write("\n")
    
    
