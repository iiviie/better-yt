# YouTube Channel Recommendation System Guide

## How to Use

### 1. Install Dependencies

First, make sure you have the new dependencies installed:

```bash
pip install -r requirements.txt
```

### 2. Run the Recommendation Script

```bash
python recommend_channels.py
```

### 3. Enter a Channel Name

When prompted, enter the name of a channel from your subscriptions:

```
Channel name: Veritasium
```

Or type `list` to see all your subscribed channels first.

### 4. View Results

The script will:
- Analyze the target channel's content, category, and metadata
- Search for similar channels on YouTube
- Calculate similarity scores based on:
  - Description/keyword matching (30% weight)
  - Topic category overlap (25% weight)
  - Video content similarity (30% weight)
  - Subscriber count range (15% weight)
- Show top 10 most similar channels with similarity percentages

## Understanding the Results

### Similarity Score
- **80-100%**: Very similar content and style
- **60-79%**: Similar topics and audience
- **40-59%**: Some overlap in content
- **20-39%**: Loosely related
- **0-19%**: Minimal similarity

### What Gets Compared
1. **Channel Description**: Keywords and topics mentioned
2. **Video Titles**: What kind of content they make
3. **Categories**: YouTube's topic classifications
4. **Channel Size**: Similar subscriber counts (similar reach/production quality)

## Output Files

Results are saved to:
```
recommendations_[ChannelName].json
```

This JSON file contains:
- Target channel name
- List of recommended channels with full details
- Similarity scores
- Channel URLs and descriptions

## Tips for Best Results

1. **Use well-established channels**: Channels with more videos and metadata give better recommendations
2. **Try different channels**: Different channels in your subscriptions will yield different recommendations
3. **Check subscriber counts**: The script finds channels of similar size (small YouTubers get small recommendations, big ones get big recommendations)
4. **Filter results**: You might want to manually filter out very small channels or adjust the minimum subscriber threshold

## Customization

You can edit `recommend_channels.py` to:
- Change the number of recommendations (default: 10)
- Adjust similarity weights
- Add minimum subscriber count filter
- Change the number of candidates analyzed

## API Quota Usage

The script uses YouTube API quota:
- ~1 unit per channel detail fetch
- Analyzing 20 candidates = ~40-50 API units
- Daily quota: 10,000 units
- You can run this ~200 times per day

## Troubleshooting

**"No similar channels found"**
- The channel might be too niche
- Try a more popular channel from your subscriptions
- The search might not have found good candidates

**Getting low-quality recommendations**
- This is normal - YouTube search returns all channels, including small ones
- Look for channels with higher subscriber counts in the results
- The similarity score is what matters most

**API quota exceeded**
- Wait 24 hours for quota to reset
- Or create a new Google Cloud project
