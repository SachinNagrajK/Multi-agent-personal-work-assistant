# Fix: Wrong OAuth Client Type

## The Problem
Your OAuth client is type **"Web application"** but needs to be **"Desktop app"**.

Error shows: `urn:ietf:wg:oauth:2.0:oob, can only be used by a Client ID for native application`

## Quick Fix (3 minutes)

### Step 1: Delete the Old Client
1. Go to: https://console.cloud.google.com/apis/credentials
2. Find your OAuth 2.0 Client ID
3. Click the trash icon to delete it
4. Confirm deletion

### Step 2: Create New Desktop Client
1. Click **"+ CREATE CREDENTIALS"** → **"OAuth client ID"**
2. **IMPORTANT**: Select **"Desktop app"** (NOT Web application!)
3. Name: `Workspace Assistant Desktop`
4. Click **"CREATE"**

### Step 3: Download New Credentials
1. Click **"DOWNLOAD JSON"** in the popup
2. Save the file
3. **Rename it to exactly:** `credentials.json`
4. **Move it to:** `S:\Studies\Projects\multi-agent-langgraph\backend\credentials.json`
5. **Replace the old file**

### Step 4: Try Again
```powershell
python google_auth.py
```

## Why This Happens
- **Web application** = Uses http://localhost redirects (needs configuration)
- **Desktop app** = Uses special OOB flow (no redirect needed)

For desktop Python scripts, you MUST use "Desktop app" type!

## Visual Guide

When creating credentials, make sure you see:

```
Create OAuth client ID

Application type:
  ○ Web application
  ○ Android
  ○ Chrome app
  ○ iOS
  ● Desktop app          ← SELECT THIS!
  ○ Universal Windows Platform (UWP)

Name: Workspace Assistant Desktop

                [CREATE]
```

Let me know when you have the new credentials.json file!
