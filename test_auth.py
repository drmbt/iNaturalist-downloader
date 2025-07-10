#!/usr/bin/env python3
"""
Test script to verify iNaturalist API authentication is working properly.
"""

import os
import sys
import requests
from dotenv import load_dotenv

def test_public_api():
    """Test public API access."""
    try:
        response = requests.get("https://api.inaturalist.org/v1/observations", 
                             params={'per_page': 1}, timeout=10)
        if response.status_code == 200:
            print("✅ Public API access working")
            return True
        else:
            print(f"❌ Public API returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Public API test failed: {e}")
        return False

def test_authenticated_api(access_token):
    """Test authenticated API access."""
    try:
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get("https://api.inaturalist.org/v1/users/me", 
                             headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Authenticated API access working")
            print(f"   Authenticated as: {user_data.get('login', 'Unknown')}")
            return True
        else:
            print(f"❌ Authenticated API returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Authenticated API test failed: {e}")
        return False

def test_high_resolution_images(access_token):
    """Test access to high resolution images."""
    try:
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Get a single observation with photos
        response = requests.get("https://api.inaturalist.org/v1/observations", 
                             params={'per_page': 1, 'has_photos': True},
                             headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('results') and data['results'][0].get('photos'):
                photo = data['results'][0]['photos'][0]
                
                # Check if we have access to original_url (high resolution)
                if photo.get('original_url'):
                    print("✅ High resolution image access working")
                    print(f"   Original URL available: {photo['original_url'][:50]}...")
                    return True
                else:
                    print("⚠️  No high resolution URLs in response")
                    return False
            else:
                print("⚠️  No photos found in test observation")
                return False
        else:
            print(f"❌ Failed to get test observation: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ High resolution image test failed: {e}")
        return False

def main():
    """Run authentication tests."""
    print("Testing iNaturalist API Authentication")
    print("=" * 50)
    
    # Test public API
    print("\n1. Testing Public API Access...")
    public_ok = test_public_api()
    
    # Load environment variables
    load_dotenv()
    access_token = os.getenv('INATURALIST_ACCESS_TOKEN')
    
    if not access_token:
        print("\n2. Testing Authenticated API Access...")
        print("❌ No access token found in .env file")
        print("   Run the authentication setup first:")
        print("   python inaturalist_auth.py --client-id YOUR_ID --client-secret YOUR_SECRET --setup")
        return
    
    print("\n2. Testing Authenticated API Access...")
    auth_ok = test_authenticated_api(access_token)
    
    if auth_ok:
        print("\n3. Testing High Resolution Image Access...")
        high_res_ok = test_high_resolution_images(access_token)
        
        print("\n" + "=" * 50)
        print("SUMMARY:")
        print(f"Public API: {'✅ Working' if public_ok else '❌ Failed'}")
        print(f"Authenticated API: {'✅ Working' if auth_ok else '❌ Failed'}")
        print(f"High Resolution Images: {'✅ Working' if high_res_ok else '❌ Failed'}")
        
        if public_ok and auth_ok and high_res_ok:
            print("\n🎉 All tests passed! You're ready to download high-resolution images.")
        else:
            print("\n⚠️  Some tests failed. Check the authentication setup.")
    else:
        print("\n❌ Authentication failed. Please check your access token.")

if __name__ == "__main__":
    main() 