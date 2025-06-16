// Improvements for IVA Margem Turismo Frontend

// 1. Missing functions for buttons
const missingFunctions = `
                // Download Excel function
                async downloadExcel() {
                    if (!this.sessionId || !this.finalResults.totalSales) {
                        this.showNotification('Aviso', 'Por favor calcule primeiro os resultados', 'warning');
                        return;
                    }
                    
                    this.loading = true;
                    this.loadingMessage = 'A gerar ficheiro Excel...';
                    
                    try {
                        const response = await fetch(\`\${this.apiUrl}/api/calculate\`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                session_id: this.sessionId,
                                vat_rate: this.vatRate
                            })
                        });
                        
                        if (!response.ok) {
                            throw new Error('Erro ao gerar Excel');
                        }
                        
                        const blob = await response.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = \`iva_margem_\${new Date().toISOString().split('T')[0]}.xlsx\`;
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                        window.URL.revokeObjectURL(url);
                        
                        this.showNotification('Sucesso!', 'Ficheiro Excel descarregado', 'success');
                        
                    } catch (error) {
                        console.error('Download error:', error);
                        this.showNotification('Erro', 'Erro ao descarregar Excel', 'error');
                    } finally {
                        this.loading = false;
                    }
                },
                
                // Start new analysis
                startNew() {
                    if (confirm('Tem a certeza que deseja iniciar uma nova análise? Os dados atuais serão perdidos.')) {
                        // Reset all data
                        this.currentStep = 1;
                        this.sessionId = null;
                        this.sales = [];
                        this.costs = [];
                        this.selectedSales = [];
                        this.selectedCosts = [];
                        this.finalResults = {};
                        this.efaturaFiles = {
                            vendas: null,
                            compras: null
                        };
                        
                        // Clear session storage
                        localStorage.removeItem('ivaSession');
                        
                        this.showNotification('Nova Análise', 'Pronto para iniciar nova análise', 'info');
                    }
                },
                
                // Download PDF function
                async downloadPDF() {
                    if (!this.sessionId || !this.finalResults.totalSales) {
                        this.showNotification('Aviso', 'Por favor calcule primeiro os resultados', 'warning');
                        return;
                    }
                    
                    this.loading = true;
                    this.loadingMessage = 'A gerar PDF...';
                    
                    try {
                        const response = await fetch(\`\${this.apiUrl}/api/export-pdf\`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                session_id: this.sessionId,
                                vat_rate: this.vatRate,
                                results: this.finalResults
                            })
                        });
                        
                        if (!response.ok) {
                            throw new Error('Erro ao gerar PDF');
                        }
                        
                        const blob = await response.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = \`relatorio_iva_margem_\${new Date().toISOString().split('T')[0]}.pdf\`;
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                        window.URL.revokeObjectURL(url);
                        
                        this.showNotification('Sucesso!', 'Relatório PDF descarregado', 'success');
                        
                    } catch (error) {
                        console.error('PDF download error:', error);
                        this.showNotification('Erro', 'Erro ao gerar PDF', 'error');
                    } finally {
                        this.loading = false;
                    }
                },`;

