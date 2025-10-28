# New Channel Discovery Guide

## Overview

`discover_new_channels.py` finds **NEW** channels you're not subscribed to yet, based on a channel you already like.

## How It Works

The script uses multiple discovery methods:

### 1. **Video-Based Discovery** (Primary method)
- Gets the most popular videos from your seed channel
- Finds "related videos" for those popular videos
- Extracts the channels that made those related videos
- Channels that appear multiple times get boosted in ranking

### 2. **Topic-Based Discovery** (Secondary method)
- Analyzes the seed channel's topic categories
- Searches YouTube for other channels in those categories
- Filters by relevance and quality

### 3. **Quality Filtering**
- Minimum subscriber count (default: 50,000)
- Must have at least 10 videos
- Active channels only
- Excludes channels you're already subscribed to

### 4. **Similarity Scoring**
- Compares video content (titles and descriptions)
- Matches topic categories
- Considers channel size similarity
- Boosts channels that appeared multiple times during discovery

## Usage

### Basic Usage

```bash
python discover_new_channels.py
```

Then enter a channel name from your subscriptions:
```
Channel name: Veritasium
```

Press Enter to use default minimum subscriber count (50,000).

### Custom Subscriber Threshold

You can adjust the minimum subscriber count:

```
Minimum subscriber count for recommendations (default: 50,000)
Press Enter for default, or enter a number: 10000
```

**Examples:**
- `100000` - Only well-established channels
- `10000` - Include smaller but growing channels
- `1000` - Discover hidden gems (may include lower quality)

## Understanding Results

### Output Format

```
1. Channel Name
   🎯 Similarity: 65.3%        ← How similar to your seed channel
   👥 Subscribers: 2,500,000   ← Channel size
   🎥 Videos: 450              ← Total video count
   🔄 Found 3 times            ← How many times discovered (higher = more relevant)
   📂 Topics: Knowledge, Science
   🔗 https://youtube.com/...
   📝 Channel description...
```

### Similarity Score Breakdown

- **60-100%**: Very similar content and style
- **40-59%**: Similar topics, good match
- **20-39%**: Related content, worth exploring

### Discovery Frequency

The "Found X times" metric indicates how many different discovery methods found this channel:
- **3+ times**: Highly relevant, strongly recommended
- **2 times**: Good match, appeared in multiple searches
- **1 time**: Still relevant but less common

## Tips for Best Results

### 1. Choose Good Seed Channels
- Use well-established channels (not tiny ones)
- Channels with clear niches work best
- More popular channels = better related video data

### 2. Adjust Subscriber Threshold Based on Niche
- **Tech/Science**: 50k-100k works well
- **Gaming**: Can go higher (100k+)
- **Niche topics**: Lower threshold (10k-25k)
- **Educational**: 25k-75k sweet spot

### 3. Try Multiple Seed Channels
Different channels in the same genre might discover different recommendations:

```bash
# Try multiple seeds for comprehensive discovery
python discover_new_channels.py  # Seed: Veritasium
python discover_new_channels.py  # Seed: Kurzgesagt
python discover_new_channels.py  # Seed: Mark Rober
```

### 4. Combine Results
Compare the JSON outputs to find channels that appear across multiple discoveries - these are usually the best matches!

## API Quota Management

### Daily Quota: 10,000 units

**Typical usage per discovery session:**
- Popular videos fetch: ~10 units
- Related videos (3 videos × 25 each): ~75 units
- Topic search: ~30 units
- Channel details (50 channels): ~50 units
- Video details for similarity: ~100 units

**Total per session: ~250-300 units**

You can run discovery **30-40 times per day** before hitting quota limits.

### If You Hit Quota Limit

1. **Wait 24 hours** - Quota resets at midnight Pacific Time
2. **Create a new Google Cloud project** with new credentials
3. **Reduce MAX_CANDIDATES** in the script (line 22)

### Quota-Saving Tips

- Lower the minimum subscriber threshold initially
- Use specific seed channels (not generic ones)
- Don't run discovery repeatedly for the same channel

## Customization

You can edit `discover_new_channels.py` to customize:

```python
# Line 22-23: Discovery settings
MIN_SUBSCRIBERS = 50000  # Minimum subscriber count
MAX_CANDIDATES = 50      # How many channels to analyze
```

**Recommendations:**
- `MIN_SUBSCRIBERS`: 10,000 - 200,000 depending on niche
- `MAX_CANDIDATES`: 30-100 (higher = more results but more API quota)

## Output Files

Results are saved to:
```
new_channels_[SeedChannelName].json
```

This file contains:
- Seed channel name
- Minimum subscriber threshold used
- List of discovered channels with full details
- Similarity scores and discovery frequency

## Example Workflow

1. **Fetch your subscriptions first:**
   ```bash
   python get_subscriptions.py
   ```

2. **Discover new channels:**
   ```bash
   python discover_new_channels.py
   ```

3. **Enter your favorite channel:**
   ```
   Channel name: Veritasium
   Minimum subscribers: [Enter]
   ```

4. **Review results** and visit interesting channels

5. **Try another seed** for more discoveries

## Troubleshooting

### "No new channels found"
- **Lower the minimum subscriber count**
- Try a more popular seed channel
- The seed channel might be too niche
- Check if you've hit API quota

### "Quota exceeded"
- Wait 24 hours for quota reset
- Or create a new Google Cloud project

### Getting low-quality recommendations
- **Increase** minimum subscriber count
- Use more established seed channels
- Look for higher similarity scores (>40%)

### Channels seem unrelated
- The seed channel might have broad topics
- Try a more specialized seed channel
- Adjust weights in similarity calculation (advanced)

## Advanced: Comparing with Your Subscriptions

Want to see which NEW discoveries are most similar to your existing tastes?

1. Run `recommend_channels.py` for the same seed
2. Run `discover_new_channels.py` for the same seed
3. Compare the similarity scores
4. High-scoring NEW channels are likely great matches!

## Privacy Note

All discovery happens through official YouTube API. No data is stored except:
- Your local `token.pickle` (OAuth credentials)
- Output JSON files (channel information)

No personal data is sent anywhere except to YouTube's official API for authentication and queries.
