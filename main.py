from Lyrics_Scrape_NLP.azlyrics import AZLyrics
from Lyrics_Scrape_NLP.text_encoder import TextEncoder
import tqdm
import os
import pandas as pd
import numpy as np
from time import sleep
import json

def extract_lyrics_billboard():
    data_path = "Spotify_API_scrape/by_year_data"
    
    # by year
    files = os.listdir(data_path)
    
    unprocessed_list = pd.DataFrame()
    for file in files:
        if file.endswith("_music_data.csv"):
            df = pd.read_csv(os.path.join(data_path, file))
            
            # for accurate tqdem tracking, we'll store each song individually
            try:
                year = int(file.split("_")[0])
            except:
                print("Unexpected naming convention, please check file type, or modify code to fit convention")
                exit(1)
            
            df["year"] = year
            unprocessed_list = pd.concat([unprocessed_list, df])


    az = AZLyrics()
    encoder = TextEncoder()

    found = 0
    not_found = 0
    total = 0

    file = open("lyrics_log.txt", "w")
    save_point = json.load(open("save_point.json"))

    print(f"Save point: {save_point}")

    unprocessed_list["lyrics"] = None
    unprocessed_list["encoding"] = pd.Series([[None] * 300] * len(unprocessed_list), dtype=object)

    for i, row in tqdm.tqdm(unprocessed_list.iterrows(), total=unprocessed_list.shape[0]):
        artist = row["Artists"]
        title = row["Track Name"]
        print(f"Processing {artist} - {title}")
        
        lyrics_search = az.fetch_all_lyrics(f"{artist} {title}")

        file.write(f"found results for {artist} - {title}: [{lyrics_search}]\n")
        
        if not lyrics_search:
            file.write(f"No lyrics found for {artist} - {title}\n")
            not_found += 1
            total += 1
            unprocessed_list.at[i, "lyrics"] = None
            unprocessed_list.at[i, "encoding"] = None
        else:
            lyrics = az.fetch_lyrics(lyrics_search[0]["href"])
            encoding = encoder.encode(lyrics)
            unprocessed_list.at[i, "lyrics"] = lyrics
            
            series = pd.Series([encoding], index=unprocessed_list.index[[i]])
            unprocessed_list.loc[[i], "encoding"] = series
            
            file.write(f"found lyrics for: {artist} - {title}\n")
            found += 1
            total += 1

        sleep(2)

    unprocessed_list.to_csv("processed_lyrics.csv")

    print(f"Found {found} lyrics out of {total} songs for a success rate of {found/total}")
    file.write(f"\nFound {found} lyrics out of {total} songs for a success rate of {found/total}")
    file.close()
    

def main():
    #entry point
    extract_lyrics_billboard()

if __name__ == "__main__":
    main()