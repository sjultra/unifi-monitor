# UniFi DHCP Reservation Management Scripts

This folder contains scripts for managing DHCP reservations on a UniFi OS device (UDM Pro, Cloud Key, etc.) using the local API and an API key.

## Features
- List current DHCP reservations
- Create or update reservations from a JSON file
- Sync reservations (add, update, and remove to match a JSON file)

## Requirements
- Python 3.7+
- `requests`, `python-dotenv`, `urllib3` (install with `pip install -r requirements.txt`)
- A UniFi OS API key (see below)

## Environment Variables
Create a `.env` file in the root of your project or export these variables in your shell:

```
UNIFI_BASE_URL=https://<your-udm-ip>
UNIFI_API_KEY=<your-api-key>
```

- `UNIFI_BASE_URL`: The base URL of your UniFi OS device (e.g., `https://192.168.1.1`)
- `UNIFI_API_KEY`: Your UniFi OS API key (see [how to generate](https://help.ui.com/hc/en-us/articles/115012442607-UniFi-How-to-Create-and-Apply-API-Tokens))

**Do not hardcode credentials in scripts. Always use environment variables or a `.env` file.**

## Usage

### List current DHCP reservations
```
python unifi_export.py
```

### Create reservations from a JSON file (legacy, only adds/updates)
```
python unifi_export.py --create-from-json reservations.json
```

### Sync reservations from a JSON file (add, update, and remove to match file)
```
python unifi_export.py --sync-from-json reservations.json
```

### Dry run sync (show what would be done)
```
python unifi_export.py --sync-from-json reservations.json --dry-run
```

### Specify a site (if not 'default')
```
python unifi_export.py --site <site_name>
```

## Security
- **Never commit your API key or sensitive credentials to version control.**
- Use a `.env` file or environment variables for secrets.
- Restrict your API key's permissions to the minimum required.

## API Key Generation
See [UniFi - How to Create and Apply API Tokens](https://help.ui.com/hc/en-us/articles/115012442607-UniFi-How-to-Create-and-Apply-API-Tokens) for instructions on generating an API key for your UniFi OS device.

## License
MIT 