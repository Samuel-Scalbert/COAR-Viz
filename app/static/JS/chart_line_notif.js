document.addEventListener("DOMContentLoaded", function () {
    // Fetch notification counts from Flask
    fetch("/software/api/notification_count")
        .then(response => response.json())
        .then(data => {
            const labels = [];
            const notificationData = [];

            console.log(data)

            const skipped = (ctx, value) => ctx.p0.skip || ctx.p1.skip ? value : undefined;

            // Prepare data for the chart
            const chartData = {
                labels: labels,
                datasets: [
                    {
                        label: 'Notifications (last 30 days)',
                        data: notificationData,
                        fill: false,
                        spanGaps: true, // allows NaN to show as gaps
                        segment: {
                            borderColor: ctx => skipped(ctx, 'rgb(0,0,0,0.2)'),
                            borderDash: ctx => skipped(ctx, [6, 6]),
                        },
                    }
                ]
            };

            // Chart configuration
            const chartConfig = {
                type: 'line',
                data: chartData,
                options: {
                    fill: false,
                    radius: 5,
                    interaction: { intersect: false },
                    plugins: {
                        datalabels: {
                            display: false
                        }
                    },
                    scales: {
                        x: {
                            display: true,
                            title: {
                                display: true,
                                text: 'Date'
                            }
                        },
                        y: {
                            display: true,
                            title: {
                                display: true,
                                text: 'Number of Notifications'
                            },
                            beginAtZero: true
                        }
                    }
                }
            };

            // Render the chart
            const ctx = document.getElementById('lineChartNotif').getContext('2d');
            window.myLineChart = new Chart(ctx, chartConfig);
        })
        .catch(error => console.error("Error fetching notification data:", error));
});
