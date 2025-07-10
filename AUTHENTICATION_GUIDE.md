# iNaturalist API Authentication Guide

This guide explains how to set up authenticated access to the iNaturalist API for enhanced features. **Note: Authentication is optional - the main script works perfectly without it and can download high-resolution images using predictable URLs.**

## Why Use Authentication?

**Public API (No Authentication) - Default:**
- ✅ No setup required
- ✅ Access to basic observation data
- ✅ Downloads high-resolution images (1920x1080+) using predictable URLs
- ✅ Handles missing/deleted photos gracefully
- ❌ Rate limited to 100 requests per minute
- ❌ No access to private observations

**Authenticated API (OAuth 2.0) - Optional:**
- ✅ Access to full resolution images via direct API URLs
- ✅ Higher rate limits (1000 requests per minute)
- ✅ Access to private observations (if you have permission)
- ✅ Additional metadata fields
- ✅ More reliable access to some photo URLs
- ❌ Requires OAuth application setup

## Method 1: OAuth 2.0 Authentication (Recommended)

### Step 1: Create an OAuth Application

1. **Go to iNaturalist OAuth Applications:**
   ```
   https://www.inaturalist.org/oauth/applications
   ```

2. **Click "New Application"**

3. **Fill in the application details:**
   - **Name**: `iNaturalist Image Downloader` (or your preferred name)
   - **Description**: `Script to download high-resolution images from iNaturalist observations`
   - **Application Type**: `Web`
   - **Redirect URI**: `urn:ietf:wg:oauth:2.0:oob` (for manual code entry)
   - **Scopes**: Check `read` (for read-only access)

4. **Click "Create Application"**

5. **Note your Client ID and Client Secret** (you'll need these for authentication)

### Step 2: Authenticate Using the Helper Script

1. **Run the authentication setup:**
   ```bash
   python inaturalist_auth.py --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET --setup
   ```

2. **Follow the prompts:**
   - The script will open your browser to the iNaturalist authorization page
   - Log in to iNaturalist and authorize your application
   - Copy the authorization code from the page

3. **Complete the authentication:**
   ```bash
   python inaturalist_auth.py --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET --code YOUR_AUTHORIZATION_CODE --save-token
   ```

4. **The script will create a `.env` file** with your authentication tokens

### Step 3: Use the Authenticated Downloader

```bash
# Use the authenticated downloader (automatically loads from .env)
python inaturalist_downloader_auth.py --lat -8.132489362310453 --lon 115.36386760679501 --radius 5

# Or specify the access token directly
python inaturalist_downloader_auth.py --access-token YOUR_ACCESS_TOKEN --lat -8.132489362310453 --lon 115.36386760679501 --radius 5
```

## Method 2: Personal Access Token (Alternative)

If you prefer not to create an OAuth application, you can use a personal access token:

### Step 1: Generate a Personal Access Token

1. **Go to your iNaturalist account settings:**
   ```
   https://www.inaturalist.org/users/edit
   ```

2. **Scroll down to "API Access"**

3. **Click "Generate Token"**

4. **Copy the generated token**

### Step 2: Use the Token

```bash
python inaturalist_downloader_auth.py --access-token YOUR_PERSONAL_TOKEN --lat -8.132489362310453 --lon 115.36386760679501 --radius 5
```

## Method 3: Environment Variables

You can also set authentication via environment variables:

```bash
# Set environment variables
export INATURALIST_ACCESS_TOKEN="your_access_token_here"

# Run the script (it will automatically detect the token)
python inaturalist_downloader_auth.py --lat -8.132489362310453 --lon 115.36386760679501 --radius 5
```

## Token Management

### Refreshing Expired Tokens

OAuth tokens expire after a certain time. To refresh them:

```bash
python inaturalist_auth.py --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET --refresh-token YOUR_REFRESH_TOKEN
```

### Checking Token Status

You can test if your token is still valid:

```bash
python inaturalist_auth.py --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET --refresh-token YOUR_REFRESH_TOKEN
```

## Security Best Practices

1. **Never commit tokens to version control**
   - The `.env` file is automatically created and should be added to `.gitignore`
   - Keep your client secret private

2. **Use minimal scopes**
   - Only request the `read` scope unless you need write access
   - This limits the potential damage if your token is compromised

3. **Rotate tokens regularly**
   - Generate new tokens periodically
   - Delete old tokens when no longer needed

4. **Use environment variables in production**
   - Don't hardcode tokens in scripts
   - Use environment variables or secure secret management

## Troubleshooting

### Common Issues

**"Invalid client_id"**
- Double-check your client ID and secret
- Ensure the OAuth application is properly configured

**"Authorization code expired"**
- Authorization codes expire quickly (usually 10 minutes)
- Generate a new authorization code

**"Invalid redirect_uri"**
- Make sure the redirect URI matches exactly what you configured
- Use `urn:ietf:wg:oauth:2.0:oob` for manual code entry

**"Token expired"**
- Use the refresh token to get a new access token
- Personal access tokens don't expire but can be revoked

**"Rate limit exceeded"**
- Authenticated requests have higher rate limits
- Add delays between requests if needed

### Getting Help

- **iNaturalist API Documentation**: https://www.inaturalist.org/pages/api+reference
- **OAuth 2.0 Documentation**: https://oauth.net/2/
- **iNaturalist Community**: https://forum.inaturalist.org/

## Comparison: Public vs Authenticated API

| Feature | Public API | Authenticated API |
|---------|------------|-------------------|
| **Image Quality** | High resolution (1920x1080+) via predictable URLs | Full resolution via direct API URLs |
| **Rate Limits** | 100 requests/minute | 1000 requests/minute |
| **Setup Complexity** | None | OAuth application required |
| **Image URLs** | Manual construction from photo IDs | Direct URLs from API |
| **Error Handling** | Comprehensive with retry logic | Enhanced with better error messages |
| **API Endpoints** | Limited | Full access |
| **Private Observations** | No access | Access if you have permission |

## Example Usage

### Basic Authenticated Download

```bash
# Download high-resolution images with authentication
python inaturalist_downloader_auth.py \
    --lat -8.132489362310453 \
    --lon 115.36386760679501 \
    --radius 5 \
    --image-quality original \
    --max-observations 100
```

### Filtered Authenticated Download

```bash
# Download only research-grade bird observations with original quality
python inaturalist_downloader_auth.py \
    --lat -8.132489362310453 \
    --lon 115.36386760679501 \
    --radius 5 \
    --iconic-taxon Aves \
    --quality-grade research \
    --image-quality original \
    --max-observations 50
```

### Using Personal Access Token

```bash
# Use personal access token for authentication
python inaturalist_downloader_auth.py \
    --access-token YOUR_PERSONAL_TOKEN \
    --lat -8.132489362310453 \
    --lon 115.36386760679501 \
    --radius 5 \
    --image-quality large
```

## File Structure

After setting up authentication, your project should look like:

```
iNaturalist/
├── inaturalist_downloader.py          # Original script (public API)
├── inaturalist_downloader_auth.py     # Authenticated version
├── inaturalist_auth.py               # Authentication helper
├── .env                              # Authentication tokens (auto-generated)
├── requirements.txt
├── README.md
├── AUTHENTICATION_GUIDE.md           # This file
└── images/                           # Downloaded images
```

## Next Steps

1. **Set up OAuth authentication** using the guide above
2. **Test with a small download** to verify everything works
3. **Download your desired images** with full resolution
4. **Consider rate limiting** for large downloads
5. **Backup your tokens** securely

Happy downloading! 🦋📸 