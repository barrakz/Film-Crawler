from datetime import datetime, timedelta
from googleapiclient.discovery import build
from langdetect import detect
import re
import config

# wprowadź swój klucz API YouTube
api_key = config.youtube_api_key

# wprowadź frazę wyszukiwania
search_query = input("Wpisz frazę wyszukiwania: ")

# wprowadź ilość dni wstecz, z których mają być wyszukane filmy
days_back = int(input("Z ilu ostatnich dni chcesz uzyskać wynik wyszukiwania? "))

# oblicz datę publikacji wideo, która jest dni_back dni przed dzisiejszą datą
published_after = (datetime.utcnow() - timedelta(days=days_back)).strftime('%Y-%m-%dT%H:%M:%SZ')

# tworzenie obiektu YouTube Data API
youtube = build('youtube', 'v3', developerKey=api_key)

# wyszukaj filmy związane z frazą wyszukiwania opublikowane w ciągu ostatnich dni_back dni
search_response = youtube.search().list(
    q=search_query,
    type='video',
    part='id,snippet',
    fields='items(id(videoId),snippet(title,channelTitle)),nextPageToken',
    maxResults=50,
    order='viewCount',
    publishedAfter=published_after
).execute()

# wyświetl tytuły i nazwy kanałów dla pierwszych pięciu filmów z największą liczbą wyświetleń
for search_result in search_response.get('items', []):
    video_id = search_result['id']['videoId']
    video_title = search_result['snippet']['title']
    channel_title = search_result['snippet']['channelTitle']
    try:
        # wyodrębnij słowa z tytułu
        words = re.findall('\w+', video_title)
        # zlicz ilość polskich słów w tytule
        pl_words_count = sum(detect(word) == 'pl' for word in words)
        # sprawdź, czy tytuł zawiera przynajmniej dwa polskie słowa
        if pl_words_count >= 2:
            # pobierz informacje o liczbie wyświetleń z endpointu videos.list
            video_response = youtube.videos().list(
                id=video_id,
                part='statistics'
            ).execute()
            view_count = video_response['items'][0]['statistics']['viewCount']
            print(f"Film: {video_title} \nKanał: {channel_title}\nLiczba wyświetleń: {view_count}\n")
    except:
        pass
