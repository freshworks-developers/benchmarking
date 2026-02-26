# Zapier Contact Sync for Freshdesk

A Freshworks app that automatically synchronizes Freshdesk contacts with Zapier via webhooks. This app listens to contact events (create, update, delete) and sends them to your Zapier webhook URL in real-time.

## Features

- **Real-time Sync**: Automatically syncs contacts when they are created, updated, or deleted in Freshdesk
- **Event Types**: Supports three event types:
  - `contact.created` - When a new contact is created
  - `contact.updated` - When an existing contact is updated
  - `contact.deleted` - When a contact is deleted
- **Easy Configuration**: Simple setup with just your Zapier webhook URL
- **Comprehensive Data**: Sends complete contact information including custom fields

## Prerequisites

- Freshdesk account with admin access
- Zapier account with a webhook URL ready
- Freshworks FDK (Freshworks Developer Kit) installed

## Installation

1. **Install FDK** (if not already installed):
   ```bash
   npm install -g https://cdn.freshdev.io/fdk/latest.tgz
   ```

2. **Navigate to the app directory**:
   ```bash
   cd zapier
   ```

3. **Run the app locally**:
   ```bash
   fdk run
   ```

4. **Install the app in Freshdesk**:
   - Open the app URL provided by FDK (usually `https://localhost:10001`)
   - Follow the installation wizard
   - Enter your Zapier webhook URL when prompted

## Configuration

### Getting Your Zapier Webhook URL

1. Log in to your Zapier account
2. Create a new Zap or edit an existing one
3. Add a "Webhooks by Zapier" trigger
4. Choose "Catch Hook" as the trigger event
5. Copy the webhook URL provided
6. Paste this URL in the app's installation parameters

### App Settings

During installation, you'll be prompted to enter:
- **Zapier Webhook URL**: Your Zapier webhook URL (e.g., `https://hooks.zapier.com/hooks/catch/123456/abcdef`)

## Data Format

The app sends the following JSON structure to your Zapier webhook:

```json
{
  "event_type": "contact.created",
  "contact": {
    "id": 123456,
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "address": "123 Main St",
    "description": "Contact description",
    "other_emails": ["john2@example.com"],
    "custom_fields": {
      "cf_custom_field": "value"
    },
    "created_at": "2024-01-01T00:00:00.000Z"
  },
  "timestamp": 1636116313.0883152,
  "region": "US"
}
```

## Event Types

### contact.created
Triggered when a new contact is created in Freshdesk. Includes all contact details.

### contact.updated
Triggered when an existing contact is updated. Includes the updated contact information.

### contact.deleted
Triggered when a contact is deleted. Includes basic contact information (id, name, email).

## Development

### Project Structure

```
zapier/
├── manifest.json          # App configuration and event handlers
├── server.js              # Serverless event handlers
├── index.html             # Frontend UI
├── scripts/
│   └── app.js            # Frontend JavaScript
├── styles/
│   ├── style.css         # Frontend styles
│   └── images/
│       └── icon.svg      # App icon
├── config/
│   ├── iparams.json      # Installation parameters
│   └── requests.json     # Request templates
└── README.md             # This file
```

### Testing

1. Run the app locally using `fdk run`
2. Create, update, or delete a contact in Freshdesk
3. Check your Zapier webhook logs to verify the data is being received
4. Check the app logs in the FDK console for any errors

### Debugging

- Check the FDK console for server-side logs
- Use browser developer tools for frontend debugging
- Verify your Zapier webhook URL is correctly configured
- Ensure your Zapier Zap is active and receiving webhooks

## Troubleshooting

### Contacts not syncing

1. Verify the Zapier webhook URL is correctly configured in app settings
2. Check that your Zapier Zap is active
3. Review the FDK console logs for any errors
4. Ensure the webhook URL is accessible (not behind a firewall)

### Webhook URL parsing errors

- Make sure the webhook URL is a complete URL starting with `https://`
- Verify the URL format matches: `https://hooks.zapier.com/hooks/catch/...`

## Support

For issues or questions:
- Check the [Freshworks Developer Documentation](https://developers.freshworks.com/docs/)
- Review the [Zapier Webhooks Documentation](https://zapier.com/apps/webhook/help)

## License

This app is provided as-is for use with Freshdesk and Zapier integrations.
