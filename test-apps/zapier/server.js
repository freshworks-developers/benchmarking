/**
 * Serverless functions for syncing Freshdesk contacts to Zapier
 */

/**
 * Parse webhook URL to extract host and path
 * @param {string} url - Full webhook URL
 * @returns {Object} Object with host and path
 */
function parseWebhookUrl(url) {
  try {
    const urlObj = new URL(url);
    return {
      host: urlObj.hostname,
      path: urlObj.pathname + urlObj.search
    };
  } catch (error) {
    console.error("Error parsing webhook URL:", error);
    // Fallback: assume hooks.zapier.com and use full URL as path
    return {
      host: "hooks.zapier.com",
      path: url.startsWith("http") ? url.replace(/^https?:\/\/[^\/]+/, "") : url
    };
  }
}

exports = {
  /**
   * Handler for app installation
   * Validates that Zapier webhook URL is configured
   */
  onAppInstallHandler: function (payload) {
    console.log("App installed successfully");
    const zapierWebhookUrl = payload.iparams.zapier_webhook_url;
    
    if (!zapierWebhookUrl) {
      console.log("Warning: Zapier webhook URL not configured. Please configure it in the app settings.");
    } else {
      console.log("Zapier webhook URL configured:", zapierWebhookUrl);
      const parsed = parseWebhookUrl(zapierWebhookUrl);
      console.log("Parsed webhook - Host:", parsed.host, "Path:", parsed.path);
    }
  },

  /**
   * Handler for app uninstallation
   */
  onAppUninstallHandler: function (payload) {
    console.log("App uninstalled successfully");
  },

  /**
   * Handler for contact creation event
   * Syncs new contact to Zapier
   */
  onContactCreateHandler: async function (payload) {
    try {
      const contact = payload.data.contact;
      const zapierWebhookUrl = payload.iparams.zapier_webhook_url;

      if (!zapierWebhookUrl) {
        console.log("Zapier webhook URL not configured. Skipping sync.");
        return;
      }

      console.log("Syncing new contact to Zapier:", contact.email);

      const { host, path } = parseWebhookUrl(zapierWebhookUrl);

      const contactData = {
        event_type: "contact.created",
        contact: {
          id: contact.id,
          name: contact.name,
          email: contact.email,
          phone: contact.phone,
          address: contact.address,
          description: contact.description,
          other_emails: contact.other_emails || [],
          custom_fields: contact.custom_fields || {},
          created_at: new Date().toISOString()
        },
        timestamp: payload.timestamp,
        region: payload.region
      };

      await $request.invokeTemplate("zapierWebhook", {
        body: JSON.stringify(contactData),
        context: {
          webhook_host: host,
          webhook_path: path
        }
      });

      console.log("Successfully synced contact to Zapier:", contact.email);
    } catch (error) {
      console.error("Error syncing contact to Zapier:", error);
    }
  },

  /**
   * Handler for contact update event
   * Syncs updated contact to Zapier
   */
  onContactUpdateHandler: async function (payload) {
    try {
      const contact = payload.data.contact;
      const zapierWebhookUrl = payload.iparams.zapier_webhook_url;

      if (!zapierWebhookUrl) {
        console.log("Zapier webhook URL not configured. Skipping sync.");
        return;
      }

      console.log("Syncing updated contact to Zapier:", contact.email);

      const { host, path } = parseWebhookUrl(zapierWebhookUrl);

      const contactData = {
        event_type: "contact.updated",
        contact: {
          id: contact.id,
          name: contact.name,
          email: contact.email,
          phone: contact.phone,
          address: contact.address,
          description: contact.description,
          other_emails: contact.other_emails || [],
          custom_fields: contact.custom_fields || {},
          updated_at: new Date().toISOString()
        },
        timestamp: payload.timestamp,
        region: payload.region
      };

      await $request.invokeTemplate("zapierWebhook", {
        body: JSON.stringify(contactData),
        context: {
          webhook_host: host,
          webhook_path: path
        }
      });

      console.log("Successfully synced updated contact to Zapier:", contact.email);
    } catch (error) {
      console.error("Error syncing updated contact to Zapier:", error);
    }
  },

  /**
   * Handler for contact deletion event
   * Notifies Zapier about deleted contact
   */
  onContactDeleteHandler: async function (payload) {
    try {
      const contact = payload.data.contact;
      const zapierWebhookUrl = payload.iparams.zapier_webhook_url;

      if (!zapierWebhookUrl) {
        console.log("Zapier webhook URL not configured. Skipping sync.");
        return;
      }

      console.log("Notifying Zapier about deleted contact:", contact.email);

      const { host, path } = parseWebhookUrl(zapierWebhookUrl);

      const contactData = {
        event_type: "contact.deleted",
        contact: {
          id: contact.id,
          name: contact.name,
          email: contact.email,
          deleted_at: new Date().toISOString()
        },
        timestamp: payload.timestamp,
        region: payload.region
      };

      await $request.invokeTemplate("zapierWebhook", {
        body: JSON.stringify(contactData),
        context: {
          webhook_host: host,
          webhook_path: path
        }
      });

      console.log("Successfully notified Zapier about deleted contact:", contact.email);
    } catch (error) {
      console.error("Error notifying Zapier about deleted contact:", error);
    }
  }
};
