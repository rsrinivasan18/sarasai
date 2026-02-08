// Professional Investment Platform Application
class ProfessionalInvestmentApp {
    constructor() {
        this.apiUrl = 'http://localhost:8000';
        this.currentRoute = 'dashboard';
        this.portfolio = [];
        this.watchlist = [];
        this.orders = [];
        this.marketData = {};
        this.realTimeData = new Map();
        this.notifications = [];
        
        // App state - will be loaded from config API
        this.state = {
            user: {
                name: 'Loading...',
                role: 'Loading...',
                balance: 0.00
            },
            filters: {
                positions: {},
                orders: {}
            },
            sorting: {
                positions: { column: null, direction: 'asc' },
                orders: { column: null, direction: 'asc' }
            },
            settings: {
                autoRefresh: true,
                refreshInterval: 5000,
                theme: 'light'
            }
        };

        // Initialize application - ensure DOM and dependencies are fully ready
        this.initializationRetries = 0;
        this.maxRetries = 3;
        
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.safeInit());
        } else {
            // Give additional time for scripts and styles to load
            setTimeout(() => this.safeInit(), 250);
        }
    }

    async safeInit() {
        try {
            console.log('🚀 Starting Professional Investment App initialization...');
            
            // Verify critical DOM elements exist
            if (!this.verifyDOMElementsExist()) {
                throw new Error('Critical DOM elements missing');
            }
            
            this.showLoading('Initializing application...');
            
            // Load configuration with retry logic
            await this.loadConfigurationWithRetry();
            
            // Setup event listeners (defensive)
            this.setupEventListenersDefensive();
            
            // Setup router
            this.setupRouter();
            
            // Load initial data with retry logic
            await this.loadInitialDataWithRetry();
            
            // Setup real-time updates
            this.setupRealTimeUpdates();
            
            // Initial route
            this.navigateToRoute(this.currentRoute);
            
            this.hideLoading();
            this.showNotification('Welcome to Sarasai Professional', 'success');
            
            console.log('✅ Professional Investment App initialized successfully!');
            
        } catch (error) {
            console.error('❌ Application initialization failed:', error);
            this.handleInitializationError(error);
        }
    }
    
    verifyDOMElementsExist() {
        const criticalElements = [
            'loading-overlay',
            'notifications-container', 
            'dashboard-view',
            'app'
        ];
        
        for (const elementId of criticalElements) {
            const element = document.getElementById(elementId);
            if (!element) {
                console.error(`Critical element missing: ${elementId}`);
                return false;
            }
        }
        
        console.log('✅ All critical DOM elements verified');
        return true;
    }
    
    async handleInitializationError(error) {
        this.hideLoading();
        
        if (this.initializationRetries < this.maxRetries) {
            this.initializationRetries++;
            console.log(`🔄 Retrying initialization (attempt ${this.initializationRetries}/${this.maxRetries})...`);
            
            // Wait before retry with exponential backoff
            const delay = Math.min(1000 * Math.pow(2, this.initializationRetries - 1), 5000);
            setTimeout(() => this.safeInit(), delay);
            
            this.showNotification(`Initialization failed, retrying... (${this.initializationRetries}/${this.maxRetries})`, 'warning');
        } else {
            console.error('❌ Max retries exceeded, initialization failed permanently');
            this.showNotification('Failed to initialize application after multiple attempts. Please refresh the page.', 'error');
            
            // Show fallback UI
            this.showFallbackUI();
        }
    }
    
    showFallbackUI() {
        const appContainer = document.getElementById('app');
        if (appContainer) {
            appContainer.innerHTML = `
                <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; text-align: center; padding: 2rem;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">⚠️</div>
                    <h2 style="color: #dc2626; margin-bottom: 1rem;">Application Failed to Initialize</h2>
                    <p style="color: #6b7280; margin-bottom: 2rem; max-width: 500px;">
                        The application encountered an error during startup. This could be due to network issues or server problems.
                    </p>
                    <button onclick="window.location.reload()" style="padding: 0.75rem 1.5rem; background: #3b82f6; color: white; border: none; border-radius: 0.5rem; font-size: 1rem; cursor: pointer;">
                        🔄 Refresh Page
                    </button>
                </div>
            `;
        }
    }

    async loadConfigurationWithRetry() {
        for (let attempt = 1; attempt <= this.maxRetries; attempt++) {
            try {
                console.log(`💾 Loading application configuration (attempt ${attempt}/${this.maxRetries})...`);
                
                await this.loadConfiguration();
                console.log('✅ Configuration loaded successfully');
                return; // Success, exit retry loop
                
            } catch (error) {
                console.warn(`Configuration loading failed (attempt ${attempt}/${this.maxRetries}):`, error);
                
                if (attempt === this.maxRetries) {
                    console.error('❌ Max retries exceeded for configuration loading');
                    this.loadFallbackConfiguration();
                } else {
                    // Wait before retry
                    await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
                }
            }
        }
    }
    
    async loadConfiguration() {
        console.log('Loading application configuration...');
        
        // Create promises for all API calls
        const configPromises = [
            this.fetchWithTimeout(`${this.apiUrl}/api/config/user`, 'user'),
            this.fetchWithTimeout(`${this.apiUrl}/api/config/branding`, 'branding'),
            this.fetchWithTimeout(`${this.apiUrl}/api/config/ui`, 'ui')
        ];
        
        // Execute all requests in parallel with error handling
        const results = await Promise.allSettled(configPromises);
        
        // Process user configuration
        if (results[0].status === 'fulfilled' && results[0].value.response.ok) {
            const userData = results[0].value.data;
            this.state.user = {
                name: userData.name || 'User',
                role: userData.role || 'Trader', 
                balance: userData.initial_balance || 10000.00,
                email: userData.email || '',
                timezone: userData.timezone || 'Asia/Singapore'
            };
            console.log('✅ User config loaded:', this.state.user.name);
        }
        
        // Process branding configuration
        if (results[1].status === 'fulfilled' && results[1].value.response.ok) {
            this.branding = results[1].value.data;
            console.log('✅ Branding config loaded:', this.branding.application?.name);
            
            // Update page title safely
            try {
                document.title = this.branding.application?.full_name || 'Sarasai - Professional Investment Platform';
            } catch (e) {
                console.warn('Failed to update document title:', e);
            }
        }
        
        // Process UI text configuration  
        if (results[2].status === 'fulfilled' && results[2].value.response.ok) {
            this.uiText = results[2].value.data;
            console.log('✅ UI text config loaded');
        }
        
        // Check if any critical config failed
        const criticalFailures = results.filter(r => r.status === 'rejected').length;
        if (criticalFailures === results.length) {
            throw new Error('All configuration endpoints failed');
        }
        
        // Setup timezone and update UI
        this.setupTimezone();
        this.updateUIWithConfigDefensive();
    }
    
    async fetchWithTimeout(url, type, timeout = 5000) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);
        
        try {
            const response = await fetch(url, { signal: controller.signal });
            clearTimeout(timeoutId);
            
            if (response.ok) {
                const data = await response.json();
                return { response, data, type };
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
        } catch (error) {
            clearTimeout(timeoutId);
            console.warn(`Failed to fetch ${type} config from ${url}:`, error.message);
            throw error;
        }
    }
    
    loadFallbackConfiguration() {
        console.log('🔄 Loading fallback configuration...');
        
        // Fallback to hardcoded values if config fails
        this.state.user = {
            name: 'Srinivasan Ramarao',
            role: 'Premium Trader',
            balance: 10000.00,
            timezone: 'Asia/Singapore'
        };
        
        this.branding = {
            application: {
                name: 'Sarasai',
                full_name: 'Sarasai - Professional Investment Platform'
            }
        };
        
        this.uiText = {
            navigation: {
                dashboard: 'Dashboard',
                portfolio: 'Portfolio',
                watchlist: 'Watchlist'
            }
        };
        
        this.setupTimezone();
        this.updateUIWithConfigDefensive();
        
        console.log('✅ Fallback configuration loaded');
    }
    
    setupTimezone() {
        // Setup Singapore timezone for all time displays
        this.timezone = this.state.user.timezone || 'Asia/Singapore';
        console.log('🕐 Timezone set to:', this.timezone);
    }
    
    formatTimeInSGT(date) {
        // Format time in Singapore timezone
        return new Intl.DateTimeFormat('en-SG', {
            timeZone: this.timezone,
            year: 'numeric',
            month: 'short', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            timeZoneName: 'short'
        }).format(date);
    }
    
    updateUIWithConfigDefensive() {
        try {
            console.log('🎨 Updating UI with configuration (defensive mode)...');
            
            // Update user profile in sidebar
            this.updateUserProfileDefensive();
            
            // Update branding elements
            this.updateBrandingElementsDefensive();
            
            // Update navigation with UI text
            this.updateNavigationTextDefensive();
            
            // Update time displays
            this.updateTimeDisplaysDefensive();
            
            console.log('✅ UI updated with configuration');
            
        } catch (error) {
            console.warn('Failed to update UI with config:', error);
        }
    }
    
    // Keep original for backward compatibility
    updateUIWithConfig() {
        this.updateUIWithConfigDefensive();
    }
    
    updateUserProfileDefensive() {
        try {
            // Update user name in sidebar with timeout protection
            this.safeUpdateElement('.user-name', this.state.user.name, 'text');
            
            // Update user role
            this.safeUpdateElement('.user-role', this.state.user.role, 'text');
            
            // Update cash balance with user's initial balance
            if (this.state.user.balance) {
                const formattedBalance = `$${this.state.user.balance.toLocaleString('en-US', {minimumFractionDigits: 2})}`;
                this.safeUpdateElement('#cash-balance', formattedBalance, 'text');
            }
            
        } catch (error) {
            console.warn('Error updating user profile:', error);
        }
    }
    
    // Keep original for backward compatibility
    updateUserProfile() {
        this.updateUserProfileDefensive();
    }
    
    safeUpdateElement(selector, value, updateType = 'text') {
        try {
            const element = document.querySelector(selector);
            if (!element) {
                console.warn(`Element not found: ${selector}`);
                return false;
            }
            
            if (!value) {
                console.warn(`No value provided for element: ${selector}`);
                return false;
            }
            
            switch (updateType) {
                case 'text':
                    element.textContent = value;
                    break;
                case 'html':
                    element.innerHTML = value;
                    break;
                case 'value':
                    element.value = value;
                    break;
                default:
                    element.textContent = value;
            }
            
            return true;
        } catch (error) {
            console.warn(`Failed to update element ${selector}:`, error);
            return false;
        }
    }
    
    updateBrandingElementsDefensive() {
        try {
            if (!this.branding) {
                console.warn('No branding data available for UI update');
                return;
            }
            
            // Update logo text
            if (this.branding.application?.name) {
                this.safeUpdateElement('.logo-text', this.branding.application.name, 'text');
            }
            
            // Update welcome message if exists
            const welcomeText = `Welcome to ${this.branding.application?.name || 'Sarasai'} Professional`;
            const welcomeElements = document.querySelectorAll('[data-welcome-text]');
            
            if (welcomeElements.length > 0) {
                welcomeElements.forEach(element => {
                    try {
                        element.textContent = welcomeText;
                    } catch (e) {
                        console.warn('Failed to update welcome element:', e);
                    }
                });
            }
            
        } catch (error) {
            console.warn('Error updating branding elements:', error);
        }
    }
    
    // Keep original for backward compatibility
    updateBrandingElements() {
        this.updateBrandingElementsDefensive();
    }
    
    updateNavigationTextDefensive() {
        try {
            if (!this.uiText || !this.uiText.navigation) {
                console.warn('No UI text data available for navigation update');
                return;
            }
            
            // Update navigation labels
            Object.keys(this.uiText.navigation).forEach(key => {
                try {
                    const selector = `[data-route="${key}"] .nav-text`;
                    this.safeUpdateElement(selector, this.uiText.navigation[key], 'text');
                } catch (error) {
                    console.warn(`Failed to update navigation text for ${key}:`, error);
                }
            });
            
            // Update button text
            if (this.uiText.buttons) {
                Object.keys(this.uiText.buttons).forEach(key => {
                    try {
                        const selector = `[data-button="${key}"]`;
                        this.safeUpdateElement(selector, this.uiText.buttons[key], 'text');
                    } catch (error) {
                        console.warn(`Failed to update button text for ${key}:`, error);
                    }
                });
            }
            
        } catch (error) {
            console.warn('Error updating navigation text:', error);
        }
    }
    
    // Keep original for backward compatibility
    updateNavigationText() {
        this.updateNavigationTextDefensive();
    }
    
    updateTimeDisplaysDefensive() {
        try {
            const now = new Date();
            const sgtTime = this.formatTimeInSGT(now);
            
            // Update market time with Singapore timezone
            this.safeUpdateElement('.market-time', sgtTime, 'text');
            
            // Update any other time displays
            const timeElements = document.querySelectorAll('[data-time-display]');
            if (timeElements.length > 0) {
                timeElements.forEach(element => {
                    try {
                        element.textContent = sgtTime;
                    } catch (e) {
                        console.warn('Failed to update time display element:', e);
                    }
                });
            }
            
        } catch (error) {
            console.warn('Error updating time displays:', error);
        }
    }
    
    // Keep original for backward compatibility  
    updateTimeDisplays() {
        this.updateTimeDisplaysDefensive();
    }
    
    refreshUIDataDefensive() {
        try {
            console.log('🔄 Refreshing UI data (defensive mode)...');
            
            // Update portfolio metrics display
            try {
                this.updatePortfolioMetrics();
            } catch (error) {
                console.warn('Error updating portfolio metrics:', error);
            }
            
            // Update user profile again (in case balance changed)
            try {
                this.updateUserProfileDefensive();
            } catch (error) {
                console.warn('Error updating user profile:', error);
            }
            
            // Update time displays
            try {
                this.updateTimeDisplaysDefensive();
            } catch (error) {
                console.warn('Error updating time displays:', error);
            }
            
            console.log('✅ UI data refreshed');
            
        } catch (error) {
            console.warn('Error refreshing UI data:', error);
        }
    }
    
    // Keep original for backward compatibility
    refreshUIData() {
        this.refreshUIDataDefensive();
    }

    setupEventListenersDefensive() {
        try {
            console.log('🎯 Setting up event listeners (defensive mode)...');
            
            // Sidebar navigation with error handling
            this.safeAddEventListeners('.nav-item', 'click', (e) => {
                try {
                    e.preventDefault();
                    const route = e.currentTarget.getAttribute('data-route');
                    if (route) {
                        this.navigateToRoute(route);
                    }
                } catch (error) {
                    console.warn('Navigation error:', error);
                }
            });

            // Sidebar toggle
            this.safeAddEventListener('#sidebar-toggle', 'click', () => {
                this.toggleSidebar();
            });

            // Global search with defensive handling
            this.safeAddEventListener('#global-search', 'input', (e) => {
                try {
                    this.handleGlobalSearch(e.target.value);
                } catch (error) {
                    console.warn('Search input error:', error);
                }
            });
            
            this.safeAddEventListener('#global-search', 'keypress', (e) => {
                try {
                    if (e.key === 'Enter' && e.target.value.trim()) {
                        this.executeSearch(e.target.value.trim());
                    }
                } catch (error) {
                    console.warn('Search keypress error:', error);
                }
            });

            // Portfolio actions
            this.safeAddEventListener('#add-position', 'click', () => {
                this.showAddPositionModal();
            });

            this.safeAddEventListener('#export-portfolio', 'click', () => {
                this.exportPortfolioData();
            });

        // Filter and sort buttons
        document.getElementById('filter-positions')?.addEventListener('click', () => {
            this.showPositionFilters();
        });

        document.getElementById('sort-positions')?.addEventListener('click', () => {
            this.showSortOptions('positions');
        });

        // Chart period buttons
        document.querySelectorAll('.chart-period-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const period = e.target.getAttribute('data-period');
                this.updatePerformanceChart(period);
                
                // Update active state
                document.querySelectorAll('.chart-period-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
            });
        });

        // Table sorting
        document.querySelectorAll('.data-table th.sortable').forEach(th => {
            th.addEventListener('click', () => {
                const table = th.closest('table');
                const column = th.getAttribute('data-sort');
                this.sortTable(table.id, column);
            });
        });

        // Modal close
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', () => {
                this.closeModal();
            });
        });

        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tab = e.target.getAttribute('data-tab');
                this.switchTab(e.target.closest('.card'), tab);
            });
        });

        // Hash change for routing
        window.addEventListener('hashchange', () => {
            const route = window.location.hash.slice(1) || 'dashboard';
            this.navigateToRoute(route);
        });

        // Click outside modal to close
        window.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-backdrop')) {
                this.closeModal();
            }
        });

        // Hide search suggestions when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.search-container')) {
                this.hideSuggestions();
            }
        });

        // Escape key to close modals
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeModal();
                this.hideSuggestions();
            }
        });

            // Intelligence Dashboard Event Listeners
            this.setupIntelligenceEventListenersDefensive();
            
            console.log('✅ Event listeners setup completed');
            
        } catch (error) {
            console.error('Error setting up event listeners:', error);
            // Continue with app initialization even if some listeners fail
        }
    }
    
    // Keep original for backward compatibility
    setupEventListeners() {
        this.setupEventListenersDefensive();
    }
    
    safeAddEventListener(selector, eventType, handler) {
        try {
            const element = document.querySelector(selector);
            if (element) {
                element.addEventListener(eventType, handler);
                return true;
            } else {
                console.warn(`Element not found for event listener: ${selector}`);
                return false;
            }
        } catch (error) {
            console.warn(`Failed to add ${eventType} listener to ${selector}:`, error);
            return false;
        }
    }
    
    safeAddEventListeners(selector, eventType, handler) {
        try {
            const elements = document.querySelectorAll(selector);
            if (elements.length > 0) {
                elements.forEach((element, index) => {
                    try {
                        element.addEventListener(eventType, handler);
                    } catch (error) {
                        console.warn(`Failed to add ${eventType} listener to ${selector}[${index}]:`, error);
                    }
                });
                return elements.length;
            } else {
                console.warn(`No elements found for event listeners: ${selector}`);
                return 0;
            }
        } catch (error) {
            console.warn(`Failed to add ${eventType} listeners to ${selector}:`, error);
            return 0;
        }
    }

    setupRouter() {
        // Simple hash-based routing
        this.routes = {
            'dashboard': () => this.showDashboard(),
            'portfolio': () => this.showPortfolio(),
            'watchlist': () => this.showWatchlist(),
            'orders': () => this.showOrders(),
            'discover': () => this.showDiscover(),
            'screener': () => this.showScreener(),
            'market': () => this.showMarket(),
            'performance': () => this.showPerformance(),
            'risk': () => this.showRiskAnalysis(),
            'reports': () => this.showReports(),
            'settings': () => this.showSettings(),
            'portfolio-intelligence': () => this.showPortfolioIntelligence(),
            'news-intelligence': () => this.showNewsIntelligence(),
            'expert-advisor': () => this.showExpertAdvisor(),
            'stock-analysis': () => this.showStockAnalysis()
        };

        // Intelligence data cache
        this.intelligenceData = {
            portfolioRecommendations: [],
            portfolioHealth: {},
            newsAnalysis: {},
            expertConsensus: {},
            stockAnalysis: {}
        };
    }

    async loadInitialDataWithRetry() {
        for (let attempt = 1; attempt <= this.maxRetries; attempt++) {
            try {
                console.log(`📊 Loading initial data (attempt ${attempt}/${this.maxRetries})...`);
                
                await this.loadInitialData();
                console.log('✅ Initial data loaded successfully');
                return; // Success, exit retry loop
                
            } catch (error) {
                console.warn(`Initial data loading failed (attempt ${attempt}/${this.maxRetries}):`, error);
                
                if (attempt === this.maxRetries) {
                    console.error('❌ Max retries exceeded for initial data loading');
                    this.loadFallbackData();
                } else {
                    // Wait before retry
                    await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
                }
            }
        }
    }
    
    async loadInitialData() {
        console.log('📊 Loading initial data...');
        
        // Load data in parallel for better performance
        const dataPromises = [
            this.loadPortfolioDataSafe().catch(e => ({ error: e, type: 'portfolio' })),
            this.loadMarketDataSafe().catch(e => ({ error: e, type: 'market' })),
            this.loadWatchlistDataSafe().catch(e => ({ error: e, type: 'watchlist' }))
        ];
        
        const results = await Promise.allSettled(dataPromises);
        
        // Check for critical failures
        const failures = results.filter(r => 
            r.status === 'rejected' || 
            (r.status === 'fulfilled' && r.value.error)
        );
        
        if (failures.length > 0) {
            console.warn('Some data loading failed:', failures);
        }
        
        // Update UI counters and refresh - these should work even with partial data
        try {
            this.updateNavigationCountersDefensive();
            this.refreshUIDataDefensive();
        } catch (error) {
            console.warn('Error updating UI after data load:', error);
        }
    }
    
    async loadPortfolioDataSafe() {
        try {
            await this.loadPortfolioData();
        } catch (error) {
            console.warn('Portfolio data loading failed, using fallback:', error);
            await this.loadMockPortfolioData();
        }
    }
    
    async loadMarketDataSafe() {
        try {
            await this.loadMarketData();
        } catch (error) {
            console.warn('Market data loading failed, using fallback:', error);
            this.marketData = {
                stocks: [],
                indices: [
                    { name: 'S&P 500', value: 4150.25, change: 0.62 },
                    { name: 'NASDAQ', value: 12850.80, change: -0.34 },
                    { name: 'DOW', value: 34195.40, change: 0.38 }
                ],
                gainers: [],
                losers: []
            };
        }
    }
    
    async loadWatchlistDataSafe() {
        try {
            await this.loadWatchlistData();
        } catch (error) {
            console.warn('Watchlist data loading failed, using fallback:', error);
            this.watchlist = [
                { symbol: 'TSLA', name: 'Tesla, Inc.', price: 242.84, change: 2.45 },
                { symbol: 'NVDA', name: 'NVIDIA Corporation', price: 875.50, change: -1.23 }
            ];
        }
    }
    
    loadFallbackData() {
        console.log('🔄 Loading fallback data...');
        
        // Ensure we have basic portfolio data
        if (!this.portfolio || this.portfolio.length === 0) {
            this.loadMockPortfolioData();
        }
        
        // Ensure we have basic market data
        if (!this.marketData || !this.marketData.indices) {
            this.loadMarketDataSafe();
        }
        
        // Ensure we have basic watchlist
        if (!this.watchlist || this.watchlist.length === 0) {
            this.loadWatchlistDataSafe();
        }
        
        // Update UI with fallback data
        this.updateNavigationCountersDefensive();
        this.refreshUIDataDefensive();
        
        console.log('✅ Fallback data loaded');
    }

    async loadPortfolioData() {
        try {
            // Load real portfolio data from API
            const [positionsResponse, metricsResponse] = await Promise.all([
                fetch(`${this.apiUrl}/api/trading/portfolio/positions`),
                fetch(`${this.apiUrl}/api/trading/portfolio/metrics`)
            ]);
            
            if (positionsResponse.ok && metricsResponse.ok) {
                const positions = await positionsResponse.json();
                const metrics = await metricsResponse.json();
                
                // Convert API format to internal format
                this.portfolio = positions.map(pos => ({
                    symbol: pos.symbol,
                    name: pos.name,
                    shares: pos.shares,
                    avgPrice: pos.avg_price,
                    currentPrice: pos.current_price,
                    marketValue: pos.market_value,
                    gainLoss: pos.gain_loss,
                    gainLossPercent: pos.gain_loss_percent,
                    recommendation: pos.recommendation
                }));
                
                this.portfolioMetrics = {
                    totalValue: metrics.total_value,
                    totalGainLoss: metrics.total_gain_loss,
                    totalGainLossPercent: metrics.total_gain_loss_percent,
                    dayGainLoss: metrics.day_gain_loss,
                    dayGainLossPercent: metrics.day_gain_loss_percent,
                    cashBalance: metrics.cash_balance
                };
            } else {
                throw new Error('Failed to fetch portfolio data');
            }
            
        } catch (error) {
            console.error('Failed to load portfolio data:', error);
            // Fall back to mock data
            await this.loadMockPortfolioData();
        }
    }

    async loadMockPortfolioData() {
        const mockHoldings = [
            {
                symbol: 'AAPL',
                name: 'Apple Inc.',
                shares: 100,
                avgPrice: 150.00,
                currentPrice: 185.92,
                marketValue: 18592.00,
                gainLoss: 3592.00,
                gainLossPercent: 23.95,
                recommendation: 'BUY'
            },
            {
                symbol: 'GOOGL',
                name: 'Alphabet Inc.',
                shares: 50,
                avgPrice: 120.00,
                currentPrice: 141.80,
                marketValue: 7090.00,
                gainLoss: 1090.00,
                gainLossPercent: 18.17,
                recommendation: 'HOLD'
            },
            {
                symbol: 'MSFT',
                name: 'Microsoft Corporation',
                shares: 75,
                avgPrice: 300.00,
                currentPrice: 378.91,
                marketValue: 28418.25,
                gainLoss: 5918.25,
                gainLossPercent: 26.30,
                recommendation: 'BUY'
            }
        ];
        
        this.portfolio = mockHoldings;
        this.calculatePortfolioMetrics();
    }

    calculatePortfolioMetrics() {
        const totalValue = this.portfolio.reduce((sum, holding) => sum + holding.marketValue, 0);
        const totalGainLoss = this.portfolio.reduce((sum, holding) => sum + holding.gainLoss, 0);
        const totalCost = totalValue - totalGainLoss;
        const totalGainLossPercent = totalCost > 0 ? (totalGainLoss / totalCost) * 100 : 0;

        this.portfolioMetrics = {
            totalValue,
            totalGainLoss,
            totalGainLossPercent,
            dayGainLoss: totalGainLoss * 0.1, // Simulate day's change
            dayGainLossPercent: totalGainLossPercent * 0.1,
            cashBalance: this.state.user.balance
        };
    }

    async loadMarketData() {
        try {
            const response = await fetch(`${this.apiUrl}/stocks`);
            const data = await response.json();
            
            this.marketData = {
                stocks: data.stocks,
                indices: [
                    { name: 'S&P 500', value: 4150.25, change: 0.62 },
                    { name: 'NASDAQ', value: 12850.80, change: -0.34 },
                    { name: 'DOW', value: 34195.40, change: 0.38 }
                ],
                gainers: data.stocks.filter(s => Math.random() > 0.5).slice(0, 5),
                losers: data.stocks.filter(s => Math.random() > 0.5).slice(0, 5)
            };
            
        } catch (error) {
            console.error('Failed to load market data:', error);
            // Use fallback data
            this.marketData = {
                stocks: [],
                indices: [],
                gainers: [],
                losers: []
            };
        }
    }

    async loadWatchlistData() {
        // Simulate watchlist data
        this.watchlist = [
            { symbol: 'TSLA', name: 'Tesla, Inc.', price: 242.84, change: 2.45 },
            { symbol: 'NVDA', name: 'NVIDIA Corporation', price: 875.50, change: -1.23 }
        ];
    }

    setupRealTimeUpdates() {
        if (this.state.settings.autoRefresh) {
            this.realTimeInterval = setInterval(() => {
                this.updateRealTimeData();
            }, this.state.settings.refreshInterval);
        }
    }

    async updateRealTimeData() {
        // Simulate real-time price updates
        this.portfolio.forEach(holding => {
            const priceChange = (Math.random() - 0.5) * 0.02; // ±1% change
            holding.currentPrice *= (1 + priceChange);
            holding.marketValue = holding.shares * holding.currentPrice;
            holding.gainLoss = holding.marketValue - (holding.shares * holding.avgPrice);
            holding.gainLossPercent = ((holding.currentPrice - holding.avgPrice) / holding.avgPrice) * 100;
        });

        this.calculatePortfolioMetrics();
        
        // Update UI if on dashboard
        if (this.currentRoute === 'dashboard') {
            this.updateDashboardMetrics();
            this.updatePositionsTable();
        }
    }

    navigateToRoute(route) {
        if (this.routes[route]) {
            this.currentRoute = route;
            
            // Update URL
            window.history.pushState(null, null, `#${route}`);
            
            // Update breadcrumb
            this.updateBreadcrumb(route);
            
            // Update active navigation
            this.updateActiveNavigation(route);
            
            // Show view
            this.routes[route]();
            
        } else {
            console.warn(`Route not found: ${route}`);
            this.navigateToRoute('dashboard');
        }
    }

    updateBreadcrumb(route) {
        const routeNames = {
            'dashboard': 'Dashboard',
            'portfolio': 'Portfolio',
            'watchlist': 'Watchlist',
            'orders': 'Orders',
            'discover': 'Discover',
            'screener': 'Stock Screener',
            'market': 'Market News',
            'performance': 'Performance',
            'risk': 'Risk Analysis',
            'reports': 'Reports',
            'settings': 'Settings'
        };

        const sectionElement = document.getElementById('breadcrumb-section');
        const pageElement = document.getElementById('breadcrumb-page');
        
        if (sectionElement && pageElement) {
            sectionElement.textContent = 'Trading'; // Could be dynamic based on route category
            pageElement.textContent = routeNames[route] || route;
        }
    }

    updateActiveNavigation(route) {
        // Remove active from all nav items
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        
        // Add active to current route
        const activeItem = document.querySelector(`[data-route="${route}"]`);
        if (activeItem) {
            activeItem.classList.add('active');
        }
    }

    showDashboard() {
        this.showView('dashboard-view');
        this.updateDashboardMetrics();
        this.updatePositionsTable();
        this.updateAllocationChart();
        this.updatePerformanceChart('1M');
        this.updateMarketOverview();
        this.updateTopMovers();
        this.updateActivityFeed();
    }

    showView(viewId) {
        // Hide all views
        document.querySelectorAll('.view').forEach(view => {
            view.classList.remove('active');
        });
        
        // Show target view
        const targetView = document.getElementById(viewId);
        if (targetView) {
            targetView.classList.add('active');
        }
    }

    updateDashboardMetrics() {
        if (!this.portfolioMetrics) return;

        const metrics = this.portfolioMetrics;
        
        // Update metric values
        this.updateElement('total-portfolio-value', this.formatCurrency(metrics.totalValue));
        this.updateElement('day-gain-loss', this.formatCurrency(metrics.dayGainLoss));
        this.updateElement('total-gain-loss', this.formatCurrency(metrics.totalGainLoss));
        this.updateElement('cash-balance', this.formatCurrency(metrics.cashBalance));
        
        // Update changes
        this.updateMetricChange('portfolio-change', metrics.totalGainLoss, metrics.totalGainLossPercent);
        this.updateMetricChange('day-change-percent', metrics.dayGainLoss, metrics.dayGainLossPercent);
        this.updateMetricChange('total-change-percent', metrics.totalGainLoss, metrics.totalGainLossPercent);
    }

    updateMetricChange(elementId, value, percent) {
        const element = document.getElementById(elementId);
        if (!element) return;

        const isPositive = value >= 0;
        const icon = element.querySelector('i');
        const span = element.querySelector('span');
        
        if (icon && span) {
            // Update classes
            element.className = `metric-change ${isPositive ? 'positive' : 'negative'}`;
            
            // Update icon
            icon.className = `fas fa-arrow-${isPositive ? 'up' : 'down'}`;
            
            // Update text
            span.textContent = `${isPositive ? '+' : ''}${this.formatCurrency(value)} (${percent.toFixed(2)}%)`;
        }
    }

    updatePositionsTable() {
        const tbody = document.getElementById('positions-tbody');
        if (!tbody) return;

        tbody.innerHTML = '';

        if (this.portfolio.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="9" class="text-center text-muted" style="padding: 2rem;">
                        No positions in portfolio. <a href="#" onclick="app.showAddPositionModal()">Add your first position</a>
                    </td>
                </tr>
            `;
            return;
        }

        this.portfolio.forEach((position, index) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <strong>${position.symbol}</strong>
                        <button class="btn btn-outline btn-sm" onclick="app.viewStockDetails('${position.symbol}')" style="padding: 0.25rem 0.5rem; font-size: 0.75rem;">
                            <i class="fas fa-external-link-alt"></i>
                        </button>
                    </div>
                </td>
                <td>
                    <div>
                        <div class="font-semibold">${position.name}</div>
                        <div class="text-muted" style="font-size: 0.75rem;">Technology</div>
                    </div>
                </td>
                <td class="numeric font-mono">${position.shares.toLocaleString()}</td>
                <td class="numeric font-mono">${this.formatCurrency(position.avgPrice)}</td>
                <td class="numeric font-mono">
                    <div style="display: flex; align-items: center; justify-content: flex-end; gap: 0.5rem;">
                        ${this.formatCurrency(position.currentPrice)}
                        <span class="badge ${position.gainLossPercent >= 0 ? 'success' : 'danger'}" style="padding: 0.125rem 0.375rem; font-size: 0.625rem; border-radius: 0.25rem;">
                            ${position.gainLossPercent >= 0 ? '+' : ''}${position.gainLossPercent.toFixed(2)}%
                        </span>
                    </div>
                </td>
                <td class="numeric font-mono">${this.formatCurrency(position.marketValue)}</td>
                <td class="numeric font-mono ${position.gainLoss >= 0 ? 'text-success' : 'text-danger'}">
                    <div>
                        <div>${position.gainLoss >= 0 ? '+' : ''}${this.formatCurrency(position.gainLoss)}</div>
                        <div style="font-size: 0.75rem;">${position.gainLoss >= 0 ? '+' : ''}${position.gainLossPercent.toFixed(2)}%</div>
                    </div>
                </td>
                <td>
                    <span class="recommendation-badge ${position.recommendation.toLowerCase()}" style="padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.75rem; font-weight: 600;">
                        ${position.recommendation}
                    </span>
                </td>
                <td class="actions">
                    <div style="display: flex; gap: 0.25rem;">
                        <button class="btn btn-outline btn-sm" onclick="app.buyStock('${position.symbol}')" title="Buy More">
                            <i class="fas fa-plus"></i>
                        </button>
                        <button class="btn btn-outline btn-sm" onclick="app.sellStock('${position.symbol}')" title="Sell">
                            <i class="fas fa-minus"></i>
                        </button>
                        <button class="btn btn-outline btn-sm" onclick="app.viewAnalysis('${position.symbol}')" title="Analyze">
                            <i class="fas fa-chart-line"></i>
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });

        // Update position count
        document.getElementById('position-count').textContent = `${this.portfolio.length} positions`;
    }

    updateAllocationChart() {
        const chartDiv = document.getElementById('allocation-chart');
        if (!chartDiv || this.portfolio.length === 0) return;

        const data = [{
            labels: this.portfolio.map(p => p.symbol),
            values: this.portfolio.map(p => p.marketValue),
            type: 'pie',
            hole: 0.4,
            textinfo: 'label+percent',
            textposition: 'outside',
            marker: {
                colors: ['#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']
            }
        }];

        const layout = {
            margin: { t: 20, b: 20, l: 20, r: 20 },
            showlegend: false,
            font: { family: 'Inter, sans-serif', size: 12 }
        };

        if (typeof Plotly !== 'undefined') {
            Plotly.newPlot(chartDiv, data, layout, { responsive: true, displayModeBar: false });
        } else {
            chartDiv.innerHTML = '<p style="text-align: center; padding: 2rem; color: #666;">Chart library not available. Please refresh the page.</p>';
        }
    }

    async updatePerformanceChart(period) {
        const chartDiv = document.getElementById('performance-chart');
        if (!chartDiv) return;

        try {
            // Try to get real performance data from API
            const response = await fetch(`${this.apiUrl}/api/trading/analytics/performance?period=${period}`);
            let performanceData;
            
            if (response.ok) {
                performanceData = await response.json();
            } else {
                // Fallback to mock data
                performanceData = this.generateMockPerformanceData(period);
            }

            const data = [{
                x: performanceData.data.map(point => point.date),
                y: performanceData.data.map(point => point.value),
                type: 'scatter',
                mode: 'lines',
                line: {
                    color: '#3b82f6',
                    width: 2
                },
                fill: 'tozeroy',
                fillcolor: 'rgba(59, 130, 246, 0.1)',
                hovertemplate: '<b>%{x}</b><br>Portfolio Value: $%{y:,.2f}<extra></extra>'
            }];

            const layout = {
                margin: { t: 20, b: 40, l: 60, r: 20 },
                xaxis: {
                    showgrid: false,
                    zeroline: false,
                    title: ''
                },
                yaxis: {
                    showgrid: true,
                    gridcolor: '#f1f5f9',
                    zeroline: false,
                    tickformat: '$,.0f',
                    title: ''
                },
                showlegend: false,
                font: { family: 'Inter, sans-serif', size: 12 },
                plot_bgcolor: 'transparent',
                paper_bgcolor: 'transparent'
            };

            const config = {
                responsive: true,
                displayModeBar: false,
                staticPlot: false
            };

            if (typeof Plotly !== 'undefined') {
                Plotly.newPlot(chartDiv, data, layout, config);
            } else {
                chartDiv.innerHTML = '<p style="text-align: center; padding: 2rem; color: #666;">Chart library not available. Please refresh the page.</p>';
            }
            
        } catch (error) {
            console.error('Error updating performance chart:', error);
            // Show fallback chart
            this.showFallbackChart(chartDiv, period);
        }
    }

    generateMockPerformanceData(period) {
        const periods = {
            '1D': { points: 24, interval: 'hour' },
            '1W': { points: 7, interval: 'day' },
            '1M': { points: 30, interval: 'day' },
            '3M': { points: 90, interval: 'day' },
            '1Y': { points: 365, interval: 'day' }
        };

        const config = periods[period] || periods['1M'];
        const data = [];
        
        const baseValue = this.portfolioMetrics ? this.portfolioMetrics.totalValue : 50000;
        let currentValue = baseValue;

        for (let i = config.points; i >= 0; i--) {
            const date = new Date();
            if (config.interval === 'hour') {
                date.setHours(date.getHours() - i);
            } else {
                date.setDate(date.getDate() - i);
            }
            
            // Simulate price movement
            const change = (Math.random() - 0.5) * 0.02;
            currentValue *= (1 + change);
            
            data.push({
                date: date.toISOString(),
                value: currentValue
            });
        }

        return { period, data };
    }

    showFallbackChart(chartDiv, period) {
        chartDiv.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; height: 300px; color: #64748b;">
                <div style="text-align: center;">
                    <i class="fas fa-chart-line" style="font-size: 2rem; margin-bottom: 1rem;"></i>
                    <div>Chart will appear here for ${period} period</div>
                </div>
            </div>
        `;
    }

    updateMarketOverview() {
        if (!this.marketData.indices) return;

        const container = document.querySelector('.market-indices');
        if (!container) return;

        container.innerHTML = '';

        this.marketData.indices.forEach(index => {
            const item = document.createElement('div');
            item.className = 'index-item';
            item.innerHTML = `
                <span class="index-name">${index.name}</span>
                <span class="index-value">${index.value.toLocaleString()}</span>
                <span class="index-change ${index.change >= 0 ? 'positive' : 'negative'}">
                    ${index.change >= 0 ? '+' : ''}${index.change.toFixed(2)}%
                </span>
            `;
            container.appendChild(item);
        });
    }

    updateTopMovers() {
        const container = document.getElementById('movers-content');
        if (!container) return;

        // Show gainers by default
        this.showMovers('gainers');
    }

    showMovers(type) {
        const container = document.getElementById('movers-content');
        if (!container) return;

        const stocks = type === 'gainers' ? this.marketData.gainers : this.marketData.losers;
        
        container.innerHTML = '';

        stocks.forEach(stock => {
            const change = (Math.random() - 0.5) * 10; // Mock change
            const item = document.createElement('div');
            item.className = 'index-item';
            item.innerHTML = `
                <span class="index-name">${stock.symbol}</span>
                <span class="index-value">$${stock.price.toFixed(2)}</span>
                <span class="index-change ${type === 'gainers' ? 'positive' : 'negative'}">
                    ${type === 'gainers' ? '+' : ''}${Math.abs(change).toFixed(2)}%
                </span>
            `;
            container.appendChild(item);
        });
    }

    updateActivityFeed() {
        const feed = document.getElementById('activity-feed');
        if (!feed) return;

        const activities = [
            {
                type: 'buy',
                title: 'Purchased AAPL',
                description: 'Bought 10 shares at $185.92',
                time: '2 minutes ago',
                icon: 'fa-plus',
                iconBg: '#22c55e'
            },
            {
                type: 'alert',
                title: 'Price Alert Triggered',
                description: 'TSLA reached target price of $245.00',
                time: '15 minutes ago',
                icon: 'fa-bell',
                iconBg: '#f59e0b'
            },
            {
                type: 'analysis',
                title: 'New Analysis Report',
                description: 'Portfolio risk analysis completed',
                time: '1 hour ago',
                icon: 'fa-chart-bar',
                iconBg: '#3b82f6'
            }
        ];

        feed.innerHTML = '';

        activities.forEach(activity => {
            const item = document.createElement('div');
            item.className = 'activity-item';
            item.innerHTML = `
                <div class="activity-icon" style="background: ${activity.iconBg}; color: white;">
                    <i class="fas ${activity.icon}"></i>
                </div>
                <div class="activity-content">
                    <div class="activity-title">${activity.title}</div>
                    <div class="activity-description">${activity.description}</div>
                    <div class="activity-time">${activity.time}</div>
                </div>
            `;
            feed.appendChild(item);
        });
    }

    updateNavigationCountersDefensive() {
        try {
            this.safeUpdateElement('#holdings-count', this.portfolio?.length || 0, 'text');
            this.safeUpdateElement('#watchlist-count', this.watchlist?.length || 0, 'text');
            this.safeUpdateElement('#pending-orders', this.orders?.length || 0, 'text');
        } catch (error) {
            console.warn('Error updating navigation counters:', error);
        }
    }
    
    // Keep original for backward compatibility
    updateNavigationCounters() {
        this.updateNavigationCountersDefensive();
    }

    // Trading Actions
    showAddPositionModal() {
        const modal = document.getElementById('add-position-modal');
        if (modal) {
            modal.classList.add('active');
            // Clear form
            document.getElementById('add-position-form').reset();
            // Focus on first input
            setTimeout(() => {
                const firstInput = document.getElementById('position-symbol');
                if (firstInput) firstInput.focus();
            }, 100);
        }
    }

    async addPositionFromModal() {
        const form = document.getElementById('add-position-form');
        const formData = new FormData(form);
        
        const symbol = formData.get('symbol').toUpperCase().trim();
        const shares = parseFloat(formData.get('shares'));
        const price = parseFloat(formData.get('price'));
        
        // Validate inputs
        if (!symbol || !shares || !price) {
            this.showNotification('Please fill in all required fields', 'error');
            return;
        }
        
        if (shares <= 0 || price <= 0) {
            this.showNotification('Shares and price must be positive numbers', 'error');
            return;
        }
        
        try {
            this.showLoading('Adding position...');
            
            // Call API to add position
            const response = await fetch(`${this.apiUrl}/api/trading/portfolio/positions?symbol=${symbol}&shares=${shares}&price=${price}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                const result = await response.json();
                this.showNotification(`Successfully added ${shares} shares of ${symbol}`, 'success');
                
                // Refresh portfolio data
                await this.loadPortfolioData();
                this.updateDashboardMetrics();
                this.updatePositionsTable();
                this.updateAllocationChart();
                this.updateNavigationCounters();
                
                // Close modal
                this.closeModal();
            } else {
                throw new Error('Failed to add position');
            }
        } catch (error) {
            console.error('Error adding position:', error);
            this.showNotification('Failed to add position. Please try again.', 'error');
        } finally {
            this.hideLoading();
        }
    }

    closeModal() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.remove('active');
        });
    }

    async buyStock(symbol) {
        // Show buy order dialog
        const quantity = prompt(`How many shares of ${symbol} would you like to buy?`, '10');
        if (!quantity || isNaN(quantity) || quantity <= 0) {
            return;
        }

        try {
            this.showLoading('Placing buy order...');
            
            const response = await fetch(`${this.apiUrl}/api/trading/orders`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    symbol: symbol,
                    side: 'BUY',
                    quantity: parseFloat(quantity),
                    order_type: 'MARKET'
                })
            });

            if (response.ok) {
                const result = await response.json();
                this.showNotification(`Buy order placed for ${quantity} shares of ${symbol}`, 'success');
                
                // Refresh portfolio and orders
                await this.loadPortfolioData();
                this.updateDashboardMetrics();
                this.updatePositionsTable();
                this.updateNavigationCounters();
            } else {
                throw new Error('Failed to place order');
            }
        } catch (error) {
            console.error('Error placing buy order:', error);
            this.showNotification('Failed to place buy order', 'error');
        } finally {
            this.hideLoading();
        }
    }

    async sellStock(symbol) {
        // Find current position
        const position = this.portfolio.find(p => p.symbol === symbol);
        if (!position) {
            this.showNotification(`You don't own any shares of ${symbol}`, 'error');
            return;
        }

        const maxShares = position.shares;
        const quantity = prompt(`How many shares of ${symbol} would you like to sell? (You own ${maxShares})`, Math.min(10, maxShares).toString());
        
        if (!quantity || isNaN(quantity) || quantity <= 0) {
            return;
        }

        if (quantity > maxShares) {
            this.showNotification(`You can't sell more than ${maxShares} shares`, 'error');
            return;
        }

        try {
            this.showLoading('Placing sell order...');
            
            const response = await fetch(`${this.apiUrl}/api/trading/orders`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    symbol: symbol,
                    side: 'SELL',
                    quantity: parseFloat(quantity),
                    order_type: 'MARKET'
                })
            });

            if (response.ok) {
                const result = await response.json();
                this.showNotification(`Sell order placed for ${quantity} shares of ${symbol}`, 'success');
                
                // Refresh portfolio and orders
                await this.loadPortfolioData();
                this.updateDashboardMetrics();
                this.updatePositionsTable();
                this.updateNavigationCounters();
            } else {
                throw new Error('Failed to place order');
            }
        } catch (error) {
            console.error('Error placing sell order:', error);
            this.showNotification('Failed to place sell order', 'error');
        } finally {
            this.hideLoading();
        }
    }

    viewStockDetails(symbol) {
        window.open(`${this.apiUrl}/portfolio/dashboard/${symbol}`, '_blank');
    }

    viewAnalysis(symbol) {
        this.navigateToRoute('discover');
        // Show detailed analysis for the symbol
    }

    // Search and filters
    async handleGlobalSearch(query) {
        if (query.length < 2) {
            this.hideSuggestions();
            return;
        }

        try {
            // Search through both portfolio and available stocks
            const portfolioResults = this.portfolio.filter(stock => 
                stock.symbol.toLowerCase().includes(query.toLowerCase()) ||
                stock.name.toLowerCase().includes(query.toLowerCase())
            );

            const marketResults = this.marketData.stocks?.filter(stock => 
                stock.symbol.toLowerCase().includes(query.toLowerCase()) ||
                stock.name.toLowerCase().includes(query.toLowerCase())
            ).slice(0, 8) || [];

            const allResults = [...portfolioResults, ...marketResults];
            const uniqueResults = allResults.filter((item, index, self) => 
                index === self.findIndex(t => t.symbol === item.symbol)
            ).slice(0, 10);

            this.showSearchSuggestions(uniqueResults, query);
        } catch (error) {
            console.error('Search error:', error);
        }
    }

    showSearchSuggestions(results, query) {
        const container = document.getElementById('search-suggestions');
        if (!container) return;

        if (results.length === 0) {
            container.innerHTML = `
                <div style="padding: 1rem; text-align: center; color: #64748b;">
                    No results found for "${query}"
                </div>
            `;
            container.style.display = 'block';
            return;
        }

        container.innerHTML = '';
        results.forEach(stock => {
            const item = document.createElement('div');
            item.className = 'suggestion-item';
            item.style.cssText = `
                padding: 0.75rem; 
                cursor: pointer; 
                border-bottom: 1px solid #e2e8f0;
                transition: background-color 0.2s ease;
            `;
            
            const price = stock.currentPrice || stock.price || 0;
            const isPortfolioStock = this.portfolio.find(p => p.symbol === stock.symbol);
            
            item.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <strong>${stock.symbol}</strong>
                            ${isPortfolioStock ? '<span style="background: #10b981; color: white; padding: 0.125rem 0.375rem; border-radius: 0.25rem; font-size: 0.625rem;">OWNED</span>' : ''}
                        </div>
                        <div style="font-size: 0.875rem; color: #64748b;">${stock.name}</div>
                    </div>
                    <div style="font-family: monospace; font-weight: 600;">$${price.toFixed(2)}</div>
                </div>
            `;
            
            item.addEventListener('mouseenter', () => {
                item.style.backgroundColor = '#f8fafc';
            });
            
            item.addEventListener('mouseleave', () => {
                item.style.backgroundColor = '';
            });
            
            item.addEventListener('click', () => {
                this.executeSearch(stock.symbol);
                this.hideSuggestions();
                // Clear search input
                document.getElementById('global-search').value = stock.symbol;
            });
            
            container.appendChild(item);
        });

        container.style.display = 'block';
    }

    hideSuggestions() {
        const container = document.getElementById('search-suggestions');
        if (container) {
            container.style.display = 'none';
        }
    }

    executeSearch(query) {
        this.showNotification(`Searching for: ${query}`, 'info');
        // Implement search execution
        this.navigateToRoute('discover');
    }

    // Table operations
    sortTable(tableId, column) {
        const table = document.getElementById(tableId);
        if (!table) return;

        const currentSort = this.state.sorting.positions;
        
        // Determine sort direction
        if (currentSort.column === column) {
            currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
        } else {
            currentSort.column = column;
            currentSort.direction = 'asc';
        }

        // Update UI
        table.querySelectorAll('th').forEach(th => {
            th.classList.remove('sort-asc', 'sort-desc');
        });
        
        const header = table.querySelector(`th[data-sort="${column}"]`);
        if (header) {
            header.classList.add(`sort-${currentSort.direction}`);
        }

        // Sort data and update table
        if (tableId === 'positions-table') {
            this.sortPortfolioData(column, currentSort.direction);
            this.updatePositionsTable();
        }
    }

    sortPortfolioData(column, direction) {
        this.portfolio.sort((a, b) => {
            let aVal = a[column];
            let bVal = b[column];
            
            // Handle numeric columns
            if (typeof aVal === 'number' && typeof bVal === 'number') {
                return direction === 'asc' ? aVal - bVal : bVal - aVal;
            }
            
            // Handle string columns
            aVal = String(aVal).toLowerCase();
            bVal = String(bVal).toLowerCase();
            
            if (direction === 'asc') {
                return aVal.localeCompare(bVal);
            } else {
                return bVal.localeCompare(aVal);
            }
        });
    }

    exportPortfolioData() {
        const data = {
            timestamp: new Date().toISOString(),
            portfolio: this.portfolio,
            metrics: this.portfolioMetrics
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `portfolio-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        
        URL.revokeObjectURL(url);
        this.showNotification('Portfolio data exported successfully', 'success');
    }

    toggleSidebar() {
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) {
            sidebar.classList.toggle('collapsed');
        }
    }

    switchTab(card, tab) {
        const tabs = card.querySelectorAll('.tab-btn');
        tabs.forEach(t => t.classList.remove('active'));
        
        const activeTab = card.querySelector(`[data-tab="${tab}"]`);
        if (activeTab) {
            activeTab.classList.add('active');
        }

        // Handle tab content switching
        if (tab === 'losers') {
            this.showMovers('losers');
        } else if (tab === 'gainers') {
            this.showMovers('gainers');
        }
    }

    // Utility methods
    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    }

    updateElement(id, content) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = content;
        }
    }

    showLoading(message = 'Loading...') {
        try {
            const overlay = document.getElementById('loading-overlay');
            if (overlay) {
                const text = overlay.querySelector('.loading-text');
                if (text) {
                    text.textContent = message;
                }
                overlay.classList.add('active');
            } else {
                console.warn('Loading overlay not found');
            }
        } catch (error) {
            console.warn('Error showing loading overlay:', error);
        }
    }

    hideLoading() {
        try {
            const overlay = document.getElementById('loading-overlay');
            if (overlay) {
                overlay.classList.remove('active');
            } else {
                console.warn('Loading overlay not found for hiding');
            }
        } catch (error) {
            console.warn('Error hiding loading overlay:', error);
        }
    }

    showNotification(message, type = 'info') {
        try {
            const container = document.getElementById('notifications-container');
            if (!container) {
                console.warn('Notifications container not found');
                return;
            }

            const notification = document.createElement('div');
            notification.className = `notification notification-${type}`;
            
            const colors = {
                'success': '#22c55e',
                'error': '#ef4444', 
                'warning': '#f59e0b',
                'info': '#3b82f6'
            };
            
            const icons = {
                'success': 'fa-check-circle',
                'error': 'fa-exclamation-circle',
                'warning': 'fa-exclamation-triangle', 
                'info': 'fa-info-circle'
            };
            
            const color = colors[type] || colors.info;
            const icon = icons[type] || icons.info;
            
            notification.style.cssText = `
                background: white;
                border: 1px solid #e2e8f0;
                border-left: 4px solid ${color};
                border-radius: 0.5rem;
                padding: 1rem;
                margin-bottom: 0.75rem;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                display: flex;
                align-items: center;
                justify-content: space-between;
                min-width: 300px;
                animation: slideIn 0.3s ease;
                z-index: 1000;
            `;
            
            notification.innerHTML = `
                <div style="display: flex; align-items: center; gap: 0.75rem;">
                    <i class="fas ${icon}" style="color: ${color};"></i>
                    <span style="color: #374151; font-weight: 500;">${message}</span>
                </div>
                <button onclick="this.parentElement.remove()" style="background: none; border: none; color: #9ca3af; cursor: pointer; font-size: 1.25rem;">×</button>
            `;

            container.appendChild(notification);

            // Auto remove after different times based on type
            const autoRemoveTime = type === 'error' ? 8000 : type === 'warning' ? 6000 : 5000;
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.remove();
                }
            }, autoRemoveTime);
            
        } catch (error) {
            console.error('Error showing notification:', error);
            // Fallback to console log
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }

    // Intelligence Dashboard Event Listeners
    setupIntelligenceEventListenersDefensive() {
        try {
            console.log('🧠 Setting up intelligence event listeners...');
            
            // Portfolio Intelligence listeners
            this.safeAddEventListener('#refresh-intelligence', 'click', () => {
                this.refreshPortfolioIntelligence();
            });

            this.safeAddEventListener('#export-recommendations', 'click', () => {
                this.exportRecommendations();
            });

            this.safeAddEventListener('#filter-recommendations', 'click', () => {
                this.showRecommendationFilters();
            });

            // News Intelligence listeners
            this.safeAddEventListener('#refresh-news', 'click', () => {
                this.refreshNewsIntelligence();
            });

            this.safeAddEventListener('#stock-news-selector', 'change', (e) => {
                this.loadStockNewsAnalysis(e.target.value);
            });

            // Expert Advisor listeners
            this.safeAddEventListener('#refresh-experts', 'click', () => {
                this.refreshExpertAdvisor();
            });

            this.safeAddEventListener('#expert-stock-selector', 'change', (e) => {
                this.loadIndividualExpertOpinions(e.target.value);
            });

            // Stock Analysis listeners
            this.safeAddEventListener('#analyze-stock', 'click', () => {
                const symbol = document.getElementById('analysis-stock-search')?.value?.trim();
                if (symbol) {
                    this.analyzeStock(symbol);
                }
            });

            this.safeAddEventListener('#analysis-stock-search', 'keypress', (e) => {
                if (e.key === 'Enter') {
                    const symbol = e.target.value.trim();
                    if (symbol) {
                        this.analyzeStock(symbol);
                    }
                }
            });
            
            console.log('✅ Intelligence event listeners setup completed');
            
        } catch (error) {
            console.error('Error setting up intelligence event listeners:', error);
        }
    }
    
    // Keep original for backward compatibility
    setupIntelligenceEventListeners() {
        this.setupIntelligenceEventListenersDefensive();
    }

    // Portfolio Intelligence Dashboard Methods
    async showPortfolioIntelligence() {
        this.showView('portfolio-intelligence-view');
        await this.loadPortfolioIntelligence();
    }

    async loadPortfolioIntelligence() {
        try {
            this.showLoading('Loading portfolio intelligence...');
            
            // Load portfolio health and recommendations
            const [healthResponse, recommendationsResponse] = await Promise.all([
                fetch(`${this.apiUrl}/api/portfolio/health`),
                fetch(`${this.apiUrl}/api/portfolio/recommendations`)
            ]);

            if (healthResponse.ok && recommendationsResponse.ok) {
                this.intelligenceData.portfolioHealth = await healthResponse.json();
                this.intelligenceData.portfolioRecommendations = await recommendationsResponse.json();
                
                this.updatePortfolioHealthDisplay();
                this.updateAIRecommendationsDisplay();
                this.updateAllocationAnalysis();
                this.updateHealthTimestamp();
            } else {
                throw new Error('Failed to load portfolio intelligence data');
            }

        } catch (error) {
            console.error('Error loading portfolio intelligence:', error);
            this.showNotification('Failed to load portfolio intelligence', 'error');
        } finally {
            this.hideLoading();
        }
    }

    updatePortfolioHealthDisplay() {
        const health = this.intelligenceData.portfolioHealth;
        
        // Update health score circles
        this.updateHealthScoreCircle('overall-health-score', health.health_score);
        this.updateHealthScoreCircle('diversification-score', health.diversification_score);
        this.updateHealthScoreCircle('performance-score', health.performance_score);
        this.updateHealthScoreCircle('risk-score', health.risk_score);
    }

    updateHealthScoreCircle(elementId, score) {
        const element = document.getElementById(elementId);
        if (!element) return;

        const scoreValue = element.querySelector('.score-value');
        if (scoreValue) {
            scoreValue.textContent = Math.round(score || 0);
        }

        // Update CSS variable for conic gradient
        element.style.setProperty('--score', score || 0);
        
        // Add color based on score
        const colorClass = score >= 80 ? 'excellent' : score >= 60 ? 'good' : score >= 40 ? 'average' : 'poor';
        element.className = element.className.replace(/excellent|good|average|poor/g, '');
        element.classList.add(colorClass);
    }

    updateAIRecommendationsDisplay() {
        const container = document.getElementById('ai-recommendations-list');
        const countElement = document.getElementById('ai-recommendation-count');
        
        if (!container) return;

        const recommendations = this.intelligenceData.portfolioRecommendations;
        
        // Update count
        if (countElement) {
            countElement.textContent = `${recommendations.length} recommendations`;
        }

        container.innerHTML = '';

        if (recommendations.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-brain fa-2x"></i>
                    <p>No AI recommendations available</p>
                </div>
            `;
            return;
        }

        recommendations.forEach(rec => {
            const item = document.createElement('div');
            item.className = 'recommendation-item';
            
            const confidencePercent = (rec.confidence || 0);
            const actionClass = (rec.action || '').toLowerCase().replace('_', '-');
            
            item.innerHTML = `
                <div class="recommendation-header">
                    <div class="recommendation-symbol">${rec.symbol}</div>
                    <div class="recommendation-action ${actionClass}">${rec.action}</div>
                </div>
                <div class="recommendation-confidence">
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: ${confidencePercent}%"></div>
                    </div>
                    <span class="confidence-text">${confidencePercent.toFixed(0)}%</span>
                </div>
                <div class="recommendation-meta">
                    <strong>${rec.name}</strong> - ${rec.sector} | ${rec.market}
                </div>
                <div class="recommendation-price-info">
                    Current: $${rec.current_price?.toFixed(2)} 
                    ${rec.target_price ? `| Target: $${rec.target_price.toFixed(2)}` : ''}
                </div>
                <div class="recommendation-reasoning">${rec.reasoning}</div>
            `;
            
            // Add click handler for detailed view
            item.addEventListener('click', () => {
                this.showRecommendationDetails(rec);
            });
            
            container.appendChild(item);
        });
    }

    updateAllocationAnalysis() {
        const health = this.intelligenceData.portfolioHealth;
        
        this.updateAllocationChart('sector-allocation-chart', health.sector_allocation);
        this.updateAllocationChart('market-allocation-chart', health.market_allocation);
    }

    updateAllocationChart(chartId, data) {
        const chartDiv = document.getElementById(chartId);
        if (!chartDiv || !data) return;

        // Convert data to Plotly format
        const labels = Object.keys(data);
        const values = Object.values(data);

        if (labels.length === 0) {
            chartDiv.innerHTML = '<p style="text-align: center; padding: 2rem; color: #666;">No data available</p>';
            return;
        }

        const plotData = [{
            labels: labels,
            values: values,
            type: 'pie',
            hole: 0.4,
            textinfo: 'label+percent',
            textposition: 'outside',
            marker: {
                colors: ['#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#84cc16', '#f97316']
            }
        }];

        const layout = {
            margin: { t: 10, b: 10, l: 10, r: 10 },
            showlegend: false,
            font: { family: 'Inter, sans-serif', size: 10 }
        };

        if (typeof Plotly !== 'undefined') {
            Plotly.newPlot(chartDiv, plotData, layout, { responsive: true, displayModeBar: false });
        } else {
            chartDiv.innerHTML = '<p style="text-align: center; padding: 2rem; color: #666;">Chart library not available</p>';
        }
    }

    updateHealthTimestamp() {
        const element = document.getElementById('health-timestamp');
        if (element) {
            element.textContent = `Last updated: ${new Date().toLocaleString()}`;
        }
    }

    async refreshPortfolioIntelligence() {
        await this.loadPortfolioIntelligence();
        this.showNotification('Portfolio intelligence refreshed', 'success');
    }

    // News Intelligence Methods
    async showNewsIntelligence() {
        this.showView('news-intelligence-view');
        await this.loadNewsIntelligence();
    }

    async loadNewsIntelligence() {
        try {
            this.showLoading('Loading news intelligence...');
            
            // Load portfolio news summary and populate stock selector
            const [portfolioNewsResponse] = await Promise.all([
                fetch(`${this.apiUrl}/api/news/portfolio`)
            ]);

            if (portfolioNewsResponse.ok) {
                this.intelligenceData.newsAnalysis.portfolio = await portfolioNewsResponse.json();
                this.updatePortfolioNewsSummary();
                this.populateStockNewsSelector();
                this.loadMarketSentiment();
            }

        } catch (error) {
            console.error('Error loading news intelligence:', error);
            this.showNotification('Failed to load news intelligence', 'error');
        } finally {
            this.hideLoading();
        }
    }

    updatePortfolioNewsSummary() {
        const newsData = this.intelligenceData.newsAnalysis.portfolio;
        
        // Update sentiment indicators
        const sentimentElement = document.getElementById('portfolio-sentiment');
        const impactElement = document.getElementById('news-impact');
        
        if (sentimentElement && newsData) {
            const sentimentScore = sentimentElement.querySelector('.sentiment-score');
            if (sentimentScore) {
                sentimentScore.textContent = newsData.overall_sentiment || 'N/A';
            }
        }

        if (impactElement && newsData) {
            const impactScore = impactElement.querySelector('.impact-score');
            if (impactScore) {
                impactScore.textContent = newsData.impact_score || 'N/A';
            }
        }

        // Update news summary
        const container = document.getElementById('portfolio-news-summary');
        if (!container) return;

        if (!newsData || !newsData.top_stories) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-newspaper fa-2x"></i>
                    <p>No news data available</p>
                </div>
            `;
            return;
        }

        container.innerHTML = '';
        newsData.top_stories.forEach(story => {
            const item = document.createElement('div');
            item.className = 'news-item';
            
            item.innerHTML = `
                <div class="news-header">
                    <span class="news-source">${story.source || 'News'}</span>
                    <span class="news-timestamp">${this.formatRelativeTime(story.published_at)}</span>
                </div>
                <div class="news-title">${story.title}</div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.5rem;">
                    <span class="news-sentiment-badge ${this.getSentimentClass(story.sentiment)}">
                        ${this.formatSentiment(story.sentiment)}
                    </span>
                    <span style="font-size: 0.75rem; color: #64748b;">Impact: ${story.impact_score || 'N/A'}</span>
                </div>
            `;
            
            container.appendChild(item);
        });
    }

    populateStockNewsSelector() {
        const selector = document.getElementById('stock-news-selector');
        if (!selector) return;

        // Clear existing options except the first one
        selector.innerHTML = '<option value="">Select a stock</option>';

        // Add portfolio stocks
        if (this.portfolio && this.portfolio.length > 0) {
            this.portfolio.forEach(stock => {
                const option = document.createElement('option');
                option.value = stock.symbol;
                option.textContent = `${stock.symbol} - ${stock.name}`;
                selector.appendChild(option);
            });
        }
    }

    async loadStockNewsAnalysis(symbol) {
        if (!symbol) {
            document.getElementById('stock-news-analysis').innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-newspaper fa-2x"></i>
                    <p>Select a stock to view news analysis</p>
                </div>
            `;
            return;
        }

        try {
            this.showLoading('Loading stock news...');
            
            const response = await fetch(`${this.apiUrl}/api/news/stock/${symbol}`);
            if (response.ok) {
                const newsData = await response.json();
                this.updateStockNewsDisplay(newsData);
            }
            
        } catch (error) {
            console.error('Error loading stock news:', error);
            this.showNotification(`Failed to load news for ${symbol}`, 'error');
        } finally {
            this.hideLoading();
        }
    }

    updateStockNewsDisplay(newsData) {
        const container = document.getElementById('stock-news-analysis');
        if (!container) return;

        container.innerHTML = `
            <div class="stock-news-header">
                <h4>${newsData.symbol} News Analysis</h4>
                <div class="news-metrics">
                    <div class="metric">
                        <span class="metric-label">Articles</span>
                        <span class="metric-value">${newsData.news_count}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Sentiment</span>
                        <span class="metric-value ${this.getSentimentClass(newsData.overall_sentiment)}">
                            ${this.formatSentiment(newsData.overall_sentiment)}
                        </span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Impact</span>
                        <span class="metric-value">${newsData.impact_score || 'N/A'}</span>
                    </div>
                </div>
            </div>
            <div class="news-headlines">
                ${newsData.recent_headlines.map(headline => `
                    <div class="headline-item">
                        <div class="headline-text">${headline}</div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    async loadMarketSentiment() {
        try {
            const response = await fetch(`${this.apiUrl}/api/news/market/global`);
            if (response.ok) {
                const marketData = await response.json();
                this.updateMarketSentimentChart(marketData);
            }
        } catch (error) {
            console.error('Error loading market sentiment:', error);
        }
    }

    updateMarketSentimentChart(data) {
        const chartDiv = document.getElementById('market-sentiment-chart');
        if (!chartDiv) return;

        // Simple sentiment display for now
        chartDiv.innerHTML = `
            <div style="text-align: center; padding: 2rem;">
                <div style="font-size: 2rem; margin-bottom: 1rem;">📈</div>
                <div style="font-size: 1.25rem; font-weight: 600; margin-bottom: 0.5rem;">Market Sentiment</div>
                <div style="font-size: 1rem; color: #64748b;">${data?.sentiment || 'Neutral'}</div>
            </div>
        `;
    }

    async refreshNewsIntelligence() {
        await this.loadNewsIntelligence();
        this.showNotification('News intelligence refreshed', 'success');
    }

    // Expert Advisor Methods
    async showExpertAdvisor() {
        this.showView('expert-advisor-view');
        await this.loadExpertAdvisor();
    }

    async loadExpertAdvisor() {
        try {
            this.showLoading('Loading expert analysis...');
            
            // Load portfolio expert analysis and populate selector
            const [portfolioExpertsResponse] = await Promise.all([
                fetch(`${this.apiUrl}/api/experts/portfolio/analysis`)
            ]);

            if (portfolioExpertsResponse.ok) {
                this.intelligenceData.expertConsensus.portfolio = await portfolioExpertsResponse.json();
                this.updatePortfolioExpertConsensus();
                this.populateExpertStockSelector();
                this.loadExpertTrackRecords();
            }

        } catch (error) {
            console.error('Error loading expert advisor:', error);
            this.showNotification('Failed to load expert analysis', 'error');
        } finally {
            this.hideLoading();
        }
    }

    updatePortfolioExpertConsensus() {
        const container = document.getElementById('portfolio-expert-consensus');
        if (!container) return;

        const expertsData = this.intelligenceData.expertConsensus.portfolio;
        
        if (!expertsData || !expertsData.stock_consensus) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-user-graduate fa-2x"></i>
                    <p>No expert consensus available</p>
                </div>
            `;
            return;
        }

        container.innerHTML = '';
        expertsData.stock_consensus.forEach(consensus => {
            const item = document.createElement('div');
            item.className = 'expert-consensus-item';
            
            const actionClass = (consensus.consensus_action || '').toLowerCase().replace('_', '-');
            
            item.innerHTML = `
                <div class="expert-consensus-header">
                    <div class="expert-consensus-symbol">${consensus.symbol}</div>
                    <div class="expert-consensus-action ${actionClass}">${consensus.consensus_action}</div>
                </div>
                <div class="expert-metrics">
                    <div class="expert-metric">
                        <div class="expert-metric-value">${consensus.expert_count}</div>
                        <div class="expert-metric-label">Experts</div>
                    </div>
                    <div class="expert-metric">
                        <div class="expert-metric-value">${(consensus.consensus_confidence * 100).toFixed(0)}%</div>
                        <div class="expert-metric-label">Confidence</div>
                    </div>
                    <div class="expert-metric">
                        <div class="expert-metric-value">${(consensus.agreement_level * 100).toFixed(0)}%</div>
                        <div class="expert-metric-label">Agreement</div>
                    </div>
                    <div class="expert-metric">
                        <div class="expert-metric-value">$${consensus.consensus_target_price?.toFixed(2) || 'N/A'}</div>
                        <div class="expert-metric-label">Target Price</div>
                    </div>
                </div>
                <div class="expert-arguments">
                    <div style="font-size: 0.875rem; color: #374151; margin-bottom: 0.5rem;">
                        <strong>Key Arguments:</strong>
                    </div>
                    <ul style="font-size: 0.75rem; color: #6b7280; padding-left: 1rem;">
                        ${consensus.key_arguments.map(arg => `<li>${arg}</li>`).join('')}
                    </ul>
                </div>
            `;
            
            container.appendChild(item);
        });
    }

    populateExpertStockSelector() {
        const selector = document.getElementById('expert-stock-selector');
        if (!selector) return;

        // Clear existing options
        selector.innerHTML = '<option value="">Select a stock</option>';

        // Add portfolio stocks
        if (this.portfolio && this.portfolio.length > 0) {
            this.portfolio.forEach(stock => {
                const option = document.createElement('option');
                option.value = stock.symbol;
                option.textContent = `${stock.symbol} - ${stock.name}`;
                selector.appendChild(option);
            });
        }
    }

    async loadIndividualExpertOpinions(symbol) {
        if (!symbol) {
            document.getElementById('individual-expert-opinions').innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-user-graduate fa-2x"></i>
                    <p>Select a stock to view expert opinions</p>
                </div>
            `;
            return;
        }

        try {
            this.showLoading('Loading expert opinions...');
            
            const response = await fetch(`${this.apiUrl}/api/experts/recommendations/${symbol}`);
            if (response.ok) {
                const expertOpinions = await response.json();
                this.updateIndividualExpertOpinions(expertOpinions);
            }
            
        } catch (error) {
            console.error('Error loading expert opinions:', error);
            this.showNotification(`Failed to load expert opinions for ${symbol}`, 'error');
        } finally {
            this.hideLoading();
        }
    }

    updateIndividualExpertOpinions(opinions) {
        const container = document.getElementById('individual-expert-opinions');
        if (!container) return;

        if (!opinions || opinions.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-user-graduate fa-2x"></i>
                    <p>No expert opinions available</p>
                </div>
            `;
            return;
        }

        container.innerHTML = '';
        opinions.forEach(opinion => {
            const item = document.createElement('div');
            item.className = 'expert-opinion-item';
            
            const trackRecordStars = '★'.repeat(Math.round(opinion.track_record_score));
            const actionClass = (opinion.action || '').toLowerCase().replace('_', '-');
            
            item.innerHTML = `
                <div class="expert-opinion-header">
                    <div class="expert-name">${opinion.expert_name}</div>
                    <div class="expert-type">${opinion.expert_type}</div>
                </div>
                <div class="expert-recommendation">
                    <div class="recommendation-action ${actionClass}">${opinion.action}</div>
                    <div class="expert-confidence">${(opinion.confidence * 100).toFixed(0)}% confidence</div>
                </div>
                <div class="expert-details">
                    <div class="target-price">Target: $${opinion.target_price?.toFixed(2) || 'N/A'}</div>
                    <div class="time-horizon">${opinion.time_horizon}</div>
                </div>
                <div class="expert-reasoning">${opinion.reasoning}</div>
                <div class="expert-track-record">
                    <span class="track-record-stars">${trackRecordStars}</span>
                    <span>Track Record: ${(opinion.track_record_score * 5).toFixed(1)}/5</span>
                </div>
            `;
            
            container.appendChild(item);
        });
    }

    async loadExpertTrackRecords() {
        try {
            const response = await fetch(`${this.apiUrl}/api/experts/track-records`);
            if (response.ok) {
                const trackRecords = await response.json();
                this.updateExpertTrackRecords(trackRecords);
            }
        } catch (error) {
            console.error('Error loading expert track records:', error);
        }
    }

    updateExpertTrackRecords(data) {
        const container = document.getElementById('expert-track-records');
        if (!container) return;

        container.innerHTML = `
            <div style="text-align: center; padding: 2rem;">
                <div style="font-size: 2rem; margin-bottom: 1rem;">📊</div>
                <div style="font-size: 1.25rem; font-weight: 600; margin-bottom: 0.5rem;">Expert Performance</div>
                <div style="font-size: 1rem; color: #64748b;">Track records and success rates</div>
            </div>
        `;
    }

    async refreshExpertAdvisor() {
        await this.loadExpertAdvisor();
        this.showNotification('Expert analysis refreshed', 'success');
    }

    // Enhanced Stock Analysis Methods
    async showStockAnalysis() {
        this.showView('stock-analysis-view');
        // Show empty state initially
        this.showStockAnalysisEmptyState();
    }

    showStockAnalysisEmptyState() {
        const content = document.getElementById('stock-analysis-content');
        if (content) {
            content.innerHTML = `
                <div class="intelligence-card full-width">
                    <div class="card-content">
                        <div class="empty-state">
                            <i class="fas fa-search fa-3x"></i>
                            <h3>Enhanced Stock Analysis</h3>
                            <p>Enter a stock symbol above to get comprehensive analysis including technical indicators, fundamental scores, and sentiment analysis.</p>
                        </div>
                    </div>
                </div>
            `;
        }
    }

    async analyzeStock(symbol) {
        if (!symbol) {
            this.showNotification('Please enter a stock symbol', 'error');
            return;
        }

        try {
            this.showLoading(`Analyzing ${symbol.toUpperCase()}...`);
            
            const response = await fetch(`${this.apiUrl}/api/stocks/${symbol.toUpperCase()}/analysis`);
            if (response.ok) {
                const analysisData = await response.json();
                this.displayStockAnalysis(symbol.toUpperCase(), analysisData);
            } else {
                throw new Error(`Analysis not available for ${symbol}`);
            }
            
        } catch (error) {
            console.error('Error analyzing stock:', error);
            this.showNotification(`Failed to analyze ${symbol}`, 'error');
        } finally {
            this.hideLoading();
        }
    }

    displayStockAnalysis(symbol, data) {
        // Update stock overview
        document.getElementById('analyzed-stock-name').textContent = `${symbol} Analysis`;
        document.getElementById('analyzed-stock-price').textContent = `$${data.current_price?.toFixed(2) || '--'}`;
        document.getElementById('stock-market').textContent = data.market || '--';
        document.getElementById('stock-sector').textContent = data.sector || '--';
        document.getElementById('stock-market-cap').textContent = data.fundamentals?.market_cap_millions ? 
            `$${data.fundamentals.market_cap_millions.toFixed(0)}M` : '--';
        document.getElementById('stock-currency').textContent = data.currency || 'USD';

        // Update technical indicators
        this.updateTechnicalIndicator('rsi', data.technical?.rsi, 0, 100);
        this.updateTechnicalIndicator('momentum', data.technical?.price_momentum, -20, 20);
        this.updateTechnicalIndicator('volatility', data.technical?.volatility, 0, 50);

        // Update fundamental scores
        this.updateScoreCircle('value-score-circle', 'value-score', data.fundamentals?.value_score);
        this.updateScoreCircle('growth-score-circle', 'growth-score', data.fundamentals?.growth_score);
        this.updateScoreCircle('quality-score-circle', 'quality-score', data.fundamentals?.quality_score);

        // Update fundamental metrics
        document.getElementById('pe-ratio').textContent = data.fundamentals?.pe_ratio?.toFixed(1) || '--';
        document.getElementById('dividend-yield').textContent = data.fundamentals?.dividend_yield ? 
            `${data.fundamentals.dividend_yield.toFixed(2)}%` : '--';

        // Update sentiment gauges
        this.updateSentimentGauge('analyst-rating-gauge', 'analyst-rating', data.sentiment?.analyst_rating, 1, 5);
        this.updateSentimentGauge('news-sentiment-gauge', 'news-sentiment', data.sentiment?.news_sentiment, -1, 1);
    }

    updateTechnicalIndicator(indicatorName, value, min, max) {
        const progressElement = document.getElementById(`${indicatorName}-bar`);
        const valueElement = document.getElementById(`${indicatorName}-value`);
        
        if (progressElement && value !== null && value !== undefined) {
            const percentage = ((value - min) / (max - min)) * 100;
            progressElement.style.width = `${Math.max(0, Math.min(100, percentage))}%`;
        }
        
        if (valueElement) {
            if (value !== null && value !== undefined) {
                valueElement.textContent = value.toFixed(1);
            } else {
                valueElement.textContent = '--';
            }
        }
    }

    updateScoreCircle(circleId, valueId, score) {
        const circleElement = document.getElementById(circleId);
        const valueElement = document.getElementById(valueId);
        
        if (valueElement) {
            valueElement.textContent = score ? Math.round(score) : '--';
        }
        
        if (circleElement && score) {
            circleElement.style.setProperty('--score', score);
        }
    }

    updateSentimentGauge(gaugeId, valueId, value, min, max) {
        const gaugeElement = document.getElementById(gaugeId);
        const valueElement = document.getElementById(valueId);
        
        if (valueElement) {
            if (value !== null && value !== undefined) {
                if (gaugeId.includes('analyst')) {
                    valueElement.textContent = `${value.toFixed(1)}/5`;
                } else {
                    valueElement.textContent = value > 0 ? 'Positive' : value < 0 ? 'Negative' : 'Neutral';
                }
            } else {
                valueElement.textContent = '--';
            }
        }
        
        if (gaugeElement && value !== null && value !== undefined) {
            const fillElement = gaugeElement.querySelector('.gauge-fill');
            if (fillElement) {
                const percentage = ((value - min) / (max - min)) * 100;
                const rotation = -90 + (percentage * 1.8); // -90 to +90 degrees
                fillElement.style.transform = `rotate(${Math.max(-90, Math.min(90, rotation))}deg)`;
            }
        }
    }

    // Utility Methods for Intelligence Dashboard
    formatSentiment(sentiment) {
        if (sentiment > 0.1) return 'Positive';
        if (sentiment < -0.1) return 'Negative';
        return 'Neutral';
    }

    getSentimentClass(sentiment) {
        if (sentiment > 0.1) return 'positive';
        if (sentiment < -0.1) return 'negative';
        return 'neutral';
    }

    formatRelativeTime(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffInHours = Math.floor((now - date) / (1000 * 60 * 60));
        
        if (diffInHours < 1) return 'Just now';
        if (diffInHours < 24) return `${diffInHours}h ago`;
        const diffInDays = Math.floor(diffInHours / 24);
        return `${diffInDays}d ago`;
    }

    showRecommendationDetails(recommendation) {
        // Create a detailed modal for the recommendation
        this.showNotification(`Detailed view for ${recommendation.symbol} recommendation`, 'info');
    }

    showRecommendationFilters() {
        this.showNotification('Recommendation filters coming soon', 'info');
    }

    exportRecommendations() {
        const data = {
            timestamp: new Date().toISOString(),
            recommendations: this.intelligenceData.portfolioRecommendations,
            portfolioHealth: this.intelligenceData.portfolioHealth
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `ai-recommendations-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        
        URL.revokeObjectURL(url);
        this.showNotification('Recommendations exported successfully', 'success');
    }

    // Portfolio Management View
    async showPortfolio() {
        this.showView('portfolio-view');
        this.updateBreadcrumb('Portfolio', 'Management');
        this.showLoading();
        
        try {
            // Get portfolio metrics and positions from trading API
            const [metrics, positions] = await Promise.all([
                this.fetchAPI('/api/trading/portfolio/metrics'),
                this.fetchAPI('/api/trading/portfolio/positions')
            ]);
            
            if (positions && positions.length > 0) {
                this.updateHoldingsTable(positions);
            }
            
            if (metrics) {
                this.updatePortfolioSummary({
                    totalValue: metrics.total_value,
                    dayChange: metrics.day_gain_loss,
                    totalReturn: metrics.total_gain_loss_percent,
                    positionCount: metrics.positions_count
                });
            } else {
                // Fallback to sample data for MVP
                this.updateHoldingsTable(this.getSampleHoldingsData());
                this.updatePortfolioSummary(this.getSamplePortfolioSummary());
            }
            
        } catch (error) {
            console.error('Error loading portfolio:', error);
            // Fallback to sample data for MVP
            this.updateHoldingsTable(this.getSampleHoldingsData());
            this.updatePortfolioSummary(this.getSamplePortfolioSummary());
            this.showNotification('Using sample data - Portfolio API not available', 'warning');
        } finally {
            this.hideLoading();
        }
    }

    // Watchlist View
    async showWatchlist() {
        this.showView('watchlist-view');
        this.updateBreadcrumb('Research', 'Watchlist');
        this.showLoading();
        
        try {
            // Try to get watchlist from localStorage or use sample data
            const savedWatchlist = JSON.parse(localStorage.getItem('watchlist') || '[]');
            if (savedWatchlist.length > 0) {
                // Get current prices for saved watchlist symbols
                const watchlistWithPrices = await this.getWatchlistWithPrices(savedWatchlist);
                this.updateWatchlistTable(watchlistWithPrices);
            } else {
                // Load sample watchlist data for MVP
                this.updateWatchlistTable(this.getSampleWatchlistData());
            }
            
        } catch (error) {
            console.error('Error loading watchlist:', error);
            // Load sample watchlist data for MVP
            this.updateWatchlistTable(this.getSampleWatchlistData());
        } finally {
            this.hideLoading();
        }
    }

    // Orders Management View
    async showOrders() {
        this.showView('orders-view');
        this.updateBreadcrumb('Trading', 'Orders');
        this.showLoading();
        
        try {
            const ordersData = await this.fetchAPI('/api/orders/history') || [];
            this.updateOrdersTable(ordersData);
            this.updateOrdersSummary(ordersData);
            
        } catch (error) {
            console.error('Error loading orders:', error);
            // Load sample orders data for MVP
            this.updateOrdersTable(this.getSampleOrdersData());
            this.updateOrdersSummary(this.getSampleOrdersData());
        } finally {
            this.hideLoading();
        }
    }

    // Stock Discovery View
    async showDiscover() {
        this.showView('discover-view');
        this.updateBreadcrumb('Research', 'Discovery');
        this.showLoading();
        
        try {
            // Use existing stock search API to get available stocks
            const stocksResponse = await this.fetchAPI('/api/stocks/search?q=');
            if (stocksResponse && stocksResponse.length > 0) {
                // Transform the response to match our discovery format
                const discoveryStocks = stocksResponse.slice(0, 10).map(stock => ({
                    symbol: stock.symbol,
                    name: stock.name,
                    price: stock.current_price,
                    change: stock.current_price * (stock.change_percent || 0) / 100,
                    changePercent: stock.change_percent || 0,
                    volume: Math.floor(Math.random() * 10000000), // Sample volume
                    score: Math.floor(Math.random() * 30) + 70 // Sample score 70-99
                }));
                this.updateDiscoveryTable(discoveryStocks, 'trending');
            } else {
                // Load sample discovery data for MVP
                this.updateDiscoveryTable(this.getSampleDiscoveryData(), 'trending');
            }
            
        } catch (error) {
            console.error('Error loading discovery data:', error);
            // Load sample discovery data for MVP
            this.updateDiscoveryTable(this.getSampleDiscoveryData(), 'trending');
        } finally {
            this.hideLoading();
        }
    }

    // Stock Screener View
    async showScreener() {
        this.showView('screener-view');
        this.updateBreadcrumb('Research', 'Screener');
        this.showLoading();
        
        try {
            // Initialize screener with all stocks
            const allStocks = await this.fetchAPI('/api/stocks/all') || [];
            this.updateScreenerResults(allStocks);
            
        } catch (error) {
            console.error('Error loading screener data:', error);
            // Load sample screener data for MVP
            this.updateScreenerResults(this.getSampleScreenerData());
        } finally {
            this.hideLoading();
        }
    }

    // Market News View
    async showMarket() {
        this.showView('market-view');
        this.updateBreadcrumb('Research', 'Market News');
        this.showLoading();
        
        try {
            const marketNews = await this.fetchAPI('/api/news/market/global') || {};
            this.updateNewsContent(marketNews);
            
        } catch (error) {
            console.error('Error loading news:', error);
            // Load sample news data for MVP
            this.updateNewsContent(this.getSampleNewsData());
        } finally {
            this.hideLoading();
        }
    }

    // Performance Analysis View
    async showPerformance() {
        this.showView('performance-view');
        this.updateBreadcrumb('Analysis', 'Performance');
        this.showLoading();
        
        try {
            const performanceData = await this.fetchAPI('/api/portfolio/performance') || {};
            this.updatePerformanceMetrics(performanceData);
            this.renderPerformanceChart(performanceData);
            
        } catch (error) {
            console.error('Error loading performance data:', error);
            // Load sample performance data for MVP
            this.updatePerformanceMetrics(this.getSamplePerformanceData());
            this.renderPerformanceChart(this.getSamplePerformanceData());
        } finally {
            this.hideLoading();
        }
    }

    // Risk Analysis View
    async showRiskAnalysis() {
        this.showView('risk-view');
        this.updateBreadcrumb('Analysis', 'Risk');
        this.showLoading();
        
        try {
            const riskData = await this.fetchAPI('/api/portfolio/risk-analysis') || {};
            this.updateRiskScore(riskData);
            this.updateRiskBreakdown(riskData);
            this.updateVaRMetrics(riskData);
            
        } catch (error) {
            console.error('Error loading risk data:', error);
            // Load sample risk data for MVP
            this.updateRiskScore(this.getSampleRiskData());
            this.updateRiskBreakdown(this.getSampleRiskData());
            this.updateVaRMetrics(this.getSampleRiskData());
        } finally {
            this.hideLoading();
        }
    }

    // Reports View
    async showReports() {
        this.showView('reports-view');
        this.updateBreadcrumb('Analysis', 'Reports');
        this.showLoading();
        
        try {
            const reportsData = await this.fetchAPI('/api/reports/history') || [];
            this.updateReportsTable(reportsData);
            
        } catch (error) {
            console.error('Error loading reports:', error);
            // Load sample reports data for MVP
            this.updateReportsTable(this.getSampleReportsData());
        } finally {
            this.hideLoading();
        }
    }

    // Settings View
    showSettings() {
        this.showView('settings-view');
        this.updateBreadcrumb('Account', 'Settings');
        this.loadUserSettings();
    }
    
    // UI Update Methods for New Views
    
    updatePortfolioSummary(data) {
        document.getElementById('portfolio-total-value').textContent = 
            this.formatCurrency(data?.totalValue || 0);
        document.getElementById('portfolio-day-change').textContent = 
            this.formatCurrency(data?.dayChange || 0);
        document.getElementById('portfolio-total-return').textContent = 
            this.formatPercentage(data?.totalReturn || 0);
        document.getElementById('portfolio-position-count').textContent = 
            data?.positionCount || 0;
        document.getElementById('portfolio-timestamp').textContent = 
            `Last updated: ${new Date().toLocaleTimeString()}`;
    }

    updateHoldingsTable(holdings) {
        const tbody = document.getElementById('holdings-tbody');
        if (!tbody) return;
        
        // Calculate total portfolio value for percentage calculation
        const totalValue = holdings.reduce((sum, h) => sum + (h.market_value || h.marketValue || 0), 0);
        
        tbody.innerHTML = holdings.map(holding => {
            // Handle both API format and sample data format
            const symbol = holding.symbol;
            const name = holding.name || holding.symbol;
            const shares = holding.shares;
            const avgCost = holding.avg_price || holding.avgCost;
            const currentPrice = holding.current_price || holding.currentPrice;
            const marketValue = holding.market_value || holding.marketValue;
            const gainLoss = holding.gain_loss || holding.unrealizedPL || (marketValue - (shares * avgCost));
            const portfolioPercent = totalValue > 0 ? (marketValue / totalValue * 100) : 0;
            
            return `
            <tr>
                <td><strong>${symbol}</strong></td>
                <td>${name}</td>
                <td>${shares.toLocaleString()}</td>
                <td>${this.formatCurrency(avgCost)}</td>
                <td>${this.formatCurrency(currentPrice)}</td>
                <td>${this.formatCurrency(marketValue)}</td>
                <td class="${gainLoss >= 0 ? 'positive' : 'negative'}">
                    ${this.formatCurrency(gainLoss)}
                </td>
                <td>${this.formatPercentage(portfolioPercent)}</td>
                <td>
                    <button class="btn btn-sm btn-outline" onclick="app.showStockDetails('${symbol}')">
                        <i class="fas fa-chart-line"></i>
                    </button>
                    <button class="btn btn-sm btn-primary" onclick="app.addToWatchlist('${symbol}')">
                        <i class="fas fa-eye"></i>
                    </button>
                </td>
            </tr>
        `;
        }).join('');
    }

    updateWatchlistTable(watchlist) {
        const tbody = document.getElementById('watchlist-tbody');
        if (!tbody) return;
        
        tbody.innerHTML = watchlist.map(stock => `
            <tr>
                <td><strong>${stock.symbol}</strong></td>
                <td>${stock.name || stock.symbol}</td>
                <td>${this.formatCurrency(stock.price)}</td>
                <td class="${stock.change >= 0 ? 'positive' : 'negative'}">
                    ${this.formatCurrency(stock.change)}
                </td>
                <td class="${stock.changePercent >= 0 ? 'positive' : 'negative'}">
                    ${this.formatPercentage(stock.changePercent)}
                </td>
                <td>${stock.volume?.toLocaleString() || '--'}</td>
                <td>${stock.marketCap ? this.formatLargeNumber(stock.marketCap) : '--'}</td>
                <td>${stock.peRatio || '--'}</td>
                <td>
                    <button class="btn btn-sm btn-outline" onclick="app.addToPortfolio('${stock.symbol}')">
                        <i class="fas fa-plus"></i>
                    </button>
                    <button class="btn btn-sm btn-outline" onclick="app.removeFromWatchlist('${stock.symbol}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    }

    updateOrdersTable(orders) {
        const tbody = document.getElementById('orders-tbody');
        if (!tbody) return;
        
        tbody.innerHTML = orders.map(order => `
            <tr>
                <td>${order.orderId}</td>
                <td><strong>${order.symbol}</strong></td>
                <td>${order.type}</td>
                <td class="${order.side === 'BUY' ? 'positive' : 'negative'}">${order.side}</td>
                <td>${order.quantity.toLocaleString()}</td>
                <td>${this.formatCurrency(order.price)}</td>
                <td><span class="badge ${this.getOrderStatusClass(order.status)}">${order.status}</span></td>
                <td>${new Date(order.timestamp).toLocaleString()}</td>
                <td>
                    ${order.status === 'PENDING' ? 
                        `<button class="btn btn-sm btn-outline" onclick="app.cancelOrder('${order.orderId}')">Cancel</button>` : 
                        '--'
                    }
                </td>
            </tr>
        `).join('');
    }

    updateOrdersSummary(orders) {
        const pending = orders.filter(o => o.status === 'PENDING').length;
        const filled = orders.filter(o => o.status === 'FILLED').length;
        const cancelled = orders.filter(o => o.status === 'CANCELLED').length;
        
        document.getElementById('pending-orders-count').textContent = pending;
        document.getElementById('filled-orders-count').textContent = filled;
        document.getElementById('cancelled-orders-count').textContent = cancelled;
    }

    updateDiscoveryTable(stocks, category) {
        const tbody = document.getElementById('discovery-tbody');
        if (!tbody) return;
        
        tbody.innerHTML = stocks.map(stock => `
            <tr>
                <td><strong>${stock.symbol}</strong></td>
                <td>${stock.name || stock.symbol}</td>
                <td>${this.formatCurrency(stock.price)}</td>
                <td class="${stock.change >= 0 ? 'positive' : 'negative'}">
                    ${this.formatCurrency(stock.change)}
                </td>
                <td class="${stock.changePercent >= 0 ? 'positive' : 'negative'}">
                    ${this.formatPercentage(stock.changePercent)}
                </td>
                <td>${stock.volume?.toLocaleString() || '--'}</td>
                <td><span class="score-badge">${stock.score || '--'}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline" onclick="app.addToWatchlist('${stock.symbol}')">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-outline" onclick="app.showStockAnalysis('${stock.symbol}')">
                        <i class="fas fa-chart-line"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    }

    updateScreenerResults(stocks) {
        const tbody = document.getElementById('screener-tbody');
        const resultCount = document.getElementById('screener-results-count');
        if (!tbody) return;
        
        resultCount.textContent = `${stocks.length} stocks found`;
        
        tbody.innerHTML = stocks.map(stock => `
            <tr>
                <td><strong>${stock.symbol}</strong></td>
                <td>${stock.name || stock.symbol}</td>
                <td>${this.formatCurrency(stock.price)}</td>
                <td>${stock.marketCap ? this.formatLargeNumber(stock.marketCap) : '--'}</td>
                <td>${stock.peRatio || '--'}</td>
                <td>${stock.volume?.toLocaleString() || '--'}</td>
                <td>${stock.sector || '--'}</td>
                <td>
                    <button class="btn btn-sm btn-outline" onclick="app.addToWatchlist('${stock.symbol}')">
                        <i class="fas fa-eye"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    }

    updateNewsContent(newsData) {
        const container = document.getElementById('news-feed-container');
        const timestamp = document.getElementById('news-timestamp');
        if (!container) return;
        
        timestamp.textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
        
        const articles = newsData.articles || this.getSampleNewsData().articles;
        container.innerHTML = articles.map(article => `
            <div class="news-item">
                <div class="news-header">
                    <h4 class="news-title">${article.title}</h4>
                    <span class="news-time">${new Date(article.publishedAt).toLocaleString()}</span>
                </div>
                <p class="news-summary">${article.description || article.summary}</p>
                <div class="news-meta">
                    <span class="news-source">${article.source}</span>
                    <span class="news-sentiment ${article.sentiment === 'positive' ? 'positive' : article.sentiment === 'negative' ? 'negative' : 'neutral'}">
                        ${article.sentiment || 'neutral'}
                    </span>
                </div>
            </div>
        `).join('');
    }

    updatePerformanceMetrics(data) {
        document.getElementById('total-return-metric').textContent = 
            this.formatPercentage(data?.totalReturn || 0);
        document.getElementById('annualized-return-metric').textContent = 
            this.formatPercentage(data?.annualizedReturn || 0);
        document.getElementById('sharpe-ratio-metric').textContent = 
            (data?.sharpeRatio || 0).toFixed(2);
        document.getElementById('max-drawdown-metric').textContent = 
            this.formatPercentage(data?.maxDrawdown || 0);
    }

    updateRiskScore(data) {
        const scoreElement = document.getElementById('overall-risk-score')?.querySelector('.score-value');
        const levelElement = document.getElementById('risk-level')?.querySelector('.risk-level-text');
        
        if (scoreElement) scoreElement.textContent = data?.riskScore || '--';
        if (levelElement) levelElement.textContent = data?.riskLevel || '--';
    }

    updateRiskBreakdown(data) {
        const risks = ['concentration', 'volatility', 'sector', 'correlation'];
        risks.forEach(risk => {
            const progressEl = document.getElementById(`${risk}-risk`);
            const valueEl = document.getElementById(`${risk}-risk-value`);
            const riskValue = data?.risks?.[risk] || 0;
            
            if (progressEl) progressEl.style.width = `${riskValue}%`;
            if (valueEl) valueEl.textContent = `${riskValue}%`;
        });
    }

    updateVaRMetrics(data) {
        document.getElementById('var-1day').textContent = 
            this.formatCurrency(data?.var1Day || 0);
        document.getElementById('var-1week').textContent = 
            this.formatCurrency(data?.var1Week || 0);
        document.getElementById('var-1month').textContent = 
            this.formatCurrency(data?.var1Month || 0);
    }

    updateReportsTable(reports) {
        const tbody = document.getElementById('reports-tbody');
        if (!tbody) return;
        
        tbody.innerHTML = reports.map(report => `
            <tr>
                <td>${report.name}</td>
                <td>${report.type}</td>
                <td>${new Date(report.generated).toLocaleString()}</td>
                <td><span class="badge ${report.status === 'completed' ? 'success' : 'pending'}">${report.status}</span></td>
                <td>${report.size}</td>
                <td>
                    <button class="btn btn-sm btn-outline" onclick="app.downloadReport('${report.id}')">
                        <i class="fas fa-download"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    }

    loadUserSettings() {
        // Load current settings values
        const userName = document.getElementById('user-name');
        const userEmail = document.getElementById('user-email');
        
        // Set default values or load from localStorage
        if (userName) userName.value = localStorage.getItem('userName') || 'John Doe';
        if (userEmail) userEmail.value = localStorage.getItem('userEmail') || 'john.doe@example.com';
    }

    // Helper Methods
    
    async getWatchlistWithPrices(symbols) {
        // Get current prices for watchlist symbols
        const watchlistData = [];
        for (const symbol of symbols.slice(0, 10)) { // Limit to 10 for performance
            try {
                const stockData = await this.fetchAPI(`/api/stocks/search?q=${symbol}`);
                if (stockData && stockData.length > 0) {
                    const stock = stockData[0];
                    watchlistData.push({
                        symbol: stock.symbol,
                        name: stock.name,
                        price: stock.current_price,
                        change: stock.current_price * (stock.change_percent || 0) / 100,
                        changePercent: stock.change_percent || 0,
                        volume: Math.floor(Math.random() * 10000000),
                        marketCap: Math.floor(Math.random() * 1000000),
                        peRatio: (Math.random() * 50 + 10).toFixed(1)
                    });
                }
            } catch (error) {
                console.error(`Error loading data for ${symbol}:`, error);
            }
        }
        return watchlistData.length > 0 ? watchlistData : this.getSampleWatchlistData();
    }

    // Sample Data Methods for MVP (fallback when APIs are not available)
    
    getSamplePortfolioSummary() {
        return {
            totalValue: 125750.50,
            dayChange: 2845.30,
            totalReturn: 15.6,
            positionCount: 8
        };
    }

    getSampleHoldingsData() {
        return [
            {
                symbol: 'AAPL',
                name: 'Apple Inc.',
                shares: 100,
                avgCost: 150.25,
                currentPrice: 175.20,
                marketValue: 17520.00,
                unrealizedPL: 2495.00,
                portfolioPercent: 13.9
            },
            {
                symbol: 'MSFT',
                name: 'Microsoft Corporation',
                shares: 50,
                avgCost: 320.80,
                currentPrice: 378.85,
                marketValue: 18942.50,
                unrealizedPL: 2902.50,
                portfolioPercent: 15.1
            },
            {
                symbol: 'GOOGL',
                name: 'Alphabet Inc.',
                shares: 75,
                avgCost: 118.40,
                currentPrice: 125.30,
                marketValue: 9397.50,
                unrealizedPL: 517.50,
                portfolioPercent: 7.5
            },
            {
                symbol: 'TSLA',
                name: 'Tesla Inc.',
                shares: 25,
                avgCost: 215.60,
                currentPrice: 245.60,
                marketValue: 6140.00,
                unrealizedPL: 750.00,
                portfolioPercent: 4.9
            }
        ];
    }
    
    getSampleWatchlistData() {
        return [
            {symbol: 'AAPL', name: 'Apple Inc.', price: 175.20, change: 2.50, changePercent: 1.45, volume: 45623000, marketCap: 2750000, peRatio: 28.5},
            {symbol: 'MSFT', name: 'Microsoft Corporation', price: 378.85, change: -1.20, changePercent: -0.32, volume: 22456000, marketCap: 2810000, peRatio: 32.1},
            {symbol: 'GOOGL', name: 'Alphabet Inc.', price: 125.30, change: 0.85, changePercent: 0.68, volume: 25789000, marketCap: 1580000, peRatio: 25.2},
            {symbol: 'TSLA', name: 'Tesla Inc.', price: 245.60, change: 8.90, changePercent: 3.76, volume: 98754000, marketCap: 780000, peRatio: 58.7},
            {symbol: 'NVDA', name: 'NVIDIA Corporation', price: 820.45, change: 15.30, changePercent: 1.90, volume: 42123000, marketCap: 2020000, peRatio: 65.8}
        ];
    }

    getSampleOrdersData() {
        return [
            {orderId: 'ORD001', symbol: 'AAPL', type: 'LIMIT', side: 'BUY', quantity: 100, price: 175.00, status: 'FILLED', timestamp: new Date(Date.now() - 3600000)},
            {orderId: 'ORD002', symbol: 'MSFT', type: 'MARKET', side: 'SELL', quantity: 50, price: 378.85, status: 'PENDING', timestamp: new Date(Date.now() - 1800000)},
            {orderId: 'ORD003', symbol: 'GOOGL', type: 'STOP', side: 'BUY', quantity: 25, price: 125.30, status: 'CANCELLED', timestamp: new Date(Date.now() - 7200000)}
        ];
    }

    getSampleDiscoveryData() {
        return [
            {symbol: 'AI', name: 'C3.ai Inc.', price: 28.50, change: 2.10, changePercent: 7.96, volume: 5623000, score: 85},
            {symbol: 'PLTR', name: 'Palantir Technologies', price: 18.75, change: 1.45, changePercent: 8.38, volume: 8234000, score: 82},
            {symbol: 'SNOW', name: 'Snowflake Inc.', price: 195.30, change: 12.20, changePercent: 6.66, volume: 3456000, score: 79},
            {symbol: 'CRM', name: 'Salesforce Inc.', price: 245.80, change: 8.90, changePercent: 3.76, volume: 2789000, score: 77}
        ];
    }

    getSampleScreenerData() {
        return [
            {symbol: 'AAPL', name: 'Apple Inc.', price: 175.20, marketCap: 2750000, peRatio: 28.5, volume: 45623000, sector: 'Technology'},
            {symbol: 'MSFT', name: 'Microsoft Corporation', price: 378.85, marketCap: 2810000, peRatio: 32.1, volume: 22456000, sector: 'Technology'},
            {symbol: 'JNJ', name: 'Johnson & Johnson', price: 158.40, marketCap: 420000, peRatio: 15.8, volume: 8234000, sector: 'Healthcare'},
            {symbol: 'JPM', name: 'JPMorgan Chase', price: 145.30, marketCap: 425000, peRatio: 12.4, volume: 12456000, sector: 'Financial'}
        ];
    }

    getSampleNewsData() {
        return {
            articles: [
                {
                    title: 'Technology Stocks Rally on AI Optimism',
                    description: 'Major tech companies see gains as artificial intelligence investment continues to drive market sentiment.',
                    source: 'MarketWatch',
                    publishedAt: new Date(Date.now() - 1800000),
                    sentiment: 'positive'
                },
                {
                    title: 'Federal Reserve Maintains Interest Rates',
                    description: 'The Fed keeps rates unchanged, citing economic stability and controlled inflation.',
                    source: 'Reuters',
                    publishedAt: new Date(Date.now() - 3600000),
                    sentiment: 'neutral'
                },
                {
                    title: 'Energy Sector Faces Headwinds',
                    description: 'Oil prices decline amid global economic concerns and increased renewable energy adoption.',
                    source: 'Bloomberg',
                    publishedAt: new Date(Date.now() - 5400000),
                    sentiment: 'negative'
                }
            ]
        };
    }

    getSamplePerformanceData() {
        return {
            totalReturn: 15.6,
            annualizedReturn: 12.3,
            sharpeRatio: 1.45,
            maxDrawdown: -8.2
        };
    }

    getSampleRiskData() {
        return {
            riskScore: 65,
            riskLevel: 'Moderate',
            risks: {
                concentration: 35,
                volatility: 45,
                sector: 25,
                correlation: 55
            },
            var1Day: -2500,
            var1Week: -8900,
            var1Month: -18500
        };
    }

    getSampleReportsData() {
        return [
            {id: 'RPT001', name: 'Monthly Performance Report', type: 'Performance', generated: new Date(Date.now() - 86400000), status: 'completed', size: '2.5 MB'},
            {id: 'RPT002', name: 'Risk Assessment Report', type: 'Risk', generated: new Date(Date.now() - 172800000), status: 'completed', size: '1.8 MB'},
            {id: 'RPT003', name: 'Tax Summary Report', type: 'Tax', generated: new Date(Date.now() - 259200000), status: 'pending', size: '--'}
        ];
    }

    // Utility Methods
    
    getOrderStatusClass(status) {
        switch(status) {
            case 'FILLED': return 'success';
            case 'PENDING': return 'warning';
            case 'CANCELLED': return 'danger';
            default: return 'neutral';
        }
    }

    formatLargeNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        }
        if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }

    renderPerformanceChart(data) {
        // Placeholder for performance chart rendering
        const container = document.getElementById('performance-chart-container');
        if (container) {
            container.innerHTML = '<div class="chart-placeholder">Performance chart will be rendered here</div>';
        }
    }

    // Action Methods
    
    async addToPortfolio(symbol) {
        this.showNotification(`Adding ${symbol} to portfolio...`, 'info');
        
        try {
            // For MVP, we'll use the existing add position modal
            const addPositionModal = document.getElementById('add-position-modal');
            if (addPositionModal) {
                document.getElementById('position-symbol').value = symbol;
                addPositionModal.style.display = 'flex';
            } else {
                this.showNotification(`${symbol} position setup - use Add Position button`, 'info');
            }
        } catch (error) {
            console.error('Error adding to portfolio:', error);
            this.showNotification('Failed to add to portfolio', 'error');
        }
    }

    async addToWatchlist(symbol) {
        this.showNotification(`Adding ${symbol} to watchlist...`, 'info');
        
        try {
            // Get current watchlist from localStorage
            const watchlist = JSON.parse(localStorage.getItem('watchlist') || '[]');
            
            if (!watchlist.includes(symbol)) {
                watchlist.push(symbol);
                localStorage.setItem('watchlist', JSON.stringify(watchlist));
                this.showNotification(`${symbol} added to watchlist`, 'success');
                
                // Refresh watchlist if currently viewing
                const currentView = document.querySelector('.view.active');
                if (currentView && currentView.id === 'watchlist-view') {
                    this.showWatchlist();
                }
            } else {
                this.showNotification(`${symbol} is already in watchlist`, 'warning');
            }
        } catch (error) {
            console.error('Error adding to watchlist:', error);
            this.showNotification('Failed to add to watchlist', 'error');
        }
    }

    async removeFromWatchlist(symbol) {
        this.showNotification(`Removing ${symbol} from watchlist...`, 'info');
        
        try {
            // Get current watchlist from localStorage
            const watchlist = JSON.parse(localStorage.getItem('watchlist') || '[]');
            const updatedWatchlist = watchlist.filter(s => s !== symbol);
            
            localStorage.setItem('watchlist', JSON.stringify(updatedWatchlist));
            this.showNotification(`${symbol} removed from watchlist`, 'success');
            
            // Refresh watchlist if currently viewing
            const currentView = document.querySelector('.view.active');
            if (currentView && currentView.id === 'watchlist-view') {
                this.showWatchlist();
            }
        } catch (error) {
            console.error('Error removing from watchlist:', error);
            this.showNotification('Failed to remove from watchlist', 'error');
        }
    }

    cancelOrder(orderId) {
        this.showNotification(`Cancelling order ${orderId}...`, 'info');
        // For MVP, simulate order cancellation
        setTimeout(() => {
            this.showNotification(`Order ${orderId} cancelled successfully`, 'success');
            this.showOrders(); // Refresh orders view
        }, 1000);
    }

    downloadReport(reportId) {
        this.showNotification(`Downloading report ${reportId}...`, 'info');
        // For MVP, simulate report download
        setTimeout(() => {
            this.showNotification(`Report ${reportId} download started`, 'success');
        }, 1000);
    }

    async showStockDetails(symbol) {
        this.showNotification(`Loading details for ${symbol}...`, 'info');
        
        try {
            // Navigate to stock analysis view
            await this.showStockAnalysis();
            // Set the symbol in analysis search
            const searchInput = document.getElementById('analysis-stock-search');
            if (searchInput) {
                searchInput.value = symbol;
                await this.analyzeStock(); // Trigger analysis
            }
        } catch (error) {
            console.error('Error loading stock details:', error);
            this.showNotification('Failed to load stock details', 'error');
        }
    }

    async showStockAnalysis(symbol) {
        // Navigate to the existing stock analysis view
        this.showStockAnalysisView();
        
        if (symbol) {
            this.showNotification(`Loading analysis for ${symbol}...`, 'info');
            // Set the symbol and trigger analysis
            const searchInput = document.getElementById('analysis-stock-search');
            if (searchInput) {
                searchInput.value = symbol;
                await this.analyzeStock();
            }
        }
    }
    
    showPositionFilters() { this.showNotification('Position filters coming soon', 'info'); }
    showSortOptions() { this.showNotification('Advanced sort options coming soon', 'info'); }
}

// Additional CSS for recommendations and badges
const additionalStyles = `
<style>
.recommendation-badge.buy {
    background: #dcfce7;
    color: #15803d;
}
.recommendation-badge.sell {
    background: #fee2e2;
    color: #dc2626;
}
.recommendation-badge.hold {
    background: #fef3c7;
    color: #d97706;
}
.badge.success {
    background: #dcfce7;
    color: #15803d;
}
.badge.danger {
    background: #fee2e2;
    color: #dc2626;
}
@keyframes slideIn {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}
.suggestion-item:hover {
    background: #f8fafc;
}
</style>
`;

// Insert additional styles
document.head.insertAdjacentHTML('beforeend', additionalStyles);

// Initialize application - force reinitialization to ensure it works
let app;
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing Professional Investment App...');
    
    // Clear any existing app instance
    if (window.app) {
        console.log('Clearing existing app instance...');
        delete window.app;
    }
    
    // Create new app instance
    app = new ProfessionalInvestmentApp();
    window.app = app; // Make app globally available
    
    // Debug log
    console.log('Professional Investment App initialized:', app);
    
    // Test that the app is working by calling a method
    if (app && typeof app.init === 'function') {
        console.log('App initialization successful - ready for user interactions!');
    } else {
        console.error('App initialization failed!');
    }
});

// Global functions for onclick handlers - these need to be available immediately
window.buyStock = function(symbol) {
    if (window.app) {
        window.app.buyStock(symbol);
    } else {
        console.log('App not ready, queuing action:', 'buy', symbol);
    }
};

window.sellStock = function(symbol) {
    if (window.app) {
        window.app.sellStock(symbol);
    } else {
        console.log('App not ready, queuing action:', 'sell', symbol);
    }
};

window.viewAnalysis = function(symbol) {
    if (window.app) {
        window.app.viewAnalysis(symbol);
    } else {
        console.log('App not ready, queuing action:', 'analyze', symbol);
    }
};

// Duplicate initialization removed - using single initialization above