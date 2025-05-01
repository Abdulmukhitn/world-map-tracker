// Change from ES modules to CDN usage
const client = new Appwrite.Client();
const auth = new Appwrite.Account(client);

client
    .setEndpoint('https://fra.cloud.appwrite.io/v1')
    .setProject('68125b020008f58668cb');

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Appwrite
    const client = new Appwrite();
    
    // Set Appwrite project details
    client
        .setEndpoint('https://fra.cloud.appwrite.io/v1')
        .setProject('68125b020008f58668cb');
    
    const account = new Appwrite.Account(client);
    
    const googleLoginBtn = document.getElementById('google-login');
    const loginForm = document.getElementById('login-form');
    
    // Handle Google Login
    if (googleLoginBtn) {
        googleLoginBtn.addEventListener('click', async function(e) {
            e.preventDefault();
            try {
                console.log('Starting Google OAuth...');
                // Create OAuth2 session
                const session = await account.createOAuth2Session(
                    'google',
                    'https://world-map-tracker-gnda.onrender.com/auth/callback',
                    'https://world-map-tracker-gnda.onrender.com/users/login/',
                    ['profile', 'email']
                );
                console.log('OAuth session created:', session);
            } catch (error) {
                console.error('Google login failed:', error);
                const errorDiv = document.createElement('div');
                errorDiv.className = 'error-message';
                errorDiv.textContent = 'Failed to login with Google. Please try again.';
                googleLoginBtn.parentNode.insertBefore(errorDiv, googleLoginBtn.nextSibling);
            }
        });
    }

    // Handle Traditional Login
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const username = document.getElementById('id_username').value;
            const password = document.getElementById('id_password').value;

            try {
                await auth.createEmailSession(username, password);
                window.location.href = '/';
            } catch (error) {
                console.error('Login failed:', error);
                showError('Invalid username or password.');
            }
        });
    }

    function showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        
        const existingError = document.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }
        
        loginForm?.appendChild(errorDiv);
    }
});