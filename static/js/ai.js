document.addEventListener('DOMContentLoaded', function() {
    const countrySelect = document.getElementById('country-select');
    const queryInput = document.getElementById('query-input');
    const askButton = document.getElementById('ask-ai');
    const aiResponse = document.getElementById('ai-response');

    askButton.addEventListener('click', function() {
        const countryIso = countrySelect.value;
        const query = queryInput.value;
        if (!countryIso || !query) {
            aiResponse.style.display = 'block';
            aiResponse.innerHTML = '<p class="text-danger">Please select a country and enter a query.</p>';
            return;
        }

        fetch(`/ai_guide/api/travel-guide/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
            body: JSON.stringify({ country_iso: countryIso, query: query }),
        })
        .then(response => response.json())
        .then(data => {
            aiResponse.style.display = 'block';
            if (data.response) {
                aiResponse.innerHTML = `<p>${data.response}</p>`;
            } else {
                aiResponse.innerHTML = '<p class="text-danger">Error: Unable to get a response.</p>';
            }
        })
        .catch(error => {
            aiResponse.style.display = 'block';
            aiResponse.innerHTML = '<p class="text-danger">Error: Unable to connect to the AI guide.</p>';
        });
    });

    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
});