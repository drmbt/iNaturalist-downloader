#!/usr/bin/env python3
"""
iNaturalist Authenticated Image Downloader

This script downloads images from iNaturalist observations within a specified radius
of a given location and compiles metadata about identified species into a JSON file.
This version supports OAuth 2.0 authentication for access to higher resolution images.

Default location: Les village, Bali, Indonesia - home to Sea Communities and site of Dinacon 2025
Coordinates: -8.132489362310453, 115.36386760679501

Usage:
    python inaturalist_downloader_auth.py  # Uses default Les village coordinates
    python inaturalist_downloader_auth.py --lat -8.132489362310453 --lon 115.36386760679501 --radius 5
    python inaturalist_downloader_auth.py --lat -8.132489362310453 --lon 115.36386760679501 --radius 5 --output metadata.json
"""

import argparse
import json
import os
import requests
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class iNaturalistAuthenticatedDownloader:
    """Class to handle authenticated iNaturalist API interactions and image downloads."""
    
    def __init__(self, access_token: str = None):
        self.base_url = "https://api.inaturalist.org/v1"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'iNaturalist-Authenticated-Downloader/1.0 (https://github.com/your-repo)'
        })
        
        # Add authentication if token provided
        if access_token:
            self.session.headers.update({
                'Authorization': f'Bearer {access_token}'
            })
            logger.info("Using authenticated API access")
        else:
            logger.info("Using public API access (limited features)")
    
    def get_observations(self, lat: float, lon: float, radius_km: float, 
                        per_page: int = 200, quality_grade: str = None,
                        iconic_taxon_id: int = None, observed_since: str = None,
                        observed_before: str = None, captive: bool = None,
                        introduced: bool = None, threatened: bool = None,
                        endemic: bool = None, native: bool = None) -> List[Dict[str, Any]]:
        """
        Fetch observations within the specified radius using authenticated API.
        
        Args:
            lat: Latitude of the center point
            lon: Longitude of the center point
            radius_km: Radius in kilometers
            per_page: Number of results per page
            quality_grade: Filter by quality grade (research, needs_id, casual)
            iconic_taxon_id: Filter by iconic taxon (e.g., 1=Animalia, 47126=Plantae, 47158=Insecta)
            observed_since: Filter observations since this date (YYYY-MM-DD)
            observed_before: Filter observations before this date (YYYY-MM-DD)
            captive: Filter by captive/cultivated status
            introduced: Filter by introduced species
            threatened: Filter by threatened species
            endemic: Filter by endemic species
            native: Filter by native species
            
        Returns:
            List of observation dictionaries with full photo URLs
        """
        observations = []
        page = 1
        
        while True:
            params = {
                'lat': lat,
                'lng': lon,
                'radius': radius_km,
                'per_page': per_page,
                'page': page,
                'has_photos': True,  # Only get observations with photos
                'identified': True,   # Only get identified observations
                'order': 'created',   # Sort by creation date
                'order_by': 'desc'
            }
            
            # Add optional filters
            if quality_grade:
                params['quality_grade'] = quality_grade
            if iconic_taxon_id:
                params['iconic_taxon_id'] = iconic_taxon_id
            if observed_since:
                params['observed_since'] = observed_since
            if observed_before:
                params['observed_before'] = observed_before
            if captive is not None:
                params['captive'] = captive
            if introduced is not None:
                params['introduced'] = introduced
            if threatened is not None:
                params['threatened'] = threatened
            if endemic is not None:
                params['endemic'] = endemic
            if native is not None:
                params['native'] = native
            
            try:
                response = self.session.get(f"{self.base_url}/observations", params=params)
                response.raise_for_status()
                data = response.json()
                
                if not data.get('results'):
                    break
                
                observations.extend(data['results'])
                logger.info(f"Fetched page {page} with {len(data['results'])} observations")
                
                # Check if we've reached the end
                if len(data['results']) < per_page:
                    break
                    
                page += 1
                
                # Rate limiting - be respectful to the API
                time.sleep(0.5)
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Error fetching observations: {e}")
                break
        
        logger.info(f"Total observations fetched: {len(observations)}")
        return observations
    
    def get_observation_details(self, observation_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific observation including full photo URLs.
        
        Args:
            observation_id: The ID of the observation
            
        Returns:
            Detailed observation dictionary or None if failed
        """
        try:
            response = self.session.get(f"{self.base_url}/observations/{observation_id}")
            response.raise_for_status()
            data = response.json()
            
            if data.get('results'):
                return data['results'][0]
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching observation {observation_id}: {e}")
            return None
    
    def download_image(self, image_url: str, output_dir: str, filename: str) -> Optional[str]:
        """
        Download an image from the given URL.
        
        Args:
            image_url: URL of the image to download
            output_dir: Directory to save the image
            filename: Name for the saved file
            
        Returns:
            Path to the downloaded file or None if failed
        """
        try:
            response = self.session.get(image_url, stream=True)
            response.raise_for_status()
            
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Downloaded: {filename}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to download {image_url}: {e}")
            return None
    
    def extract_species_metadata(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract relevant metadata about the species from an observation.
        
        Args:
            observation: Observation dictionary from the API
            
        Returns:
            Dictionary containing species metadata
        """
        metadata = {
            'observation_id': observation.get('id'),
            'observed_on': observation.get('observed_on'),
            'time_observed_at': observation.get('time_observed_at'),
            'created_at': observation.get('created_at'),
            'updated_at': observation.get('updated_at'),
            'latitude': observation.get('latitude'),
            'longitude': observation.get('longitude'),
            'positional_accuracy': observation.get('positional_accuracy'),
            'public_positional_accuracy': observation.get('public_positional_accuracy'),
            'quality_grade': observation.get('quality_grade'),
            'num_identification_agreements': observation.get('num_identification_agreements'),
            'num_identification_disagreements': observation.get('num_identification_disagreements'),
            'captive_cultivated': observation.get('captive_cultivated'),
            'description': observation.get('description'),
            'place_guess': observation.get('place_guess'),
            'geoprivacy': observation.get('geoprivacy'),
            'obscured': observation.get('obscured'),
            'mappable': observation.get('mappable'),
            'license_code': observation.get('license_code'),
            'uri': observation.get('uri'),
            'user': {
                'id': observation.get('user', {}).get('id'),
                'login': observation.get('user', {}).get('login'),
                'name': observation.get('user', {}).get('name'),
                'observations_count': observation.get('user', {}).get('observations_count'),
                'species_count': observation.get('user', {}).get('species_count')
            },
            'photos': [],
            'species': None,
            'identifications': [],
            'comments_count': observation.get('comments_count'),
            'faves_count': observation.get('faves_count'),
            'tags': observation.get('tags', [])
        }
        
        # Extract species information
        if observation.get('taxon'):
            taxon = observation['taxon']
            metadata['species'] = {
                'id': taxon.get('id'),
                'name': taxon.get('name'),
                'preferred_common_name': taxon.get('preferred_common_name'),
                'english_common_name': taxon.get('english_common_name'),
                'rank': taxon.get('rank'),
                'rank_level': taxon.get('rank_level'),
                'ancestry': taxon.get('ancestry'),
                'is_active': taxon.get('is_active'),
                'conservation_status': taxon.get('conservation_status'),
                'conservation_status_name': taxon.get('conservation_status_name'),
                'iconic_taxon_id': taxon.get('iconic_taxon_id'),
                'iconic_taxon_name': taxon.get('iconic_taxon_name'),
                'wikipedia_url': taxon.get('wikipedia_url'),
                'extinct': taxon.get('extinct'),
                'introduced': taxon.get('introduced'),
                'native': taxon.get('native'),
                'endemic': taxon.get('endemic'),
                'threatened': taxon.get('threatened'),
                'observations_count': taxon.get('observations_count'),
                'default_photo': taxon.get('default_photo')
            }
        
        # Extract photo information with full URLs (if authenticated)
        if observation.get('photos'):
            for i, photo in enumerate(observation['photos']):
                photo_info = {
                    'id': photo.get('id'),
                    'license_code': photo.get('license_code'),
                    'url': photo.get('url'),
                    'original_url': photo.get('original_url'),
                    'large_url': photo.get('large_url'),
                    'medium_url': photo.get('medium_url'),
                    'small_url': photo.get('small_url'),
                    'square_url': photo.get('square_url'),
                    'original_dimensions': photo.get('original_dimensions'),
                    'attribution': photo.get('attribution'),
                    'native_page_url': photo.get('native_page_url'),
                    'native_photo_id': photo.get('native_photo_id'),
                    'type': photo.get('type'),
                    'flags': photo.get('flags', []),
                    'moderator_actions': photo.get('moderator_actions', []),
                    'hidden': photo.get('hidden', False)
                }
                metadata['photos'].append(photo_info)
        
        # Extract identification information
        if observation.get('identifications'):
            for ident in observation['identifications']:
                ident_info = {
                    'id': ident.get('id'),
                    'user': {
                        'id': ident.get('user', {}).get('id'),
                        'login': ident.get('user', {}).get('login'),
                        'name': ident.get('user', {}).get('name')
                    },
                    'taxon_id': ident.get('taxon_id'),
                    'body': ident.get('body'),
                    'category': ident.get('category'),
                    'current': ident.get('current'),
                    'vision': ident.get('vision'),
                    'created_at': ident.get('created_at')
                }
                metadata['identifications'].append(ident_info)
        
        return metadata

def load_env_vars():
    """Load environment variables from .env file if it exists."""
    env_vars = {}
    
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    
    return env_vars

def main():
    """Main function to handle CLI arguments and execute the download process."""
    parser = argparse.ArgumentParser(
        description="Download iNaturalist images with authenticated API access",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use with OAuth token from .env file
  python inaturalist_downloader_auth.py --lat -8.132489362310453 --lon 115.36386760679501 --radius 5
  
  # Use with explicit access token
  python inaturalist_downloader_auth.py --access-token YOUR_TOKEN --lat -8.132489362310453 --lon 115.36386760679501 --radius 5
  
  # Use without authentication (public API)
  python inaturalist_downloader_auth.py --no-auth --lat -8.132489362310453 --lon 115.36386760679501 --radius 5
        """
    )
    
    # Authentication arguments
    parser.add_argument('--access-token',
                       help='OAuth access token for authenticated API access')
    parser.add_argument('--no-auth', action='store_true',
                       help='Use public API without authentication')
    parser.add_argument('--use-env', action='store_true', default=True,
                       help='Load authentication from .env file (default: True)')
    
    # Standard arguments
    parser.add_argument('--lat', type=float, default=-8.132489362310453,
                       help='Latitude of the center point (default: Les village, Bali)')
    parser.add_argument('--lon', type=float, default=115.36386760679501,
                       help='Longitude of the center point (default: Les village, Bali)')
    parser.add_argument('--radius', type=float, default=5.0,
                       help='Radius in miles (will be converted to kilometers, default: 5)')
    parser.add_argument('--output', type=str, default='inaturalist_metadata.json',
                       help='Output JSON file for metadata (default: inaturalist_metadata.json)')
    parser.add_argument('--images-dir', type=str, default='./images',
                       help='Directory to save downloaded images (default: ./images)')
    parser.add_argument('--download-images', action='store_true', default=True,
                       help='Download images (default: True)')
    parser.add_argument('--max-observations', type=int, default=None,
                       help='Maximum number of observations to process (default: all)')
    parser.add_argument('--image-quality', type=str, default='best',
                       choices=['original', 'large', 'medium', 'small'],
                       help='Image quality to download (default: best - tries original, then large, then url)')
    
    # Additional filtering options
    parser.add_argument('--quality-grade', type=str, choices=['research', 'needs_id', 'casual'],
                       help='Filter by observation quality grade')
    parser.add_argument('--iconic-taxon', type=str, choices=['Animalia', 'Plantae', 'Insecta', 'Aves', 'Mammalia', 'Reptilia', 'Amphibia', 'Mollusca', 'Arachnida', 'Fungi'],
                       help='Filter by iconic taxon (e.g., Animalia, Plantae, Insecta)')
    parser.add_argument('--observed-since', type=str,
                       help='Filter observations since this date (YYYY-MM-DD)')
    parser.add_argument('--observed-before', type=str,
                       help='Filter observations before this date (YYYY-MM-DD)')
    parser.add_argument('--captive-only', action='store_true',
                       help='Only include captive/cultivated observations')
    parser.add_argument('--wild-only', action='store_true',
                       help='Only include wild observations (exclude captive/cultivated)')
    parser.add_argument('--introduced-only', action='store_true',
                       help='Only include introduced species')
    parser.add_argument('--native-only', action='store_true',
                       help='Only include native species')
    parser.add_argument('--threatened-only', action='store_true',
                       help='Only include threatened species')
    parser.add_argument('--endemic-only', action='store_true',
                       help='Only include endemic species')
    
    args = parser.parse_args()
    
    # Determine access token
    access_token = None
    
    if args.no_auth:
        logger.info("Using public API access")
    elif args.access_token:
        access_token = args.access_token
        logger.info("Using provided access token")
    elif args.use_env:
        env_vars = load_env_vars()
        access_token = env_vars.get('INATURALIST_ACCESS_TOKEN')
        if access_token:
            logger.info("Using access token from .env file")
        else:
            logger.info("No access token found in .env file, using public API")
    
    # Convert radius from miles to kilometers
    radius_km = args.radius * 1.60934
    
    # Create output directory for images
    if args.download_images:
        os.makedirs(args.images_dir, exist_ok=True)
        logger.info(f"Images will be saved to: {args.images_dir}")
    
    # Initialize downloader
    downloader = iNaturalistAuthenticatedDownloader(access_token)
    
    # Map iconic taxon names to IDs
    iconic_taxon_map = {
        'Animalia': 1, 'Plantae': 47126, 'Insecta': 47158, 'Aves': 3,
        'Mammalia': 40151, 'Reptilia': 26036, 'Amphibia': 20978,
        'Mollusca': 47115, 'Arachnida': 47119, 'Fungi': 47170
    }
    
    # Prepare filter parameters
    iconic_taxon_id = None
    if args.iconic_taxon:
        iconic_taxon_id = iconic_taxon_map.get(args.iconic_taxon)
        if not iconic_taxon_id:
            logger.warning(f"Unknown iconic taxon: {args.iconic_taxon}")
    
    # Handle captive/wild filters
    captive = None
    if args.captive_only:
        captive = True
    elif args.wild_only:
        captive = False
    
    # Handle introduced/native filters
    introduced = None
    native = None
    if args.introduced_only:
        introduced = True
    elif args.native_only:
        native = True
    
    # Handle threatened/endemic filters
    threatened = None
    endemic = None
    if args.threatened_only:
        threatened = True
    elif args.endemic_only:
        endemic = True
    
    # Fetch observations
    logger.info(f"Fetching observations within {args.radius} miles ({radius_km:.2f} km) of ({args.lat}, {args.lon})")
    observations = downloader.get_observations(
        args.lat, args.lon, radius_km,
        quality_grade=args.quality_grade,
        iconic_taxon_id=iconic_taxon_id,
        observed_since=args.observed_since,
        observed_before=args.observed_before,
        captive=captive,
        introduced=introduced,
        threatened=threatened,
        endemic=endemic,
        native=native
    )
    
    if not observations:
        logger.warning("No observations found in the specified area")
        return
    
    # Limit observations if specified
    if args.max_observations:
        observations = observations[:args.max_observations]
        logger.info(f"Limited to {len(observations)} observations")
    
    # Process observations and compile metadata
    metadata_list = []
    downloaded_count = 0
    
    for i, observation in enumerate(observations, 1):
        logger.info(f"Processing observation {i}/{len(observations)} (ID: {observation.get('id')})")
        
        # Get detailed observation info if authenticated (for full photo URLs)
        if access_token:
            detailed_obs = downloader.get_observation_details(observation['id'])
            if detailed_obs:
                observation = detailed_obs
        
        # Extract metadata
        observation_metadata = downloader.extract_species_metadata(observation)
        
        # Download images if requested
        if args.download_images and observation.get('photos'):
            for j, photo in enumerate(observation['photos']):
                # Choose image URL based on quality preference
                # With authentication, we get full URLs from the API
                if access_token and photo.get('original_url'):
                    # Use the full URLs provided by authenticated API
                    if args.image_quality == 'original':
                        image_url = photo.get('original_url') or photo.get('large_url') or photo.get('url')
                    elif args.image_quality == 'large':
                        image_url = photo.get('large_url') or photo.get('original_url') or photo.get('url')
                    elif args.image_quality == 'medium':
                        image_url = photo.get('medium_url') or photo.get('large_url') or photo.get('original_url') or photo.get('url')
                    elif args.image_quality == 'small':
                        image_url = photo.get('small_url') or photo.get('medium_url') or photo.get('large_url') or photo.get('original_url') or photo.get('url')
                    else:  # 'best'
                        image_url = photo.get('original_url') or photo.get('large_url') or photo.get('url')
                else:
                    # Fall back to manual URL construction for public API
                    photo_id = photo.get('id')
                    base_url = f"https://inaturalist-open-data.s3.amazonaws.com/photos/{photo_id}"
                    
                    if args.image_quality == 'original':
                        image_url = f"{base_url}/original.jpg"
                    elif args.image_quality == 'large':
                        image_url = f"{base_url}/large.jpg"
                    elif args.image_quality == 'medium':
                        image_url = f"{base_url}/medium.jpg"
                    elif args.image_quality == 'small':
                        image_url = f"{base_url}/small.jpg"
                    else:  # 'best'
                        image_url = f"{base_url}/original.jpg"
                
                if image_url:
                    # Create filename based on observation ID and photo index
                    filename = f"obs_{observation['id']}_photo_{j}.jpg"
                    
                    # Try to download the requested quality, with fallbacks
                    downloaded_path = None
                    if access_token and photo.get('original_url'):
                        # With authentication, we have direct URLs
                        downloaded_path = downloader.download_image(image_url, args.images_dir, filename)
                    else:
                        # Without authentication, use fallback logic
                        if args.image_quality == 'original':
                            for quality in ['original', 'large', 'square']:
                                fallback_url = f"{base_url}/{quality}.jpg"
                                downloaded_path = downloader.download_image(fallback_url, args.images_dir, filename)
                                if downloaded_path:
                                    break
                        elif args.image_quality == 'large':
                            for quality in ['large', 'original', 'square']:
                                fallback_url = f"{base_url}/{quality}.jpg"
                                downloaded_path = downloader.download_image(fallback_url, args.images_dir, filename)
                                if downloaded_path:
                                    break
                        elif args.image_quality == 'medium':
                            for quality in ['medium', 'large', 'original', 'square']:
                                fallback_url = f"{base_url}/{quality}.jpg"
                                downloaded_path = downloader.download_image(fallback_url, args.images_dir, filename)
                                if downloaded_path:
                                    break
                        elif args.image_quality == 'small':
                            for quality in ['small', 'medium', 'large', 'original', 'square']:
                                fallback_url = f"{base_url}/{quality}.jpg"
                                downloaded_path = downloader.download_image(fallback_url, args.images_dir, filename)
                                if downloaded_path:
                                    break
                        else:  # 'best'
                            for quality in ['original', 'large', 'square']:
                                fallback_url = f"{base_url}/{quality}.jpg"
                                downloaded_path = downloader.download_image(fallback_url, args.images_dir, filename)
                                if downloaded_path:
                                    break
                    
                    if downloaded_path:
                        downloaded_count += 1
                        # Add local file path to metadata
                        observation_metadata['photos'][j]['local_path'] = downloaded_path
        
        metadata_list.append(observation_metadata)
    
    # Save metadata to JSON file
    output_data = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'center_latitude': args.lat,
            'center_longitude': args.lon,
            'radius_miles': args.radius,
            'radius_km': radius_km,
            'total_observations': len(metadata_list),
            'images_downloaded': downloaded_count,
            'images_directory': args.images_dir,
            'authenticated': access_token is not None
        },
        'observations': metadata_list
    }
    
    with open(args.output, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    logger.info(f"Metadata saved to: {args.output}")
    logger.info(f"Summary: {len(metadata_list)} observations processed, {downloaded_count} images downloaded")
    
    # Print summary statistics
    if metadata_list:
        species_counts = {}
        for obs in metadata_list:
            if obs.get('species'):
                species_name = obs['species'].get('name', 'Unknown')
                species_counts[species_name] = species_counts.get(species_name, 0) + 1
        
        logger.info("Top species found:")
        for species, count in sorted(species_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            logger.info(f"  {species}: {count} observations")

if __name__ == "__main__":
    main() 