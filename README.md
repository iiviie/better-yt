# Better YouTube Tools

A collection of Python scripts for YouTube channel management and discovery. Find your subscriptions and discover similar channels - all with simple OAuth authentication!

## Features

- ✅ **Subscription Fetcher**: Get all your YouTube subscriptions
- ✅ **Channel Recommendations**: Find similar channels based on content analysis
- ✅ Simple OAuth 2.0 authentication (just click "Allow" in browser)
- ✅ Saves credentials for future use (no re-authentication needed)
- ✅ Exports to JSON, TXT, and URL formats
- ✅ User-friendly - no technical knowledge required for end users

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

### 3. Find Similar Channels (Optional)

```bash
python recommend_channels.py
```

- Enter a channel name from your subscriptions
- The script will analyze the channel and find similar ones
- Get top 10 recommendations with similarity scores

See **[RECOMMENDATION_GUIDE.md](RECOMMENDATION_GUIDE.md)** for detailed usage.

### 4. Next Time

The next time you run either script, you won't need to authorize again. Your credentials are saved in `token.pickle`.

## Output Files

**From get_subscriptions.py:**
- **subscriptions.json** - Full subscription details (channel ID, description, thumbnail, etc.)
- **subscriptions.txt** - Simple list of channel names
- **subscription_urls.txt** - List of channel URLs

**From recommend_channels.py:**
- **recommendations_[ChannelName].json** - Similar channels with similarity scores and details

## Project Structure

```
better-yt/
├── get_subscriptions.py      # Fetch your subscriptions
├── recommend_channels.py     # Find similar channels
├── requirements.txt          # Python dependencies
├── SETUP_OAUTH.md           # OAuth setup guide
├── RECOMMENDATION_GUIDE.md  # Recommendation system guide
├── client_secrets.json      # OAuth credentials (you create this)
├── token.pickle             # Saved user credentials (auto-generated)
├── subscriptions.json       # Output: Your subscriptions
├── subscriptions.txt        # Output: Channel names
└── recommendations_*.json   # Output: Channel recommendations
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
