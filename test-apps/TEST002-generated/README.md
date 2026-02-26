# Microsoft Teams Presence App for Freshservice

A Freshservice sidebar app that displays the Microsoft Teams presence status of ticket requesters.

## Features

- Displays a "Get Status" button in the ticket sidebar
- Retrieves the requester's email from the ticket
- Fetches the user's Microsoft Teams presence using Microsoft Graph API
- Shows availability status (Available, Busy, Away, Offline, etc.)
- Clean, modern UI with error handling and loading states

## App Structure

```
TEST002-generated/
├── manifest.json           # App configuration
├── ticket_sidebar.html     # Main HTML page
├── app.js                  # JavaScript logic
├── config/
│   └── requests.json       # API request templates
├── styles/
│   ├── style.css          # Styling
│   └── images/
│       └── icon.svg       # App icon
└── README.md              # This file
```

## Configuration

### Prerequisites

1. **Microsoft Graph API Access**: You need a Microsoft Azure AD application with the following permissions:
   - `Presence.Read` or `Presence.Read.All`

2. **Access Token**: Obtain a valid Microsoft Graph API access token

### Installation Parameters

The app requires the following installation parameter to be configured in the manifest:

- `msGraphToken`: Microsoft Graph API Bearer token

To add this, update the `manifest.json` to include:

```json
{
  "platform-version": "3.0",
  "product": {
    "freshservice": {
      "location": {
        "ticket_sidebar": {
          "url": "ticket_sidebar.html",
          "icon": "styles/images/icon.svg"
        }
      }
    }
  },
  "modules": {
    "common": {
      "requests": {
        "getTeamsPresence": {}
      }
    }
  },
  "whitelisted-domains": [
    "https://graph.microsoft.com"
  ],
  "engines": {
    "node": "18.16.0",
    "fdk": "9.1.0"
  }
}
```

## How It Works

1. **Button Click**: User clicks "Get Status" button in the ticket sidebar
2. **Fetch Requester Data**: App retrieves the ticket requester's email using `client.data.get('requester')`
3. **API Call**: App calls Microsoft Graph API endpoint `/v1.0/users/{email}/presence`
4. **Display Results**: Shows the presence status with color-coded badges

## API Integration

The app uses the Microsoft Graph API to fetch presence information:

**Endpoint**: `GET https://graph.microsoft.com/v1.0/users/{email}/presence`

**Response Format**:
```json
{
  "availability": "Available",
  "activity": "Available"
}
```

**Possible Availability Values**:
- Available
- Busy
- DoNotDisturb
- Away
- BeRightBack
- Offline
- PresenceUnknown

## Testing Locally

1. Navigate to the app directory:
   ```bash
   cd TEST002-generated
   ```

2. Run the app using FDK:
   ```bash
   fdk run
   ```

3. Open a Freshservice ticket and append `?dev=true` to the URL:
   ```
   https://your-domain.freshservice.com/helpdesk/tickets/1?dev=true
   ```

4. The app will appear in the ticket sidebar

## Error Handling

The app includes comprehensive error handling for:
- Missing requester email
- API request failures
- Network errors
- Invalid responses

Errors are displayed in a user-friendly format with red error messages.

## UI Features

- **Loading State**: Shows "Loading..." while fetching data
- **Status Display**: Color-coded badges for different availability states
  - Green: Available
  - Red: Busy
  - Yellow: Away
  - Gray: Offline/Unknown
- **Error Display**: Clear error messages when something goes wrong
- **Responsive Design**: Works well in the sidebar layout

## Notes

- The requester must have a valid email address in their Freshservice profile
- The email must correspond to a Microsoft Teams user
- The Microsoft Graph API token must have appropriate permissions
- For production use, consider implementing OAuth 2.0 for token management instead of using a static token
