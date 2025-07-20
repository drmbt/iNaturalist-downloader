# iNaturalist Image Downloader

A Python script that downloads images from iNaturalist observations within a specified radius of a location and compiles comprehensive metadata about identified species into a JSON file.

## Features

- Downloads images from iNaturalist observations within a specified radius
- Compiles detailed metadata about identified species
- Supports CLI arguments for easy customization
- Includes rate limiting to be respectful to the iNaturalist API
- Provides comprehensive logging and progress tracking
- Generates summary statistics of found species

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Download images and metadata for observations within 5 miles of a location:

```bash
python inaturalist_downloader.py --lat -8.132489 --lon 115.363868 --radius 5
```

### Advanced Usage

```bash
python inaturalist_downloader.py \
    --lat -8.132489 \
    --lon 115.363868 \
    --radius 5 \
    --output my_metadata.json \
    --images-dir ./my_images \
    --max-observations 500
```

### Command Line Arguments

| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `--lat` | float | Yes | - | Latitude of the center point |
| `--lon` | float | Yes | - | Longitude of the center point |
| `--radius` | float | Yes | - | Radius in miles (converted to km) |
| `--output` | string | No | `inaturalist_metadata.json` | Output JSON file for metadata |
| `--images-dir` | string | No | `./images` | Directory to save downloaded images |
| `--download-images` | flag | No | True | Whether to download images |
| `--max-observations` | int | No | None | Maximum number of observations to process |

### Examples

#### Download observations from Central Park, NYC
```bash
python inaturalist_downloader.py --lat 40.7829 --lon -73.9654 --radius 2
```

#### Download observations from Golden Gate Park, San Francisco
```bash
python inaturalist_downloader.py --lat 37.7694 --lon -122.4862 --radius 3
```

#### Limit to 50 observations and save to custom location
```bash
python inaturalist_downloader.py \
    --lat 34.0522 \
    --lon -118.2437 \
    --radius 5 \
    --max-observations 50 \
    --output los_angeles_species.json \
    --images-dir ./la_images
```

## Output

The script generates two types of output:

### 1. Downloaded Images
Images are saved to the specified directory (default: `./images`) with filenames in the format:
```
obs_{observation_id}_photo_{photo_index}.jpg
```

### 2. Metadata JSON File
A comprehensive JSON file containing:

- **Metadata section**: Information about the search parameters and results
- **Observations array**: Detailed information about each observation including:
  - Observation details (ID, date, location, quality grade)
  - Species information (scientific name, common name, taxonomy)
  - Photo information (URLs, licenses, local file paths)
  - User information (who made the observation)

#### Example JSON Structure
```json
{
  "metadata": {
    "generated_at": "2024-01-15T10:30:00",
    "center_latitude": -8.132489362310453,
    "center_longitude": 115.36386760679501,
    "radius_miles": 5,
    "radius_km": 8.05,
    "total_observations": 150,
    "images_downloaded": 200,
    "images_directory": "./images"
  },
  "observations": [
    {
      "observation_id": 123456,
      "observed_on": "2024-01-10",
      "latitude": -8.132489362310453,
      "longitude": 115.36386760679501,
      "quality_grade": "research",
      "description": "Found this beautiful bird in the park",
      "species": {
        "id": 789,
        "name": "Cardinalis cardinalis",
        "preferred_common_name": "Northern Cardinal",
        "rank": "species",
        "conservation_status": "LC"
      },
      "photos": [
        {
          "id": 456,
          "url": "https://...",
          "large_url": "https://...",
          "local_path": "./images/obs_123456_photo_0.jpg",
          "license_code": "cc-by-nc"
        }
      ]
    }
  ]
}
```

## Species Metadata Included

For each identified species, the script captures:

- **Taxonomic Information**: Scientific name, common name, rank, ancestry
- **Conservation Status**: IUCN status and status name
- **Iconic Taxon**: Higher-level classification (e.g., "Aves" for birds)
- **Identification Quality**: Number of agreements/disagreements
- **Observation Details**: Date, location, accuracy, quality grade
- **Photo Information**: Multiple image sizes, licenses, attribution

## Rate Limiting

The script includes built-in rate limiting (0.5 seconds between API calls) to be respectful to the iNaturalist API. This ensures:

- Reliable operation without overwhelming the server
- Compliance with iNaturalist's API usage guidelines
- Sustainable long-term usage

## Error Handling

The script includes comprehensive error handling for:

- Network connectivity issues
- API rate limiting
- Invalid coordinates
- Missing or corrupted images
- File system permissions

## Logging

The script provides detailed logging including:

- Progress updates for each observation
- Download status for each image
- Summary statistics at completion
- Error messages for troubleshooting

## API Reference

This script uses the iNaturalist API v1. Key endpoints used:

- `GET /observations` - Fetch observations with location and radius filters
- Image URLs from observation photo data

For more information, see the [iNaturalist API Reference](https://www.inaturalist.org/pages/api+reference).

## License

This script is provided as-is for educational and research purposes. Please respect the licenses of downloaded images and the iNaturalist terms of service.

## Contributing

Feel free to submit issues or pull requests to improve the functionality of this script. 