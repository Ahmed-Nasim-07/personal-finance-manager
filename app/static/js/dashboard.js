const dataElement = document.getElementById("monthly-data");

if (dataElement) {
    const monthlyData = JSON.parse(dataElement.textContent);

    const labels = monthlyData.map(item => item.month);
    const income = monthlyData.map(item => Number(item.income));
    const expenses = monthlyData.map(item => Number(item.expenses));

    const chartCanvas = document.getElementById("incomeExpenseChart");

    if (chartCanvas) {
        new Chart(chartCanvas, {
            type: "bar",

            data: {
                labels: labels,

                datasets: [
                    {
                        label: "Income",
                        data: income,
                        borderRadius: 6,
                        borderSkipped: false,
                        barPercentage: 0.7,
                        categoryPercentage: 0.7
                    },
                    {
                        label: "Expenses",
                        data: expenses,
                        borderRadius: 6,
                        borderSkipped: false,
                        barPercentage: 0.7,
                        categoryPercentage: 0.7
                    }
                ]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,

                interaction: {
                    mode: "index",
                    intersect: false
                },

                plugins: {
                    legend: {
                        position: "top",
                        align: "end",

                        labels: {
                            usePointStyle: true,
                            pointStyle: "circle",
                            padding: 20
                        }
                    },

                    tooltip: {
                        mode: "index",
                        intersect: false
                    }
                },

                scales: {
                    x: {
                        grid: {
                            display: false
                        }
                    },

                    y: {
                        beginAtZero: true,

                        grid: {
                            drawBorder: false
                        }
                    }
                }
            }
        });
    }
}