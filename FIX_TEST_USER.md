# Fix: Access Denied - Add Test User

## The Problem
Error 403: access_denied - Your app needs Google verification OR you need to add yourself as a test user.

## Quick Fix (2 minutes)

### Step 1: Go to OAuth Consent Screen
1. Open: https://console.cloud.google.com/apis/credentials/consent
2. Make sure your project is selected at the top

### Step 2: Check Publishing Status
You should see:
```
Publishing status: Testing
```

If it says "In production", click **"BACK TO TESTING"**

### Step 3: Add Test Users
1. Scroll down to **"Test users"** section
2. Click **"+ ADD USERS"**
3. Enter your email: **rdravid1777@gmail.com**
4. Click **"ADD"**
5. Click **"SAVE"** at the bottom

### Step 4: Verify Scopes (Optional)
While you're here, click **"EDIT APP"** and go through the steps:
1. App information - should be filled
2. **Scopes** - Click "ADD OR REMOVE SCOPES"
   - Search for "Gmail API" and select:
     - `.../auth/gmail.readonly`
     - `.../auth/gmail.send`
     - `.../auth/gmail.modify`
   - Search for "Calendar API" and select:
     - `.../auth/calendar.readonly`
     - `.../auth/calendar.events`
   - Click "UPDATE"
3. Test users - should show your email now
4. Click "SAVE AND CONTINUE" through all steps

### Step 5: Try Again
```powershell
python google_auth.py
```

## Important Notes

- **Testing mode** = Only test users can use the app (perfect for development)
- **Production mode** = Requires Google verification (takes weeks)
- For your personal use, **Testing mode is fine!**

## Visual Guide

OAuth Consent Screen should look like:

```
Publishing status: Testing     [PUBLISH APP]

Test users:
┌─────────────────────────────────────┐
│ rdravid1777@gmail.com              │
└─────────────────────────────────────┘
     [+ ADD USERS]
```

Let me know when you've added yourself as a test user!
