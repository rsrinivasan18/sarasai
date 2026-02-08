// Sarasai - Personal Stock Picker Application

class StockPickerApp {
    constructor() {
        this.baseURL = 'http://localhost:8000';
        this.portfolio = [];
        this.currentTab = 'dashboard';
        this.refreshInterval = null;
        this.settings = {
            currency: 'USD',
            refreshInterval: 60,
            autoRefresh: true
        };
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadSettings();
        this.loadPortfolio();
        this.loadAvailableStocks();
        this.setupAutoRefresh();
        
        // Initial load
        this.updateDashboard();
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-item').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchTab(e.target.getAttribute('data-tab'));
            });
        });

        // Add holding
        document.getElementById('add-holding-btn').addEventListener('click', () => {
            this.showAddHoldingModal();
        });

        // Search stocks
        document.getElementById('search-btn').addEventListener('click', () => {
            this.searchStock();
        });

        document.getElementById('stock-search').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.searchStock();
            }
        });

        // Portfolio analysis
        document.getElementById('analyze-btn').addEventListener('click', () => {
            this.runPortfolioAnalysis();
        });

        // Time period selection
        document.querySelectorAll('.time-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.time-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.updatePerformanceChart(e.target.getAttribute('data-period'));
            });
        });

        // Settings
        document.getElementById('currency-select').addEventListener('change', (e) => {
            this.settings.currency = e.target.value;
            this.saveSettings();
            this.updateDashboard();
        });

        document.getElementById('refresh-select').addEventListener('change', (e) => {
            this.settings.refreshInterval = parseInt(e.target.value);
            this.saveSettings();
            this.setupAutoRefresh();
        });

        document.getElementById('auto-refresh').addEventListener('change', (e) => {
            this.settings.autoRefresh = e.target.checked;
            this.saveSettings();
            this.setupAutoRefresh();
        });
    }

    switchTab(tabName) {
        // Hide all tabs
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.classList.remove('active');
        });

        // Show selected tab
        document.getElementById(`${tabName}-tab`).classList.add('active');

        // Update nav items
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        this.currentTab = tabName;

        // Load tab-specific content
        switch(tabName) {
            case 'dashboard':
                this.updateDashboard();
                break;
            case 'portfolio':
                this.updatePortfolioAnalysis();
                break;
            case 'stocks':
                this.loadAvailableStocks();
                break;
            case 'market':
                this.loadMarketData();
                break;
            case 'reports':
                this.loadReports();
                break;
            case 'settings':
                this.loadSettings();
                break;
        }
    }

    async loadAvailableStocks() {
        try {
            const response = await fetch(`${this.baseURL}/stocks`);
            const data = await response.json();
            
            const stocksList = document.getElementById('stocks-list');
            stocksList.innerHTML = '';
            
            data.stocks.forEach(stock => {
                const stockItem = document.createElement('div');
                stockItem.className = 'stock-item';
                stockItem.innerHTML = `
                    <div class="stock-info">
                        <div class="stock-symbol">${stock.symbol}</div>
                        <div class="stock-name">${stock.name}</div>
                        <div class="stock-price">$${stock.price.toFixed(2)}</div>
                    </div>
                    <div class="stock-actions">
                        <button class="btn-secondary btn-sm" onclick="app.viewStockDetails('${stock.symbol}')">
                            <i class="fas fa-chart-line"></i>
                            Analyze
                        </button>
                        <button class="btn-primary btn-sm" onclick="app.addStockToPortfolio('${stock.symbol}')">
                            <i class="fas fa-plus"></i>
                            Add
                        </button>
                    </div>
                `;
                stocksList.appendChild(stockItem);
            });
        } catch (error) {
            console.error('Error loading stocks:', error);
            document.getElementById('stocks-list').innerHTML = 
                '<div class="error">Failed to load stocks. Please try again.</div>';
        }
    }

    async searchStock() {
        const symbol = document.getElementById('stock-search').value.trim().toUpperCase();
        if (!symbol) return;

        await this.viewStockDetails(symbol);
    }

    async viewStockDetails(symbol) {
        try {
            this.showLoading('Loading stock details...');
            
            // Get stock recommendation
            const response = await fetch(`${this.baseURL}/portfolio/recommendation/${symbol}`);
            const data = await response.json();
            
            const stockDetails = document.getElementById('stock-details');
            stockDetails.innerHTML = `
                <div class="stock-detail-card">
                    <div class="stock-header">
                        <div class="stock-title">
                            <h3>${data.name} (${data.symbol})</h3>
                            <div class="stock-current-price">$${data.current_price.toFixed(2)}</div>
                        </div>
                        <div class="stock-recommendation">
                            <span class="rec-badge ${data.recommendation}">${data.recommendation.toUpperCase()}</span>
                            <span class="confidence">Confidence: ${data.confidence_score}/10</span>
                        </div>
                    </div>
                    
                    <div class="stock-analysis">
                        <div class="analysis-section">
                            <h4>Technical Analysis</h4>
                            <p>${data.technical_analysis}</p>
                        </div>
                        
                        <div class="analysis-section">
                            <h4>Fundamental Analysis</h4>
                            <p>${data.fundamental_analysis}</p>
                        </div>
                        
                        <div class="analysis-section">
                            <h4>News Sentiment</h4>
                            <p>${data.news_sentiment}</p>
                        </div>
                        
                        <div class="analysis-section">
                            <h4>Expert Consensus</h4>
                            <p>${data.guru_consensus}</p>
                        </div>
                        
                        <div class="analysis-section">
                            <h4>Reasoning</h4>
                            <p>${data.reasoning_summary}</p>
                        </div>
                    </div>
                    
                    <div class="stock-actions">
                        <button class="btn-primary" onclick="app.addStockToPortfolio('${symbol}')">
                            <i class="fas fa-plus"></i>
                            Add to Portfolio
                        </button>
                        <button class="btn-secondary" onclick="window.open('${this.baseURL}/portfolio/dashboard/${symbol}', '_blank')">
                            <i class="fas fa-external-link-alt"></i>
                            Full Report
                        </button>
                    </div>
                </div>
            `;
            
            // Update stock chart
            this.updateStockChart(data);
            
        } catch (error) {
            console.error('Error loading stock details:', error);
            document.getElementById('stock-details').innerHTML = 
                '<div class="error">Failed to load stock details. Please try again.</div>';
        } finally {
            this.hideLoading();
        }
    }

    updateStockChart(stockData) {
        // Create a simple price chart using Plotly
        const chartData = [{
            x: ['Current'],
            y: [stockData.current_price],
            type: 'bar',
            marker: {
                color: stockData.recommendation === 'buy' ? '#10b981' : 
                       stockData.recommendation === 'sell' ? '#ef4444' : '#f59e0b'
            }
        }];

        const layout = {
            title: `${stockData.symbol} Price`,
            xaxis: { title: 'Time' },
            yaxis: { title: 'Price ($)' },
            margin: { t: 50, r: 50, b: 50, l: 50 }
        };

        Plotly.newPlot('stock-chart', chartData, layout);
    }

    showAddHoldingModal() {
        document.getElementById('add-holding-modal').classList.add('active');
    }

    closeAddHoldingModal() {
        document.getElementById('add-holding-modal').classList.remove('active');
        document.getElementById('add-holding-form').reset();
    }

    async addHolding() {
        const form = document.getElementById('add-holding-form');
        const formData = new FormData(form);
        
        const holding = {
            symbol: formData.get('symbol').toUpperCase(),
            quantity: parseInt(formData.get('quantity')),
            avg_price: parseFloat(formData.get('avg_price'))
        };

        // Validate
        if (!holding.symbol || !holding.quantity || !holding.avg_price) {
            alert('Please fill all fields');
            return;
        }

        // Check if stock already exists
        const existingIndex = this.portfolio.findIndex(h => h.symbol === holding.symbol);
        if (existingIndex >= 0) {
            // Update existing holding
            const existing = this.portfolio[existingIndex];
            const totalShares = existing.quantity + holding.quantity;
            const totalValue = (existing.quantity * existing.avg_price) + (holding.quantity * holding.avg_price);
            
            this.portfolio[existingIndex] = {
                ...existing,
                quantity: totalShares,
                avg_price: totalValue / totalShares
            };
        } else {
            // Add new holding
            this.portfolio.push(holding);
        }

        this.savePortfolio();
        this.closeAddHoldingModal();
        this.updateDashboard();
        
        // Show success message
        this.showNotification(`Added ${holding.quantity} shares of ${holding.symbol}`, 'success');
    }

    addStockToPortfolio(symbol) {
        document.getElementById('symbol').value = symbol;
        this.showAddHoldingModal();
    }

    async updateDashboard() {
        if (this.portfolio.length === 0) {
            this.showEmptyPortfolio();
            return;
        }

        try {
            this.showLoading('Analyzing portfolio...');

            // Analyze portfolio
            const response = await fetch(`${this.baseURL}/portfolio/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    holdings: this.portfolio
                })
            });

            const analysis = await response.json();
            
            // Update summary stats
            document.getElementById('total-value').textContent = `$${analysis.current_value.toLocaleString()}`;
            document.getElementById('total-gain').textContent = 
                `${analysis.total_profit_loss >= 0 ? '+' : ''}$${analysis.total_profit_loss.toLocaleString()}`;
            document.getElementById('gain-percent').textContent = 
                `${analysis.total_profit_loss_percent >= 0 ? '+' : ''}${analysis.total_profit_loss_percent.toFixed(2)}%`;

            // Update holdings table
            this.updateHoldingsTable(analysis.holdings);

            // Update portfolio chart
            this.updatePortfolioChart(analysis.holdings);

            // Update recommendations
            this.updateRecommendations(analysis.recommendations);

            // Update news
            this.updateMarketNews(analysis.recommendations);

            // Update performance chart
            this.updatePerformanceChart('1M');

        } catch (error) {
            console.error('Error updating dashboard:', error);
            this.showNotification('Failed to update dashboard', 'error');
        } finally {
            this.hideLoading();
        }
    }

    showEmptyPortfolio() {
        document.getElementById('total-value').textContent = '$0';
        document.getElementById('total-gain').textContent = '$0';
        document.getElementById('gain-percent').textContent = '0%';
        
        const tbody = document.getElementById('holdings-tbody');
        tbody.innerHTML = `
            <tr class="empty-state">
                <td colspan="10">
                    <div class="empty-content">
                        <i class="fas fa-chart-line"></i>
                        <p>No holdings yet. Add your first stock to get started!</p>
                        <button class="btn-primary" onclick="app.showAddHoldingModal()">
                            <i class="fas fa-plus"></i>
                            Add First Stock
                        </button>
                    </div>
                </td>
            </tr>
        `;

        // Clear charts
        document.getElementById('portfolio-chart').innerHTML = '';
        document.getElementById('performance-chart').innerHTML = '';
    }

    updateHoldingsTable(holdings) {
        const tbody = document.getElementById('holdings-tbody');
        tbody.innerHTML = '';

        holdings.forEach((holding, index) => {
            const row = document.createElement('tr');
            row.className = 'holdings-row';
            
            // Get recommendation for this symbol (we'll store it during analysis)
            const recommendation = this.getRecommendationForSymbol(holding.symbol);
            
            row.innerHTML = `
                <td class="symbol-cell">
                    <div class="symbol-container">
                        <span class="symbol-text">${holding.symbol}</span>
                        <span class="symbol-exchange">${holding.currency}</span>
                    </div>
                </td>
                <td class="name-cell">
                    <div class="name-container">
                        <span class="company-name">${holding.name}</span>
                        <span class="company-sector">Technology</span>
                    </div>
                </td>
                <td class="quantity-cell">
                    <span class="quantity-number">${holding.quantity.toLocaleString()}</span>
                    <span class="quantity-label">shares</span>
                </td>
                <td class="price-cell">$${holding.avg_purchase_price.toFixed(2)}</td>
                <td class="price-cell">
                    <span class="current-price">$${holding.current_price.toFixed(2)}</span>
                    <span class="price-change ${holding.current_price >= holding.avg_purchase_price ? 'positive' : 'negative'}">
                        ${holding.current_price >= holding.avg_purchase_price ? '↗' : '↘'}
                    </span>
                </td>
                <td class="value-cell">
                    <span class="market-value">$${holding.current_value.toLocaleString()}</span>
                </td>
                <td class="pnl-cell ${holding.profit_loss >= 0 ? 'profit' : 'loss'}">
                    <div class="pnl-container">
                        <span class="pnl-amount">
                            ${holding.profit_loss >= 0 ? '+' : ''}$${Math.abs(holding.profit_loss).toLocaleString()}
                        </span>
                        <span class="pnl-percent">
                            (${holding.profit_loss_percent >= 0 ? '+' : ''}${holding.profit_loss_percent.toFixed(2)}%)
                        </span>
                    </div>
                </td>
                <td class="recommendation-cell">
                    <div class="rec-container">
                        <span class="rec-badge rec-${recommendation}">${recommendation.toUpperCase()}</span>
                        <span class="rec-confidence">8.5/10</span>
                    </div>
                </td>
                <td class="actions-cell">
                    <div class="action-buttons">
                        <button class="action-btn primary" onclick="app.viewStockDetails('${holding.symbol}')" title="Detailed Analysis">
                            <i class="fas fa-chart-line"></i>
                            <span>Analyze</span>
                        </button>
                        <button class="action-btn secondary" onclick="app.openStockDashboard('${holding.symbol}')" title="Full Dashboard">
                            <i class="fas fa-external-link-alt"></i>
                            <span>Dashboard</span>
                        </button>
                        <button class="action-btn danger" onclick="app.removeHolding(${index})" title="Remove from Portfolio">
                            <i class="fas fa-trash"></i>
                            <span>Remove</span>
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });

        // Add sorting functionality
        this.makeTableSortable();
    }

    makeTableSortable() {
        const table = document.getElementById('holdings-table');
        const headers = table.querySelectorAll('th');
        
        headers.forEach((header, index) => {
            if (index === headers.length - 1) return; // Skip actions column
            
            header.style.cursor = 'pointer';
            header.addEventListener('click', () => {
                this.sortTable(index);
            });
        });
    }

    sortTable(columnIndex) {
        const table = document.getElementById('holdings-table');
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr:not(.empty-state)'));
        
        if (rows.length === 0) return;

        // Get current sort direction for this column
        const headers = table.querySelectorAll('th');
        const currentHeader = headers[columnIndex];
        const currentDirection = currentHeader.getAttribute('data-sort-direction') || 'none';
        
        // Clear all sort indicators
        headers.forEach(header => {
            header.removeAttribute('data-sort-direction');
            header.classList.remove('sort-asc', 'sort-desc');
        });

        // Determine new sort direction
        let newDirection = 'asc';
        if (currentDirection === 'asc') {
            newDirection = 'desc';
        }

        // Set new sort direction
        currentHeader.setAttribute('data-sort-direction', newDirection);
        currentHeader.classList.add(`sort-${newDirection}`);

        // Sort the rows
        rows.sort((a, b) => {
            const cellA = a.cells[columnIndex];
            const cellB = b.cells[columnIndex];
            
            let valueA = this.extractSortValue(cellA, columnIndex);
            let valueB = this.extractSortValue(cellB, columnIndex);
            
            // Handle numeric comparison
            if (!isNaN(valueA) && !isNaN(valueB)) {
                return newDirection === 'asc' ? valueA - valueB : valueB - valueA;
            }
            
            // Handle string comparison
            valueA = valueA.toString().toLowerCase();
            valueB = valueB.toString().toLowerCase();
            
            if (newDirection === 'asc') {
                return valueA.localeCompare(valueB);
            } else {
                return valueB.localeCompare(valueA);
            }
        });

        // Re-append sorted rows
        rows.forEach(row => tbody.appendChild(row));
    }

    extractSortValue(cell, columnIndex) {
        // Column-specific value extraction
        switch(columnIndex) {
            case 0: // Symbol
                return cell.querySelector('.symbol-text')?.textContent || '';
            case 1: // Name
                return cell.querySelector('.company-name')?.textContent || '';
            case 2: // Quantity
                const quantityText = cell.querySelector('.quantity-number')?.textContent || '0';
                return parseFloat(quantityText.replace(/,/g, ''));
            case 3: // Avg Price
                const avgPrice = cell.textContent.replace(/[$,]/g, '');
                return parseFloat(avgPrice);
            case 4: // Current Price
                const currentPrice = cell.querySelector('.current-price')?.textContent.replace(/[$,]/g, '') || '0';
                return parseFloat(currentPrice);
            case 5: // Market Value
                const marketValue = cell.querySelector('.market-value')?.textContent.replace(/[$,]/g, '') || '0';
                return parseFloat(marketValue);
            case 6: // P&L
                const pnlText = cell.querySelector('.pnl-amount')?.textContent.replace(/[$,+]/g, '') || '0';
                return parseFloat(pnlText);
            case 7: // Recommendation
                return cell.querySelector('.rec-badge')?.textContent || '';
            default:
                return cell.textContent || '';
        }
    }

    openStockDashboard(symbol) {
        window.open(`${this.baseURL}/portfolio/dashboard/${symbol}`, '_blank');
    }

    updatePortfolioChart(holdings) {
        const data = [{
            labels: holdings.map(h => h.symbol),
            values: holdings.map(h => h.current_value),
            type: 'pie',
            marker: {
                colors: ['#667eea', '#764ba2', '#10b981', '#f59e0b', '#ef4444', '#3b82f6']
            }
        }];

        const layout = {
            title: 'Portfolio Allocation',
            margin: { t: 50, r: 50, b: 50, l: 50 },
            showlegend: true
        };

        Plotly.newPlot('portfolio-chart', data, layout);
    }

    updatePerformanceChart(period) {
        // Mock performance data for different periods
        const mockData = {
            '1M': {
                dates: Array.from({length: 30}, (_, i) => {
                    const date = new Date();
                    date.setDate(date.getDate() - (29 - i));
                    return date.toISOString().split('T')[0];
                }),
                values: Array.from({length: 30}, (_, i) => {
                    const totalValue = this.portfolio.reduce((sum, h) => sum + (h.quantity * h.avg_price), 0);
                    return totalValue * (1 + (Math.random() - 0.5) * 0.1 + i * 0.002);
                })
            }
        };

        const data = [{
            x: mockData[period].dates,
            y: mockData[period].values,
            type: 'scatter',
            mode: 'lines',
            line: { color: '#667eea', width: 2 }
        }];

        const layout = {
            title: `Portfolio Performance (${period})`,
            xaxis: { title: 'Date' },
            yaxis: { title: 'Value ($)' },
            margin: { t: 50, r: 50, b: 50, l: 50 }
        };

        Plotly.newPlot('performance-chart', data, layout);
    }

    updateRecommendations(recommendations) {
        const container = document.getElementById('recommendations-list');
        container.innerHTML = '';

        if (!recommendations || recommendations.length === 0) {
            container.innerHTML = `
                <div class="recommendation-item">
                    <div class="rec-icon rec-buy">📈</div>
                    <div class="rec-content">
                        <span class="rec-text">Add holdings to see personalized recommendations</span>
                    </div>
                </div>
            `;
            return;
        }

        recommendations.slice(0, 3).forEach(rec => {
            const item = document.createElement('div');
            item.className = 'recommendation-item';
            item.innerHTML = `
                <div class="rec-icon rec-${rec.recommendation}">
                    ${rec.recommendation === 'buy' ? '📈' : rec.recommendation === 'sell' ? '📉' : '⏸️'}
                </div>
                <div class="rec-content">
                    <div class="rec-symbol">${rec.symbol}</div>
                    <div class="rec-text">${rec.recommendation.toUpperCase()}: ${rec.reasoning_summary.substring(0, 100)}...</div>
                    <div class="rec-confidence">Confidence: ${rec.confidence_score}/10</div>
                </div>
            `;
            container.appendChild(item);
        });
    }

    async updateMarketNews(recommendations) {
        const container = document.getElementById('news-list');
        
        if (!recommendations || recommendations.length === 0) {
            container.innerHTML = `
                <div class="news-item">
                    <div class="news-content">
                        <span class="news-title">Add holdings to see relevant market news</span>
                        <span class="news-source">Sarasai</span>
                    </div>
                    <div class="news-sentiment neutral">
                        <span>Neutral</span>
                    </div>
                </div>
            `;
            return;
        }

        container.innerHTML = '';
        
        // Get news from first few stocks
        for (let i = 0; i < Math.min(3, recommendations.length); i++) {
            const rec = recommendations[i];
            if (rec.recent_news && rec.recent_news.length > 0) {
                const news = rec.recent_news[0]; // Get first news item
                const item = document.createElement('div');
                item.className = 'news-item';
                item.innerHTML = `
                    <div class="news-content">
                        <span class="news-title">${news.title}</span>
                        <span class="news-source">${news.source} • ${rec.symbol}</span>
                    </div>
                    <div class="news-sentiment ${news.sentiment_label}">
                        <span>${news.sentiment_label}</span>
                    </div>
                `;
                container.appendChild(item);
            }
        }
    }

    async runPortfolioAnalysis() {
        if (this.portfolio.length === 0) {
            this.showNotification('Add holdings to your portfolio first', 'warning');
            return;
        }

        try {
            this.showLoading('Running comprehensive portfolio analysis...');

            const response = await fetch(`${this.baseURL}/portfolio/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    holdings: this.portfolio
                })
            });

            const analysis = await response.json();
            this.updatePortfolioAnalysisResults(analysis);

        } catch (error) {
            console.error('Error running portfolio analysis:', error);
            this.showNotification('Failed to analyze portfolio', 'error');
        } finally {
            this.hideLoading();
        }
    }

    updatePortfolioAnalysisResults(analysis) {
        // Update risk score
        document.getElementById('risk-score').textContent = analysis.portfolio_risk_score;
        document.getElementById('risk-description').textContent = 
            this.getRiskDescription(analysis.portfolio_risk_score);

        // Update diversification score
        document.getElementById('div-score').textContent = analysis.diversification_score;
        document.getElementById('div-description').textContent = 
            this.getDiversificationDescription(analysis.diversification_score);

        // Update detailed analysis
        const container = document.getElementById('analysis-results');
        container.innerHTML = `
            <div class="analysis-summary">
                <div class="summary-card">
                    <h4>Portfolio Summary</h4>
                    <div class="summary-stats">
                        <div class="stat">
                            <span class="stat-label">Total Invested</span>
                            <span class="stat-value">$${analysis.total_invested.toLocaleString()}</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Current Value</span>
                            <span class="stat-value">$${analysis.current_value.toLocaleString()}</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Total Return</span>
                            <span class="stat-value ${analysis.total_profit_loss >= 0 ? 'text-success' : 'text-danger'}">
                                ${analysis.total_profit_loss >= 0 ? '+' : ''}$${analysis.total_profit_loss.toLocaleString()}
                                (${analysis.total_profit_loss_percent.toFixed(2)}%)
                            </span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Overall Sentiment</span>
                            <span class="stat-value">${analysis.overall_sentiment.toUpperCase()}</span>
                        </div>
                    </div>
                </div>

                <div class="recommendations-detailed">
                    <h4>Stock Recommendations</h4>
                    ${analysis.recommendations.map(rec => `
                        <div class="rec-detail-card">
                            <div class="rec-header">
                                <span class="rec-symbol">${rec.symbol}</span>
                                <span class="rec-badge ${rec.recommendation}">${rec.recommendation.toUpperCase()}</span>
                                <span class="rec-confidence">Confidence: ${rec.confidence_score}/10</span>
                            </div>
                            <div class="rec-reasoning">
                                <p><strong>Technical:</strong> ${rec.technical_analysis}</p>
                                <p><strong>Fundamental:</strong> ${rec.fundamental_analysis}</p>
                                <p><strong>News:</strong> ${rec.news_sentiment}</p>
                                <p><strong>Summary:</strong> ${rec.reasoning_summary}</p>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    getRiskDescription(score) {
        if (score <= 3) return 'Low Risk - Conservative portfolio with stable holdings';
        if (score <= 6) return 'Moderate Risk - Balanced portfolio with mixed volatility';
        if (score <= 8) return 'High Risk - Growth-focused portfolio with higher volatility';
        return 'Very High Risk - Aggressive portfolio requiring close monitoring';
    }

    getDiversificationDescription(score) {
        if (score <= 3) return 'Poor Diversification - Consider adding more sectors/assets';
        if (score <= 6) return 'Moderate Diversification - Good start but room for improvement';
        if (score <= 8) return 'Well Diversified - Good spread across different assets';
        return 'Excellent Diversification - Optimal risk distribution';
    }

    getRecommendationForSymbol(symbol) {
        // This would come from the last analysis
        // For now, return a default
        return 'hold';
    }

    removeHolding(index) {
        if (confirm('Are you sure you want to remove this holding?')) {
            const holding = this.portfolio[index];
            this.portfolio.splice(index, 1);
            this.savePortfolio();
            this.updateDashboard();
            this.showNotification(`Removed ${holding.symbol} from portfolio`, 'info');
        }
    }

    setupAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }

        if (this.settings.autoRefresh) {
            this.refreshInterval = setInterval(() => {
                if (this.currentTab === 'dashboard') {
                    this.updateDashboard();
                }
            }, this.settings.refreshInterval * 1000);
        }
    }

    showLoading(message = 'Loading...') {
        const overlay = document.getElementById('loading-overlay');
        overlay.querySelector('.loading-spinner p').textContent = message;
        overlay.classList.add('active');
    }

    hideLoading() {
        document.getElementById('loading-overlay').classList.remove('active');
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <span>${message}</span>
            <button onclick="this.parentElement.remove()">×</button>
        `;

        // Add to page
        document.body.appendChild(notification);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    savePortfolio() {
        localStorage.setItem('sarasai_portfolio', JSON.stringify(this.portfolio));
    }

    loadPortfolio() {
        const saved = localStorage.getItem('sarasai_portfolio');
        if (saved) {
            this.portfolio = JSON.parse(saved);
        }
    }

    saveSettings() {
        localStorage.setItem('sarasai_settings', JSON.stringify(this.settings));
    }

    loadSettings() {
        const saved = localStorage.getItem('sarasai_settings');
        if (saved) {
            this.settings = { ...this.settings, ...JSON.parse(saved) };
        }

        // Update UI
        document.getElementById('currency-select').value = this.settings.currency;
        document.getElementById('refresh-select').value = this.settings.refreshInterval;
        document.getElementById('auto-refresh').checked = this.settings.autoRefresh;
    }

    updatePortfolioAnalysis() {
        // Update risk and diversification when switching to portfolio tab
        if (this.portfolio.length > 0) {
            this.runPortfolioAnalysis();
        }
    }

    async loadMarketData() {
        try {
            this.showLoading('Loading market data...');
            
            // Load market indices data
            this.updateMarketIndices();
            
            // Load top gainers and losers
            this.updateTopGainersLosers();
            
            // Load sector performance
            this.updateSectorPerformance();
            
        } catch (error) {
            console.error('Error loading market data:', error);
            this.showNotification('Failed to load market data', 'error');
        } finally {
            this.hideLoading();
        }
    }

    updateMarketIndices() {
        // Mock market indices data
        const indices = [
            { symbol: 'SPY', name: 'S&P 500', price: 4150.25, change: 25.45, changePercent: 0.62 },
            { symbol: 'QQQ', name: 'NASDAQ 100', price: 350.80, change: -12.35, changePercent: -3.40 },
            { symbol: 'IWM', name: 'Russell 2000', price: 195.40, change: 8.20, changePercent: 4.38 },
            { symbol: 'VTI', name: 'Total Market', price: 220.15, change: 1.95, changePercent: 0.89 }
        ];

        const tbody = document.getElementById('indices-tbody');
        tbody.innerHTML = '';

        indices.forEach(index => {
            const row = document.createElement('tr');
            row.className = 'market-row';
            
            row.innerHTML = `
                <td class="symbol-cell">
                    <div class="symbol-container">
                        <span class="symbol-text">${index.symbol}</span>
                        <span class="symbol-exchange">US</span>
                    </div>
                </td>
                <td class="name-cell">
                    <div class="name-container">
                        <span class="company-name">${index.name}</span>
                        <span class="company-sector">Index</span>
                    </div>
                </td>
                <td class="price-cell">$${index.price.toFixed(2)}</td>
                <td class="change-cell ${index.change >= 0 ? 'positive' : 'negative'}">
                    <div class="change-container">
                        <span class="change-amount">
                            ${index.change >= 0 ? '+' : ''}$${index.change.toFixed(2)}
                        </span>
                        <span class="change-percent">
                            (${index.change >= 0 ? '+' : ''}${index.changePercent.toFixed(2)}%)
                        </span>
                    </div>
                </td>
                <td class="actions-cell">
                    <div class="action-buttons">
                        <button class="action-btn primary" onclick="app.viewStockDetails('${index.symbol}')" title="Analyze">
                            <i class="fas fa-chart-line"></i>
                            <span>Analyze</span>
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    updateTopGainersLosers() {
        // Mock top gainers data
        const gainers = [
            { symbol: 'NVDA', name: 'NVIDIA Corporation', price: 875.50, changePercent: 12.45 },
            { symbol: 'AMD', name: 'Advanced Micro Devices', price: 165.20, changePercent: 8.90 },
            { symbol: 'TSLA', name: 'Tesla Inc', price: 245.80, changePercent: 7.35 },
            { symbol: 'AAPL', name: 'Apple Inc', price: 185.40, changePercent: 5.20 }
        ];

        const gainersContainer = document.getElementById('gainers-tbody');
        gainersContainer.innerHTML = '';

        gainers.forEach(stock => {
            const row = document.createElement('tr');
            row.className = 'gainer-row';
            
            row.innerHTML = `
                <td class="symbol-cell">
                    <div class="symbol-container">
                        <span class="symbol-text">${stock.symbol}</span>
                        <span class="symbol-exchange">NASDAQ</span>
                    </div>
                </td>
                <td class="name-cell">
                    <div class="name-container">
                        <span class="company-name">${stock.name}</span>
                    </div>
                </td>
                <td class="price-cell">$${stock.price.toFixed(2)}</td>
                <td class="change-cell positive">
                    <div class="change-container">
                        <span class="change-percent">
                            +${stock.changePercent.toFixed(2)}%
                        </span>
                    </div>
                </td>
                <td class="actions-cell">
                    <div class="action-buttons">
                        <button class="action-btn primary" onclick="app.viewStockDetails('${stock.symbol}')" title="Analyze">
                            <i class="fas fa-chart-line"></i>
                            <span>Analyze</span>
                        </button>
                        <button class="action-btn secondary" onclick="app.addStockToPortfolio('${stock.symbol}')" title="Add to Portfolio">
                            <i class="fas fa-plus"></i>
                            <span>Add</span>
                        </button>
                    </div>
                </td>
            `;
            gainersContainer.appendChild(row);
        });

        // Mock top losers data
        const losers = [
            { symbol: 'NFLX', name: 'Netflix Inc', price: 425.30, changePercent: -6.80 },
            { symbol: 'META', name: 'Meta Platforms Inc', price: 315.60, changePercent: -4.25 },
            { symbol: 'GOOGL', name: 'Alphabet Inc', price: 140.90, changePercent: -3.15 },
            { symbol: 'AMZN', name: 'Amazon.com Inc', price: 145.20, changePercent: -2.90 }
        ];

        const losersContainer = document.getElementById('losers-tbody');
        losersContainer.innerHTML = '';

        losers.forEach(stock => {
            const row = document.createElement('tr');
            row.className = 'loser-row';
            
            row.innerHTML = `
                <td class="symbol-cell">
                    <div class="symbol-container">
                        <span class="symbol-text">${stock.symbol}</span>
                        <span class="symbol-exchange">NASDAQ</span>
                    </div>
                </td>
                <td class="name-cell">
                    <div class="name-container">
                        <span class="company-name">${stock.name}</span>
                    </div>
                </td>
                <td class="price-cell">$${stock.price.toFixed(2)}</td>
                <td class="change-cell negative">
                    <div class="change-container">
                        <span class="change-percent">
                            ${stock.changePercent.toFixed(2)}%
                        </span>
                    </div>
                </td>
                <td class="actions-cell">
                    <div class="action-buttons">
                        <button class="action-btn primary" onclick="app.viewStockDetails('${stock.symbol}')" title="Analyze">
                            <i class="fas fa-chart-line"></i>
                            <span>Analyze</span>
                        </button>
                        <button class="action-btn secondary" onclick="app.addStockToPortfolio('${stock.symbol}')" title="Add to Portfolio">
                            <i class="fas fa-plus"></i>
                            <span>Add</span>
                        </button>
                    </div>
                </td>
            `;
            losersContainer.appendChild(row);
        });
    }

    updateSectorPerformance() {
        // Mock sector performance data
        const sectors = [
            { sector: 'Technology', performance: 2.45, trend: 'up' },
            { sector: 'Healthcare', performance: 1.80, trend: 'up' },
            { sector: 'Financials', performance: 0.95, trend: 'up' },
            { sector: 'Energy', performance: -1.25, trend: 'down' },
            { sector: 'Utilities', performance: -0.80, trend: 'down' },
            { sector: 'Real Estate', performance: -2.10, trend: 'down' }
        ];

        const tbody = document.getElementById('sectors-tbody');
        tbody.innerHTML = '';

        sectors.forEach(sector => {
            const row = document.createElement('tr');
            row.className = 'sector-row';
            
            row.innerHTML = `
                <td class="sector-cell">
                    <div class="sector-container">
                        <span class="sector-name">${sector.sector}</span>
                        <span class="sector-icon">
                            <i class="fas ${this.getSectorIcon(sector.sector)}"></i>
                        </span>
                    </div>
                </td>
                <td class="performance-cell ${sector.performance >= 0 ? 'positive' : 'negative'}">
                    <div class="performance-container">
                        <span class="performance-percent">
                            ${sector.performance >= 0 ? '+' : ''}${sector.performance.toFixed(2)}%
                        </span>
                        <span class="performance-trend">
                            <i class="fas fa-arrow-${sector.trend === 'up' ? 'up' : 'down'}"></i>
                        </span>
                    </div>
                </td>
                <td class="trend-cell">
                    <div class="trend-indicator ${sector.trend}">
                        <span class="trend-text">${sector.trend.toUpperCase()}</span>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    getSectorIcon(sector) {
        const icons = {
            'Technology': 'fa-microchip',
            'Healthcare': 'fa-heartbeat',
            'Financials': 'fa-university',
            'Energy': 'fa-bolt',
            'Utilities': 'fa-plug',
            'Real Estate': 'fa-building'
        };
        return icons[sector] || 'fa-chart-bar';
    }

    async loadReports() {
        try {
            this.showLoading('Loading reports...');
            
            // Load portfolio performance report
            this.updatePortfolioPerformanceReport();
            
            // Load monthly analysis report
            this.updateMonthlyAnalysisReport();
            
            // Load risk assessment report
            this.updateRiskAssessmentReport();
            
        } catch (error) {
            console.error('Error loading reports:', error);
            this.showNotification('Failed to load reports', 'error');
        } finally {
            this.hideLoading();
        }
    }

    updatePortfolioPerformanceReport() {
        const report = {
            period: 'Last 30 Days',
            totalReturn: 12.45,
            benchmarkReturn: 8.90,
            bestPerformer: 'NVDA (+25.40%)',
            worstPerformer: 'META (-8.20%)',
            winRate: 75.0,
            totalTrades: 12
        };

        const tbody = document.getElementById('performance-tbody');
        tbody.innerHTML = '';

        const metrics = [
            { metric: 'Total Return', value: `${report.totalReturn >= 0 ? '+' : ''}${report.totalReturn.toFixed(2)}%`, status: report.totalReturn >= 0 ? 'positive' : 'negative' },
            { metric: 'Benchmark Return', value: `${report.benchmarkReturn >= 0 ? '+' : ''}${report.benchmarkReturn.toFixed(2)}%`, status: report.benchmarkReturn >= 0 ? 'positive' : 'negative' },
            { metric: 'Alpha', value: `${(report.totalReturn - report.benchmarkReturn).toFixed(2)}%`, status: (report.totalReturn - report.benchmarkReturn) >= 0 ? 'positive' : 'negative' },
            { metric: 'Win Rate', value: `${report.winRate.toFixed(1)}%`, status: report.winRate >= 60 ? 'positive' : 'negative' },
            { metric: 'Best Performer', value: report.bestPerformer, status: 'neutral' },
            { metric: 'Worst Performer', value: report.worstPerformer, status: 'neutral' }
        ];

        metrics.forEach(metric => {
            const row = document.createElement('tr');
            row.className = 'report-row';
            
            row.innerHTML = `
                <td class="metric-cell">
                    <div class="metric-container">
                        <span class="metric-name">${metric.metric}</span>
                    </div>
                </td>
                <td class="value-cell ${metric.status}">
                    <div class="value-container">
                        <span class="value-text">${metric.value}</span>
                    </div>
                </td>
                <td class="status-cell">
                    <div class="status-indicator ${metric.status}">
                        <span class="status-icon">
                            <i class="fas ${metric.status === 'positive' ? 'fa-arrow-up' : metric.status === 'negative' ? 'fa-arrow-down' : 'fa-minus'}"></i>
                        </span>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    updateMonthlyAnalysisReport() {
        const monthlyData = [
            { month: 'January 2024', return: 8.5, winRate: 70, trades: 15 },
            { month: 'February 2024', return: -2.3, winRate: 45, trades: 12 },
            { month: 'March 2024', return: 15.8, winRate: 85, trades: 18 },
            { month: 'April 2024', return: 5.2, winRate: 65, trades: 10 }
        ];

        const tbody = document.getElementById('monthly-tbody');
        tbody.innerHTML = '';

        monthlyData.forEach(data => {
            const row = document.createElement('tr');
            row.className = 'monthly-row';
            
            row.innerHTML = `
                <td class="month-cell">
                    <div class="month-container">
                        <span class="month-name">${data.month}</span>
                    </div>
                </td>
                <td class="return-cell ${data.return >= 0 ? 'positive' : 'negative'}">
                    <div class="return-container">
                        <span class="return-percent">
                            ${data.return >= 0 ? '+' : ''}${data.return.toFixed(1)}%
                        </span>
                    </div>
                </td>
                <td class="winrate-cell">
                    <div class="winrate-container">
                        <span class="winrate-percent">${data.winRate.toFixed(0)}%</span>
                        <div class="winrate-bar">
                            <div class="winrate-fill" style="width: ${data.winRate}%"></div>
                        </div>
                    </div>
                </td>
                <td class="trades-cell">
                    <div class="trades-container">
                        <span class="trades-number">${data.trades}</span>
                        <span class="trades-label">trades</span>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    updateRiskAssessmentReport() {
        const riskMetrics = [
            { metric: 'Portfolio Beta', value: '1.25', description: 'Higher volatility than market' },
            { metric: 'Sharpe Ratio', value: '1.8', description: 'Good risk-adjusted returns' },
            { metric: 'Max Drawdown', value: '-8.5%', description: 'Largest peak-to-trough loss' },
            { metric: 'VaR (95%)', value: '-$2,450', description: 'Potential daily loss at 95% confidence' },
            { metric: 'Diversification Score', value: '7.2/10', description: 'Well diversified portfolio' }
        ];

        const tbody = document.getElementById('risk-tbody');
        tbody.innerHTML = '';

        riskMetrics.forEach(metric => {
            const row = document.createElement('tr');
            row.className = 'risk-row';
            
            row.innerHTML = `
                <td class="metric-cell">
                    <div class="metric-container">
                        <span class="metric-name">${metric.metric}</span>
                        <span class="metric-description">${metric.description}</span>
                    </div>
                </td>
                <td class="value-cell">
                    <div class="value-container">
                        <span class="value-text">${metric.value}</span>
                    </div>
                </td>
                <td class="status-cell">
                    <div class="status-indicator ${this.getRiskStatus(metric.metric, metric.value)}">
                        <span class="status-icon">
                            <i class="fas ${this.getRiskIcon(metric.metric)}"></i>
                        </span>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    getRiskStatus(metric, value) {
        // Simplified risk status logic
        if (metric.includes('Sharpe') && parseFloat(value) > 1.5) return 'positive';
        if (metric.includes('Drawdown') && parseFloat(value.replace('%', '').replace('-', '')) < 10) return 'positive';
        if (metric.includes('Diversification') && parseFloat(value) > 7) return 'positive';
        return 'neutral';
    }

    getRiskIcon(metric) {
        const icons = {
            'Portfolio Beta': 'fa-tachometer-alt',
            'Sharpe Ratio': 'fa-balance-scale',
            'Max Drawdown': 'fa-arrow-down',
            'VaR (95%)': 'fa-exclamation-triangle',
            'Diversification Score': 'fa-chart-pie'
        };
        return icons[metric] || 'fa-info';
    }
}

// Global functions for modal control
function showAddHoldingModal() {
    app.showAddHoldingModal();
}

function closeAddHoldingModal() {
    app.closeAddHoldingModal();
}

function addHolding() {
    app.addHolding();
}

// Initialize app when DOM is loaded
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new StockPickerApp();
});

// Add notification styles to head
const notificationStyles = `
<style>
.notification {
    position: fixed;
    top: 90px;
    right: 20px;
    padding: 12px 20px;
    border-radius: 8px;
    color: white;
    font-weight: 500;
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    min-width: 300px;
    box-shadow: var(--shadow-lg);
    animation: slideIn 0.3s ease;
}

.notification button {
    background: none;
    border: none;
    color: white;
    font-size: 18px;
    cursor: pointer;
    padding: 0;
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.notification-success { background: var(--success); }
.notification-error { background: var(--danger); }
.notification-warning { background: var(--warning); }
.notification-info { background: var(--info); }

@keyframes slideIn {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}

.stock-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px;
    border-bottom: 1px solid var(--gray-200);
    transition: background 0.2s ease;
}

.stock-item:hover {
    background: var(--gray-50);
}

.stock-info {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.stock-symbol {
    font-weight: 600;
    color: var(--gray-800);
}

.stock-name {
    font-size: 12px;
    color: var(--gray-500);
}

.stock-price {
    font-weight: 600;
    color: var(--primary);
}

.stock-actions {
    display: flex;
    gap: 8px;
}

.stock-detail-card {
    border-radius: var(--radius-lg);
    border: 1px solid var(--gray-200);
    overflow: hidden;
}

.stock-header {
    padding: 20px;
    background: var(--gray-50);
    border-bottom: 1px solid var(--gray-200);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.stock-title h3 {
    margin: 0 0 8px 0;
    color: var(--gray-800);
}

.stock-current-price {
    font-size: 24px;
    font-weight: 700;
    color: var(--primary);
}

.stock-recommendation {
    text-align: right;
}

.confidence {
    display: block;
    font-size: 12px;
    color: var(--gray-500);
    margin-top: 4px;
}

.stock-analysis {
    padding: 20px;
}

.analysis-section {
    margin-bottom: 20px;
}

.analysis-section h4 {
    margin: 0 0 8px 0;
    color: var(--gray-700);
    font-size: 14px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.analysis-section p {
    margin: 0;
    line-height: 1.5;
    color: var(--gray-600);
}

.stock-actions {
    padding: 20px;
    border-top: 1px solid var(--gray-200);
    background: var(--gray-50);
    display: flex;
    gap: 12px;
}

.analysis-summary {
    display: grid;
    gap: 24px;
}

.summary-card {
    background: var(--gray-50);
    padding: 20px;
    border-radius: var(--radius-lg);
}

.summary-card h4 {
    margin: 0 0 16px 0;
    color: var(--gray-800);
}

.summary-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 16px;
}

.stat {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.stat-label {
    font-size: 12px;
    color: var(--gray-500);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.stat-value {
    font-size: 18px;
    font-weight: 600;
    color: var(--gray-800);
}

.recommendations-detailed h4 {
    margin: 0 0 16px 0;
    color: var(--gray-800);
}

.rec-detail-card {
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-md);
    margin-bottom: 16px;
    overflow: hidden;
}

.rec-header {
    padding: 16px;
    background: var(--gray-50);
    border-bottom: 1px solid var(--gray-200);
    display: flex;
    align-items: center;
    gap: 12px;
}

.rec-symbol {
    font-weight: 600;
    color: var(--gray-800);
}

.rec-confidence {
    font-size: 12px;
    color: var(--gray-500);
}

.rec-reasoning {
    padding: 16px;
}

.rec-reasoning p {
    margin: 0 0 12px 0;
    line-height: 1.5;
}

.rec-reasoning strong {
    color: var(--gray-700);
}

.error {
    text-align: center;
    padding: 40px;
    color: var(--danger);
    font-weight: 500;
}
</style>`;

document.head.insertAdjacentHTML('beforeend', notificationStyles);