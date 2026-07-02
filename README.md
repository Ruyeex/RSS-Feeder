# RSS-Feeder

RSS Feeder for my own news and updates.

## Project Structure

```
RSS-Feeder/
├── .github/
│   └── workflows/
│       └── update-feed.yml          # GitHub Actions workflow
├── vsmoddb_rss.py                    # Main RSS generator script
├── vsmoddb_updates.xml               # Generated RSS feed (auto-generated)
├── README.md                         # This file
└── .gitignore
```

## Setup

### Prerequisites
- Python 3.11+
- `requests` library

### Installation

```bash
pip install requests
```

### Running Locally

```bash
python vsmoddb_rss.py
```

This will generate `vsmoddb_updates.xml` with the latest mod updates.

## Automation

The workflow in `.github/workflows/update-feed.yml` automatically:
1. Runs every 6 hours
2. Fetches the latest VS Mod DB data
3. Generates the RSS feed
4. Commits and pushes changes if there are updates

### Manual Trigger

You can manually trigger the workflow from GitHub Actions tab → "Update VS Mod DB RSS Feed" → "Run workflow"

## License

This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.
