let client;

// Initialize the app
app.initialized().then(function(_client) {
  client = _client;
  
  // Add event listener to the button
  document.getElementById('getStatusBtn').addEventListener('click', getTeamsPresence);
});

// Function to get Teams presence
async function getTeamsPresence() {
  try {
    // Show loading state
    showLoading();
    hideError();
    hideStatus();
    
    // Get requester data from the ticket
    const requesterData = await client.data.get('requester');
    const requesterEmail = requesterData.requester.primary_email;
    
    if (!requesterEmail) {
      throw new Error('Requester email not found');
    }
    
    // Call Microsoft Graph API to get presence
    const response = await client.request.invokeTemplate('getTeamsPresence', {
      context: {
        email: requesterEmail
      }
    });
    
    // Parse the response
    const presenceData = JSON.parse(response.response);
    
    // Display the result
    displayPresenceStatus(presenceData, requesterEmail);
    hideLoading();
    
  } catch (error) {
    console.error('Error fetching Teams presence:', error);
    hideLoading();
    showError(error.message || 'Failed to fetch Teams presence. Please check your configuration.');
  }
}

// Function to display presence status
function displayPresenceStatus(data, email) {
  const statusContainer = document.getElementById('statusContainer');
  const statusResult = document.getElementById('statusResult');
  
  const availability = data.availability || 'Unknown';
  const activity = data.activity || 'Unknown';
  
  statusResult.innerHTML = `
    <div class="status-item">
      <strong>Email:</strong> ${email}
    </div>
    <div class="status-item">
      <strong>Availability:</strong> <span class="status-badge status-${availability.toLowerCase()}">${availability}</span>
    </div>
    <div class="status-item">
      <strong>Activity:</strong> ${activity}
    </div>
  `;
  
  statusContainer.classList.remove('hidden');
}

// Helper function to show loading state
function showLoading() {
  document.getElementById('loadingContainer').classList.remove('hidden');
}

// Helper function to hide loading state
function hideLoading() {
  document.getElementById('loadingContainer').classList.add('hidden');
}

// Helper function to show error
function showError(message) {
  const errorContainer = document.getElementById('errorContainer');
  const errorMessage = document.getElementById('errorMessage');
  errorMessage.textContent = message;
  errorContainer.classList.remove('hidden');
}

// Helper function to hide error
function hideError() {
  document.getElementById('errorContainer').classList.add('hidden');
}

// Helper function to hide status
function hideStatus() {
  document.getElementById('statusContainer').classList.add('hidden');
}
