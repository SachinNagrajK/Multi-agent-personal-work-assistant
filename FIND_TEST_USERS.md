# Finding Test Users Section - Detailed Steps

## Method 1: Direct Link
Try this direct link (make sure your project is selected):
https://console.cloud.google.com/apis/credentials/consent/edit

## Method 2: Step-by-Step Navigation

### Step 1: Get to OAuth Consent Screen
1. Go to: https://console.cloud.google.com/apis/credentials
2. In the left menu, click **"OAuth consent screen"** (NOT "Credentials")

### Step 2: Click "EDIT APP"
- You should see a button that says **"EDIT APP"** 
- Click it

### Step 3: Navigate Through the Form
You'll see a multi-step form:

**Step 1: App information**
- Just click "SAVE AND CONTINUE" at bottom

**Step 2: Scopes**
- Just click "SAVE AND CONTINUE" at bottom

**Step 3: Test users** ← THIS IS WHERE YOU ADD USERS!
- Here you'll see:
  ```
  Test users
  Add up to 100 test users while publishing status is "Testing"
  
  [+ ADD USERS]
  ```
- Click **"+ ADD USERS"**
- Enter: `rdravid1777@gmail.com`
- Click "Add"
- Click "SAVE" at the bottom

**Step 4: Summary**
- Click "BACK TO DASHBOARD"

## Alternative: Check if Already in Testing Mode

If you don't see "EDIT APP", look for:
```
Publishing status: In production
```

If it says "In production", click **"BACK TO TESTING"** or **"UNPUBLISH APP"** first.

## Screenshot Reference

You should be looking for a page that has these elements:
```
OAuth consent screen

App name: Workspace Assistant
User type: External
Publishing status: Testing    [PUBLISH APP]

[EDIT APP]  ← Click this button
```

Let me know which step you're stuck on!
