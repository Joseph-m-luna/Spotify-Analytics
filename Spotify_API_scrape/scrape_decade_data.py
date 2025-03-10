import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import musicbrainzngs
import argparse
import os

parser = argparse.ArgumentParser(description="Scrape Spotify playlist data and enhance with MusicBrainz genres.")
parser.add_argument("--playlist_id", "-p",type=str, help="Spotify Playlist ID to scrape")
parser.add_argument("--decade", "-d", type=str, default="output.csv", help="Output CSV file name (default: output.csv)")
args = parser.parse_args()

# maybe update parser to ask for id and secret id
client_id = ""
client_secret = ""

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

# MusicBrainz setup
musicbrainzngs.set_useragent("TrendScraper", "1.0", "ishiharay15@gmail.com")

def get_playlist_data(playlist_id):
    """
    Fetches track details including name, artist, genres, duration, explicit flag, popularity, 
    and available markets from a given Spotify playlist.
    
    Args:
        playlist_id (str): The Spotify playlist ID.

    Returns:
        list: A list of lists containing track details.
    """
    
    try:
        playlist = sp.playlist_tracks(playlist_id)

        if "items" not in playlist or not playlist["items"]:
            raise ValueError(f"Playlist ID '{playlist_id}' is invalid or has no tracks.")
    
    except spotipy.exceptions.SpotifyException as e:
        raise ValueError(f"Error fetching playlist: {e}")
    
    track_data = []
    playlist = sp.playlist_tracks(playlist_id)

    for item in playlist["items"]:
        track = item["track"]
        track_name = track["name"]
        artist_name = ", ".join([artist["name"] for artist in track["artists"]])

        genres = []
        for artist in track["artists"]:
            artist_info = sp.artist(artist["id"])
            if artist_info["genres"]:
                genres.extend(artist_info["genres"])
        genres = ", ".join(set(genres)) if genres else "Unknown"

        track_duration_ms = track["duration_ms"]  # Track duration in milliseconds
        track_explicit = track["explicit"]  # True or False
        track_popularity = track["popularity"]  # Popularity score (0-100)
        available_markets = len(track["album"]["available_markets"])  # Number of available countries

        track_data.append([track_name, artist_name, genres, track_duration_ms, track_explicit, track_popularity, available_markets])

    return track_data


def get_artist_genre(artist_name):

    try:
        result = musicbrainzngs.search_artists(artist=artist_name, limit=1)

        if "artist-list" in result and len(result["artist-list"]) > 0:
            artist = result["artist-list"][0]
            artist_id = artist["id"]

            artist_info = musicbrainzngs.get_artist_by_id(artist_id, includes=["tags"])

            tag_list = artist_info.get("artist", {}).get("tag-list", [])

            sorted_tags = sorted(tag_list, key=lambda x: int(x["count"]), reverse=True) if tag_list else []

            genres = [tag["name"] for tag in sorted_tags]

            return ", ".join(genres) if genres else "Unknown"

        return "Unknown"

    except Exception as e:
        print(f"Error fetching genre for {artist_name}: {e}")
        return "Unknown"
    

def get_artist_country(artist_name):
    
    try:
        result = musicbrainzngs.search_artists(artist=artist_name, limit=1)

        if "artist-list" in result and len(result["artist-list"]) > 0:
            artist = result["artist-list"][0]
            return artist.get("country", "Unknown")  # Get country if available

    except Exception as e:
        print(f"Error fetching country for {artist_name}: {e}")

    return "Unknown"


def update_unknown_genres(df):
    
    for index, row in df.iterrows():
        if row["Genres"] == "Unknown" or "Artist Country" not in df.columns:
            artist_names = row["Artists"].split(", ")
            genre_list = []
            country_list = []

            for artist_name in artist_names:
                genres = get_artist_genre(artist_name)
                top_genre = genres.split(", ")[0] if genres != "Unknown" else "Unknown"
                
                artist_country = get_artist_country(artist_name)
                
                if top_genre != "Unknown":
                    genre_list.append(top_genre)
                
                if artist_country != "Unknown":
                    country_list.append(artist_country)

            if genre_list:
                df.at[index, "Genres"] = ", ".join(genre_list)
            if country_list:
                df.at[index, "Artist Country"] = ", ".join(country_list)

    unknown_count = (df["Genres"] == "Unknown").sum()
    print(f"Number of tracks with unknown genre: {unknown_count}")

    return df


if __name__ == "__main__":
    print(f"Fetching data for playlist: {args.playlist_id}")

    track_data = get_playlist_data(args.playlist_id)

    df = pd.DataFrame(track_data, columns=["Track Name", "Artists", "Genres", "Duration (ms)", "Explicit", "Popularity", "Available Markets"])

    df = update_unknown_genres(df)

    df["Artist Country"] = df["Artists"].apply(lambda x: ", ".join([get_artist_country(artist) for artist in x.split(", ")]))

    os.makedirs("./by_year_data", exist_ok=True)
    output_file = f"./by_year_data/{args.decade}_music_data.csv"
    df.to_csv(output_file, index=False)
    print(f"Data saved to {output_file}")