// 2. Icons for suppliers function
const supplierIconsFunction = `
                // Get icon for supplier type
                getSupplierIcon(supplier) {
                    const supplierLower = supplier.toLowerCase();
                    
                    // Hotels
                    if (supplierLower.includes('hotel') || supplierLower.includes('pestana') || 
                        supplierLower.includes('marriott') || supplierLower.includes('hilton') ||
                        supplierLower.includes('radisson') || supplierLower.includes('ibis')) {
                        return 'fas fa-bed';
                    }
                    
                    // Airlines
                    if (supplierLower.includes('tap') || supplierLower.includes('ryanair') || 
                        supplierLower.includes('easyjet') || supplierLower.includes('lufthansa') ||
                        supplierLower.includes('air') || supplierLower.includes('fly') ||
                        supplierLower.includes('aviacao') || supplierLower.includes('aviação')) {
                        return 'fas fa-plane';
                    }
                    
                    // Car rental
                    if (supplierLower.includes('rent') || supplierLower.includes('car') || 
                        supplierLower.includes('auto') || supplierLower.includes('hertz') ||
                        supplierLower.includes('avis') || supplierLower.includes('europcar')) {
                        return 'fas fa-car';
                    }
                    
                    // Trains
                    if (supplierLower.includes('cp ') || supplierLower.includes('comboios') || 
                        supplierLower.includes('train') || supplierLower.includes('rail')) {
                        return 'fas fa-train';
                    }
                    
                    // Restaurants
                    if (supplierLower.includes('restaurante') || supplierLower.includes('restaurant') || 
                        supplierLower.includes('cafe') || supplierLower.includes('café')) {
                        return 'fas fa-utensils';
                    }
                    
                    // Tourism activities
                    if (supplierLower.includes('tour') || supplierLower.includes('excurs') || 
                        supplierLower.includes('museu') || supplierLower.includes('museum')) {
                        return 'fas fa-map-marked-alt';
                    }
                    
                    // Cruises
                    if (supplierLower.includes('cruise') || supplierLower.includes('cruzeiro') || 
                        supplierLower.includes('navio')) {
                        return 'fas fa-ship';
                    }
                    
                    // Bus
                    if (supplierLower.includes('bus') || supplierLower.includes('autocarro') || 
                        supplierLower.includes('transporte')) {
                        return 'fas fa-bus';
                    }
                    
                    // Insurance
                    if (supplierLower.includes('seguro') || supplierLower.includes('insurance')) {
                        return 'fas fa-shield-alt';
                    }
                    
                    // Travel agencies
                    if (supplierLower.includes('viagens') || supplierLower.includes('travel') || 
                        supplierLower.includes('turismo')) {
                        return 'fas fa-globe-europe';
                    }
                    
                    // Default
                    return 'fas fa-receipt';
                },
                
                // Get icon color based on supplier type
                getSupplierIconColor(supplier) {
                    const icon = this.getSupplierIcon(supplier);
                    
                    switch(icon) {
                        case 'fas fa-bed': return 'text-blue-600';
                        case 'fas fa-plane': return 'text-sky-600';
                        case 'fas fa-car': return 'text-gray-600';
                        case 'fas fa-train': return 'text-green-600';
                        case 'fas fa-utensils': return 'text-orange-600';
                        case 'fas fa-map-marked-alt': return 'text-purple-600';
                        case 'fas fa-ship': return 'text-cyan-600';
                        case 'fas fa-bus': return 'text-yellow-600';
                        case 'fas fa-shield-alt': return 'text-indigo-600';
                        case 'fas fa-globe-europe': return 'text-teal-600';
                        default: return 'text-gray-500';
                    }
                },`;

