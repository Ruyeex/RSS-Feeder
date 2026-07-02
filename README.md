# RSS-Feeder

Automated RSS feed generator for the Vintage Story Mod DB. Fetches the latest mods and generates an RSS feed that can be subscribed to for updates.

## Project Structure

```
RSS-Feeder/
├── .github/
│   └── workflows/
│       └── update-feed.yml              # GitHub Actions workflow
├── src/
│   ├── __init__.py
│   ├── main.py                          # Main entry point
│   ├── config.py                        # Configuration management
│   ├── logger.py                        # Logging setup
│   ├── api.py                           # API client
│   ├── rss_builder.py                   # RSS feed building
│   └── git_handler.py                   # Git operations
├── main.py                              # Root entry point
├── requirements.txt                     # Python dependencies
├── README.md                            # This file
├── .gitignore
└── LICENSE                              # GNU GPLv3
```

## Setup

### Prerequisites
- Python 3.11+
- `requests` library

### Installation

```bash
# Clone the repository
git clone https://github.com/Ruyeex/RSS-Feeder.git
cd RSS-Feeder

# Install dependencies
pip install -r requirements.txt
```

### Running Locally

```bash
python main.py
```

This will generate `vsmoddb_updates.xml` with the latest mod updates.

### Configuration

Environment variables can be used to customize behavior:

```bash
# Feed settings
export FEED_OUTPUT_PATH="vsmoddb_updates.xml"
export FEED_NUM_ITEMS="30"

# Git settings (for manual pushes)
export GIT_USER_NAME="Your Name"
export GIT_USER_EMAIL="your@email.com"
export GIT_BRANCH="main"

# Logging
export LOG_LEVEL="INFO"
export LOG_FILE="logs/rss_feed.log"

python main.py
```

## Automation

The workflow in `.github/workflows/update-feed.yml` automatically:

1. **Runs every 6 hours** - Fetches the latest mods from the Vintage Story Mod DB
2. **Generates the RSS feed** - Creates an updated XML feed file
3. **Commits and pushes changes** - Pushes updates to the repository only if the feed has changed

### Manual Trigger

Manually trigger the workflow from GitHub:
1. Go to your repository
2. Navigate to **Actions** tab
3. Select **"Update VS Mod DB RSS Feed"** workflow
4. Click **"Run workflow"** → **"Run workflow"** button

## Development

### Adding Features

The modular structure makes it easy to extend:

- **New data sources**: Add to `src/api.py`
- **Feed formatting**: Modify `src/rss_builder.py`
- **Configuration**: Update `src/config.py`
- **Logging**: Configure in `src/logger.py`

### Testing

```bash
# Run the generator without git operations
python main.py

# Check the generated feed
cat vsmoddb_updates.xml
```

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Troubleshooting

### Workflow fails with "fetch first" error
- The workflow now includes proper `git pull --rebase` logic before pushing
- Ensure your repository doesn't have conflicting commits

### No changes committed
- The workflow only commits when `vsmoddb_updates.xml` actually changes
- Check the workflow logs for details

### API connection issues
- Verify the Vintage Story Mod DB API is accessible: https://mods.vintagestory.at/api/mods
- Check your internet connection and firewall settings

## Support

For issues or questions, please open a GitHub issue in this repository.
