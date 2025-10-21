#!/usr/bin/env python3
"""
YouTube Channel Recommendation System
Finds similar channels by analyzing your existing subscriptions.
"""

import os
import json
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Scopes required for reading YouTube data
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']


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
    """
    Fetch detailed information about a channel.

    Returns:
        dict: Channel details including category, tags, subscriber count, etc.
    """
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
        branding = channel.get('brandingSettings', {})

        return {
            'channel_id': channel_id,
            'title': snippet['title'],
            'description': snippet.get('description', ''),
            'category': branding.get('channel', {}).get('keywords', ''),
            'subscriber_count': int(stats.get('subscriberCount', 0)),
            'video_count': int(stats.get('videoCount', 0)),
            'view_count': int(stats.get('viewCount', 0)),
            'topic_categories': topics.get('topicCategories', []),
            'country': snippet.get('country', ''),
            'custom_url': snippet.get('customUrl', ''),
        }
    except HttpError as e:
        print(f"Error fetching channel details: {e}")
        return None


def get_recent_videos(youtube, channel_id, max_results=10):
    """Fetch recent videos from a channel to analyze content."""
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
        print(f"Error fetching videos: {e}")
        return []


def calculate_similarity_score(target_channel, candidate_channel, target_videos, candidate_videos):
    """
    Calculate similarity between two channels using multiple factors.

    Returns:
        float: Similarity score between 0 and 1
    """
    scores = []
    weights = []

    # 1. Topic category overlap (most important)
    target_topics = set(target_channel.get('topic_categories', []))
    candidate_topics = set(candidate_channel.get('topic_categories', []))

    if target_topics and candidate_topics:
        topic_overlap = len(target_topics & candidate_topics) / len(target_topics | candidate_topics)
        scores.append(topic_overlap)
        weights.append(0.35)  # Increased weight

    # 2. Video content similarity (titles + descriptions)
    target_content = ' '.join([f"{v['title']} {v['description']}" for v in target_videos])
    candidate_content = ' '.join([f"{v['title']} {v['description']}" for v in candidate_videos])

    if target_content and candidate_content and len(target_content) > 50 and len(candidate_content) > 50:
        try:
            vectorizer = TfidfVectorizer(stop_words='english', max_features=100, min_df=1)
            tfidf_matrix = vectorizer.fit_transform([target_content, candidate_content])
            content_similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            scores.append(content_similarity)
            weights.append(0.40)  # Increased weight
        except:
            pass

    # 3. Subscriber count similarity (penalize huge differences)
    target_subs = target_channel.get('subscriber_count', 0)
    candidate_subs = candidate_channel.get('subscriber_count', 0)

    if target_subs > 0 and candidate_subs > 0:
        # Use log scale and be more forgiving of size differences
        log_ratio = abs(np.log10(max(target_subs, 1)) - np.log10(max(candidate_subs, 1)))
        # Convert to similarity (0 = identical, 3+ = very different)
        sub_similarity = max(0, 1 - (log_ratio / 3))
        scores.append(sub_similarity)
        weights.append(0.15)

    # 4. Upload frequency similarity
    target_videos_count = target_channel.get('video_count', 0)
    candidate_videos_count = candidate_channel.get('video_count', 0)

    if target_videos_count > 0 and candidate_videos_count > 0:
        video_ratio = min(target_videos_count, candidate_videos_count) / max(target_videos_count, candidate_videos_count)
        scores.append(video_ratio ** 0.5)
        weights.append(0.10)

    # Calculate weighted average
    if not scores or sum(weights) == 0:
        return 0.0

    total_weight = sum(weights)
    weighted_score = sum(s * w for s, w in zip(scores, weights)) / total_weight

    return weighted_score


