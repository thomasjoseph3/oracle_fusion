import React from "react";
import { Bar } from "react-chartjs-2";
import "chart.js/auto";

export default function Chart({ data }) {
    console.log("inside chat compoent")
    const { columns, rows } = data;

    if (!columns || !rows || rows.length === 0) {
        return <p>No data available</p>;
    }

    const labels = rows.map(row => row[0]);

    const singleColor = "#4CAF50"; 
    const multiColors = ["#FF9800", "#4CAF50", "#2196F3", "#9C27B0", "#FFC107"];


    const datasets = columns.slice(1).map((col, colIndex) => ({
        label: col,
        data: rows.map(row => row[colIndex + 1]),
        // backgroundColor: col.toLowerCase().includes("profit") ? "#FF9800" : "#4CAF50",
        backgroundColor: columns.length > 2 ? multiColors[colIndex % multiColors.length] : singleColor,

    }));
    const chartData = {
        labels,
        datasets,
    };

    console.log({chartData})

    const options = {
        responsive: true,
        plugins: {
            legend: { display: true },
        },
        scales: {
            x: {
                grid: { display: false },
                title: {
                    display: true,
                    text: columns[0], 
                },
            },
            y: {
                beginAtZero: true,
                grid: { display: true },
                title: {
                    display: true,
                    // text: "Amount in AED",
                },
            },
        },
    };

    return (
        <div>
            <h3 className="font-medium text-[15px] pb-3 text-[#1A1C1D]">{columns[0]}</h3>
            <Bar data={chartData} options={options} />
        </div>
    );
}
