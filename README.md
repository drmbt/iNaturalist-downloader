# iNaturalist Image Downloader

A Python script that downloads images from iNaturalist observations within a specified radius of a location and compiles comprehensive metadata about identified species into a JSON file.

**Default Location**: Les village, Bali, Indonesia - home to Sea Communities and site of Dinacon 2025

## Features

- Downloads images from iNaturalist observations within a specified radius
- Compiles detailed metadata about identified species
- Supports CLI arguments for easy customization
- Includes rate limiting to be respectful to the iNaturalist API
- Provides comprehensive logging and progress tracking
- Generates summary statistics of found species
- **Smart file handling**: Skips downloads if files already exist
- **High-resolution images**: Downloads full-resolution images without authentication using predictable URLs
- **Optional OAuth**: Enhanced features available with authentication (see Authentication section)

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. (Optional) Set up authentication for enhanced features:
   - Copy `env.example` to `.env`
   - Follow the authentication guide in `AUTHENTICATION_GUIDE.md`
   - **Note**: Authentication is optional - the script works without it and can download full-resolution images using predictable URLs

## Usage

### Basic Usage

Download images and metadata for observations within 5 miles of Les village, Bali (default):

```bash
python inaturalist_downloader.py
```

Or specify custom coordinates:

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
| `--lat` | float | No | -8.132489 | Latitude of the center point (default: Les village, Bali) |
| `--lon` | float | No | 115.363868 | Longitude of the center point (default: Les village, Bali) |
| `--radius` | float | No | 5.0 | Radius in miles (converted to km) |
| `--output` | string | No | `inaturalist_metadata.json` | Output JSON file for metadata |
| `--images-dir` | string | No | `./images` | Directory to save downloaded images |
| `--download-images` | flag | No | True | Whether to download images |
| `--image-quality` | string | No | best | Image quality: original, large, medium, small, or best |
| `--max-observations` | int | No | None | Maximum number of observations to process |

### Filtering Options (for Artists & Naturalists)

| Argument | Type | Description |
|----------|------|-------------|
| `--quality-grade` | string | Filter by quality grade: research, needs_id, casual |
| `--iconic-taxon` | string | Filter by taxon: Animalia, Plantae, Insecta, Aves, Mammalia, etc. |
| `--observed-since` | string | Filter observations since date (YYYY-MM-DD) |
| `--observed-before` | string | Filter observations before date (YYYY-MM-DD) |
| `--captive-only` | flag | Only include captive/cultivated observations |
| `--wild-only` | flag | Only include wild observations |
| `--introduced-only` | flag | Only include introduced species |
| `--native-only` | flag | Only include native species |
| `--threatened-only` | flag | Only include threatened species |
| `--endemic-only` | flag | Only include endemic species |

### Available Iconic Taxa

| Taxon | ID | Description | Use Cases |
|-------|----|-------------|-----------|
| `Animalia` | 1 | All animals | General animal biodiversity |
| `Plantae` | 47126 | All plants | Botanical studies, flora documentation |
| `Insecta` | 47158 | Insects | Entomology, pollinator studies |
| `Aves` | 3 | Birds | Ornithology, bird watching |
| `Mammalia` | 40151 | Mammals | Wildlife studies, conservation |
| `Reptilia` | 26036 | Reptiles | Herpetology, reptile surveys |
| `Amphibia` | 20978 | Amphibians | Herpetology, amphibian monitoring |
| `Mollusca` | 47115 | Mollusks | Malacology, shell collecting |
| `Arachnida` | 47119 | Arachnids | Arachnology, spider studies |
| `Fungi` | 47170 | Fungi | Mycology, mushroom identification |

### Quality Grades Explained

| Grade | Description | Use Cases |
|-------|-------------|-----------|
| `research` | High-quality observations with community agreement | Scientific research, conservation studies |
| `needs_id` | Observations that need identification | Discovery, learning, community engagement |
| `casual` | Informal observations | Artistic inspiration, general documentation |

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

#### Download highest quality images available
```bash
python inaturalist_downloader.py \
    --lat -8.132489 \
    --lon 115.363868 \
    --radius 5 \
    --image-quality original
```

#### Filter for research-grade observations only
```bash
python inaturalist_downloader.py --quality-grade research
```

#### Download only bird observations from the last year
```bash
python inaturalist_downloader.py \
    --iconic-taxon Aves \
    --observed-since 2024-01-01 \
    --quality-grade research
```

#### Download only native, threatened species
```bash
python inaturalist_downloader.py \
    --native-only \
    --threatened-only \
    --quality-grade research
```

#### Download only wild (non-captive) observations
```bash
python inaturalist_downloader.py --wild-only
```

#### Download only insects with research-grade quality
```bash
python inaturalist_downloader.py --iconic-taxon Insecta --quality-grade research
```

#### Download only plants observed in the last 6 months
```bash
python inaturalist_downloader.py \
    --iconic-taxon Plantae \
    --observed-since 2024-07-01 \
    --quality-grade research
```

#### Download only mammals with original quality images
```bash
python inaturalist_downloader.py \
    --iconic-taxon Mammalia \
    --image-quality original \
    --quality-grade research
```

#### Download only endemic species from a specific date range
```bash
python inaturalist_downloader.py \
    --endemic-only \
    --observed-since 2024-01-01 \
    --observed-before 2024-12-31 \
    --quality-grade research
```

#### Download only introduced species (non-native)
```bash
python inaturalist_downloader.py --introduced-only
```

#### Download only threatened species with limited observations
```bash
python inaturalist_downloader.py \
    --threatened-only \
    --max-observations 50 \
    --image-quality original
```

#### Download only reptiles and amphibians
```bash
python inaturalist_downloader.py \
    --iconic-taxon Reptilia \
    --quality-grade research
```

