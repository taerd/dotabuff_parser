from selenium.webdriver.common.by import By

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.service import Service

import pandas as pd
import numpy as np
import time
from config import *

import requests
from bs4 import BeautifulSoup as bs

def delay(sec):
    print(f'[DELAY]: {sec} seconds', end='')
    for i in range(sec):
        time.sleep(1)
        print('.', end='')
    print()

def log(message, level):
    if LOG_LEVEL >= level:
        print(f'[LOG] {message}')

#Для каждого турнира из URL
for URL in URLS:

    log("Current tournament : "+URL,-1)
    tournament = URL.split('/')[5]

    try:
        op = ChromeOptions()
        if HEADLESS:
            op.add_argument('--headless')
        service = Service('chromedriver.exe')
        browser = Chrome(service=service, options=op)
        browser.get(url=URL)
        delay(DELAY_TIME)

        #Узнаем количество страниц

        pagination = browser.find_element(By.XPATH,"/html/body/div[2]/div[2]/div[3]/div[4]/section[2]/div/article/nav/span[8]/a")
        last_page = int(pagination.get_attribute('href').split('&')[1].split('=')[1])
        matches_on_tournament = pd.DataFrame(columns = ['match_id','hero','dire_side','dire_win'])

        for i in range(1,last_page+1):
            url_page = URL+"?original_slug="+URL.split('/')[5]+"&page="+str(i)
            log("Current page : "+url_page,0)
            delay(DELAY_TIME)
            browser.get(url=url_page)

            #Узнаем количество матчей на странице
            col_matches_on_page = browser.find_elements(By.XPATH,"//*[@class= 'table table-striped table-condensed recent-esports-matches']/tbody/tr")
            match_col = len(col_matches_on_page)+1
            matches_on_page = pd.DataFrame(columns = ['match_id','hero','dire_side','dire_win'])

            for match in range(1,match_col):
                heroes_on_match = pd.DataFrame(columns = ['hero','dire_side'])

                # айди матча
                table_match = browser.find_element(By.XPATH,
                    f'/ html / body / div[2] / div[2] / div[3] / div[4] / section[2] / div / article / table / tbody / tr[{match}] / td[1] / a')
                match_id = table_match.get_attribute('href').split('/')[4]
                log("Current match_id dotabuff : "+match_id,1)

                # Победная сторона
                side_winner = browser.find_element(By.XPATH,f'/html/body/div[2]/div[2]/div[3]/div[4]/section[2]/div/article/table/tbody/tr[{match}]/td[3]/span')
                side_winner = side_winner.get_attribute('class')
                #print(side_winner)
                if side_winner == 'radiant':
                    side_winner = 0
                else:
                    side_winner = 1


                for k in range (3,5):
                    heroes_on_side = pd.DataFrame(columns = ['hero','dire_side'])

                    # Узнать сторону пика
                    playing_side = browser.find_element(By.XPATH, f'/html/body/div[2]/div[2]/div[3]/div[4]/section[2]/div/article/table/tbody/tr[{match}]/td[{k}]/span')
                    playing_side = playing_side.get_attribute('class')
                    #print(playing_side)
                    if playing_side =='radiant':
                        playing_side = 0
                    else:
                        playing_side = 1

                    for i in range(1,6):
                        #Достать героя из картинки под таблицей матча
                        table_ = browser.find_element(By.XPATH,
                            f'/html/body/div[2]/div[2]/div[3]/div[4]/section[2]/div/article/table/tbody/tr[{match}]/td[{k}]/div/img[{i}]')
                        name_hero = table_.get_attribute('src').split('/')[5]


                        # full name hero
                        name_hero = name_hero.split('.')[0].split('-')
                        name_hero_str = ''
                        for i in range(len(name_hero)-1):
                            name_hero_str = name_hero_str+name_hero[i]


                        heroes_on_side = heroes_on_side.append(pd.DataFrame([[name_hero_str,playing_side]],columns=['hero','dire_side']))

                    heroes_on_match = heroes_on_match.append(heroes_on_side)


                heroes_on_match.insert(0, "match_id", match_id)
                heroes_on_match.insert(3,"dire_win", side_winner)
                log("Heroes on the match : \n"+heroes_on_match.to_string(),2)


                #heroes_on_match.to_csv(f'{match_id}.csv')
                matches_on_page = matches_on_page.append(heroes_on_match,ignore_index=True)
            matches_on_tournament = matches_on_tournament.append(matches_on_page,ignore_index=True)
        matches_on_tournament.to_csv(f'{tournament}.csv')
        browser.close()
    except Exception:
        print(f'Something went wrong')
        browser.close()