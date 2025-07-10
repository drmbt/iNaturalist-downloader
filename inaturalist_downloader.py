#!/usr/bin/env python3
"""
iNaturalist Image Downloader

This script downloads images from iNaturalist observations within a specified radius
of a given location and compiles metadata about identified species into a JSON file.

Default location: Les village, Bali, Indonesia - home to Sea Communities and site of Dinacon 2025
Coordinates: -8.132489362310453, 115.36386760679501

Usage:
    python inaturalist_downloader.py  # Uses default Les village coordinates
    python inaturalist_downloader.py --lat -8.132489362310453 --lon 115.36386760679501 --radius 5
    python inaturalist_downloader.py --lat -8.132489362310453 --lon 115.36386760679501 --radius 5 --output metadata.json
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

class iNaturalistDownloader:
    """Class to handle iNaturalist API interactions and image downloads."""
    
    def __init__(self):
        self.base_url = "https://api.inaturalist.org/v1"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'iNaturalist-Downloader/1.0 (https://github.com/your-repo)'
        })
    
    def get_observations(self, lat: float, lon: float, radius_km: float, 
                        per_page: int = 200, quality_grade: str = None,
                        iconic_taxon_id: int = None, observed_since: str = None,
                        observed_before: str = None, captive: bool = None,
                        introduced: bool = None, threatened: bool = None,
                        endemic: bool = None, native: bool = None) -> List[Dict[str, Any]]:
        """
        Fetch observations within the specified radius.
        
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
            List of observation dictionaries
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
        filepath = os.path.join(output_dir, filename)
        
        # Check if file already exists
        if os.path.exists(filepath):
            logger.debug(f"Skipping existing file: {filename}")
            return filepath
        
        try:
            response = self.session.get(image_url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Downloaded: {filename}")
            return filepath
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                # Photo no longer exists - this is normal, not an error
                logger.debug(f"Photo not found (404): {filename} - photo may have been deleted")
                return None
            elif e.response.status_code == 429:
                # Rate limit hit - wait and retry
                logger.warning(f"Rate limit hit, waiting 60 seconds before retry...")
                time.sleep(60)
                return self.download_image(image_url, output_dir, filename)  # Retry once
            elif e.response.status_code >= 500:
                # Server error - wait and retry
                logger.warning(f"Server error ({e.response.status_code}), waiting 10 seconds before retry...")
                time.sleep(10)
                return self.download_image(image_url, output_dir, filename)  # Retry once
            else:
                logger.warning(f"HTTP error downloading {filename}: {e}")
                return None
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout downloading {filename}, retrying...")
            time.sleep(5)
            return self.download_image(image_url, output_dir, filename)  # Retry once
        except requests.exceptions.ConnectionError:
            logger.warning(f"Connection error downloading {filename}, retrying in 10 seconds...")
            time.sleep(10)
            return self.download_image(image_url, output_dir, filename)  # Retry once
        except Exception as e:
            logger.error(f"Unexpected error downloading {filename}: {e}")
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
        
        # Extract photo information
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

def main():
    """Main function to handle CLI arguments and execute the download process."""
    parser = argparse.ArgumentParser(
        description="Download iNaturalist images within a specified radius and compile species metadata",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python inaturalist_downloader.py --lat -8.132489362310453 --lon 115.36386760679501 --radius 5
  python inaturalist_downloader.py --lat -8.132489362310453 --lon 115.36386760679501 --radius 5 --output metadata.json --images-dir ./images
        """
    )
    
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
    
    # Additional filtering options for artists and naturalists
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
    
    # Convert radius from miles to kilometers
    radius_km = args.radius * 1.60934
    
    # Create output directory for images
    if args.download_images:
        os.makedirs(args.images_dir, exist_ok=True)
        logger.info(f"Images will be saved to: {args.images_dir}")
    
    # Initialize downloader
    downloader = iNaturalistDownloader()
    
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
    skipped_count = 0
    failed_count = 0
    missing_photos_count = 0
    
    for i, observation in enumerate(observations, 1):
        logger.info(f"Processing observation {i}/{len(observations)} (ID: {observation.get('id')})")
        
        # Extract metadata
        observation_metadata = downloader.extract_species_metadata(observation)
        
        # Download images if requested
        if args.download_images and observation.get('photos'):
            observation_photos = len(observation['photos'])
            observation_downloaded = 0
            observation_skipped = 0
            observation_failed = 0
            
            for j, photo in enumerate(observation['photos']):
                # Choose image URL based on quality preference
                # Since the API only provides square.jpg URLs, we need to construct higher resolution URLs manually
                photo_id = photo.get('id')
                base_url = f"https://inaturalist-open-data.s3.amazonaws.com/photos/{photo_id}"
                
                if args.image_quality == 'original':
                    # Try original.jpg first, then large.jpg, then square.jpg
                    image_url = f"{base_url}/original.jpg"
                elif args.image_quality == 'large':
                    # Try large.jpg first, then original.jpg, then square.jpg
                    image_url = f"{base_url}/large.jpg"
                elif args.image_quality == 'medium':
                    # Try medium.jpg first, then large.jpg, then original.jpg, then square.jpg
                    image_url = f"{base_url}/medium.jpg"
                elif args.image_quality == 'small':
                    # Try small.jpg first, then medium.jpg, then large.jpg, then original.jpg, then square.jpg
                    image_url = f"{base_url}/small.jpg"
                else:  # 'best' - try original.jpg first, then large.jpg, then square.jpg
                    image_url = f"{base_url}/original.jpg"
                
                if image_url:
                    # Create filename based on observation ID and photo index
                    filename = f"obs_{observation['id']}_photo_{j}.jpg"
                    
                    # Try to download the requested quality, with fallbacks
                    downloaded_path = None
                    if args.image_quality == 'original':
                        # Try original.jpg, then large.jpg, then square.jpg
                        for quality in ['original', 'large', 'square']:
                            fallback_url = f"{base_url}/{quality}.jpg"
                            downloaded_path = downloader.download_image(fallback_url, args.images_dir, filename)
                            if downloaded_path:
                                break
                    elif args.image_quality == 'large':
                        # Try large.jpg, then original.jpg, then square.jpg
                        for quality in ['large', 'original', 'square']:
                            fallback_url = f"{base_url}/{quality}.jpg"
                            downloaded_path = downloader.download_image(fallback_url, args.images_dir, filename)
                            if downloaded_path:
                                break
                    elif args.image_quality == 'medium':
                        # Try medium.jpg, then large.jpg, then original.jpg, then square.jpg
                        for quality in ['medium', 'large', 'original', 'square']:
                            fallback_url = f"{base_url}/{quality}.jpg"
                            downloaded_path = downloader.download_image(fallback_url, args.images_dir, filename)
                            if downloaded_path:
                                break
                    elif args.image_quality == 'small':
                        # Try small.jpg, then medium.jpg, then large.jpg, then original.jpg, then square.jpg
                        for quality in ['small', 'medium', 'large', 'original', 'square']:
                            fallback_url = f"{base_url}/{quality}.jpg"
                            downloaded_path = downloader.download_image(fallback_url, args.images_dir, filename)
                            if downloaded_path:
                                break
                    else:  # 'best'
                        # Try original.jpg, then large.jpg, then square.jpg
                        for quality in ['original', 'large', 'square']:
                            fallback_url = f"{base_url}/{quality}.jpg"
                            downloaded_path = downloader.download_image(fallback_url, args.images_dir, filename)
                            if downloaded_path:
                                break
                    
                    if downloaded_path:
                        # Check if this was a new download or skipped existing file
                        file_stat = os.stat(downloaded_path)
                        current_time = time.time()
                        # If file was modified in the last 10 seconds, it was just downloaded
                        if current_time - file_stat.st_mtime < 10:
                            downloaded_count += 1
                            observation_downloaded += 1
                        else:
                            skipped_count += 1
                            observation_skipped += 1
                        
                        # Add local file path to metadata
                        observation_metadata['photos'][j]['local_path'] = downloaded_path
                    else:
                        failed_count += 1
                        observation_failed += 1
                        missing_photos_count += 1
            
            # Log observation summary
            if observation_failed > 0:
                logger.info(f"  Observation {observation.get('id')}: {observation_downloaded} downloaded, {observation_skipped} skipped, {observation_failed} missing/deleted")
            elif observation_skipped > 0:
                logger.info(f"  Observation {observation.get('id')}: {observation_downloaded} downloaded, {observation_skipped} skipped")
            else:
                logger.info(f"  Observation {observation.get('id')}: {observation_downloaded}/{observation_photos} photos downloaded")
        
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
            'images_skipped': skipped_count,
            'images_failed': failed_count,
            'success_rate_percent': round(((downloaded_count + skipped_count) / (downloaded_count + skipped_count + failed_count) * 100) if (downloaded_count + skipped_count + failed_count) > 0 else 0, 1),
            'images_directory': args.images_dir if args.download_images else None
        },
        'observations': metadata_list
    }
    
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Metadata saved to: {args.output}")
    
    # Print comprehensive summary
    total_photos_attempted = downloaded_count + skipped_count + failed_count
    success_rate = ((downloaded_count + skipped_count) / total_photos_attempted * 100) if total_photos_attempted > 0 else 0
    
    logger.info("=" * 60)
    logger.info("DOWNLOAD SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Observations processed: {len(metadata_list)}")
    logger.info(f"Images downloaded: {downloaded_count}")
    logger.info(f"Images skipped (already exist): {skipped_count}")
    logger.info(f"Images failed/missing: {failed_count}")
    logger.info(f"Success rate: {success_rate:.1f}%")
    
    if failed_count > 0:
        logger.info(f"Note: {failed_count} photos were not found (404 errors). This is normal -")
        logger.info("      photos may have been deleted by users or removed from iNaturalist.")
    
    if skipped_count > 0:
        logger.info(f"Note: {skipped_count} images were skipped because they already exist.")
        logger.info("      This allows you to safely re-run the script to resume downloads.")
    
    # Print summary statistics
    species_count = {}
    for obs in metadata_list:
        # Handle cases where species might be None
        species_data = obs.get('species')
        if species_data and species_data.get('name'):
            species_name = species_data['name']
            species_count[species_name] = species_count.get(species_name, 0) + 1
    
    if species_count:
        logger.info("\nTop species found:")
        sorted_species = sorted(species_count.items(), key=lambda x: x[1], reverse=True)
        for species, count in sorted_species[:10]:  # Show top 10
            logger.info(f"  {species}: {count} observations")

if __name__ == "__main__":
    main() 