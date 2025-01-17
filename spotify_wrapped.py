import json
import os
from collections import defaultdict
from datetime import datetime

def format_time(ms):
    if ms >= 3600000:
        hours = ms / 3600000
        return f"{hours:.2f} hours"
    else:
        minutes = ms / 60000
        return f"{minutes:.2f} minutes"

def load_data(*files):
    data = []
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            data += json.load(f)
    return data

def filter_by_date_range(data, start_date, end_date):
    filtered_data = []
    for entry in data:
        try:
            entry_date = datetime.strptime(entry["ts"], "%Y-%m-%dT%H:%M:%SZ")
            if start_date <= entry_date <= end_date:
                filtered_data.append(entry)
        except (KeyError, ValueError):
            continue
    return filtered_data

def aggregate_play_time(data):
    song_play_time = defaultdict(int)
    artist_play_time = defaultdict(int)
    total_play_time = 0
    
    for entry in data:
        artist = entry.get("master_metadata_album_artist_name")
        track = entry.get("master_metadata_track_name")
        ms_played = entry.get("ms_played", 0)

        if not artist or not track:
            continue

        song_play_time[(artist, track)] += ms_played
        artist_play_time[artist] += ms_played
        total_play_time += ms_played
    
    return song_play_time, artist_play_time, total_play_time

def save_results(song_play_time, artist_play_time, total_play_time, name):
    # sort by total time desc
    sorted_songs = sorted(song_play_time.items(), key=lambda x: x[1], reverse=True)
    sorted_artists = sorted(artist_play_time.items(), key=lambda x: x[1], reverse=True)
    
    total_hours = total_play_time / 3600000
    summary = f"Total listening time: {total_hours:.2f} hours = {total_hours*60:.0f} minutes\n"

    # write songs to file
    with open(f'{name}_songs.txt', 'w', encoding='utf-8') as song_file:
        song_file.write(summary)
        for idx, ((artist, track), total_ms) in enumerate(sorted_songs, start=1):
            song_file.write(f"{idx}. {artist} - {track}: {format_time(total_ms)}\n")

    # write artists to file
    with open(f'{name}_artists.txt', 'w', encoding='utf-8') as artist_file:
        artist_file.write(summary)
        for idx, (artist, total_ms) in enumerate(sorted_artists, start=1):
            artist_file.write(f"{idx}. {artist}: {format_time(total_ms)}\n")

    print(summary)

def main():
    start_date_str = input("Enter start date (YYYY-MM-DD): ")
    end_date_str = input("Enter end date (YYYY-MM-DD): ")
    name = input("Enter a name for the output files: ")

    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

    files = [file for file in os.listdir(os.getcwd()) if file.startswith("Streaming_History_Audio")]
    data = load_data(*files)
    
    # filter by date range
    filtered_data = filter_by_date_range(data, start_date, end_date)
    
    # aggregate play time by song and by artist, and calculate total time
    song_play_time, artist_play_time, total_play_time = aggregate_play_time(filtered_data)
    
    # save to file
    save_results(song_play_time, artist_play_time, total_play_time, name)

if __name__ == "__main__":
    main()