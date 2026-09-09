const dataElement = document.getElementById("monthly-data");

let monthlyData = [];

if (dataElement) {
    monthlyData = JSON.parse(dataElement.textContent);

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

const categoryDataElement = document.getElementById("category-data");

if (categoryDataElement) {
    const categoryData = JSON.parse(
        categoryDataElement.textContent
    );

    const chartCanvas = document.getElementById(
        "spendingCategoryChart"
    );

    if (chartCanvas && categoryData.length > 0) {

        const labels = categoryData.map(
            item => item.category
        );

        const amounts = categoryData.map(
            item => Number(item.amount)
        );

        new Chart(chartCanvas, {
            type: "doughnut",

            data: {
                labels: labels,

                datasets: [
                    {
                        data: amounts
                    }
                ]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,

                plugins: {
                    legend: {
                        position: "right",

                        labels: {
                            usePointStyle: true,
                            pointStyle: "circle",
                            padding: 16
                        }
                    },

                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return ` ₹${context.parsed.toFixed(2)}`;
                            }
                        }
                    }
                },

                cutout: "65%"
            }
        });

    } else if (chartCanvas) {

        const container = chartCanvas.parentElement;

        container.innerHTML = `
            <div class="chart-empty-state">
                <p>No expense data available yet.</p>
            </div>
        `;
    }
}

const monthlySpendingCanvas = document.getElementById(
    "monthlySpendingChart"
);

if (monthlySpendingCanvas && monthlyData.length > 0) {

    const spendingLabels = monthlyData.map(
        item => item.month
    );

    const spendingAmounts = monthlyData.map(
        item => Number(item.expenses)
    );

    new Chart(monthlySpendingCanvas, {
        type: "line",

        data: {
            labels: spendingLabels,

            datasets: [
                {
                    label: "Expenses",
                    data: spendingAmounts,
                    tension: 0.3,
                    fill: false,
                    pointRadius: 4,
                    pointHoverRadius: 6
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
                    display: false
                },

                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return ` ₹${context.parsed.y.toFixed(2)}`;
                        }
                    }
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

const categoryPeriodSelect = document.getElementById(
    "categoryPeriod"
);

if (categoryPeriodSelect) {
    categoryPeriodSelect.addEventListener(
        "change",
        function() {
            const selectedPeriod = this.value;

            const url = new URL(
                window.location.href
            );

            url.searchParams.set(
                "category_period",
                selectedPeriod
            );

            window.location.href = url.toString();
        }
    );
}

const budgetDataElement = document.getElementById(
    "budget-data"
);

if (budgetDataElement) {

    const budgetData = JSON.parse(
        budgetDataElement.textContent
    );

    const chartCanvas = document.getElementById(
        "budgetPerformanceChart"
    );

    if (chartCanvas && budgetData.length > 0) {

        const labels = budgetData.map(
            item => item.category
        );

        const budgetAmounts = budgetData.map(
            item => Number(item.budget)
        );

        const spentAmounts = budgetData.map(
            item => Number(item.spent)
        );

        new Chart(chartCanvas, {

            type: "bar",

            data: {
                labels: labels,

                datasets: [
                    {
                        label: "Budget",
                        data: budgetAmounts,

                        borderRadius: 6,
                        borderSkipped: false
                    },

                    {
                        label: "Spent",
                        data: spentAmounts,

                        borderRadius: 6,
                        borderSkipped: false
                    }
                ]
            },

            options: {

                indexAxis: "y",

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

                        callbacks: {

                            label: function(context) {

                                return ` ₹${context.parsed.x.toFixed(2)}`;

                            }

                        }

                    }

                },

                scales: {

                    x: {

                        beginAtZero: true,

                        grid: {
                            drawBorder: false
                        }

                    },

                    y: {

                        grid: {
                            display: false
                        }

                    }

                }

            }

        });

    } else if (chartCanvas) {

        const container = chartCanvas.parentElement;

        container.innerHTML = `
            <div class="chart-empty-state">
                <p>No budgets available for this month.</p>
            </div>
        `;
    }
}