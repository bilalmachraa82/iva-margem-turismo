// Advanced Chart Functions for IVA Margem Turismo
// Professional data visualization with 30 years of experience

function generateAdvancedTrendChart(calculations, finalResults) {
    // Group data by month for better trend analysis
    const monthlyData = {};
    
    calculations.forEach(calc => {
        const date = new Date(calc.date || calc.invoice_date);
        const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
        
        if (!monthlyData[monthKey]) {
            monthlyData[monthKey] = {
                month: monthKey,
                sales: 0,
                costs: 0,
                margin: 0,
                vatAmount: 0,
                count: 0,
                marginPercentages: []
            };
        }
        
        monthlyData[monthKey].sales += calc.sale_amount || 0;
        monthlyData[monthKey].costs += calc.total_allocated_costs || 0;
        monthlyData[monthKey].margin += calc.gross_margin || 0;
        monthlyData[monthKey].vatAmount += calc.vat_amount || 0;
        monthlyData[monthKey].count += 1;
        
        // Calculate margin percentage for each sale
        if (calc.sale_amount > 0) {
            monthlyData[monthKey].marginPercentages.push(
                (calc.gross_margin / calc.sale_amount) * 100
            );
        }
    });
    
    // Convert to array and sort by month
    const months = Object.values(monthlyData).sort((a, b) => a.month.localeCompare(b.month));
    
    // Calculate averages and trends
    months.forEach(month => {
        month.avgMarginPercent = month.marginPercentages.length > 0 
            ? month.marginPercentages.reduce((a, b) => a + b) / month.marginPercentages.length 
            : 0;
        month.avgSaleValue = month.sales / month.count;
    });
    
    return {
        type: 'line',
        data: {
            labels: months.map(m => {
                const [year, month] = m.month.split('-');
                const monthNames = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
                return `${monthNames[parseInt(month) - 1]} ${year}`;
            }),
            datasets: [
                {
                    label: 'Volume de Vendas',
                    data: months.map(m => m.sales),
                    borderColor: 'rgb(34, 197, 94)',
                    backgroundColor: 'rgba(34, 197, 94, 0.1)',
                    yAxisID: 'y',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Margem Bruta',
                    data: months.map(m => m.margin),
                    borderColor: 'rgb(59, 130, 246)',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    yAxisID: 'y',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Margem % Média',
                    data: months.map(m => m.avgMarginPercent),
                    borderColor: 'rgb(147, 51, 234)',
                    backgroundColor: 'rgba(147, 51, 234, 0.1)',
                    yAxisID: 'y1',
                    tension: 0.4,
                    borderDash: [5, 5],
                    pointStyle: 'rectRot',
                    pointRadius: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Análise de Tendências Mensais',
                    font: {
                        size: 18,
                        weight: 'bold'
                    }
                },
                subtitle: {
                    display: true,
                    text: 'Evolução do volume de vendas, margens e percentagem de lucro',
                    font: {
                        size: 14
                    },
                    padding: {
                        bottom: 20
                    }
                },
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 15
                    }
                },
                tooltip: {
                    callbacks: {
                        afterLabel: function(context) {
                            if (context.datasetIndex === 2) { // Margin percentage
                                return 'Meta recomendada: 15-20%';
                            }
                            return '';
                        }
                    }
                }
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Período'
                    },
                    grid: {
                        display: false
                    }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Valores (€)'
                    },
                    ticks: {
                        callback: function(value) {
                            return '€' + value.toLocaleString('pt-PT');
                        }
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Margem %'
                    },
                    ticks: {
                        callback: function(value) {
                            return value.toFixed(1) + '%';
                        }
                    },
                    grid: {
                        drawOnChartArea: false,
                    },
                }
            }
        }
    };
}

