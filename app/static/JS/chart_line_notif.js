document.addEventListener("DOMContentLoaded", function () {
// Generate fake data for the last 30 days
const labels = [];
let notificationData = [];

// Create 30 days of sample data
for (let i = 29; i >= 0; i--) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    const dayLabel = `${date.getMonth() + 1}/${date.getDate()}`; // e.g. "11/05"
    labels.push(dayLabel);

    // Fake random notification count between 5 and 100
    notificationData = [73, 61, 20, 93, 74, NaN, 58, 52, 57, 52, 34, NaN, 65, 69, 54, 7, 24, 53, NaN, 9, NaN, 99, 8, 80, 61, 90, NaN, 10, 63, 82];
}

console.log(notificationData)

const skipped = (ctx, value) => ctx.p0.skip || ctx.p1.skip ? value : undefined;

// Prepare data for the chart
const chartData = {
    labels: labels,
    datasets: [
        {
            label: 'Notifications (last 30 days)',
            data: notificationData,
            fill: false,
            spanGaps: true,
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
        radius : 5,
        interaction: {intersect: false},
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
window.myLineChart = new Chart(ctx, chartConfig);})
