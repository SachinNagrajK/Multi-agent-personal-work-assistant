# Google API Setup Guide

## Step 1: Create Google Cloud Project (5 minutes)

1. **Go to Google Cloud Console**:
   - Open: https://console.cloud.google.com/

2. **Create a New Project**:
   - Click "Select a project" dropdown at the top
   - Click "New Project"
   - Project name: `workspace-assistant` (or any name you like)
   - Click "Create"
   - Wait for the project to be created

3. **Select Your Project**:
   - Make sure your new project is selected in the dropdown

## Step 2: Enable APIs (3 minutes)

1. **Enable Gmail API**:
   - Go to: https://console.cloud.google.com/apis/library/gmail.googleapis.com
   - Click "Enable"
   - Wait for it to complete

2. **Enable Google Calendar API**:
   - Go to: https://console.cloud.google.com/apis/library/calendar-json.googleapis.com
   - Click "Enable"
   - Wait for it to complete

3. **Enable Google Drive API** (Optional for now):
   - Go to: https://console.cloud.google.com/apis/library/drive.googleapis.com
   - Click "Enable"

## Step 3: Configure OAuth Consent Screen (5 minutes)

1. **Go to OAuth Consent Screen**:
   - Navigate to: https://console.cloud.google.com/apis/credentials/consent
   
2. **Choose User Type**:
   - Select "External" (unless you have a Google Workspace account)
   - Click "Create"

3. **Fill in App Information**:
   - App name: `Workspace Assistant`
   - User support email: (select your email)
   - Developer contact email: (your email)
   - Click "Save and Continue"

4. **Scopes** (Step 2 of 4):
   - Click "Add or Remove Scopes"
   - Search and select:
     - `Gmail API` → `.../auth/gmail.readonly`
     - `Gmail API` → `.../auth/gmail.send`
     - `Gmail API` → `.../auth/gmail.modify`
     - `Calendar API` → `.../auth/calendar.readonly`
     - `Calendar API` → `.../auth/calendar.events`
   - Click "Update"
   - Click "Save and Continue"

5. **Test Users** (Step 3 of 4):
   - Click "Add Users"
   - Enter YOUR Gmail address
   - Click "Add"
   - Click "Save and Continue"

6. **Summary** (Step 4 of 4):
   - Review and click "Back to Dashboard"

## Step 4: Create OAuth Credentials (3 minutes)

1. **Go to Credentials**:
   - Navigate to: https://console.cloud.google.com/apis/credentials

2. **Create OAuth Client ID**:
   - Click "Create Credentials" → "OAuth client ID"
   - Application type: "Desktop app"
   - Name: `Workspace Assistant Desktop`
   - Click "Create"

3. **Download Credentials**:
   - A popup will show your Client ID and Secret
   - Click "Download JSON"
   - **IMPORTANT**: Save this file as `credentials.json`
   - Move it to: `S:\Studies\Projects\multi-agent-langgraph\backend\credentials.json`

## Step 5: Test the Connection (2 minutes)

1. **Run the test script**:
   ```powershell
   cd S:\Studies\Projects\multi-agent-langgraph\backend
   python google_auth.py
   ```

2. **Authorize the app**:
   - A browser window will open automatically
   - Sign in with your Google account (the one you added as a test user)
   - Click "Continue" when it says "Google hasn't verified this app"
   - Select ALL the permissions requested
   - Click "Continue"

3. **Check the output**:
   - You should see:
     ```
     ✅ Gmail connected!
        Email: your-email@gmail.com
        Total messages: 1234
     
     ✅ Calendar connected!
        Found 3 calendar(s)
        - Calendar 1
        - Calendar 2
        - Calendar 3
     
     ✅ All connections successful!
     ```

## Troubleshooting

### "Access blocked: This app's request is invalid"
- Make sure you completed the OAuth Consent Screen setup
- Add yourself as a test user
- Enable the APIs (Gmail, Calendar)

### "credentials.json not found"
- Make sure you downloaded the file from Google Cloud Console
- Rename it to exactly `credentials.json` (not `client_secret_xxx.json`)
- Place it in `backend/` folder

### "Invalid scope"
- Go back to OAuth Consent Screen
- Add the required scopes in "Scopes" section
- Save and try again

### Browser doesn't open
- Check if the script printed a URL
- Copy and paste the URL manually into your browser
- Complete the authorization
- Copy the authorization code back to the terminal

## Security Notes

⚠️ **IMPORTANT**:
- `credentials.json` contains client ID and secret - DO NOT commit to Git
- `token.pickle` contains your access token - DO NOT commit to Git
- Both files are in `.gitignore` already

## Next Steps

Once you see "All connections successful!", you're ready to:
1. Implement real Gmail tools
2. Implement real Calendar tools
3. Test with your actual data

## Quick Reference

**Files created**:
- `backend/credentials.json` - OAuth client credentials (from Google Cloud Console)
- `backend/token.pickle` - Your access token (created automatically)
- `backend/google_auth.py` - Authentication utility (already created)

**APIs enabled**:
- Gmail API - Read, send, modify emails
- Calendar API - Read, create, modify events
- Drive API - Read files (optional)

**Scopes granted**:
- `gmail.readonly` - Read your emails
- `gmail.send` - Send emails on your behalf
- `gmail.modify` - Modify emails (labels, etc.)
- `calendar.readonly` - Read calendar events
- `calendar.events` - Create/modify calendar events

Let me know when you have `credentials.json` in the backend folder, and I'll help you test the connection!