// 3. Enhanced chart function with better quality
const enhancedChartFunction = `
                // Enhanced chart drawing with better quality
                drawChart() {
                    const ctx = document.getElementById('marginChart');
                    if (!ctx) return;
                    
                    // Destroy existing chart if any
                    if (this.chart) {
                        this.chart.destroy();
                    }
                    
                    // Create gradient backgrounds
                    const gradient1 = ctx.getContext('2d').createLinearGradient(0, 0, 0, 400);
                    gradient1.addColorStop(0, 'rgba(34, 197, 94, 0.8)');
                    gradient1.addColorStop(1, 'rgba(34, 197, 94, 0.3)');
                    
                    const gradient2 = ctx.getContext('2d').createLinearGradient(0, 0, 0, 400);
                    gradient2.addColorStop(0, 'rgba(239, 68, 68, 0.8)');
                    gradient2.addColorStop(1, 'rgba(239, 68, 68, 0.3)');
                    
                    const gradient3 = ctx.getContext('2d').createLinearGradient(0, 0, 0, 400);
                    gradient3.addColorStop(0, 'rgba(59, 130, 246, 0.8)');
                    gradient3.addColorStop(1, 'rgba(59, 130, 246, 0.3)');
                    
                    const gradient4 = ctx.getContext('2d').createLinearGradient(0, 0, 0, 400);
                    gradient4.addColorStop(0, 'rgba(147, 51, 234, 0.8)');
                    gradient4.addColorStop(1, 'rgba(147, 51, 234, 0.3)');
                    
                    this.chart = new Chart(ctx, {
                        type: 'bar',
                        data: {
                            labels: ['Vendas', 'Custos', 'Margem Bruta', 'IVA', 'Margem Líquida'],
                            datasets: [{
                                label: 'Valores (€)',
                                data: [
                                    this.finalResults.totalSales,
                                    -this.finalResults.totalCosts,
                                    this.finalResults.grossMargin,
                                    -this.finalResults.totalVAT,
                                    this.finalResults.netMargin
                                ],
                                backgroundColor: [
                                    gradient1,
                                    gradient2,
                                    gradient3,
                                    gradient4,
                                    gradient3
                                ],
                                borderColor: [
                                    'rgba(34, 197, 94, 1)',
                                    'rgba(239, 68, 68, 1)',
                                    'rgba(59, 130, 246, 1)',
                                    'rgba(147, 51, 234, 1)',
                                    'rgba(59, 130, 246, 1)'
                                ],
                                borderWidth: 2,
                                borderRadius: 8,
                                borderSkipped: false,
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: {
                                    display: false
                                },
                                title: {
                                    display: true,
                                    text: 'Análise Financeira - IVA sobre Margem',
                                    font: {
                                        size: 18,
                                        weight: 'bold',
                                        family: "'Work Sans', sans-serif"
                                    },
                                    padding: 20
                                },
                                tooltip: {
                                    callbacks: {
                                        label: function(context) {
                                            let label = context.dataset.label || '';
                                            if (label) {
                                                label += ': ';
                                            }
                                            const value = Math.abs(context.parsed.y);
                                            label += '€' + value.toLocaleString('pt-PT', {
                                                minimumFractionDigits: 2,
                                                maximumFractionDigits: 2
                                            });
                                            return label;
                                        }
                                    },
                                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                                    titleFont: {
                                        size: 14,
                                        weight: 'bold'
                                    },
                                    bodyFont: {
                                        size: 13
                                    },
                                    padding: 12,
                                    cornerRadius: 8
                                }
                            },
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    grid: {
                                        color: 'rgba(0, 0, 0, 0.05)',
                                        drawBorder: false
                                    },
                                    ticks: {
                                        callback: function(value) {
                                            return '€' + Math.abs(value).toLocaleString('pt-PT');
                                        },
                                        font: {
                                            size: 12
                                        }
                                    }
                                },
                                x: {
                                    grid: {
                                        display: false,
                                        drawBorder: false
                                    },
                                    ticks: {
                                        font: {
                                            size: 13,
                                            weight: '500'
                                        }
                                    }
                                }
                            },
                            animation: {
                                duration: 1500,
                                easing: 'easeInOutQuart'
                            }
                        }
                    });
                    
                    // Create pie chart for margin distribution
                    const pieCtx = document.getElementById('marginPieChart');
                    if (pieCtx) {
                        if (this.pieChart) {
                            this.pieChart.destroy();
                        }
                        
                        this.pieChart = new Chart(pieCtx, {
                            type: 'doughnut',
                            data: {
                                labels: ['Margem Líquida', 'IVA', 'Custos'],
                                datasets: [{
                                    data: [
                                        this.finalResults.netMargin,
                                        this.finalResults.totalVAT,
                                        this.finalResults.totalCosts
                                    ],
                                    backgroundColor: [
                                        'rgba(59, 130, 246, 0.8)',
                                        'rgba(147, 51, 234, 0.8)',
                                        'rgba(239, 68, 68, 0.8)'
                                    ],
                                    borderColor: [
                                        'rgba(59, 130, 246, 1)',
                                        'rgba(147, 51, 234, 1)',
                                        'rgba(239, 68, 68, 1)'
                                    ],
                                    borderWidth: 2
                                }]
                            },
                            options: {
                                responsive: true,
                                maintainAspectRatio: false,
                                plugins: {
                                    legend: {
                                        position: 'bottom',
                                        labels: {
                                            padding: 20,
                                            font: {
                                                size: 13
                                            }
                                        }
                                    },
                                    title: {
                                        display: true,
                                        text: 'Distribuição da Margem',
                                        font: {
                                            size: 16,
                                            weight: 'bold'
                                        },
                                        padding: 20
                                    },
                                    tooltip: {
                                        callbacks: {
                                            label: function(context) {
                                                const value = context.parsed;
                                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                                const percentage = ((value / total) * 100).toFixed(1);
                                                return context.label + ': €' + value.toLocaleString('pt-PT', {
                                                    minimumFractionDigits: 2
                                                }) + ' (' + percentage + '%)';
                                            }
                                        }
                                    }
                                },
                                animation: {
                                    animateRotate: true,
                                    animateScale: true
                                }
                            }
                        });
                    }
                },`;

// Export all improvements
export { missingFunctions, supplierIconsFunction, enhancedChartFunction };