def find_similar_channels_in_subscriptions(youtube, channel_name, subscriptions, top_n=10):
    """
    Find similar channels from your existing subscriptions.
    This guarantees quality channels you might already know about!
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

    print(f"\n🎯 Analyzing '{channel_name}' and comparing with your {len(subscriptions)-1} other subscriptions...")

    # Get detailed info about target channel
    target_details = get_channel_details(youtube, target_channel_id)
    if not target_details:
        print("Failed to fetch channel details")
        return None

    print(f"✓ Category: {target_details.get('topic_categories', ['Unknown'])[0].split('/')[-1] if target_details.get('topic_categories') else 'Unknown'}")
    print(f"✓ Subscribers: {target_details.get('subscriber_count', 0):,}")

    # Get recent videos
    print("✓ Fetching recent videos for content analysis...")
    target_videos = get_recent_videos(youtube, target_channel_id, max_results=10)

    # Compare with all other subscriptions
    print(f"\n📊 Comparing with your subscriptions (this may take a minute)...")

    recommendations = []
    total = len(subscriptions) - 1  # Exclude target channel
    processed = 0

    for i, sub in enumerate(subscriptions):
        if sub['channel_id'] == target_channel_id:
            continue

        processed += 1
        print(f"  Analyzing {processed}/{total}...", end='\r')

        # Get details for this subscription
        candidate_details = get_channel_details(youtube, sub['channel_id'])
        if not candidate_details:
            continue

        candidate_videos = get_recent_videos(youtube, sub['channel_id'], max_results=10)

        # Calculate similarity
        similarity = calculate_similarity_score(
            target_details, candidate_details,
            target_videos, candidate_videos
        )

        if similarity > 0.15:  # Only include meaningful similarities
            recommendations.append({
                'channel_id': sub['channel_id'],
                'channel_title': candidate_details['title'],
                'channel_url': f"https://www.youtube.com/channel/{sub['channel_id']}",
                'description': candidate_details['description'][:200] + '...' if len(candidate_details['description']) > 200 else candidate_details['description'],
                'subscriber_count': candidate_details['subscriber_count'],
                'similarity_score': similarity,
                'topic_categories': candidate_details.get('topic_categories', []),
                'video_count': candidate_details.get('video_count', 0)
            })

    print(" " * 50, end='\r')  # Clear progress line

    # Sort by similarity
    recommendations.sort(key=lambda x: x['similarity_score'], reverse=True)

    return recommendations[:top_n]


def main():
    print("=" * 70)
    print("YouTube Channel Recommendation System")
    print("Finds similar channels from your existing subscriptions")
    print("=" * 70)

    # Load subscriptions
    subscriptions = load_subscriptions()
    if not subscriptions:
        return

    # Get authenticated YouTube service
    youtube = get_authenticated_service()
    if not youtube:
        return

    # Get channel name from user
    print(f"\nYou have {len(subscriptions)} subscriptions.")
    print("\nEnter a channel name to find similar channels:")
    print("(or type 'list' to see all your subscriptions)\n")

    channel_name = input("Channel name: ").strip()

    if channel_name.lower() == 'list':
        print("\nYour subscriptions:")
        for i, sub in enumerate(subscriptions, 1):
            print(f"  {i}. {sub['channel_title']}")
        print()
        channel_name = input("Channel name: ").strip()

    # Find similar channels
    recommendations = find_similar_channels_in_subscriptions(
        youtube, channel_name, subscriptions, top_n=10
    )

    if not recommendations:
        print("\n❌ No similar channels found in your subscriptions.")
        print("   Try a different channel, or you might want to discover new channels!")
        return

    # Display recommendations
    print(f"\n✨ Top {len(recommendations)} channels from YOUR subscriptions similar to '{channel_name}':\n")
    print("=" * 70)

    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec['channel_title']}")
        print(f"   🎯 Similarity: {rec['similarity_score']*100:.1f}%")
        print(f"   👥 Subscribers: {rec['subscriber_count']:,}")
        print(f"   🎥 Videos: {rec['video_count']:,}")

        if rec['topic_categories']:
            topics = [t.split('/')[-1] for t in rec['topic_categories'][:3]]
            print(f"   📂 Topics: {', '.join(topics)}")

        print(f"   🔗 {rec['channel_url']}")

    # Save recommendations
    output_file = f"recommendations_{channel_name.replace(' ', '_')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'target_channel': channel_name,
            'source': 'existing_subscriptions',
            'recommendations': recommendations
        }, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Recommendations saved to {output_file}")
    print("\n" + "=" * 70)
    print("\n💡 Tip: These are channels YOU already subscribe to!")
    print("   If you want to discover NEW channels, let me know and I'll")
    print("   add a feature to search beyond your subscriptions.\n")


if __name__ == '__main__':
    main()
