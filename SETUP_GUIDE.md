# GreenPulse Setup Guide

This guide will help you set up and run the GreenPulse agricultural monitoring backend.

## Prerequisites

1. **Google Cloud Account**
   - You need a Google Cloud account to use Google Earth Engine
   - Earth Engine is free for non-commercial research and education

2. **Python 3.11**
   - Already installed in this Replit environment

## Step-by-Step Setup

### 1. Set Up Google Earth Engine

#### Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select an existing one
3. Note your Project ID (you'll need this later)

#### Enable Earth Engine API
1. In your Google Cloud project, go to APIs & Services
2. Click "Enable APIs and Services"
3. Search for "Earth Engine API"
4. Click "Enable"

#### Authenticate Earth Engine
Open the Shell tab in Replit and run:

```bash
earthengine authenticate
```

This will:
- Open a browser window asking you to sign in with your Google account
- Grant Earth Engine permissions
- Save authentication credentials

**Important**: If the browser doesn't open automatically, copy the URL from the terminal and paste it in your browser.

### 2. Configure Environment Variables

Click the "Secrets" tab (🔒 icon) in Replit and add these secrets:

#### Required:
- **Key**: `GEE_PROJECT_ID`
  - **Value**: Your Google Cloud Project ID (from step 1)

#### Optional (for AI Assistant):
  - **Value**: Your GROQ provider API key
 **Key**: `GROQ_MODEL` (optional)
 **Value**: The GROQ model to use (defaults to "llama‑3.1‑8b‑instant")

### 3. Verify Setup

Once you've added the environment variables:

1. The backend will automatically restart
2. Visit the webview to see the API documentation
3. Click the URL or use the health check endpoint

### 4. Test the API

#### Quick Health Check
```bash
curl https://your-replit-url.replit.dev/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "GreenPulse Backend",
  "earth_engine_initialized": true
}
```

If `earth_engine_initialized` is `false`, check that:
- You've run `earthengine authenticate`
- `GEE_PROJECT_ID` is set correctly in Secrets

#### Test with Real Data

Try the full analysis endpoint with sample coordinates:

```bash
curl -X POST https://your-replit-url.replit.dev/api/full-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "coordinates": [
      [
        [-120.5, 37.0],
        [-120.5, 37.05],
        [-120.45, 37.05],
        [-120.45, 37.0],
        [-120.5, 37.0]
      ]
    ]
  }'
```

## Troubleshooting

### "GEE_PROJECT_ID not set" Warning

**Cause**: The environment variable isn't configured.

**Fix**: 
1. Click the Secrets tab (🔒 icon)
2. Add `GEE_PROJECT_ID` with your Google Cloud Project ID
3. The server will restart automatically

### Earth Engine Authentication Failed

**Cause**: Earth Engine credentials aren't set up.

**Fix**: Run in the Shell tab:
```bash
earthengine authenticate
```

### "Cannot determine project ID" Error

**Cause**: Earth Engine is authenticated but doesn't know which project to use.

**Fix**: Make sure `GEE_PROJECT_ID` is set in Secrets

### AI Assistant Not Working

**Cause**: GROQ API key isn't configured (this is optional).

**Fix**: 
1. Get an API key from your GROQ provider (follow your provider's docs)
2. Add it to Secrets as `GROQ_API_KEY` and optionally set `GROQ_API_URL` if required
3. The AI assistant endpoints will then work

## Finding Agricultural Field Coordinates

To analyze your own fields, you need coordinates in `[longitude, latitude]` format:

1. Go to [Google Earth](https://earth.google.com)
2. Find your field
3. Use the polygon tool to draw around your field
4. Copy the coordinates

Or use [geojson.io](https://geojson.io):
1. Draw a polygon around your field
2. Copy the coordinates from the JSON output
3. Format as needed for the API

## Next Steps

Once setup is complete:

1. **Test all endpoints** - See `examples/api_examples.md` for detailed examples
2. **Integrate with frontend** - Use the API endpoints in your web or mobile app
3. **Set up monitoring** - Track API usage in Google Cloud Console
4. **Deploy to production** - Click the "Deploy" button when ready to publish

## Support

For issues:
- Check the console logs in the Replit workspace
- Review the `README.md` for detailed API documentation
- Verify all environment variables are set correctly
- Ensure Google Earth Engine is properly authenticated

## Important Notes

- **Rate Limits**: Google Earth Engine has usage quotas. Monitor usage in Google Cloud Console.
- **Data Availability**: Results depend on satellite image availability and cloud coverage.
- **Coordinates**: Always use `[longitude, latitude]` format (longitude first!).
- **Dates**: Use `YYYY-MM-DD` format for all date parameters.
