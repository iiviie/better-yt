#!/usr/bin/env python3
"""
YouTube New Channel Discovery
Discovers NEW channels you're not subscribed to based on your interests.
"""

import os
import json
import pickle
from collections import defaultdict
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Scopes required for reading YouTube data
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']

# Configurable settings
MIN_SUBSCRIBERS = 50000  # Minimum subscriber count for quality filter
MAX_CANDIDATES = 50      # Number of candidate channels to analyze


def get_authenticated_service():
    """Authenticate with YouTube using OAuth 2.0."""
    credentials = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            if not os.path.exists('client_secrets.json'):
                print("ERROR: client_secrets.json file not found!")
                print("Run get_subscriptions.py first to set up authentication.")
                return None

            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json', SCOPES)
            credentials = flow.run_local_server(port=8080)

        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)

    return build('youtube', 'v3', credentials=credentials)


def load_subscriptions():
    """Load subscriptions from JSON file."""
    if not os.path.exists('subscriptions.json'):
        print("ERROR: subscriptions.json not found!")
        print("Run get_subscriptions.py first to fetch your subscriptions.")
        return None

    with open('subscriptions.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def get_channel_details(youtube, channel_id):
    """Fetch detailed information about a channel."""
    try:
        request = youtube.channels().list(
            part='snippet,statistics,topicDetails,brandingSettings',
            id=channel_id
        )
        response = request.execute()

        if not response['items']:
            return None

        channel = response['items'][0]
        snippet = channel['snippet']
        stats = channel.get('statistics', {})
        topics = channel.get('topicDetails', {})

        return {
            'channel_id': channel_id,
            'title': snippet['title'],
            'description': snippet.get('description', ''),
            'subscriber_count': int(stats.get('subscriberCount', 0)),
            'video_count': int(stats.get('videoCount', 0)),
            'view_count': int(stats.get('viewCount', 0)),
            'topic_categories': topics.get('topicCategories', []),
            'published_at': snippet.get('publishedAt', ''),
            'thumbnail': snippet['thumbnails'].get('default', {}).get('url', ''),
        }
    except HttpError as e:
        print(f"Error fetching channel details: {e}")
        return None


def get_popular_videos(youtube, channel_id, max_results=10):
    """Get the most popular videos from a channel."""
    try:
        # Search for videos from the channel, ordered by view count
        request = youtube.search().list(
            part='snippet',
            channelId=channel_id,
            maxResults=max_results,
            order='viewCount',
            type='video'
        )
        response = request.execute()

        video_ids = [item['id']['videoId'] for item in response.get('items', [])]

        if not video_ids:
            return []

        # Get detailed stats for these videos
        video_request = youtube.videos().list(
            part='snippet,statistics',
            id=','.join(video_ids)
        )
        video_response = video_request.execute()

        videos = []
        for item in video_response.get('items', []):
            videos.append({
                'video_id': item['id'],
                'title': item['snippet']['title'],
                'description': item['snippet'].get('description', ''),
                'view_count': int(item['statistics'].get('viewCount', 0)),
            })

        return sorted(videos, key=lambda x: x['view_count'], reverse=True)

    except HttpError as e:
        print(f"Error fetching popular videos: {e}")
        return []


def get_related_videos(youtube, video_id, max_results=25):
    """Get related videos for a given video."""
    try:
        request = youtube.search().list(
            part='snippet',
            relatedToVideoId=video_id,
            type='video',
            maxResults=max_results
        )
        response = request.execute()

        related = []
        for item in response.get('items', []):
            related.append({
                'video_id': item['id']['videoId'],
                'channel_id': item['snippet']['channelId'],
                'channel_title': item['snippet']['channelTitle'],
                'title': item['snippet']['title'],
            })

        return related

    except HttpError as e:
        # Related videos endpoint might be deprecated or limited
        return []


def get_recent_videos(youtube, channel_id, max_results=10):
    """Fetch recent videos from a channel."""
    try:
        request = youtube.search().list(
            part='snippet',
            channelId=channel_id,
            maxResults=max_results,
            order='date',
            type='video'
        )
        response = request.execute()

        videos = []
        for item in response.get('items', []):
            videos.append({
                'title': item['snippet']['title'],
                'description': item['snippet']['description']
            })
        return videos
    except HttpError as e:
        return []


def search_by_topics(youtube, topic_categories, max_results=30):
    """Search for channels by topic categories."""
    channels = []

    for topic_url in topic_categories[:3]:  # Limit to top 3 topics
        topic_name = topic_url.split('/')[-1].replace('_', ' ')

        try:
            request = youtube.search().list(
                part='snippet',
                q=topic_name,
                type='channel',
                maxResults=max_results,
                order='relevance'
            )
            response = request.execute()

            for item in response.get('items', []):
                channels.append(item['snippet']['channelId'])

        except HttpError:
            continue

    return list(set(channels))  # Remove duplicates


def calculate_similarity_score(target_channel, candidate_channel, target_videos, candidate_videos):
    """Calculate similarity between two channels."""
    scores = []
    weights = []

    # 1. Topic category overlap
    target_topics = set(target_channel.get('topic_categories', []))
    candidate_topics = set(candidate_channel.get('topic_categories', []))

    if target_topics and candidate_topics:
        topic_overlap = len(target_topics & candidate_topics) / len(target_topics | candidate_topics)
        scores.append(topic_overlap)
        weights.append(0.35)

    # 2. Video content similarity
    target_content = ' '.join([f"{v['title']} {v.get('description', '')}" for v in target_videos])
    candidate_content = ' '.join([f"{v['title']} {v.get('description', '')}" for v in candidate_videos])

    if target_content and candidate_content and len(target_content) > 50 and len(candidate_content) > 50:
        try:
            vectorizer = TfidfVectorizer(stop_words='english', max_features=100, min_df=1)
            tfidf_matrix = vectorizer.fit_transform([target_content, candidate_content])
            content_similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            scores.append(content_similarity)
            weights.append(0.45)
        except:
            pass

    # 3. Subscriber count similarity (logarithmic scale)
    target_subs = target_channel.get('subscriber_count', 0)
    candidate_subs = candidate_channel.get('subscriber_count', 0)

    if target_subs > 0 and candidate_subs > 0:
        log_ratio = abs(np.log10(max(target_subs, 1)) - np.log10(max(candidate_subs, 1)))
        sub_similarity = max(0, 1 - (log_ratio / 3))
        scores.append(sub_similarity)
        weights.append(0.20)

    if not scores or sum(weights) == 0:
        return 0.0

    total_weight = sum(weights)
    weighted_score = sum(s * w for s, w in zip(scores, weights)) / total_weight

    return weighted_score


def discover_new_channels(youtube, channel_name, subscriptions, min_subs=MIN_SUBSCRIBERS, top_n=15):
    """
    Discover new channels based on a seed channel.
    Uses multiple discovery methods to find quality channels.
    """
    # Find the target channel
    target_channel_id = None
    for sub in subscriptions:
        if sub['channel_title'].lower() == channel_name.lower():
            target_channel_id = sub['channel_id']
            break

    if not target_channel_id:
        print(f"Channel '{channel_name}' not found in your subscriptions!")
        return None

    subscribed_ids = {sub['channel_id'] for sub in subscriptions}

    print(f"\n🔍 Discovering new channels similar to '{channel_name}'...")

    # Get target channel details
    target_details = get_channel_details(youtube, target_channel_id)
    if not target_details:
        print("Failed to fetch channel details")
        return None

    print(f"✓ Analyzing '{target_details['title']}'")
    print(f"✓ Subscribers: {target_details['subscriber_count']:,}")

    target_videos = get_recent_videos(youtube, target_channel_id, max_results=10)

    # Discovery Method 1: Related videos from popular content
    print(f"\n📹 Finding channels through popular video recommendations...")
    popular_videos = get_popular_videos(youtube, target_channel_id, max_results=5)

    candidate_channels = defaultdict(int)

    for i, video in enumerate(popular_videos[:3], 1):
        print(f"  Analyzing video {i}/{min(3, len(popular_videos))}: {video['title'][:50]}...")
        related = get_related_videos(youtube, video['video_id'], max_results=25)

        for rel in related:
            if rel['channel_id'] not in subscribed_ids and rel['channel_id'] != target_channel_id:
                candidate_channels[rel['channel_id']] += 1

    # Discovery Method 2: Topic-based search
    print(f"\n🏷️  Searching by topic categories...")
    if target_details.get('topic_categories'):
        topic_channels = search_by_topics(youtube, target_details['topic_categories'], max_results=20)
        for ch_id in topic_channels:
            if ch_id not in subscribed_ids and ch_id != target_channel_id:
                candidate_channels[ch_id] += 1

    # Sort candidates by frequency (how many times they appeared)
    sorted_candidates = sorted(candidate_channels.items(), key=lambda x: x[1], reverse=True)

    print(f"\n✓ Found {len(sorted_candidates)} potential channels")
    print(f"\n📊 Analyzing and filtering channels (min {min_subs:,} subscribers)...")

    # Analyze and score candidates
    recommendations = []
    analyzed = 0

    for channel_id, frequency in sorted_candidates[:MAX_CANDIDATES]:
        analyzed += 1
        print(f"  Analyzing {analyzed}/{min(MAX_CANDIDATES, len(sorted_candidates))}...", end='\r')

        details = get_channel_details(youtube, channel_id)
        if not details:
            continue

        # Quality filters
        if details['subscriber_count'] < min_subs:
            continue

        if details['video_count'] < 10:  # At least 10 videos
            continue

        # Get recent videos for similarity calculation
        candidate_videos = get_recent_videos(youtube, channel_id, max_results=10)

        # Calculate similarity
        similarity = calculate_similarity_score(
            target_details, details,
            target_videos, candidate_videos
        )

        # Boost score if channel appeared multiple times
        discovery_boost = min(frequency / 3, 0.2)  # Max 20% boost
        final_score = min(similarity + discovery_boost, 1.0)

        if final_score > 0.2:  # Minimum similarity threshold
            recommendations.append({
                'channel_id': channel_id,
                'channel_title': details['title'],
                'channel_url': f"https://www.youtube.com/channel/{channel_id}",
                'description': details['description'][:200] + '...' if len(details['description']) > 200 else details['description'],
                'subscriber_count': details['subscriber_count'],
                'video_count': details['video_count'],
                'similarity_score': final_score,
                'discovery_frequency': frequency,
                'topic_categories': details.get('topic_categories', []),
                'published_at': details.get('published_at', ''),
            })

    print(" " * 50, end='\r')

    # Sort by similarity score
    recommendations.sort(key=lambda x: x['similarity_score'], reverse=True)

    return recommendations[:top_n]


def main():
    print("=" * 70)
    print("YouTube NEW Channel Discovery")
    print("Find channels you're NOT subscribed to yet!")
    print("=" * 70)

    # Load subscriptions
    subscriptions = load_subscriptions()
    if not subscriptions:
        return

    # Get authenticated YouTube service
    youtube = get_authenticated_service()
    if not youtube:
        return

    # Get user input
    print(f"\nYou have {len(subscriptions)} subscriptions.")
    print("\nEnter a channel name to discover similar channels:")
    print("(or type 'list' to see all your subscriptions)\n")

    channel_name = input("Channel name: ").strip()

    if channel_name.lower() == 'list':
        print("\nYour subscriptions:")
        for i, sub in enumerate(subscriptions, 1):
            print(f"  {i}. {sub['channel_title']}")
        print()
        channel_name = input("Channel name: ").strip()

    # Optional: ask for minimum subscriber count
    print(f"\nMinimum subscriber count for recommendations (default: {MIN_SUBSCRIBERS:,})")
    min_subs_input = input(f"Press Enter for default, or enter a number: ").strip()

    min_subs = MIN_SUBSCRIBERS
    if min_subs_input.isdigit():
        min_subs = int(min_subs_input)

    # Discover channels
    recommendations = discover_new_channels(
        youtube, channel_name, subscriptions,
        min_subs=min_subs, top_n=15
    )

    if not recommendations:
        print("\n❌ No new channels found.")
        print("   Try lowering the minimum subscriber count or try a different seed channel.")
        return

    # Display recommendations
    print(f"\n✨ Discovered {len(recommendations)} NEW channels similar to '{channel_name}':\n")
    print("=" * 70)

    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec['channel_title']}")
        print(f"   🎯 Similarity: {rec['similarity_score']*100:.1f}%")
        print(f"   👥 Subscribers: {rec['subscriber_count']:,}")
        print(f"   🎥 Videos: {rec['video_count']:,}")
        print(f"   🔄 Found {rec['discovery_frequency']} times during discovery")

        if rec['topic_categories']:
            topics = [t.split('/')[-1].replace('_', ' ') for t in rec['topic_categories'][:2]]
            print(f"   📂 Topics: {', '.join(topics)}")

        print(f"   🔗 {rec['channel_url']}")

        if rec['description']:
            print(f"   📝 {rec['description'][:150]}...")

    # Save recommendations
    output_file = f"new_channels_{channel_name.replace(' ', '_')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'seed_channel': channel_name,
            'min_subscribers': min_subs,
            'discovered_channels': recommendations
        }, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Recommendations saved to {output_file}")
    print("\n" + "=" * 70)
    print("\n💡 These are NEW channels you're not subscribed to yet!")
    print(f"   All have at least {min_subs:,} subscribers.\n")


if __name__ == '__main__':
    main()
