#!/usr/bin/env python3
"""
YouTube Subscriptions Fetcher
Retrieves all subscriptions from a YouTube account using OAuth 2.0.
Users just need to click "Allow" in their browser - no API key needed!
"""

import os
import json
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Scopes required for reading subscriptions
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']

def get_authenticated_service():
    """
    Authenticate with YouTube using OAuth 2.0.
    Opens browser for user to authorize access.
    Saves token for future use.
    """
    credentials = None

    # Load previously saved credentials
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)

    # If credentials are invalid or don't exist, authenticate
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print("Refreshing access token...")
            credentials.refresh(Request())
        else:
            if not os.path.exists('client_secrets.json'):
                print("ERROR: client_secrets.json file not found!")
                print("\nPlease follow these steps:")
                print("1. Go to https://console.cloud.google.com/")
                print("2. Create a project or select existing one")
                print("3. Enable YouTube Data API v3")
                print("4. Go to Credentials > Create Credentials > OAuth client ID")
                print("5. Choose 'Desktop app' as application type")
                print("6. Download the JSON file and save it as 'client_secrets.json' in this folder")
                return None

            print("Opening browser for authentication...")
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json', SCOPES)
            credentials = flow.run_local_server(port=8080)

        # Save credentials for future use
        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)
        print("Authentication successful! Token saved for future use.\n")

    return build('youtube', 'v3', credentials=credentials)


def get_all_subscriptions(youtube):
    """
    Fetch all YouTube subscriptions for the authenticated user.

    Args:
        youtube: Authenticated YouTube API client

    Returns:
        List of subscription dictionaries containing channel information
    """
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
                    'thumbnail_url': item['snippet']['thumbnails']['default']['url'],
                    'channel_url': f"https://www.youtube.com/channel/{item['snippet']['resourceId']['channelId']}"
                }
                subscriptions.append(subscription_info)

            # Check for more pages
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break

            print(f"Fetched {len(subscriptions)} subscriptions so far...")

    except HttpError as e:
        print(f"An HTTP error occurred: {e}")
        return None

    return subscriptions


def save_subscriptions(subscriptions, output_file='subscriptions.json'):
    """Save subscriptions to a JSON file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(subscriptions, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved {len(subscriptions)} subscriptions to {output_file}")


def main():
    print("YouTube Subscriptions Fetcher")
    print("=" * 40)

    # Authenticate and get YouTube service
    youtube = get_authenticated_service()

    if not youtube:
        return

    print("Fetching your YouTube subscriptions...")
    subscriptions = get_all_subscriptions(youtube)

    if subscriptions is not None:
        print(f"\n✓ Found {len(subscriptions)} subscriptions\n")

        # Display first few subscriptions
        print("First 10 subscriptions:")
        for i, sub in enumerate(subscriptions[:10], 1):
            print(f"  {i}. {sub['channel_title']}")

        if len(subscriptions) > 10:
            print(f"  ... and {len(subscriptions) - 10} more")

        # Save to file
        print()
        save_subscriptions(subscriptions)

        # Also save a simple text list
        with open('subscriptions.txt', 'w', encoding='utf-8') as f:
            for sub in subscriptions:
                f.write(f"{sub['channel_title']}\n")
        print(f"✓ Saved channel names to subscriptions.txt")

        # Save URLs list
        with open('subscription_urls.txt', 'w', encoding='utf-8') as f:
            for sub in subscriptions:
                f.write(f"{sub['channel_url']}\n")
        print(f"✓ Saved channel URLs to subscription_urls.txt")

        print("\nDone! 🎉")
    else:
        print("Failed to fetch subscriptions")


if __name__ == '__main__':
    main()
