# Fix OAuth "redirect_uri_mismatch" Error

## The Problem
You're seeing: **Error 400: redirect_uri_mismatch**

This means the redirect URI used by the app doesn't match what's configured in Google Cloud Console.

## Quick Fix (2 minutes)

### Step 1: Go to Google Cloud Console Credentials
1. Open: https://console.cloud.google.com/apis/credentials
2. Find your OAuth 2.0 Client ID (should be named "Workspace Assistant Desktop")
3. Click on it to edit

### Step 2: Add Authorized Redirect URIs
In the "Authorized redirect URIs" section, add BOTH of these:

```
http://localhost:8080/
http://localhost:8080
```

**Important**: Add both with AND without the trailing slash!

### Step 3: Save
- Click "SAVE" at the bottom
- Wait a few seconds for changes to propagate

### Step 4: Try Again
```powershell
python google_auth.py
```

## Alternative: Use Manual Copy-Paste Flow

If the above doesn't work, I can switch to a manual flow where you:
1. Get a URL from the script
2. Open it in your browser
3. Copy the authorization code
4. Paste it back into the terminal

Let me know if you want this backup option!

## What Changed

I updated the code to use port **8080** explicitly instead of a random port. This makes the redirect URI predictable: `http://localhost:8080/`

## Visual Guide

When editing the OAuth client in Google Cloud Console, you should see:

```
Application type: Desktop app
Name: Workspace Assistant Desktop

Authorized redirect URIs:
┌──────────────────────────────────┐
│ http://localhost:8080/           │  ← Add this
│ http://localhost:8080            │  ← And this
└──────────────────────────────────┘
       [+ ADD URI]

                [SAVE]
```

## Still Not Working?

If you still get the error:

1. **Check the exact error message** - It should show what redirect URI it's trying to use
2. **Make sure you saved** the changes in Google Cloud Console
3. **Wait 1-2 minutes** after saving (changes take time to propagate)
4. **Try again** - Run `python google_auth.py`

Or let me know and I'll switch to the manual authorization flow!
