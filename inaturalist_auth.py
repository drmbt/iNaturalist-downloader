#!/usr/bin/env python3
"""
iNaturalist API Authentication Helper

This script demonstrates how to authenticate with the iNaturalist API using OAuth 2.0.
This provides access to higher resolution images and additional API features.

Usage:
    python inaturalist_auth.py --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET
"""

import argparse
import json
import os
import requests
import webbrowser
from urllib.parse import urlencode
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class iNaturalistAuth:
    """Handles OAuth 2.0 authentication with iNaturalist API."""
    
    def __init__(self):
        self.auth_url = "https://www.inaturalist.org/oauth/authorize"
        self.token_url = "https://www.inaturalist.org/oauth/token"
        self.api_base = "https://api.inaturalist.org/v1"
        
    def get_authorization_url(self, client_id: str, redirect_uri: str = "urn:ietf:wg:oauth:2.0:oob") -> str:
        """
        Generate the authorization URL for OAuth 2.0.
        
        Args:
            client_id: Your OAuth application client ID
            redirect_uri: Redirect URI (default: urn:ietf:wg:oauth:2.0:oob for manual entry)
            
        Returns:
            Authorization URL to open in browser
        """
        params = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': 'read'  # Read-only access
        }
        
        return f"{self.auth_url}?{urlencode(params)}"
    
    def get_access_token(self, client_id: str, client_secret: str, authorization_code: str, 
                        redirect_uri: str = "urn:ietf:wg:oauth:2.0:oob") -> dict:
        """
        Exchange authorization code for access token.
        
        Args:
            client_id: Your OAuth application client ID
            client_secret: Your OAuth application client secret
            authorization_code: Code received from authorization step
            redirect_uri: Redirect URI (must match authorization request)
            
        Returns:
            Dictionary containing access token and other OAuth data
        """
        data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'code': authorization_code,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        response = requests.post(self.token_url, data=data)
        response.raise_for_status()
        
        return response.json()
    
    def refresh_access_token(self, client_id: str, client_secret: str, refresh_token: str) -> dict:
        """
        Refresh an expired access token.
        
        Args:
            client_id: Your OAuth application client ID
            client_secret: Your OAuth application client secret
            refresh_token: Refresh token from previous authentication
            
        Returns:
            Dictionary containing new access token and refresh token
        """
        data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        
        response = requests.post(self.token_url, data=data)
        response.raise_for_status()
        
        return response.json()
    
    def test_authenticated_request(self, access_token: str) -> dict:
        """
        Test the authenticated API access.
        
        Args:
            access_token: Valid access token
            
        Returns:
            User information from API
        """
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(f"{self.api_base}/users/me", headers=headers)
        response.raise_for_status()
        
        return response.json()

def main():
    """Main function to handle OAuth authentication."""
    parser = argparse.ArgumentParser(
        description="Authenticate with iNaturalist API using OAuth 2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # First time setup - get authorization URL
  python inaturalist_auth.py --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET --setup
  
  # Complete authentication with authorization code
  python inaturalist_auth.py --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET --code AUTHORIZATION_CODE
  
  # Refresh existing token
  python inaturalist_auth.py --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET --refresh-token REFRESH_TOKEN
        """
    )
    
    parser.add_argument('--client-id', required=True,
                       help='Your iNaturalist OAuth application client ID')
    parser.add_argument('--client-secret', required=True,
                       help='Your iNaturalist OAuth application client secret')
    parser.add_argument('--setup', action='store_true',
                       help='Generate authorization URL for first-time setup')
    parser.add_argument('--code',
                       help='Authorization code from browser (for completing setup)')
    parser.add_argument('--refresh-token',
                       help='Refresh token for renewing access')
    parser.add_argument('--save-token', action='store_true',
                       help='Save token to .env file for future use')
    
    args = parser.parse_args()
    
    auth = iNaturalistAuth()
    
    if args.setup:
        # Generate authorization URL
        auth_url = auth.get_authorization_url(args.client_id)
        print(f"\n🔗 Authorization URL:")
        print(f"{auth_url}")
        print(f"\n📋 Please:")
        print(f"1. Open this URL in your browser")
        print(f"2. Log in to iNaturalist and authorize the application")
        print(f"3. Copy the authorization code from the page")
        print(f"4. Run this script again with --code YOUR_CODE")
        
        # Try to open browser automatically
        try:
            webbrowser.open(auth_url)
            print(f"\n🌐 Browser opened automatically!")
        except:
            print(f"\n📝 Please manually open the URL above in your browser")
    
    elif args.code:
        # Complete authentication with authorization code
        try:
            token_data = auth.get_access_token(args.client_id, args.client_secret, args.code)
            
            print(f"\n✅ Authentication successful!")
            print(f"Access Token: {token_data['access_token'][:20]}...")
            print(f"Refresh Token: {token_data['refresh_token'][:20]}...")
            print(f"Expires In: {token_data['expires_in']} seconds")
            
            # Test the token
            user_info = auth.test_authenticated_request(token_data['access_token'])
            print(f"\n👤 Authenticated as: {user_info.get('login', 'Unknown')}")
            
            # Save token if requested
            if args.save_token:
                env_content = f"""# iNaturalist API Authentication
INATURALIST_CLIENT_ID={args.client_id}
INATURALIST_CLIENT_SECRET={args.client_secret}
INATURALIST_ACCESS_TOKEN={token_data['access_token']}
INATURALIST_REFRESH_TOKEN={token_data['refresh_token']}
INATURALIST_TOKEN_EXPIRES_IN={token_data['expires_in']}
"""
                with open('.env', 'w') as f:
                    f.write(env_content)
                print(f"\n💾 Token saved to .env file")
            
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
    
    elif args.refresh_token:
        # Refresh existing token
        try:
            token_data = auth.refresh_access_token(args.client_id, args.client_secret, args.refresh_token)
            
            print(f"\n✅ Token refreshed successfully!")
            print(f"New Access Token: {token_data['access_token'][:20]}...")
            print(f"New Refresh Token: {token_data['refresh_token'][:20]}...")
            print(f"Expires In: {token_data['expires_in']} seconds")
            
            # Test the new token
            user_info = auth.test_authenticated_request(token_data['access_token'])
            print(f"\n👤 Authenticated as: {user_info.get('login', 'Unknown')}")
            
        except Exception as e:
            print(f"❌ Token refresh failed: {e}")
    
    else:
        print("❌ Please specify either --setup, --code, or --refresh-token")
        parser.print_help()

if __name__ == "__main__":
    main() 