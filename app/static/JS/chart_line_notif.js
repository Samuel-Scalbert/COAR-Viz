document.addEventListener("DOMContentLoaded", () => {
    // Helper function to create a line chart with custom colors
    function createChart(apiUrl, elementId, label, yTitle, lineColor = "rgba(54,162,235,1)", pointColor = "rgba(54,162,235,1)") {
        fetch(apiUrl)
            .then(res => res.json())
            .then(data => {
                // Generate labels for the last 30 days (MM/DD)
                const labels = Array.from({ length: 30 }, (_, i) => {
                    const date = new Date();
                    date.setDate(date.getDate() - (29 - i));
                    return `${date.getMonth() + 1}/${date.getDate()}`;
                });

                // Function for dashed lines on skipped points
                const skipped = (ctx, value) =>
                    ctx.p0.skip || ctx.p1.skip ? value : undefined;

                // Build the chart
                const ctx = document.getElementById(elementId).getContext("2d");
                const chart = new Chart(ctx, {
                    type: "line",
                    data: {
                        labels,
                        datasets: [
                            {
                                label,
                                data,
                                fill: false,
                                spanGaps: true, // show gaps for null values
                                borderColor: lineColor,          // line color
                                pointBackgroundColor: pointColor, // point color
                                pointBorderColor: pointColor,
                                segment: {
                                    borderColor: ctx => skipped(ctx, "rgba(0,0,0,0.2)"),
                                    borderDash: ctx => skipped(ctx, [6, 6]),
                                },
                            },
                        ],
                    },
                    options: {
                        plugins: {
                            title: { display: false },
                            datalabels: { display: false },
                        },
                        radius: 5,
                        interaction: { intersect: false },
                        scales: {
                            x: { display: true },
                            y: {
                                display: true,
                                beginAtZero: true,
                                title: { display: true, text: yTitle },
                                ticks: {
                                    callback: value =>
                                        Number.isInteger(value) ? value : null,
                                },
                            },
                        },
                    },
                });

                // Store chart globally (optional)
                window[`myChart_${elementId}`] = chart;
            })
            .catch(err => console.error(`Error fetching ${label} data:`, err));
    }

    // Create all charts with custom line & point colors 🎨
    createChart(
        "/software/api/notification_count",
        "lineChartNotif",
        "Notifications received (last 30 days)",
        "Number of Notifications",
        "rgba(255, 159, 64, 1)",   // line color (orange)
        "rgba(255, 205, 86, 1)"    // point color (yellow)
    );

    createChart(
        "/software/api/mention_count",
        "lineChartMention",
        "Mentions received (last 30 days)",
        "Number of Mentions",
        "rgba(75, 192, 192, 1)",   // line color (teal)
        "rgba(75, 192, 192, 1)"    // point color (same)
    );

    createChart(
        "/software/api/accepted_count",
        "lineChartMentionAccepted",
        "Mentions accepted (last 30 days)",
        "Number of Mentions",
        "rgba(54, 162, 235, 1)",   // line color (blue)
        "rgba(54, 162, 235, 1)"    // point color (same)
    );

    createChart(
        "/software/api/rejected_count",
        "lineChartMentionRejected",
        "Mentions rejected (last 30 days)",
        "Number of Mentions",
        "rgba(255, 99, 132, 1)",   // line color (red)
        "rgba(255, 99, 132, 1)"    // point color (same)
    );
});
