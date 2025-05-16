document.addEventListener('DOMContentLoaded', function() {
    // Fetch stats data
    fetch('/api/travel-stats/')
        .then(response => response.json())
        .then(data => {
            // Create regions chart
            const regionsCtx = document.getElementById('regionsChart').getContext('2d');
            new Chart(regionsCtx, {
                type: 'doughnut',
                data: {
                    labels: data.top_regions.map(r => r.country__region),
                    datasets: [{
                        data: data.top_regions.map(r => r.count),
                        backgroundColor: [
                            '#2ecc71',
                            '#3498db',
                            '#9b59b6',
                            '#f1c40f',
                            '#e74c3c'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Error:', error));

    // Add animation to stats cards
    const cards = document.querySelectorAll('.stats-card');
    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = 1;
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        },
        { threshold: 0.1 }
    );

    cards.forEach(card => {
        card.style.opacity = 0;
        card.style.transform = 'translateY(20px)';
        observer.observe(card);
    });
});