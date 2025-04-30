// Change from ES modules to CDN usage
const client = new Appwrite.Client();
const auth = new Appwrite.Account(client);

client
    .setEndpoint('https://fra.cloud.appwrite.io/v1')
    .setProject('68125b020008f58668cb');

document.addEventListener('DOMContentLoaded', function() {
    const googleLoginBtn = document.getElementById('google-login');
    const loginForm = document.getElementById('login-form');
    
    // Handle Google Login
    if (googleLoginBtn) {
        googleLoginBtn.addEventListener('click', async function(e) {
            e.preventDefault();
            try {
                // Create OAuth2 session
                await auth.createOAuth2Session(
                    'google',
                    'https://fra.cloud.appwrite.io/v1/account/sessions/oauth2/callback/google/68125b020008f58668cb',
                    'https://world-map-tracker-gnda.onrender.com/users/login/?next=/',
                    ['profile', 'email']
                );
            } catch (error) {
                console.error('Google login failed:', error);
                showError('Failed to login with Google. Please try again.');
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