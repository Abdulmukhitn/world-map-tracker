document.addEventListener('DOMContentLoaded', function() {
    // Travel Plans
    const planForm = document.getElementById('plan-form');
    if (planForm) {
        planForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(planForm);
            try {
                const response = await fetch('/api/travel-plans/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify(Object.fromEntries(formData))
                });
                if (response.ok) {
                    location.reload();
                }
            } catch (error) {
                console.error('Error:', error);
            }
        });
    }

    // Travel Groups
    const joinButtons = document.querySelectorAll('.join-group');
    joinButtons.forEach(button => {
        button.addEventListener('click', async () => {
            const groupId = button.dataset.groupId;
            try {
                const response = await fetch(`/api/groups/${groupId}/join/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                });
                if (response.ok) {
                    button.textContent = 'Leave Group';
                    button.classList.replace('btn-primary', 'btn-danger');
                }
            } catch (error) {
                console.error('Error:', error);
            }
        });
    });
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}