#### Download only fungi observations
```bash
python inaturalist_downloader.py --iconic-taxon Fungi
```

#### Download only mollusks (snails, clams, etc.)
```bash
python inaturalist_downloader.py --iconic-taxon Mollusca
```

#### Download only arachnids (spiders, scorpions, etc.)
```bash
python inaturalist_downloader.py --iconic-taxon Arachnida
```

#### Download observations from a specific season
```bash
python inaturalist_downloader.py \
    --observed-since 2024-06-01 \
    --observed-before 2024-08-31 \
    --quality-grade research
```

#### Download only casual observations (for artistic inspiration)
```bash
python inaturalist_downloader.py --quality-grade casual
```

#### Download only observations that need identification
```bash
python inaturalist_downloader.py --quality-grade needs_id
```

#### Download only native species with high-quality images
```bash
python inaturalist_downloader.py \
    --native-only \
    --image-quality original \
    --quality-grade research
```

#### Download only captive/cultivated observations (for botanical gardens, etc.)
```bash
python inaturalist_downloader.py --captive-only
```

#### Download only observations from a specific radius with custom output
```bash
python inaturalist_downloader.py \
    --radius 10 \
    --output my_biodiversity_data.json \
    --images-dir ./my_images
```

#### Download only observations with multiple photos
```bash
python inaturalist_downloader.py \
    --quality-grade research \
    --max-observations 100
```

#### Download only observations from experienced users (high observation counts)
```bash
python inaturalist_downloader.py \
    --quality-grade research \
    --max-observations 200
```

## Practical Use Cases

### For Artists & Illustrators
- **Reference Material**: Download high-quality images for artistic reference
- **Seasonal Studies**: Use date filters to study seasonal changes
- **Taxonomic Focus**: Focus on specific groups (birds, insects, plants) for themed artwork
- **Conservation Art**: Use threatened/endemic filters for conservation-themed projects

### For Researchers & Scientists
- **Biodiversity Surveys**: Use quality filters for reliable data
- **Temporal Studies**: Use date ranges for longitudinal research
- **Taxonomic Studies**: Focus on specific taxa for detailed analysis
- **Conservation Monitoring**: Track threatened and endemic species

### For Educators & Students
- **Learning Resources**: Download diverse observations for educational materials
- **Identification Practice**: Use needs_id grade for identification exercises
- **Local Biodiversity**: Study local species with geographic filters
- **Seasonal Changes**: Track biodiversity changes over time

### For Conservationists
- **Threatened Species**: Focus on conservation priority species
- **Native vs Introduced**: Study invasive species and native biodiversity
- **Endemic Species**: Document unique local species
- **Population Monitoring**: Track species over time with date filters

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

## Enhanced Metadata for Artists & Naturalists

The script now captures comprehensive metadata useful for artists, researchers, and naturalists:

### Species Information
- **Taxonomic Details**: Scientific name, common name, rank, ancestry, Wikipedia URL
- **Conservation Status**: IUCN status, threatened status, endemic status
- **Origin Information**: Native, introduced, extinct status
- **Population Data**: Global observation count for the species
- **Default Photo**: Reference image for the species

### Observation Details
- **Temporal Data**: Observed date, time, timezone information
- **Spatial Data**: Coordinates, accuracy, geoprivacy settings
- **Quality Metrics**: Research grade, identification agreements/disagreements
- **User Information**: Observer details, their experience level
- **Social Data**: Comments count, favorites count, tags

### Photo Information
- **Multiple Resolutions**: Original, large, medium, small, square URLs
- **Licensing**: License codes and attribution information
- **Moderation**: Flags, moderator actions, hidden status
- **Technical Details**: Original dimensions, file types

### Identification Data
- **Community Input**: All identifications with user details
- **AI Contributions**: Vision-based identifications
- **Disagreements**: Identification conflicts and resolutions

## Authentication & Image Quality

### Without Authentication (Default)
The script works perfectly without authentication and can download high-resolution images using predictable URLs constructed from photo IDs. This approach:
- Downloads images at 1920x1080 resolution or higher
- Works with the public iNaturalist API
- Requires no setup or API keys
- Handles missing/deleted photos gracefully

### With OAuth Authentication (Optional)
Authentication provides enhanced features:
- Access to private observations (if you have permission)
- Higher API rate limits
- Additional metadata fields
- More reliable access to some photo URLs

**Setup**: See `AUTHENTICATION_GUIDE.md` for detailed instructions.

## File Handling

The script includes smart file handling:
- **Skip existing files**: If an image file already exists, the download is skipped
- **Resume interrupted downloads**: Run the script multiple times safely
- **No duplicate downloads**: Efficient for large datasets
- **Progress tracking**: Shows which files are being skipped vs. downloaded

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

## File Structure

```
iNaturalist/
├── inaturalist_downloader.py          # Main script (public API)
├── inaturalist_downloader_auth.py     # Authenticated version
├── inaturalist_auth.py               # OAuth authentication helper
├── test_installation.py              # Dependency test script
├── test_auth.py                     # Authentication test script
├── requirements.txt                  # Python dependencies
├── README.md                        # This file
├── AUTHENTICATION_GUIDE.md          # Authentication setup guide
├── env.example                      # Example environment file
├── .gitignore                       # Git ignore rules
└── images/                          # Downloaded images (auto-created)
```

## Security Notes

- The `.env` file contains sensitive authentication tokens and is automatically ignored by git
- Never commit your actual tokens to version control
- Use the `env.example` file as a template for your `.env` file
- Keep your OAuth client secret private

## License

This script is provided as-is for educational and research purposes. Please respect the licenses of downloaded images and the iNaturalist terms of service.

## Contributing

Feel free to submit issues or pull requests to improve the functionality of this script. 