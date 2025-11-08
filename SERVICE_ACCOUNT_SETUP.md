# Service Account Setup for Google Earth Engine (No Browser Required!)

This guide shows you how to set up Google Earth Engine authentication without needing to open a browser tab. This is perfect for cloud environments like Replit.

## Why Use Service Account Authentication?

✅ **No browser needed** - Perfect for cloud/server environments  
✅ **More secure** - Credentials stored as secrets  
✅ **Automated** - No manual authentication steps  
✅ **Production-ready** - Recommended for deployed applications

---

## Step-by-Step Setup

### Step 1: Create a Service Account

1. **Go to Google Cloud Console**  
   Visit: https://console.cloud.google.com

2. **Select your project**  
   (The one you created for Earth Engine)

3. **Navigate to Service Accounts**  
   - Click the menu (☰) → **IAM & Admin** → **Service Accounts**

4. **Create Service Account**  
   - Click **"+ Create Service Account"**
   - **Name**: `greenpulse-backend`
   - **Description**: `Service account for GreenPulse Earth Engine access`
   - Click **"Create and Continue"**

5. **Grant Permissions**  
   - Click **"Select a role"**
   - Search for and select: **"Earth Engine Resource Viewer"**
   - Click **"Continue"**
   - Click **"Done"**

### Step 2: Create and Download Private Key

1. **Find your service account** in the list
2. Click on it to open details
3. Go to the **"KEYS"** tab
4. Click **"Add Key"** → **"Create new key"**
5. Select **JSON** format
6. Click **"Create"**
7. **Save the downloaded JSON file** - you'll need it in the next step

The file will look something like `greenpulse-backend-abc123.json`

### Step 3: Register Service Account with Earth Engine

1. **Visit Earth Engine Service Account Registration**  
   https://signup.earthengine.google.com/#!/service_accounts

2. **Enter your service account email**  
   - Open the JSON file you downloaded
   - Find the `client_email` field
   - Copy the email (looks like: `greenpulse-backend@your-project.iam.gserviceaccount.com`)
   - Paste it in the registration form

3. **Click "Register"**

### Step 4: Add Credentials to Replit Secrets

1. **Open the JSON file** you downloaded in a text editor
2. **Copy the ENTIRE content** (everything from `{` to `}`)

3. **In Replit**:
   - Click the **Tools** icon (four squares 📱) on the left
   - Select **"Secrets"** (lock icon 🔒)
   - Click **"New Secret"**

4. **Add the service account key**:
   - **Key**: `GEE_SERVICE_ACCOUNT_KEY`
   - **Value**: Paste the entire JSON content
   - Click **"Add Secret"**

5. **Add your project ID**:
   - Click **"New Secret"** again
   - **Key**: `GEE_PROJECT_ID`
   - **Value**: Your Google Cloud project ID
   - Click **"Add Secret"**

### Step 5: Test It!

The backend will automatically restart and use the service account. No browser authentication needed!

Check the logs - you should see:
```
Earth Engine initialized with service account: greenpulse-backend@your-project.iam.gserviceaccount.com
```

---

## Troubleshooting

### Error: "Service account not registered"

**Fix**: Make sure you completed Step 3 (registering the service account email at signup.earthengine.google.com)

### Error: "Invalid credentials"

**Fix**: 
- Verify you copied the ENTIRE JSON file content
- Make sure there are no extra spaces or characters
- The JSON must be valid

### Error: "Permission denied"

**Fix**: 
- Ensure the service account has "Earth Engine Resource Viewer" role
- Wait a few minutes for permissions to propagate

### Still seeing browser authentication prompts?

**Fix**: The service account setup isn't complete. Double-check:
1. JSON key is added to Secrets as `GEE_SERVICE_ACCOUNT_KEY`
2. Project ID is added to Secrets as `GEE_PROJECT_ID`
3. Service account is registered at signup.earthengine.google.com

---

## What's in the JSON Key File?

The service account key contains:
```json
{
  "type": "service_account",
  "project_id": "your-project",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...",
  "client_email": "greenpulse-backend@your-project.iam.gserviceaccount.com",
  "client_id": "...",
  ...
}
```

**Important**: Keep this file secure! It's like a password for your Earth Engine access.

---

## Security Best Practices

✅ **Do**:
- Store the JSON key in Replit Secrets (encrypted)
- Rotate keys periodically (create new key, delete old one)
- Use different service accounts for dev/production

❌ **Don't**:
- Commit the JSON file to git
- Share the private key publicly
- Store it in plain text files

---

## Quick Reference

**Service Account Email Format**:
```
service-account-name@project-id.iam.gserviceaccount.com
```

**Required Secrets in Replit**:
- `GEE_SERVICE_ACCOUNT_KEY` = Full JSON content
- `GEE_PROJECT_ID` = Your Google Cloud project ID

**Registration URL**:
https://signup.earthengine.google.com/#!/service_accounts

---

That's it! Your backend will now authenticate automatically without any browser interaction. 🎉
