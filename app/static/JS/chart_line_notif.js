document.addEventListener("DOMContentLoaded", function () {
    fetch("/api/notification_count")
        .then(response => response.json())
        .then(notificationData => {
            // Generate labels for the last 30 days (MM/DD)
            const labels = [];
            for (let i = 29; i >= 0; i--) {
                const date = new Date();
                date.setDate(date.getDate() - i);
                labels.push(`${date.getMonth() + 1}/${date.getDate()}`);
            }

            const skipped = (ctx, value) => ctx.p0.skip || ctx.p1.skip ? value : undefined;

            const chartData = {
                labels: labels,
                datasets: [
                    {
                        label: 'Notifications (last 30 days)',
                        data: notificationData,
                        fill: false,
                        spanGaps: true, // show gaps for NaN
                        segment: {
                            borderColor: ctx => skipped(ctx, 'rgb(0,0,0,0.2)'),
                            borderDash: ctx => skipped(ctx, [6, 6]),
                        },
                    }
                ]
            };

            const chartConfig = {
                type: 'line',
                data: chartData,
                options: {
                    fill: false,
                    radius: 5,
                    interaction: { intersect: false },
                    plugins: { datalabels: { display: false } },
                    scales: {
                        x: { display: true, title: { display: true, text: 'Date' } },
                        y: { display: true, title: { display: true, text: 'Number of Notifications' }, beginAtZero: true }
                    }
                }
            };

            const ctx = document.getElementById('lineChartNotif').getContext('2d');
            window.myLineChart = new Chart(ctx, chartConfig);
        })
        .catch(error => console.error("Error fetching notification data:", error));
});
