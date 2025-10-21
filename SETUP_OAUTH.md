# How to Get OAuth Credentials (One-Time Setup)

This is a **one-time setup** that you (the developer) need to do. Your users will then just click "Allow" in their browser.

## Step-by-Step Guide

### 1. Go to Google Cloud Console
Visit: https://console.cloud.google.com/

### 2. Create a New Project
- Click the project dropdown at the top left
- Click "New Project"
- Name it (e.g., "YouTube Subscriptions App")
- Click "Create"

### 3. Enable YouTube Data API v3
- In the left sidebar, go to **"APIs & Services"** > **"Library"**
- Search for **"YouTube Data API v3"**
- Click on it and press **"Enable"**

### 4. Configure OAuth Consent Screen
- Go to **"APIs & Services"** > **"OAuth consent screen"**
- Choose **"External"** (unless you have a Google Workspace account)
- Click **"Create"**

Fill in the required fields:
- **App name**: "YouTube Subscriptions Fetcher" (or whatever you want)
- **User support email**: Your email
- **Developer contact email**: Your email
- Click **"Save and Continue"**

On the **Scopes** page:
- Click **"Save and Continue"** (no need to add scopes manually here)

On the **Test users** page:
- Click **"+ Add Users"**
- Add your Gmail address (and any other users who will test this)
- Click **"Save and Continue"**

### 5. Create OAuth Client ID
- Go to **"APIs & Services"** > **"Credentials"**
- Click **"+ Create Credentials"** at the top
- Select **"OAuth client ID"**
- Choose **"Desktop app"** as the application type
- Name it (e.g., "Desktop Client")
- Click **"Create"**

### 6. Download the Credentials
- A dialog will appear with your Client ID and Secret
- Click **"Download JSON"**
- Save the downloaded file as **`client_secrets.json`** in the same folder as `get_subscriptions.py`

## Security Notes

⚠️ **IMPORTANT**:
- Keep `client_secrets.json` private
- Add it to `.gitignore` if using git
- Do NOT share it publicly or commit it to version control

## Done!

Now users can simply run:
```bash
python get_subscriptions.py
```

The script will:
1. Open their browser
2. Ask them to sign in with Google
3. Ask them to click "Allow"
4. Save their credentials for future use (in `token.pickle`)

Next time they run it, they won't need to authorize again!
