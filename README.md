# Better YouTube Tools

A collection of Python scripts for YouTube channel management and discovery. Find your subscriptions and discover similar channels - all with simple OAuth authentication!

## Features

- ✅ **Subscription Fetcher**: Get all your YouTube subscriptions
- ✅ **Channel Recommendations**: Find similar channels from your existing subscriptions
- ✅ **NEW Channel Discovery**: Discover channels you're NOT subscribed to yet!
- ✅ Simple OAuth 2.0 authentication (just click "Allow" in browser)
- ✅ Smart content similarity analysis using TF-IDF and topic matching
- ✅ Quality filters (minimum subscribers, active channels only)
- ✅ Saves credentials for future use (no re-authentication needed)
- ✅ Exports to JSON, TXT, and URL formats

## For Developers: One-Time Setup

If you're setting this up for the first time, you need to create OAuth credentials. See **[SETUP_OAUTH.md](SETUP_OAUTH.md)** for detailed instructions.

**Quick version:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project and enable YouTube Data API v3
3. Create OAuth 2.0 credentials (Desktop app)
4. Download the JSON file and save as `client_secrets.json`

## For Users: How to Use

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Your Subscriptions

```bash
python get_subscriptions.py
```

- Your browser will open automatically
- Sign in with your Google account
- Click "Allow" to grant access
- Your subscriptions will be saved to JSON/TXT files

### 3. Find Similar Channels in Your Subscriptions

```bash
python recommend_channels.py
```

- Enter a channel name from your subscriptions
- Compares with ALL your other subscriptions
- Shows top 10 most similar channels you already follow

### 4. Discover NEW Channels (The Main Feature!)

```bash
python discover_new_channels.py
```

- Enter a channel name as your "seed" (what you like)
- Analyzes that channel's popular videos
- Finds related videos and extracts their channels
- Searches by topic categories
- Filters for quality (default: 50k+ subscribers)
- Returns 10-15 NEW channels you're not subscribed to!

**This is what you wanted!** Real channel discovery beyond your subscriptions.

### 5. Next Time

The next time you run any script, you won't need to authorize again. Your credentials are saved in `token.pickle`.

## Output Files

**From get_subscriptions.py:**
- **subscriptions.json** - Full subscription details (channel ID, description, thumbnail, etc.)
- **subscriptions.txt** - Simple list of channel names
- **subscription_urls.txt** - List of channel URLs

**From recommend_channels.py:**
- **recommendations_[ChannelName].json** - Similar channels from your subscriptions

**From discover_new_channels.py:**
- **new_channels_[ChannelName].json** - NEW channels to discover (not in your subscriptions)

## Project Structure

```
better-yt/
├── get_subscriptions.py      # Fetch your subscriptions
├── recommend_channels.py     # Find similar channels from your subs
├── discover_new_channels.py  # 🌟 Discover NEW channels (main feature!)
├── requirements.txt          # Python dependencies
├── SETUP_OAUTH.md           # OAuth setup guide
├── RECOMMENDATION_GUIDE.md  # Recommendation system guide
├── client_secrets.json      # OAuth credentials (you create this)
├── token.pickle             # Saved user credentials (auto-generated)
├── subscriptions.json       # Output: Your subscriptions
├── subscriptions.txt        # Output: Channel names
├── recommendations_*.json   # Output: Similar channels from your subs
└── new_channels_*.json      # Output: NEW channel discoveries
```

## Security & Privacy

- **client_secrets.json** - Keep this private (developer only)
- **token.pickle** - User's personal credentials (don't share)
- Add both to `.gitignore` if using version control

## Troubleshooting

**"client_secrets.json file not found!"**
- You need to create OAuth credentials first
- See [SETUP_OAUTH.md](SETUP_OAUTH.md) for instructions

**"Access blocked: This app's request is invalid"**
- Make sure you added your email as a test user in the OAuth consent screen
- The app might be in "Testing" mode (which is fine for personal use)

**Browser doesn't open automatically**
- Copy the URL from the terminal and paste it in your browser manually

**"Token has been expired or revoked"**
- Delete `token.pickle` and run the script again to re-authenticate

## How It Works

1. Script checks for existing credentials (`token.pickle`)
2. If none exist, opens browser for OAuth authorization
3. User signs in and clicks "Allow"
4. Script saves credentials for future use
5. Fetches all subscriptions using YouTube Data API v3
6. Saves to multiple output formats

## API Quota

YouTube API has a daily quota of 10,000 units. This script uses approximately 1 unit per 50 subscriptions, so you can fetch subscriptions many times per day without issues.
