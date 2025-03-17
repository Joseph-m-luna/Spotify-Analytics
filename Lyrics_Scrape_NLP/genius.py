import requests
from pprint import pprint
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep
import random
from text_encoder import TextEncoder
import numpy as np
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import matplotlib.pyplot as plt
from plyer import notification

class Genius:
    def __init__(self):
        self.base_url = "https://api.genius.com"
        self.headers_alts = [{
            "User-Agent" : "CompuServe Classic/1.22",
            "Accept" : "application/json",
            "Host" : "api.genius.com",
            "Authorization" : "Bearer " + "0VgQZO_iJh16PgZvuRW3o8KniSgvDAv5M6kA9GjLa7SsrTqKnPXZfDchF19N_46U",
        },
        {
            "User-Agent" : "CompuServe Classic/1.22",
            "Accept" : "application/json",
            "Host" : "api.genius.com",
            "Authorization" : "Bearer " + "uwHRWOZEZ8vk3XDawpHxH6Mp0XHZEdrPt-k0pNOrvm3r7pmCkAVjw5dwp_qWyB32",
        }]
        self.headers_alt_index = 1
        self.headers = self.headers_alts[1]
        self.options = uc.ChromeOptions()
        self.options.headless = False

        self.driver = uc.Chrome(options=self.options)


    def get_search_engine(self, song, artist):
        # options = webdriver.ChromeOptions()
        # options.add_argument("--headless")  # Run without opening a browser
        # options.add_argument("--no-sandbox")
        # options.add_argument("--disable-dev-shm-usage")

        # driver = webdriver.Chrome(options=options)
        self.driver.get("https://www.google.com")

        sleep(0.5)
        google = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="APjFqb"]')))
        # //*[@id="APjFqb"]
        # //*[@id="APjFqb"]

        cleaned_song = song.replace('"', "")
        cleaned_artist = artist.replace('"', "")
        cleaned_song = cleaned_song.replace("-", "")
        cleaned_artist = cleaned_artist.replace("-", "")
        cleaned_song = cleaned_song.replace(",", "")
        cleaned_artist = cleaned_artist.replace(",", "")
        google.send_keys(f"{cleaned_song} {cleaned_artist} genius lyrics")

        sleep(0.5)
        google.send_keys(Keys.RETURN)
        sleep(1)

        results = self.driver.find_element(By.CSS_SELECTOR, "h3")
        result_link = results.find_element(By.XPATH, "./ancestor::a").get_attribute("href")
        return result_link

    def get_search(self, song, artist, raw=False):
        data = {'q': song + " " + artist}
        try:
            response = requests.get(self.base_url + "/search", data=data, headers=self.headers)
        except Exception as e:
            print(f"Exception occurred while getting search results for {song} - {artist}: {e}")
            sleep(60)
            return None
        
        response_data = response.json()

        if len(response_data["response"]["hits"]) == 0:
            return None
        elif raw:
            return response
        else: 
            # Find most popular response
            max_popularity = 0
            max_index = -1
            for i, hit in enumerate(response_data["response"]["hits"]):
                if "pageviews" in hit["result"]["stats"].keys():
                    if hit["result"]["stats"]["pageviews"] > max_popularity:
                        max_popularity = int(hit["result"]["stats"]["pageviews"])
                        max_index = i
            if max_index == -1:
                return None
            else:
                return response_data["response"]["hits"][max_index]

    def get_lyrics(song, url="https://genius.com/Frank-sinatra-the-way-you-look-tonight-lyrics"):
        url_overrides = {
            "https://www.musixmatch.com/lyrics/Far-East-Movement-feat-Ryan-Tedder/Rocketeer" : "https://genius.com/Far-east-movement-rocketeer-lyrics",
            "https://www.musixmatch.com/lyrics/45447790/10617727" : "https://genius.com/Keri-hilson-turnin-me-on-lyrics",
        }

        if url in url_overrides.keys():
            url = url_overrides[url]

        response = requests.get(url)
        try:
            response.raise_for_status()
        except Exception as e:
            print(f"Exception occurred while getting lyrics for {song}: {e}")
            notification.notify(title="url error", message=f"address error", timeout=999999)
            return None
            

        soup = BeautifulSoup(response.text, "html.parser")
        lyrics_divs = soup.find_all("div", class_="Lyrics__Container-sc-926d9e10-1 fEHzCI", attrs={"data-lyrics-container" : "true"})

        raw_lyrics = ""
        for elements in lyrics_divs:
            for line in elements:
                if line.name == "br":
                    raw_lyrics += "\n"
                elif isinstance(line, str):
                    raw_lyrics += line
                elif line.name == "a":
                    spans = line.find_all("span")
                    if len(spans) > 0:
                        for span in spans:
                            for s_element in span:
                                if s_element.name == "br":
                                    raw_lyrics += "\n"
                                elif s_element.name == "i":
                                    raw_lyrics += s_element.text
                                elif isinstance(s_element, str):
                                    raw_lyrics += s_element

        return raw_lyrics

    def test_query(self):
        # auth_string = "Bearer " + "QdVzuiuKKt2jVyQPgsSnX9QeQ4Z-CKOEUf8ePEb--F3dsX5ryk9H-ueiQKrD0tVNcUgs4EopOEgwuPqikw8bsA"
        # auth_string = "Bearer " + "4YoCSbRjLYV7peMEBeg2j85EOjOkIvi7rMfWLel_xnHrUV_aty"
        data = {'q': 'The Battle Of New Orleans Johnny Horton'}
        response = requests.get(self.base_url + "/search", data=data, headers=self.headers)
        pprint(dict(response.json()))

    def swap_headers(self):
        if self.headers_alt_index == 0:
            self.headers_alt_index = 1
            self.headers = self.headers_alts[self.headers_alt_index]
        else:
            self.headers_alt_index = 0
            self.headers = self.headers_alts[self.headers_alt_index]

