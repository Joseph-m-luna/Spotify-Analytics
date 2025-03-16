import requests
from pprint import pprint
import json
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep
import random

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
    
    def get_search(self, song, artist, raw=False):
        data = {'q': song + " " + artist}
        response = requests.get(self.base_url + "/search", data=data, headers=self.headers)
        
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
        response = requests.get(url)
        response.raise_for_status()

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

    song_data = genius.get_search(song, artist, raw=False)
    
    pprint(song_data)

def scrape_year(year=2024):
    genius = Genius()
    
    df_1959 = pd.read_csv("../Spotify_API_scrape/by_year_data/2024_music_data.csv")
    lyrics_df = pd.DataFrame(columns=["Artist", "Song", "Lyrics"])

    for i, row in df_1959.iterrows():
        done = False
        attempts = 0

        while not done:
            artist = row["Artists"]
            song = row["Track Name"]
            print(f"searching for {artist} - {song}")

            song_data = genius.get_search(song, artist)

            list_manual = []
            
            if song_data is not None:
                url = song_data["result"]["url"]
                lyrics = genius.get_lyrics(url)
                print(f"lyrics found for {artist} - {song}")

                with open(f"./Lyrics_2024/{song.replace(' ', '_')}|||{artist.replace(' ', '_')}.txt", "w") as file:
                    file.write(lyrics)

                sleeptime = weighted_random(1, 15)
                print(f"Sleeping for {sleeptime} seconds")
                sleep(sleeptime)

                new_row = pd.DataFrame({"Artist": [artist], "Song": [song], "Lyrics": [lyrics]})
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
    for artist, song in list_manual:
        print(f"{artist} - {song}")
    
    with open("manual_search.txt", "w") as file:
        for artist, song in list_manual:
            file.write(f"{artist} - {song}\n{song} {artist}\n\n")

    lyrics_df.to_csv("1959_lyrics.csv", index=False)
    print("Done!")

if __name__ == "__main__":
    scrape_year(2024)
    # get_single_search_results("IDGAF (feat. Yeat)", "Drake, Yeat")
