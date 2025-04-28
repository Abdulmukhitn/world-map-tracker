document.addEventListener('DOMContentLoaded', function() {
    const logoutForm = document.querySelector('form[action="/logout/"]');
    if (logoutForm) {
        logoutForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            try {
                const response = await fetch('/logout/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    },
                });
                if (response.ok) {
                    window.location.href = '/users/login/';
                }
            } catch (error) {
                console.error('Logout failed:', error);
            }
        });
    }
});