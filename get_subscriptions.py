#!/usr/bin/env python3
"""
YouTube Subscriptions Fetcher
Retrieves all subscriptions from a YouTube account using the YouTube Data API v3.
"""

import os
import json
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv


def get_all_subscriptions(api_key):
    """
    Fetch all YouTube subscriptions for the authenticated user.

    Args:
        api_key: YouTube Data API v3 key

    Returns:
        List of subscription dictionaries containing channel information
    """
    youtube = build('youtube', 'v3', developerKey=api_key)

    subscriptions = []
    next_page_token = None

    try:
        while True:
            # Request subscriptions
            request = youtube.subscriptions().list(
                part='snippet,contentDetails',
                mine=True,
                maxResults=50,
                pageToken=next_page_token
            )

            response = request.execute()

            # Extract subscription data
            for item in response.get('items', []):
                subscription_info = {
                    'channel_id': item['snippet']['resourceId']['channelId'],
                    'channel_title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'published_at': item['snippet']['publishedAt'],
                    'thumbnail_url': item['snippet']['thumbnails']['default']['url']
                }
                subscriptions.append(subscription_info)

            # Check for more pages
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break

    except HttpError as e:
        print(f"An HTTP error occurred: {e}")
        return None

    return subscriptions


def save_subscriptions(subscriptions, output_file='subscriptions.json'):
    """Save subscriptions to a JSON file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(subscriptions, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(subscriptions)} subscriptions to {output_file}")


def main():
    # Load environment variables
    load_dotenv()

    api_key = os.getenv('YOUTUBE_API_KEY')

    if not api_key or api_key == 'your_api_key_here':
        print("Error: Please set your YOUTUBE_API_KEY in the .env file")
        print("Get an API key from: https://console.cloud.google.com/apis/credentials")
        return

    print("Fetching YouTube subscriptions...")
    subscriptions = get_all_subscriptions(api_key)

    if subscriptions is not None:
        print(f"Found {len(subscriptions)} subscriptions")

        # Display first few subscriptions
        print("\nFirst 5 subscriptions:")
        for sub in subscriptions[:5]:
            print(f"  - {sub['channel_title']}")

        # Save to file
        save_subscriptions(subscriptions)

        # Also save a simple text list
        with open('subscriptions.txt', 'w', encoding='utf-8') as f:
            for sub in subscriptions:
                f.write(f"{sub['channel_title']}\n")
        print(f"Also saved channel names to subscriptions.txt")
    else:
        print("Failed to fetch subscriptions")


if __name__ == '__main__':
    main()
