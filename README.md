# UniFi Monitor

A TypeScript-based Infrastructure as Code (IaC) solution for monitoring UniFi networks across multiple environments. This tool provides automated monitoring, device status reporting, and synchronization with version control.

## Features

- 📊 **Network Monitoring**: Track device status, online/offline states, and network health
- 📝 **Infrastructure as Code**: Store network configurations in TypeScript for version control
- 🤖 **Automated Monitoring**: Daily checks of network configurations with GitHub Actions
- 📈 **Change Tracking**: Track all network changes in git history
- 🔒 **Secure**: API keys stored in GitHub Secrets

## Prerequisites

- Node.js 20 or later
- UniFi Site Manager API access
- GitHub repository for configuration management

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/unifi-monitor.git
   cd unifi-monitor
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file with your UniFi API keys:
   ```env
   UNIFI_API_KEY_DEV=your_dev_api_key
   UNIFI_API_KEY_STAGE=your_stage_api_key
   UNIFI_API_KEY_PROD=your_prod_api_key
   ```

## Configuration

### Environment Setup

Configure your environments in `src/config/environments.ts`:
```typescript
export const environments = {
    dev: {
        name: "Development",
        hostname: "dev-testing",
        apiKey: process.env.UNIFI_API_KEY_DEV || "",
    },
    // ... other environments
};
```

## Usage

### Local Development

1. Monitor network status:
   ```bash
   npm run test -- read dev    # For development environment
   npm run test -- read stage  # For staging environment
   npm run test -- read prod   # For production environment
   ```

### GitHub Actions

The project includes a GitHub Actions workflow:

- **Daily Monitor** (`.github/workflows/daily-run.yml`):
  - Runs daily at midnight UTC
  - Checks all environments
  - Commits any changes to git

## GitHub Secrets Setup

Add the following secrets to your GitHub repository:
- `UNIFI_API_KEY_DEV`
- `UNIFI_API_KEY_STAGE`
- `UNIFI_API_KEY_PROD`

## Project Structure

```
unifi-monitor/
├── src/
│   ├── clients/         # API clients
│   ├── config/          # Configuration files
│   └── utils/           # Utility functions
├── scripts/             # Helper scripts
├── .github/workflows/   # GitHub Actions
└── package.json
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the ISC License.

## Acknowledgments

- [UniFi Site Manager API](https://developer.ui.com/site-manager-api/)
- [GitHub Actions](https://github.com/features/actions)