"""
Trending Videos Generator

DEVELOPER GUIDELINE: External API Resiliency
Fetches trending video data via the Gemini API and saves to CSV. Implement 
robust fallback mechanisms (like the included mock data) to ensure the 
application remains functional even when third-party APIs are down or rate-limited.
"""

import csv
import json
import os
from datetime import datetime

import google.generativeai as genai

DATA_DIR = os.path.join(os.getcwd(), 'docs', 'data')

def generate_csv(platform, data):
    """Writes a list of dictionaries to a CSV file."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    filepath = os.path.join(DATA_DIR, f'{platform}_trending.csv')
    
    if not data:
        print(f"No data to write for {platform}.")
        return

    keys = data[0].keys()
    with open(filepath, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)
    
    print(f"Successfully generated: {filepath}")

def fetch_trending_via_gemini(platform_name):
    print(f"Fetching trending data for {platform_name} via Gemini API...")
    
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    published_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if not api_key:
        print("Please set the GEMINI_API_KEY environment variable. Returning mock data as fallback.")
        if platform_name == "YouTube":
            return [
                {"Platform": "YouTube", "Title": "BLACKPINK - 'GO' M/V", "URL": "https://www.youtube.com/watch?v=mock1", "Views": "34.7M", "Category": "Music", "VideoType": "Video", "PublishedDate": published_date},
                {"Platform": "YouTube", "Title": "Lanterns | Official Teaser | HBO Max", "URL": "https://www.youtube.com/watch?v=mock2", "Views": "1.2M", "Category": "Entertainment", "VideoType": "Video", "PublishedDate": published_date},
                {"Platform": "YouTube", "Title": "Scary Movie | Official Trailer (2026 Movie)", "URL": "https://www.youtube.com/watch?v=mock3", "Views": "1.9M", "Category": "Entertainment", "VideoType": "Video", "PublishedDate": published_date},
                {"Platform": "YouTube", "Title": "Shararat | Dhurandhar", "URL": "https://www.youtube.com/watch?v=mock4", "Views": "4.0M", "Category": "Music", "VideoType": "Video", "PublishedDate": published_date},
                {"Platform": "YouTube", "Title": "Balam Pichkari (Full Video)", "URL": "https://www.youtube.com/watch?v=mock5", "Views": "3.6M", "Category": "Music", "VideoType": "Video", "PublishedDate": published_date},
                {"Platform": "YouTube", "Title": "Aadu 3 Official Trailer", "URL": "https://www.youtube.com/watch?v=mock6", "Views": "3.1M", "Category": "Entertainment", "VideoType": "Video", "PublishedDate": published_date}
            ]
        elif platform_name == "TikTok":
            return [
                {"Platform": "TikTok", "Title": "Trending Dance Challenge - @charlidamelio", "URL": "https://www.tiktok.com/t/mock1", "Views": "15.2M", "Category": "Entertainment", "VideoType": "Short Form", "PublishedDate": published_date},
                {"Platform": "TikTok", "Title": "Funny Prank Video - @mrbeast", "URL": "https://www.tiktok.com/t/mock2", "Views": "8.5M", "Category": "Comedy", "VideoType": "Short Form", "PublishedDate": published_date},
                {"Platform": "TikTok", "Title": "Satisfying ASMR - @satisfyingsounds", "URL": "https://www.tiktok.com/t/mock3", "Views": "4.1M", "Category": "ASMR", "VideoType": "Short Form", "PublishedDate": published_date},
                {"Platform": "TikTok", "Title": "Cooking Hack - @gordonramsay", "URL": "https://www.tiktok.com/t/mock4", "Views": "3.8M", "Category": "Food", "VideoType": "Short Form", "PublishedDate": published_date},
                {"Platform": "TikTok", "Title": "Daily Vlog - @alixearle", "URL": "https://www.tiktok.com/t/mock5", "Views": "2.9M", "Category": "Lifestyle", "VideoType": "Short Form", "PublishedDate": published_date}
            ]
        else: # Instagram
            return [
                {"Platform": "Instagram", "Title": "Outfit of the Day Reel", "URL": "https://www.instagram.com/reel/mock1", "Views": "5.4M", "Category": "Fashion", "VideoType": "Reel", "PublishedDate": published_date},
                {"Platform": "Instagram", "Title": "Travel Vlog Reel", "URL": "https://www.instagram.com/reel/mock2", "Views": "3.2M", "Category": "Travel", "VideoType": "Reel", "PublishedDate": published_date},
                {"Platform": "Instagram", "Title": "Fitness Routine Update", "URL": "https://www.instagram.com/reel/mock3", "Views": "2.1M", "Category": "Fitness", "VideoType": "Reel", "PublishedDate": published_date},
                {"Platform": "Instagram", "Title": "Behind the Scenes - Photo Shoot", "URL": "https://www.instagram.com/reel/mock4", "Views": "1.8M", "Category": "Behind the Scenes", "VideoType": "Reel", "PublishedDate": published_date},
                {"Platform": "Instagram", "Title": "New Makeup Look Tutorial", "URL": "https://www.instagram.com/reel/mock5", "Views": "4.5M", "Category": "Beauty", "VideoType": "Reel", "PublishedDate": published_date}
            ]

    genai.configure(api_key=api_key)
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Search the web for the top hot new videos that surpassed 1 million views in the last 24 hours on {platform_name}.
    Return exactly 5 real items based on your search.
    
    Output strictly in this JSON array format, and nothing else (no markdown blocks like ```json):
    [
      {{
        "Platform": "{platform_name}",
        "Title": "Real Video Title Here",
        "URL": "Real link to the video here",
        "Views": "View count (e.g. 1.5M)",
        "Category": "Category (e.g. Entertainment, Music, Gaming)",
        "VideoType": "Video",
        "PublishedDate": "{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
      }}
    ]
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith('```json'):
            text = text[7:]
        if text.endswith('```'):
            text = text[:-3]
            
        data = json.loads(text.strip())
        return data
    except RuntimeError as e:
        print(f"Error fetching via Gemini: {e}")
        return []

def create_trending_data():
    youtube_data = fetch_trending_via_gemini("YouTube")
    tiktok_data = fetch_trending_via_gemini("TikTok")
    instagram_data = fetch_trending_via_gemini("Instagram")
    
    if youtube_data:
        generate_csv('youtube', youtube_data)
    else:
        print("No YouTube data generated.")

    if tiktok_data:
        generate_csv('tiktok', tiktok_data)
    else:
        print("No TikTok data generated.")

    if instagram_data:
        generate_csv('instagram', instagram_data)
    else:
        print("No Instagram data generated.")

    print("\nAll Trending Video CSV files processing complete.")

if __name__ == "__main__":
    create_trending_data()
