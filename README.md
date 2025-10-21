# YouTube Subscriptions Fetcher

A Python script to retrieve all YouTube subscriptions from your account using the YouTube Data API v3.

## Setup

### 1. Get a YouTube API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the YouTube Data API v3:
   - Navigate to "APIs & Services" > "Library"
   - Search for "YouTube Data API v3"
   - Click "Enable"
4. Create credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "API Key"
   - Copy your API key

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API key:
   ```
   YOUTUBE_API_KEY=your_actual_api_key_here
   ```

## Usage

Run the script:

```bash
python get_subscriptions.py
```

The script will:
- Fetch all your YouTube subscriptions
- Display the first 5 subscriptions in the console
- Save detailed information to `subscriptions.json`
- Save a simple list of channel names to `subscriptions.txt`

## Output Files

- **subscriptions.json** - Full subscription data including channel IDs, descriptions, thumbnails, etc.
- **subscriptions.txt** - Simple text list of channel names

## Authentication Note

This script uses an API key which requires you to be authenticated with your Google account when using the API. The `mine=True` parameter in the API call fetches subscriptions for the authenticated user.

For better authentication (OAuth 2.0), you would need to modify the script to use OAuth flow instead of just an API key.

## Troubleshooting

- **"Please set your YOUTUBE_API_KEY"**: Make sure you created a `.env` file with your API key
- **HTTP 403 Error**: Your API key might be invalid or the YouTube Data API v3 is not enabled for your project
- **No subscriptions returned**: You may need to use OAuth 2.0 authentication instead of just an API key