function generateMarginDistributionChart(calculations) {
    // Analyze margin distribution to identify patterns
    const marginRanges = {
        'Negativa': { count: 0, total: 0, color: 'rgb(239, 68, 68)' },
        '0-5%': { count: 0, total: 0, color: 'rgb(251, 146, 60)' },
        '5-10%': { count: 0, total: 0, color: 'rgb(250, 204, 21)' },
        '10-15%': { count: 0, total: 0, color: 'rgb(132, 204, 22)' },
        '15-20%': { count: 0, total: 0, color: 'rgb(34, 197, 94)' },
        '>20%': { count: 0, total: 0, color: 'rgb(16, 185, 129)' }
    };
    
    calculations.forEach(calc => {
        const marginPercent = calc.sale_amount > 0 ? (calc.gross_margin / calc.sale_amount) * 100 : 0;
        
        if (marginPercent < 0) {
            marginRanges['Negativa'].count++;
            marginRanges['Negativa'].total += calc.sale_amount;
        } else if (marginPercent <= 5) {
            marginRanges['0-5%'].count++;
            marginRanges['0-5%'].total += calc.sale_amount;
        } else if (marginPercent <= 10) {
            marginRanges['5-10%'].count++;
            marginRanges['5-10%'].total += calc.sale_amount;
        } else if (marginPercent <= 15) {
            marginRanges['10-15%'].count++;
            marginRanges['10-15%'].total += calc.sale_amount;
        } else if (marginPercent <= 20) {
            marginRanges['15-20%'].count++;
            marginRanges['15-20%'].total += calc.sale_amount;
        } else {
            marginRanges['>20%'].count++;
            marginRanges['>20%'].total += calc.sale_amount;
        }
    });
    
    return {
        type: 'bar',
        data: {
            labels: Object.keys(marginRanges),
            datasets: [{
                label: 'Número de Vendas',
                data: Object.values(marginRanges).map(r => r.count),
                backgroundColor: Object.values(marginRanges).map(r => r.color),
                borderWidth: 2,
                borderColor: 'white'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Distribuição das Margens de Lucro',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                subtitle: {
                    display: true,
                    text: 'Análise da rentabilidade por faixas de margem',
                    font: {
                        size: 12
                    }
                },
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        afterLabel: function(context) {
                            const range = marginRanges[context.label];
                            return [
                                `Volume: €${range.total.toLocaleString('pt-PT', {minimumFractionDigits: 2})}`,
                                `Média: €${(range.total / range.count).toLocaleString('pt-PT', {minimumFractionDigits: 2})}`
                            ];
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Número de Documentos'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Faixa de Margem'
                    }
                }
            }
        }
    };
}

function generateTopClientsChart(calculations) {
    // Aggregate by client
    const clientData = {};
    
    calculations.forEach(calc => {
        const client = calc.client || 'Sem nome';
        if (!clientData[client]) {
            clientData[client] = {
                sales: 0,
                margin: 0,
                count: 0
            };
        }
        clientData[client].sales += calc.sale_amount || 0;
        clientData[client].margin += calc.gross_margin || 0;
        clientData[client].count += 1;
    });
    
    // Sort by total sales and get top 10
    const topClients = Object.entries(clientData)
        .map(([name, data]) => ({
            name: name.length > 20 ? name.substring(0, 20) + '...' : name,
            ...data,
            marginPercent: data.sales > 0 ? (data.margin / data.sales) * 100 : 0
        }))
        .sort((a, b) => b.sales - a.sales)
        .slice(0, 10);
    
    return {
        type: 'bar',
        data: {
            labels: topClients.map(c => c.name),
            datasets: [
                {
                    label: 'Volume de Vendas',
                    data: topClients.map(c => c.sales),
                    backgroundColor: 'rgba(59, 130, 246, 0.8)',
                    borderColor: 'rgb(59, 130, 246)',
                    borderWidth: 1
                },
                {
                    label: 'Margem Bruta',
                    data: topClients.map(c => c.margin),
                    backgroundColor: 'rgba(34, 197, 94, 0.8)',
                    borderColor: 'rgb(34, 197, 94)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Top 10 Clientes por Volume',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                tooltip: {
                    callbacks: {
                        afterLabel: function(context) {
                            const client = topClients[context.dataIndex];
                            return `Margem: ${client.marginPercent.toFixed(1)}%`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '€' + value.toLocaleString('pt-PT');
                        }
                    }
                }
            }
        }
    };
}

// Export functions
window.advancedCharts = {
    generateAdvancedTrendChart,
    generateMarginDistributionChart,
    generateTopClientsChart
};