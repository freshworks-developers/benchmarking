/**
 * Frontend application logic
 */

document.addEventListener("DOMContentLoaded", function () {
  // Initialize the app
  app.initialized().then(function (_client) {
    window.client = _client;
    checkAppStatus();
  });
});

/**
 * Check app status and display configuration status
 */
async function checkAppStatus() {
  try {
    const iparams = await client.iparams.get();
    const statusMessage = document.getElementById("status-message");
    
    if (iparams.zapier_webhook_url) {
      statusMessage.textContent = "App is configured and syncing contacts to Zapier";
      statusMessage.style.color = "#28a745";
    } else {
      statusMessage.textContent = "Please configure your Zapier webhook URL in App Settings";
      statusMessage.style.color = "#ffc107";
    }
  } catch (error) {
    console.error("Error checking app status:", error);
  }
}