def weighted_random(low, high):
    weights = [high - i for i in range(low, high + 1)]
    return random.choices(range(low, high + 1), weights=weights, k=1)[0]

def get_single_search_results(song, artist):
    genius = Genius()

    song_data = genius.get_search_engine(song, artist)

    print(song_data)

def scrape_year(year=2024):
    genius = Genius()
    encoder = TextEncoder()
    
    df_1959 = pd.read_csv(f"../Spotify_API_scrape/by_year_data/{year}_music_data.csv")
    lyrics_df = pd.DataFrame(columns=["Artist", "Song", "Lyrics", "Encoding"])

    list_manual = []

    for i, row in df_1959.iterrows():
        done = False
        attempts = 0

        while not done:
            artist = row["Artists"]
            song = row["Track Name"]
            print(f"searching for {artist} - {song}")

            if type(song) != str or type(artist) != str:
                print(f"error in row: {i}, {artist} - {song}, type is not string")
                done = True
                continue
            song_data = genius.get_search_engine(song, artist)
            
            if song_data is not None:
                url = song_data
                lyrics = genius.get_lyrics(url)
                if lyrics is None:
                    print(f"No lyrics found for {artist} - {song}")
                    list_manual.append((artist, song))
                    done = True
                else:
                    print(f"lyrics found for {artist} - {song}")

                    os.makedirs(f"./Lyrics_{year}", exist_ok=True)

                    safe_song_name = song.replace(' ', '_').replace("/", "_")
                    safe_artist_name = artist.replace(' ', '_').replace("/", "_")

                    with open(f"./Lyrics_{year}/{safe_song_name}|||{safe_artist_name}.txt", "w") as file:
                        file.write(lyrics)

                    # sleeptime = weighted_random(1, 3)
                    sleeptime = 0.5
                    print(f"Sleeping for {sleeptime} seconds")
                    sleep(sleeptime)

                    encoding = encoder.encode(lyrics)
                    encoding_list = encoding.tolist()
                    series = pd.Series([encoding_list])

                    new_row = pd.DataFrame({"Artist": [artist], "Song": [song], "Lyrics": [lyrics], "Encoding": series})
                    lyrics_df = pd.concat([lyrics_df, new_row], ignore_index=True)
                    done = True
            else:
                if attempts == 0:
                    print(f"No lyrics found for {artist} - {song}, attempting to swap headers")
                    genius.swap_headers()
                    sleep_time = 60
                    sleep(sleep_time)
                elif attempts == 1:
                    sleep_time = 180
                    print(f"No lyrics found for {artist} - {song}, implementing long wait of {sleep_time} seconds")
                    sleep(sleep_time)
                else:
                    print(f"No lyrics found for {artist} - {song}, skipping")
                    list_manual.append((artist, song))
                    done = True
                attempts += 1
    
    print("Manual search required for:")
    print(list_manual)
    
    with open(f"manual_search_{year}.txt", "w") as file:
        for artist, song in list_manual:
            file.write(f"{artist} - {song}\n{song} {artist}\n\n")

    lyrics_df.to_csv(f"{year}_lyrics.csv", index=False)
    print("Done!")

def read_test_csv():
    df = pd.read_csv("2024_test_encoding.csv")
    array_values = df["Encoding"]
    ndarraystuff = np.array(array_values[0])
    print(ndarraystuff)
    print(type(ndarraystuff))

if __name__ == "__main__":
    # for i in range(1961, 1958, -1):
    #     scrape_year(i)
    for i in [1999, 1968]:
        scrape_year(i)
    # get_single_search_results("Bulletproof", "Nate Smith")

# NOTE: 2019, thank u next, Ariana Grande
