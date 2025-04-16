document.addEventListener('DOMContentLoaded', function() {
    // Monthly Spending Chart
    if (window.monthlyData) {
        const monthlyCtx = document.getElementById('monthlyChart').getContext('2d');
        const monthlyChart = new Chart(monthlyCtx, {
            type: 'bar',
            data: {
                labels: window.monthlyData.labels,
                datasets: [{
                    label: 'Dépenses mensuelles (€)',
                    data: window.monthlyData.data,
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // Category Breakdown Chart
    if (window.categoryData) {
        const categoryCtx = document.getElementById('categoryChart').getContext('2d');
        const categoryChart = new Chart(categoryCtx, {
            type: 'pie',
            data: {
                labels: window.categoryData.labels,
                datasets: [{
                    data: window.categoryData.data,
                    backgroundColor: window.categoryData.backgroundColor,
                    borderColor: window.categoryData.borderColor,
                    borderWidth: 1
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
    }
});
