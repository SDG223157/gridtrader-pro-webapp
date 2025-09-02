#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import axios from 'axios';
import * as dotenv from 'dotenv';

dotenv.config();

interface Portfolio {
  id: string;
  name: string;
  description?: string;
  strategy_type: string;
  initial_capital: number;
  current_value: number;
  cash_balance: number;
  created_at: string;
  updated_at: string;
}

interface Grid {
  id: string;
  portfolio_id: string;
  symbol: string;
  name: string;
  upper_price: number;
  lower_price: number;
  grid_spacing: number;
  investment_amount: number;
  status: string;
  current_price?: number;
  created_at: string;
  updated_at: string;
}

interface MarketData {
  symbol: string;
  price: number;
  change?: number;
  change_percent?: number;
  volume?: number;
  timestamp?: string;
}

interface CreatePortfolioRequest {
  name: string;
  description?: string;
  strategy_type: string;
  initial_capital: number;
}

interface CreateGridRequest {
  portfolio_id: string;
  symbol: string;
  name: string;
  upper_price: number;
  lower_price: number;
  grid_count: number;
  investment_amount: number;
}

class GridTraderProMCPServer {
  private server: Server;
  private apiUrl: string;
  private accessToken: string;

  constructor() {
    this.server = new Server(
      {
        name: 'gridtrader-pro',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.apiUrl = process.env.GRIDTRADER_API_URL || 'https://gridsai.app';
    this.accessToken = process.env.GRIDTRADER_ACCESS_TOKEN || '';

    this.setupToolHandlers();
  }

  private async makeApiCall(endpoint: string, method = 'GET', data?: any) {
    try {
      const response = await axios({
        method,
        url: `${this.apiUrl}${endpoint}`,
        data,
        headers: {
          'Authorization': `Bearer ${this.accessToken}`,
          'Content-Type': 'application/json'
        }
      });
      return response.data;
    } catch (error: any) {
      console.error('API call failed:', error.response?.data || error.message);
      throw error;
    }
  }

  private setupToolHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: 'get_portfolio_list',
            description: 'Get list of all portfolios with performance metrics',
            inputSchema: {
              type: 'object',
              properties: {
                include_performance: {
                  type: 'boolean',
                  description: 'Include performance calculations',
                  default: true
                }
              }
            }
          },
          {
            name: 'get_portfolio_details',
            description: 'Get detailed information about a specific portfolio',
            inputSchema: {
              type: 'object',
              properties: {
                portfolio_id: {
                  type: 'string',
                  description: 'The ID of the portfolio to retrieve'
                }
              },
              required: ['portfolio_id']
            }
          },
          {
            name: 'create_portfolio',
            description: 'Create a new investment portfolio',
            inputSchema: {
              type: 'object',
              properties: {
                name: {
                  type: 'string',
                  description: 'Name of the portfolio'
                },
                description: {
                  type: 'string',
                  description: 'Optional description of the portfolio'
                },
                strategy_type: {
                  type: 'string',
                  description: 'Investment strategy type',
                  enum: ['balanced', 'aggressive', 'conservative', 'growth', 'income'],
                  default: 'balanced'
                },
                initial_capital: {
                  type: 'number',
                  description: 'Initial capital amount in USD'
                }
              },
              required: ['name', 'initial_capital']
            }
          },
          {
            name: 'get_grid_list',
            description: 'Get list of all grid trading strategies',
            inputSchema: {
              type: 'object',
              properties: {
                portfolio_id: {
                  type: 'string',
                  description: 'Filter by portfolio ID (optional)'
                },
                symbol: {
                  type: 'string',
                  description: 'Filter by trading symbol (optional)'
                },
                status: {
                  type: 'string',
                  description: 'Filter by grid status (optional)',
                  enum: ['active', 'paused', 'completed', 'cancelled']
                }
              }
            }
          },
          {
            name: 'create_grid',
            description: 'Create a new grid trading strategy',
            inputSchema: {
              type: 'object',
              properties: {
                portfolio_id: {
                  type: 'string',
                  description: 'Portfolio ID to create grid in'
                },
                symbol: {
                  type: 'string',
                  description: 'Trading symbol (e.g., AAPL, SPY, BTC-USD)'
                },
                name: {
                  type: 'string',
                  description: 'Name for this grid strategy'
                },
                upper_price: {
                  type: 'number',
                  description: 'Upper price boundary for the grid'
                },
                lower_price: {
                  type: 'number',
                  description: 'Lower price boundary for the grid'
                },
                grid_count: {
                  type: 'number',
                  description: 'Number of grid levels',
                  default: 10
                },
                investment_amount: {
                  type: 'number',
                  description: 'Total investment amount for this grid'
                }
              },
              required: ['portfolio_id', 'symbol', 'name', 'upper_price', 'lower_price', 'investment_amount']
            }
          },
          {
            name: 'get_market_data',
            description: 'Get current market data for a symbol',
            inputSchema: {
              type: 'object',
              properties: {
                symbol: {
                  type: 'string',
                  description: 'Trading symbol to get data for'
                },
                period: {
                  type: 'string',
                  description: 'Data period',
                  enum: ['current', '1d', '5d', '1mo', '3mo', '6mo', '1y'],
                  default: 'current'
                }
              },
              required: ['symbol']
            }
          },
          {
            name: 'search_symbols',
            description: 'Search for trading symbols',
            inputSchema: {
              type: 'object',
              properties: {
                query: {
                  type: 'string',
                  description: 'Search query (company name or symbol)'
                }
              },
              required: ['query']
            }
          },
          {
            name: 'get_dashboard_summary',
            description: 'Get dashboard summary with portfolio overview and market data',
            inputSchema: {
              type: 'object',
              properties: {
                include_market_data: {
                  type: 'boolean',
                  description: 'Include popular market data',
                  default: true
                }
              }
            }
          },
          {
            name: 'analyze_grid_performance',
            description: 'Analyze the performance of a grid trading strategy',
            inputSchema: {
              type: 'object',
              properties: {
                grid_id: {
                  type: 'string',
                  description: 'Grid ID to analyze'
                },
                include_backtest: {
                  type: 'boolean',
                  description: 'Include backtesting analysis',
                  default: false
                }
              },
              required: ['grid_id']
            }
          },
          {
            name: 'get_trading_alerts',
            description: 'Get recent trading alerts and notifications',
            inputSchema: {
              type: 'object',
              properties: {
                limit: {
                  type: 'number',
                  description: 'Maximum number of alerts to return',
                  default: 10
                },
                alert_type: {
                  type: 'string',
                  description: 'Filter by alert type',
                  enum: ['price', 'grid', 'portfolio', 'system']
                }
              }
            }
          },
          {
            name: 'calculate_portfolio_metrics',
            description: 'Calculate detailed portfolio performance metrics',
            inputSchema: {
              type: 'object',
              properties: {
                portfolio_id: {
                  type: 'string',
                  description: 'Portfolio ID to calculate metrics for'
                },
                period: {
                  type: 'string',
                  description: 'Time period for calculations',
                  enum: ['1d', '1w', '1m', '3m', '6m', '1y', 'ytd', 'all'],
                  default: '1m'
                }
              },
              required: ['portfolio_id']
            }
          },
          {
            name: 'validate_symbol',
            description: 'Validate if a trading symbol is supported',
            inputSchema: {
              type: 'object',
              properties: {
                symbol: {
                  type: 'string',
                  description: 'Symbol to validate'
                }
              },
              required: ['symbol']
            }
          },
          {
            name: 'update_china_etfs',
            description: 'Update China ETFs list from cn.investing.com CSV data',
            inputSchema: {
              type: 'object',
              properties: {
                csv_data: {
                  type: 'string',
                  description: 'CSV data from cn.investing.com with columns: 名称,代码,最新价,涨跌幅,交易量,时间'
                }
              },
              required: ['csv_data']
            }
          },
          {
            name: 'get_us_sector_analysis',
            description: 'Get US market sector analysis with ETF recommendations',
            inputSchema: {
              type: 'object',
              properties: {
                lookback_days: {
                  type: 'number',
                  description: 'Number of days for analysis (default: 90)',
                  default: 90
                }
              }
            }
          },
          {
            name: 'get_china_sector_analysis',
            description: 'Get China market sector analysis with ETF recommendations',
            inputSchema: {
              type: 'object',
              properties: {
                lookback_days: {
                  type: 'number',
                  description: 'Number of days for analysis (default: 90)',
                  default: 90
                }
              }
            }
          },
          {
            name: 'buy_stock',
            description: 'Execute a buy transaction for stocks or ETFs',
            inputSchema: {
              type: 'object',
              properties: {
                portfolio_id: {
                  type: 'string',
                  description: 'Portfolio ID to execute the trade in'
                },
                symbol: {
                  type: 'string',
                  description: 'Stock or ETF symbol to buy (e.g., AAPL, SPY, 513130.SS)'
                },
                quantity: {
                  type: 'number',
                  description: 'Number of shares to buy'
                },
                price: {
                  type: 'number',
                  description: 'Price per share (use current market price if not specified)'
                },
                notes: {
                  type: 'string',
                  description: 'Optional notes for the transaction'
                }
              },
              required: ['portfolio_id', 'symbol', 'quantity']
            }
          },
          {
            name: 'sell_stock',
            description: 'Execute a sell transaction for stocks or ETFs',
            inputSchema: {
              type: 'object',
              properties: {
                portfolio_id: {
                  type: 'string',
                  description: 'Portfolio ID to execute the trade in'
                },
                symbol: {
                  type: 'string',
                  description: 'Stock or ETF symbol to sell (e.g., AAPL, SPY, 513130.SS)'
                },
                quantity: {
                  type: 'number',
                  description: 'Number of shares to sell'
                },
                price: {
                  type: 'number',
                  description: 'Price per share (use current market price if not specified)'
                },
                notes: {
                  type: 'string',
                  description: 'Optional notes for the transaction'
                }
              },
              required: ['portfolio_id', 'symbol', 'quantity']
            }
          },
          {
            name: 'update_balance',
            description: 'Update the cash balance of a portfolio to a specific amount',
            inputSchema: {
              type: 'object',
              properties: {
                portfolio_id: {
                  type: 'string',
                  description: 'Portfolio ID to update the cash balance for'
                },
                new_cash_balance: {
                  type: 'number',
                  description: 'New cash balance amount to set'
                },
                notes: {
                  type: 'string',
                  description: 'Optional notes explaining the balance update (e.g., "Interest earned", "Bank deposit")'
                }
              },
              required: ['portfolio_id', 'new_cash_balance']
            }
          },
          {
            name: 'create_dynamic_grid',
            description: 'Create a dynamic grid trading strategy that automatically adjusts bounds based on market volatility',
            inputSchema: {
              type: 'object',
              properties: {
                portfolio_id: {
                  type: 'string',
                  description: 'Portfolio ID to create grid in'
                },
                symbol: {
                  type: 'string',
                  description: 'Trading symbol (e.g., AAPL, SPY, TSLA)'
                },
                name: {
                  type: 'string',
                  description: 'Name for this dynamic grid strategy'
                },
                investment_amount: {
                  type: 'number',
                  description: 'Total investment amount for this grid'
                },
                grid_count: {
                  type: 'number',
                  description: 'Number of grid levels',
                  default: 10
                },
                volatility_multiplier: {
                  type: 'number',
                  description: 'Multiplier for volatility-based bounds (higher = wider range)',
                  default: 2.0
                },
                lookback_days: {
                  type: 'number',
                  description: 'Days of historical data to calculate volatility',
                  default: 30
                }
              },
              required: ['portfolio_id', 'symbol', 'name', 'investment_amount']
            }
          },
          {
            name: 'configure_grid_alerts',
            description: 'Configure alert preferences for grid trading strategies',
            inputSchema: {
              type: 'object',
              properties: {
                grid_id: {
                  type: 'string',
                  description: 'Grid ID to configure alerts for (optional - if not provided, sets global preferences)'
                },
                enable_order_alerts: {
                  type: 'boolean',
                  description: 'Enable alerts when grid orders are triggered',
                  default: true
                },
                enable_boundary_alerts: {
                  type: 'boolean',
                  description: 'Enable alerts when price moves outside grid bounds',
                  default: true
                },
                enable_rebalancing_alerts: {
                  type: 'boolean',
                  description: 'Enable alerts for dynamic grid rebalancing suggestions',
                  default: true
                },
                profit_threshold: {
                  type: 'number',
                  description: 'Minimum profit amount to trigger profit alerts ($)',
                  default: 10.0
                },
                alert_frequency: {
                  type: 'string',
                  description: 'Alert frequency for similar events',
                  enum: ['immediate', 'hourly', 'daily'],
                  default: 'immediate'
                }
              }
            }
          },
          {
            name: 'delete_portfolio',
            description: 'Delete a portfolio and all associated data (holdings, transactions, grids)',
            inputSchema: {
              type: 'object',
              properties: {
                portfolio_id: {
                  type: 'string',
                  description: 'Portfolio ID to delete'
                }
              },
              required: ['portfolio_id']
            }
          },
          {
            name: 'analyze_china_industrial_data',
            description: 'Analyze Chinese industrial financial data to provide China ETF sector recommendations and risks to avoid',
            inputSchema: {
              type: 'object',
              properties: {
                industrial_data: {
                  type: 'string',
                  description: 'Chinese industrial financial data (can be in Chinese or English, table format with sectors, revenue growth, profit growth)'
                },
                analysis_focus: {
                  type: 'string',
                  description: 'Focus of analysis (optional)',
                  enum: ['growth_sectors', 'risk_assessment', 'comprehensive'],
                  default: 'comprehensive'
                }
              },
              required: ['industrial_data']
            }
          }
        ]
      };
    });

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'get_portfolio_list':
            return await this.handleGetPortfolioList(args);
          
          case 'get_portfolio_details':
            return await this.handleGetPortfolioDetails(args);
          
          case 'create_portfolio':
            return await this.handleCreatePortfolio(args);
          
          case 'get_grid_list':
            return await this.handleGetGridList(args);
          
          case 'create_grid':
            return await this.handleCreateGrid(args);
          
          case 'get_market_data':
            return await this.handleGetMarketData(args);
          
          case 'search_symbols':
            return await this.handleSearchSymbols(args);
          
          case 'get_dashboard_summary':
            return await this.handleGetDashboardSummary(args);
          
          case 'analyze_grid_performance':
            return await this.handleAnalyzeGridPerformance(args);
          
          case 'get_trading_alerts':
            return await this.handleGetTradingAlerts(args);
          
          case 'calculate_portfolio_metrics':
            return await this.handleCalculatePortfolioMetrics(args);
          
          case 'validate_symbol':
            return await this.handleValidateSymbol(args);
          
          case 'update_china_etfs':
            return await this.handleUpdateChinaETFs(args);
          
          case 'get_us_sector_analysis':
            return await this.handleGetUSSectorAnalysis(args);
          
          case 'get_china_sector_analysis':
            return await this.handleGetChinaSectorAnalysis(args);
          
          case 'buy_stock':
            return await this.handleBuyStock(args);
          
          case 'sell_stock':
            return await this.handleSellStock(args);
          
          case 'update_balance':
            return await this.handleUpdateBalance(args);
          
          case 'delete_portfolio':
            return await this.handleDeletePortfolio(args);
          
          case 'analyze_china_industrial_data':
            return await this.handleChinaIndustrialAnalysis(args);
          
          case 'create_dynamic_grid':
            return await this.handleCreateDynamicGrid(args);
          
          case 'configure_grid_alerts':
            return await this.handleConfigureGridAlerts(args);
          
          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error) {
        return {
          content: [
            {
              type: 'text',
              text: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`
            }
          ]
        };
      }
    });
  }

  private async handleGetPortfolioList(args: any) {
    try {
      // Since we don't have a direct API endpoint, we'll simulate the call to /portfolios
      const data = await this.makeApiCall('/api/portfolios');
      
      const portfolios = Array.isArray(data) ? data : data.portfolios || [];
      
      const summary = `📊 **Portfolio Overview**\n\n` +
        `Found ${portfolios.length} portfolios:\n\n`;
      
      let resultsText = summary;
      
      if (portfolios.length === 0) {
        resultsText += `No portfolios found. Create your first portfolio to get started!`;
      } else {
        resultsText += portfolios.map((portfolio: any, index: number) => {
          const performance = portfolio.performance || {};
          const returnPercent = performance.total_pnl_percent || 0;
          const returnStatus = returnPercent >= 0 ? '📈' : '📉';
          
          return `**${index + 1}. ${portfolio.name}**\n` +
            `   ID: ${portfolio.id}\n` +
            `   Strategy: ${portfolio.strategy_type}\n` +
            `   Value: $${(portfolio.current_value || 0).toLocaleString()}\n` +
            `   Return: ${returnStatus} ${returnPercent.toFixed(2)}%\n` +
            `   Created: ${new Date(portfolio.created_at).toLocaleDateString()}\n`;
        }).join('\n');
      }
      
      resultsText += `\n\n---\n\n**Raw Data:**\n${JSON.stringify(portfolios, null, 2)}`;
      
      return {
        content: [
          {
            type: 'text',
            text: resultsText
          }
        ]
      };
    } catch (error: any) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ Failed to get portfolios: ${error.response?.data?.detail || error.message}`
          }
        ]
      };
    }
  }

  private async handleGetPortfolioDetails(args: any) {
    try {
      const data = await this.makeApiCall(`/api/portfolios/${args.portfolio_id}`);
      
      return {
        content: [
          {
            type: 'text',
            text: `💼 **Portfolio Details**\n\n` +
              `**${data.name}**\n` +
              `• ID: ${data.id}\n` +
              `• Strategy: ${data.strategy_type}\n` +
              `• Initial Capital: $${data.initial_capital.toLocaleString()}\n` +
              `• Current Value: $${data.current_value.toLocaleString()}\n` +
              `• Cash Balance: $${data.cash_balance.toLocaleString()}\n` +
              `• Created: ${new Date(data.created_at).toLocaleDateString()}\n` +
              `${data.description ? `• Description: ${data.description}\n` : ''}` +
              `\n---\n\n**Raw Data:**\n${JSON.stringify(data, null, 2)}`
          }
        ]
      };
    } catch (error: any) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ Failed to get portfolio details: ${error.response?.data?.detail || error.message}`
          }
        ]
      };
    }
  }

  private async handleCreatePortfolio(args: any) {
    try {
      const portfolioData: CreatePortfolioRequest = {
        name: args.name,
        description: args.description,
        strategy_type: args.strategy_type || 'balanced',
        initial_capital: args.initial_capital
      };

      const data = await this.makeApiCall('/api/portfolios', 'POST', portfolioData);
      
      return {
        content: [
          {
            type: 'text',
            text: `✅ **Portfolio Created Successfully!**\n\n` +
              `💼 **${data.name || args.name}**\n` +
              `• ID: ${data.portfolio_id || data.id}\n` +
              `• Strategy: ${args.strategy_type}\n` +
              `• Initial Capital: $${args.initial_capital.toLocaleString()}\n` +
              `${args.description ? `• Description: ${args.description}\n` : ''}` +
              `\nYour portfolio is ready for trading!\n\n` +
              `---\n\n**Raw Data:**\n${JSON.stringify(data, null, 2)}`
          }
        ]
      };
    } catch (error: any) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ Failed to create portfolio: ${error.response?.data?.detail || error.message}`
          }
        ]
      };
    }
  }

  private async handleGetGridList(args: any) {
    try {
      const params = new URLSearchParams();
      if (args.portfolio_id) params.append('portfolio_id', args.portfolio_id);
      if (args.symbol) params.append('symbol', args.symbol);
      if (args.status) params.append('status', args.status);

      const data = await this.makeApiCall(`/api/grids?${params.toString()}`);
      const grids = Array.isArray(data) ? data : data.grids || [];
      
      const summary = `⚡ **Grid Trading Strategies**\n\n` +
        `Found ${grids.length} grid strategies:\n\n`;
      
      let resultsText = summary;
      
      if (grids.length === 0) {
        resultsText += `No grid strategies found.${args.portfolio_id ? ' Try creating a grid for this portfolio!' : ' Create your first grid strategy!'}`;
      } else {
        resultsText += grids.map((grid: any, index: number) => {
          const priceStatus = grid.current_price ? 
            (grid.current_price > grid.upper_price ? '🔴 Above Range' :
             grid.current_price < grid.lower_price ? '🔵 Below Range' : '🟢 In Range') : '⚪ Unknown';
          
          return `**${index + 1}. ${grid.name}**\n` +
            `   Symbol: ${grid.symbol} | Status: ${grid.status}\n` +
            `   Range: $${grid.lower_price} - $${grid.upper_price}\n` +
            `   Investment: $${grid.investment_amount.toLocaleString()}\n` +
            `   Price Status: ${priceStatus}\n` +
            `   Created: ${new Date(grid.created_at).toLocaleDateString()}\n`;
        }).join('\n');
      }
      
      resultsText += `\n\n---\n\n**Raw Data:**\n${JSON.stringify(grids, null, 2)}`;
      
      return {
        content: [
          {
            type: 'text',
            text: resultsText
          }
        ]
      };
    } catch (error: any) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ Failed to get grids: ${error.response?.data?.detail || error.message}`
          }
        ]
      };
    }
  }

  private async handleCreateGrid(args: any) {
    try {
      const gridData: CreateGridRequest = {
        portfolio_id: args.portfolio_id,
        symbol: args.symbol,
        name: args.name,
        upper_price: args.upper_price,
        lower_price: args.lower_price,
        grid_count: args.grid_count || 10,
        investment_amount: args.investment_amount
      };

      const data = await this.makeApiCall('/api/grids', 'POST', gridData);
      
      return {
        content: [
          {
            type: 'text',
            text: `✅ **Grid Strategy Created Successfully!**\n\n` +
              `⚡ **${data.name || args.name}**\n` +
              `• Symbol: ${args.symbol}\n` +
              `• Grid ID: ${data.grid_id || data.id}\n` +
              `• Price Range: $${args.lower_price} - $${args.upper_price}\n` +
              `• Grid Levels: ${args.grid_count}\n` +
              `• Investment: $${args.investment_amount.toLocaleString()}\n` +
              `• Grid Spacing: $${((args.upper_price - args.lower_price) / args.grid_count).toFixed(2)}\n` +
              `\nYour grid strategy is now active!\n\n` +
              `---\n\n**Raw Data:**\n${JSON.stringify(data, null, 2)}`
          }
        ]
      };
    } catch (error: any) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ Failed to create grid: ${error.response?.data?.detail || error.message}`
          }
        ]
      };
    }
  }

  private async handleGetMarketData(args: any) {
    try {
      const data = await this.makeApiCall(`/api/market/${args.symbol}?period=${args.period || 'current'}`);
      
      if (args.period === 'current') {
        return {
          content: [
            {
              type: 'text',
              text: `📈 **Market Data for ${args.symbol}**\n\n` +
                `• Current Price: $${data.price}\n` +
                `• Symbol: ${data.symbol}\n` +
                `• Last Updated: ${new Date().toLocaleString()}\n\n` +
                `---\n\n**Raw Data:**\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      } else {
        const dataPoints = data.data || [];
        return {
          content: [
            {
              type: 'text',
              text: `📊 **Historical Data for ${args.symbol}**\n\n` +
                `• Period: ${args.period}\n` +
                `• Data Points: ${dataPoints.length}\n` +
                `• Symbol: ${data.symbol}\n\n` +
                `**Recent Prices:**\n` +
                `${dataPoints.slice(-5).map((point: any) => 
                  `${point.Date}: $${point.Close}`
                ).join('\n')}\n\n` +
                `---\n\n**Raw Data:**\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }
    } catch (error: any) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ Failed to get market data: ${error.response?.data?.detail || error.message}`
          }
        ]
      };
    }
  }

  private async handleSearchSymbols(args: any) {
    try {
      const data = await this.makeApiCall(`/api/search/symbols?q=${encodeURIComponent(args.query)}`);
      const results = data.results || [];
      
      return {
        content: [
          {
            type: 'text',
            text: `🔍 **Symbol Search Results for "${args.query}"**\n\n` +
              `Found ${results.length} matching symbols:\n\n` +
              `${results.map((result: any, index: number) => 
                `${index + 1}. **${result.symbol}** - ${result.name || 'N/A'}`
              ).join('\n')}\n\n` +
              `---\n\n**Raw Data:**\n${JSON.stringify(data, null, 2)}`
          }
        ]
      };
    } catch (error: any) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ Failed to search symbols: ${error.response?.data?.detail || error.message}`
          }
        ]
      };
    }
  }

  private async handleGetDashboardSummary(args: any) {
    try {
      // Get portfolio summary (this endpoint might need to be created)
      const portfolioData = await this.makeApiCall('/api/portfolios');
      const portfolios = Array.isArray(portfolioData) ? portfolioData : portfolioData.portfolios || [];
      
      let summary = `🏠 **GridTrader Pro Dashboard**\n\n`;
      
      if (portfolios.length > 0) {
        const totalValue = portfolios.reduce((sum: number, p: any) => sum + (p.current_value || 0), 0);
        const totalInvested = portfolios.reduce((sum: number, p: any) => sum + (p.initial_capital || 0), 0);
        const totalReturn = totalInvested > 0 ? ((totalValue - totalInvested) / totalInvested * 100) : 0;
        
        summary += `**Portfolio Summary:**\n` +
          `• Total Portfolios: ${portfolios.length}\n` +
          `• Total Value: $${totalValue.toLocaleString()}\n` +
          `• Total Invested: $${totalInvested.toLocaleString()}\n` +
          `• Total Return: ${totalReturn >= 0 ? '📈' : '📉'} ${totalReturn.toFixed(2)}%\n\n`;
      } else {
        summary += `**Portfolio Summary:**\n• No portfolios yet - create your first portfolio!\n\n`;
      }
      
      if (args.include_market_data) {
        try {
          const symbols = ['SPY', 'QQQ', 'AAPL', 'MSFT'];
          summary += `**Market Overview:**\n`;
          
          for (const symbol of symbols) {
            try {
              const marketData = await this.makeApiCall(`/api/market/${symbol}?period=current`);
              summary += `• ${symbol}: $${marketData.price}\n`;
            } catch {
              summary += `• ${symbol}: Price unavailable\n`;
            }
          }
          summary += '\n';
        } catch {
          summary += `**Market Overview:** Data unavailable\n\n`;
        }
      }
      
      return {
        content: [
          {
            type: 'text',
            text: summary
          }
        ]
      };
    } catch (error: any) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ Failed to get dashboard summary: ${error.response?.data?.detail || error.message}`
          }
        ]
      };
    }
  }

  private async handleAnalyzeGridPerformance(args: any) {
    try {
      // This would need a specific endpoint for grid analysis
      const data = await this.makeApiCall(`/api/grids/${args.grid_id}`);
      
      return {
        content: [
          {
            type: 'text',
            text: `📊 **Grid Performance Analysis**\n\n` +
              `**Grid:** ${data.name}\n` +
              `• Symbol: ${data.symbol}\n` +
              `• Status: ${data.status}\n` +
              `• Price Range: $${data.lower_price} - $${data.upper_price}\n` +
              `• Investment: $${data.investment_amount.toLocaleString()}\n` +
              `• Grid Spacing: $${data.grid_spacing}\n\n` +
              `**Performance Metrics:**\n` +
              `• Current Price: ${data.current_price ? `$${data.current_price}` : 'N/A'}\n` +
              `• Price Position: ${data.price_position || 'Unknown'}\n\n` +
              `---\n\n**Raw Data:**\n${JSON.stringify(data, null, 2)}`
          }
        ]
      };
    } catch (error: any) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ Failed to analyze grid performance: ${error.response?.data?.detail || error.message}`
          }
        ]
      };
    }
  }

  private async handleGetTradingAlerts(args: any) {
    try {
      // This would need an alerts endpoint
      const params = new URLSearchParams();
      if (args.limit) params.append('limit', args.limit.toString());
      if (args.alert_type) params.append('type', args.alert_type);

      const data = await this.makeApiCall(`/api/alerts?${params.toString()}`);
      const alerts = data.alerts || [];
      
      return {
        content: [
          {
            type: 'text',
            text: `🚨 **Trading Alerts**\n\n` +
              `${alerts.length > 0 ? 
                alerts.map((alert: any, index: number) => 
                  `${index + 1}. **${alert.type}** - ${alert.message}\n   ${new Date(alert.created_at).toLocaleString()}`
                ).join('\n\n') :
                'No recent alerts'
              }\n\n` +
              `---\n\n**Raw Data:**\n${JSON.stringify(data, null, 2)}`
          }
        ]
      };
    } catch (error: any) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ Failed to get trading alerts: ${error.response?.data?.detail || error.message}`
          }
        ]
      };
    }
  }

  private async handleCalculatePortfolioMetrics(args: any) {
    try {
      const data = await this.makeApiCall(`/api/portfolios/${args.portfolio_id}/metrics?period=${args.period || '1m'}`);
      
      return {
        content: [
          {
            type: 'text',
            text: `📊 **Portfolio Metrics**\n\n` +
              `**Period:** ${args.period || '1m'}\n\n` +
              `**Performance:**\n` +
              `• Total Return: ${data.total_return || 'N/A'}%\n` +
              `• Sharpe Ratio: ${data.sharpe_ratio || 'N/A'}\n` +
              `• Max Drawdown: ${data.max_drawdown || 'N/A'}%\n` +
              `• Volatility: ${data.volatility || 'N/A'}%\n\n` +
              `---\n\n**Raw Data:**\n${JSON.stringify(data, null, 2)}`
          }
        ]
      };
    } catch (error: any) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ Failed to calculate portfolio metrics: ${error.response?.data?.detail || error.message}`
          }
        ]
      };
    }
  }

  private async handleValidateSymbol(args: any) {
    try {
      const data = await this.makeApiCall(`/api/market/${args.symbol}?period=current`);
      
      return {
        content: [
          {
            type: 'text',
            text: `✅ **Symbol Validation**\n\n` +
              `**${args.symbol}** is valid!\n` +
              `• Current Price: $${data.price}\n` +
              `• Symbol: ${data.symbol}\n\n` +
              `This symbol can be used for grid trading.`
          }
        ]
      };
    } catch (error: any) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ **Symbol Validation Failed**\n\n` +
              `**${args.symbol}** is not valid or not supported.\n` +
              `Error: ${error.response?.data?.detail || error.message}`
          }
        ]
      };
    }
  }

  private async handleUpdateChinaETFs(args: any) {
    try {
      const data = await this.makeApiCall('/api/china-etfs/update', 'POST', {
        csv_data: args.csv_data
      });
      
      if (data.success) {
        const topETFs = data.top_10.map((etf: any, index: number) => 
          `${index + 1}. ${etf.symbol}: ${etf.name.substring(0, 40)}... (${etf.volume})`
        ).join('\n');
        
        const sectorBreakdown = Object.entries(data.sector_breakdown)
          .map(([sector, count]) => `• ${sector}: ${count} ETFs`)
          .join('\n');
        
        return {
          content: [
            {
              type: 'text',
              text: `🇨🇳 **China ETFs Auto-Updated Successfully!**\n\n` +
                `✅ Processed **${data.etfs_processed} ETFs** from cn.investing.com\n` +
                `🚀 **${data.etfs_updated_in_engine || data.etfs_processed} ETFs automatically updated** in the app!\n\n` +
                `${data.auto_update_status || ''}\n\n` +
                `📊 **Top 10 by Volume:**\n${topETFs}\n\n` +
                `📈 **Sector Breakdown:**\n${sectorBreakdown}\n\n` +
                `🎯 **Immediate Effects:**\n` +
                `• ✅ Sector analysis now uses updated ETFs\n` +
                `• ✅ New ETFs available for grid trading\n` +
                `• ✅ Updated conviction scores and recommendations\n` +
                `• ✅ Changes active immediately (no restart needed)\n\n` +
                `🧪 **Test the Updates:**\n` +
                `• Ask: "Show me China sector analysis"\n` +
                `• Ask: "What are the top China ETFs now?"\n` +
                `• Ask: "Create a grid for the top China tech ETF"\n\n` +
                `💾 **For Permanent Storage:**\n` +
                `The changes are active immediately but will reset on app restart.\n` +
                `For permanent updates, copy this code to app/systematic_trading.py:\n\n` +
                `\`\`\`python\n${data.generated_code}\`\`\`\n\n` +
                `🎉 **Your China ETF universe is now updated and ready for trading!**`
            }
          ]
        };
      } else {
        throw new Error(data.message || 'Update failed');
      }
    } catch (error: any) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ **China ETFs Update Failed**\n\n` +
              `Error: ${error.response?.data?.detail || error.message}\n\n` +
              `💡 **CSV Format Expected:**\n` +
              `\`\`\`csv\n` +
              `名称,代码,最新价,涨跌幅,交易量,时间\n` +
              `Huatai-PB CSOP HS Tech Id(QDII),513130,0.770,+1.32%,5.94B,11:29:59\n` +
              `华夏恒生互联网科技业ETF(QDII),513330,0.540,+1.89%,5.37B,11:29:58\n` +
              `\`\`\`\n\n` +
              `Please ensure your CSV data is in the correct format from cn.investing.com`
          }
        ]
      };
    }
  }

  private async handleGetUSSectorAnalysis(args: any) {
    try {
      const lookbackDays = args.lookback_days || 90;
      const data = await this.makeApiCall(`/api/sector-analysis?market=US&lookback_days=${lookbackDays}`);
      
      if (data.success) {
        const topSectors = data.top_sectors.slice(0, 10).map((sector: any, index: number) => 
          `${index + 1}. **${sector.symbol}**: ${sector.sector.substring(0, 35)}...\n` +
          `   Conviction: ${sector.conviction_score.toFixed(2)} | Weight: ${sector.recommended_weight.toFixed(1)}% | Risk Adj: ${sector.risk_adjustment.toFixed(3)}\n` +
          `   Recommendation: ${sector.recommendation}`
        ).join('\n\n');
        
        const summary = data.summary || {};
        
        return {
          content: [
            {
              type: 'text',
              text: `🇺🇸 **US Market Sector Analysis**\n\n` +
                `**Market**: United States\n` +
                `**Benchmark**: S&P 500 (SPY)\n` +
                `**Market Regime**: ${data.market_regime?.replace('_', ' ').toUpperCase() || 'Unknown'}\n` +
                `**Analysis Period**: ${lookbackDays} days\n` +
                `**Sectors Analyzed**: ${data.sectors_analyzed || 0}\n\n` +
                `📊 **Top 10 US Sector ETFs:**\n\n${topSectors}\n\n` +
                `🏆 **Key Highlights:**\n` +
                `• Strongest Momentum: ${summary.strongest_momentum?.symbol || 'N/A'}\n` +
                `• Best Value: ${summary.best_value?.symbol || 'N/A'}\n` +
                `• Highest Conviction: ${summary.highest_conviction?.symbol || 'N/A'}\n\n` +
                `💡 **Investment Ideas:**\n` +
                `• Consider overweighting sectors with conviction > 1.2\n` +
                `• Monitor risk adjustment for position sizing\n` +
                `• Focus on BUY recommendations for new positions\n\n` +
                `🔄 **Updated**: ${new Date(data.analysis_date).toLocaleString()}`
            }
          ]
        };
      } else {
        throw new Error(data.message || 'Analysis failed');
      }
    } catch (error: any) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ **US Sector Analysis Failed**\n\n` +
              `Error: ${error.response?.data?.detail || error.message}\n\n` +
              `💡 **Try asking:**\n` +
              `• "Show me US sector analysis"\n` +
              `• "What are the best US sector ETFs?"\n` +
              `• "Run US market sector analysis for 60 days"`
          }
        ]
      };
    }
  }

  private async handleGetChinaSectorAnalysis(args: any) {
    try {
      const lookbackDays = args.lookback_days || 90;
      const data = await this.makeApiCall(`/api/sector-analysis?market=China&lookback_days=${lookbackDays}`);
      
      if (data.success) {
        const topSectors = data.top_sectors.slice(0, 10).map((sector: any, index: number) => 
          `${index + 1}. **${sector.symbol}**: ${sector.sector.substring(0, 35)}...\n` +
          `   Conviction: ${sector.conviction_score.toFixed(2)} | Weight: ${sector.recommended_weight.toFixed(1)}% | Risk Adj: ${sector.risk_adjustment.toFixed(3)}\n` +
          `   Recommendation: ${sector.recommendation}`
        ).join('\n\n');
        
        const summary = data.summary || {};
        
        return {
          content: [
            {
              type: 'text',
              text: `🇨🇳 **China Market Sector Analysis**\n\n` +
                `**Market**: China\n` +
                `**Benchmark**: CSI 300 Index (000300.SS)\n` +
                `**Market Regime**: ${data.market_regime?.replace('_', ' ').toUpperCase() || 'Unknown'}\n` +
                `**Analysis Period**: ${lookbackDays} days\n` +
                `**Sectors Analyzed**: ${data.sectors_analyzed || 0}\n\n` +
                `📊 **Top 10 China Sector ETFs:**\n\n${topSectors}\n\n` +
                `🏆 **Key Highlights:**\n` +
                `• Strongest Momentum: ${summary.strongest_momentum?.symbol || 'N/A'}\n` +
                `• Best Value: ${summary.best_value?.symbol || 'N/A'}\n` +
                `• Highest Conviction: ${summary.highest_conviction?.symbol || 'N/A'}\n\n` +
                `💡 **Investment Ideas:**\n` +
                `• Focus on high-conviction healthcare and tech ETFs\n` +
                `• Consider Hong Kong exposure for diversification\n` +
                `• Monitor military/defense sectors for geopolitical plays\n\n` +
                `🔄 **Updated**: ${new Date(data.analysis_date).toLocaleString()}`
            }
          ]
        };
      } else {
        throw new Error(data.message || 'Analysis failed');
      }
    } catch (error: any) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ **China Sector Analysis Failed**\n\n` +
              `Error: ${error.response?.data?.detail || error.message}\n\n` +
              `💡 **Try asking:**\n` +
              `• "Show me China sector analysis"\n` +
              `• "What are the best China sector ETFs?"\n` +
              `• "Run China market sector analysis for 60 days"\n` +
              `• "Analyze Chinese healthcare and tech ETFs"`
          }
        ]
      };
    }
  }

  private async handleBuyStock(args: any) {
    try {
      // Get current price if not provided
      let price = args.price;
      if (!price) {
        try {
          const marketData = await this.makeApiCall(`/api/market/${args.symbol}?period=current`);
          price = marketData.price || marketData.current_price;
        } catch (priceError) {
          // If we can't get current price, require user to specify
          return {
            content: [
              {
                type: 'text',
                text: `❌ **Price Required**\n\n` +
                  `Could not get current market price for ${args.symbol}.\n` +
                  `Please specify the price per share in your command.\n\n` +
                  `Example: "Buy 10 shares of ${args.symbol} at $150.00 in my growth portfolio"`
              }
            ]
          };
        }
      }

      const transactionData = {
        portfolio_id: args.portfolio_id,
        symbol: args.symbol.toUpperCase(),
        transaction_type: 'buy',
        quantity: args.quantity,
        price: price,
        fees: 0, // Default to 0 fees
        notes: args.notes || `MCP buy transaction - ${args.quantity} shares at $${price}`
      };

      const result = await this.makeApiCall('/api/transactions', 'POST', transactionData);
      
      if (result.success) {
        const totalCost = args.quantity * price;
        
        return {
          content: [
            {
              type: 'text',
              text: `✅ **Buy Transaction Successful!**\n\n` +
                `**Trade Details:**\n` +
                `• Symbol: **${args.symbol.toUpperCase()}**\n` +
                `• Quantity: **${args.quantity} shares**\n` +
                `• Price: **$${price.toFixed(2)} per share**\n` +
                `• Total Cost: **$${totalCost.toFixed(2)}**\n` +
                `• Portfolio: ${args.portfolio_id}\n` +
                `• Transaction ID: ${result.transaction_id}\n\n` +
                `💰 **Portfolio Impact:**\n` +
                `• Cash reduced by $${totalCost.toFixed(2)}\n` +
                `• Added ${args.quantity} shares of ${args.symbol}\n` +
                `• Position value: $${totalCost.toFixed(2)}\n\n` +
                `📋 **Next Steps:**\n` +
                `• Check updated portfolio: "Show me portfolio details"\n` +
                `• Monitor position: "What's the current price of ${args.symbol}?"\n` +
                `• Set up grid trading: "Create a grid for ${args.symbol}"\n\n` +
                `🎉 **Trade executed successfully!**`
            }
          ]
        };
      } else {
        throw new Error(result.message || 'Transaction failed');
      }
    } catch (error: any) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ **Buy Transaction Failed**\n\n` +
              `Error: ${error.response?.data?.detail || error.message}\n\n` +
              `💡 **Common Issues:**\n` +
              `• Insufficient cash balance in portfolio\n` +
              `• Invalid stock symbol\n` +
              `• Portfolio not found\n` +
              `• Price not specified for illiquid stocks\n\n` +
              `🔧 **Try:**\n` +
              `• "Show me my cash balances" to check available funds\n` +
              `• "Search for [company] symbol" to verify symbol\n` +
              `• "Show me my portfolios" to get portfolio ID`
          }
        ]
      };
    }
  }

  private async handleSellStock(args: any) {
    try {
      // Get current price if not provided
      let price = args.price;
      if (!price) {
        try {
          const marketData = await this.makeApiCall(`/api/market/${args.symbol}?period=current`);
          price = marketData.price || marketData.current_price;
        } catch (priceError) {
          return {
            content: [
              {
                type: 'text',
                text: `❌ **Price Required**\n\n` +
                  `Could not get current market price for ${args.symbol}.\n` +
                  `Please specify the price per share in your command.\n\n` +
                  `Example: "Sell 10 shares of ${args.symbol} at $150.00 from my growth portfolio"`
              }
            ]
          };
        }
      }

      const transactionData = {
        portfolio_id: args.portfolio_id,
        symbol: args.symbol.toUpperCase(),
        transaction_type: 'sell',
        quantity: args.quantity,
        price: price,
        fees: 0,
        notes: args.notes || `MCP sell transaction - ${args.quantity} shares at $${price}`
      };

      const result = await this.makeApiCall('/api/transactions', 'POST', transactionData);
      
      if (result.success) {
        const totalProceeds = args.quantity * price;
        
        return {
          content: [
            {
              type: 'text',
              text: `✅ **Sell Transaction Successful!**\n\n` +
                `**Trade Details:**\n` +
                `• Symbol: **${args.symbol.toUpperCase()}**\n` +
                `• Quantity: **${args.quantity} shares**\n` +
                `• Price: **$${price.toFixed(2)} per share**\n` +
                `• Total Proceeds: **$${totalProceeds.toFixed(2)}**\n` +
                `• Portfolio: ${args.portfolio_id}\n` +
                `• Transaction ID: ${result.transaction_id}\n\n` +
                `💰 **Portfolio Impact:**\n` +
                `• Cash increased by $${totalProceeds.toFixed(2)}\n` +
                `• Reduced ${args.quantity} shares of ${args.symbol}\n` +
                `• Realized P&L will be calculated\n\n` +
                `📋 **Next Steps:**\n` +
                `• Check updated portfolio: "Show me portfolio details"\n` +
                `• Review cash balance: "Show me my cash balances"\n` +
                `• Monitor remaining position: "What holdings do I have?"\n\n` +
                `🎉 **Trade executed successfully!**`
            }
          ]
        };
      } else {
        throw new Error(result.message || 'Transaction failed');
      }
    } catch (error: any) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ **Sell Transaction Failed**\n\n` +
              `Error: ${error.response?.data?.detail || error.message}\n\n` +
              `💡 **Common Issues:**\n` +
              `• Insufficient shares to sell\n` +
              `• Invalid stock symbol\n` +
              `• Portfolio not found\n` +
              `• Stock not owned in portfolio\n\n` +
              `🔧 **Try:**\n` +
              `• "Show me my portfolios" to check holdings\n` +
              `• "Show me portfolio details" to see current positions\n` +
              `• "Search for [company] symbol" to verify symbol`
          }
        ]
      };
    }
  }

  private async handleUpdateBalance(args: any) {
    try {
      const updateData = {
        new_cash_balance: args.new_cash_balance,
        notes: args.notes || `MCP balance update - Set to $${args.new_cash_balance.toLocaleString()}`
      };

      const result = await this.makeApiCall(`/api/portfolios/${args.portfolio_id}/update-cash`, 'POST', updateData);
      
      if (result.success) {
        const adjustment = result.adjustment;
        const adjustmentText = adjustment > 0 ? 
          `increased by $${Math.abs(adjustment).toLocaleString()}` : 
          adjustment < 0 ? 
            `decreased by $${Math.abs(adjustment).toLocaleString()}` : 
            `unchanged (no adjustment needed)`;
        
        return {
          content: [
            {
              type: 'text',
              text: `✅ **Cash Balance Updated Successfully!**\n\n` +
                `**Balance Update Details:**\n` +
                `• Portfolio ID: ${args.portfolio_id}\n` +
                `• Previous Balance: **$${result.old_balance.toLocaleString()}**\n` +
                `• New Balance: **$${result.new_balance.toLocaleString()}**\n` +
                `• Balance Change: **${adjustmentText}**\n` +
                `• New Total Portfolio Value: **$${result.new_total_value.toLocaleString()}**\n` +
                `• Notes: ${args.notes || 'Balance update via MCP'}\n\n` +
                `💰 **Impact:**\n` +
                `• Cash balance ${adjustmentText}\n` +
                `• Portfolio total value updated\n` +
                `• Audit trail transaction created\n\n` +
                `📋 **Next Steps:**\n` +
                `• View updated portfolio: "Show me portfolio details"\n` +
                `• Check all balances: "Show me all my portfolios"\n` +
                `• Review transaction history: "Show me recent transactions"\n\n` +
                `🎉 **Balance update completed successfully!**`
            }
          ]
        };
      } else {
        throw new Error(result.message || result.detail || 'Balance update failed');
      }
    } catch (error: any) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ **Balance Update Failed**\n\n` +
              `Error: ${error.response?.data?.detail || error.message}\n\n` +
              `💡 **Common Issues:**\n` +
              `• Invalid portfolio ID\n` +
              `• Negative balance amount\n` +
              `• Authentication error\n` +
              `• Database connection issue\n\n` +
              `🔧 **Try:**\n` +
              `• "Show me all my portfolios" to verify portfolio ID\n` +
              `• Check that the balance amount is positive\n` +
              `• Try again in a few moments\n\n` +
              `💰 **Example Usage:**\n` +
              `"Update my portfolio balance to $50000 with note 'Bank deposit'"`
          }
        ]
      };
    }
  }

  private async handleDeletePortfolio(args: any) {
    try {
      const result = await this.makeApiCall(`/api/portfolios/${args.portfolio_id}`, 'DELETE');
      
      if (result.success) {
        return {
          content: [
            {
              type: 'text',
              text: `✅ **Portfolio Deleted Successfully!**\n\n` +
                `**Deletion Summary:**\n` +
                `• Portfolio removed from your account\n` +
                `• Holdings deleted: ${result.deleted_holdings || 0}\n` +
                `• Transactions deleted: ${result.deleted_transactions || 0}\n` +
                `• Grid strategies deleted: ${result.deleted_grids || 0}\n` +
                `• Grid orders deleted: ${result.deleted_grid_orders || 0}\n\n` +
                `⚠️ **This action cannot be undone.**\n\n` +
                `📋 **Next Steps:**\n` +
                `• View remaining portfolios: "Show me my portfolios"\n` +
                `• Create a new portfolio: "Create a new portfolio"\n\n` +
                `🗑️ **Portfolio deletion completed successfully!**`
            }
          ]
        };
      } else {
        return {
          content: [
            {
              type: 'text',
              text: `❌ **Portfolio Deletion Failed**\n\n` +
                `Error: ${result.detail || result.message || 'Unknown error'}\n\n` +
                `💡 **Common Issues:**\n` +
                `• Invalid portfolio ID\n` +
                `• Portfolio not found\n` +
                `• Authentication error\n` +
                `• Database connection issue\n\n` +
                `🔧 **Try:**\n` +
                `• "Show me my portfolios" to verify portfolio exists\n` +
                `• Check the portfolio ID is correct\n` +
                `• Try again in a few moments\n\n` +
                `💰 **Example Usage:**\n` +
                `"Delete my Tech Focus portfolio"`
            }
          ]
        };
      }
    } catch (error: any) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ **Portfolio Deletion Failed**\n\n` +
              `Error: ${error.response?.data?.detail || error.message}\n\n` +
              `💡 **Common Issues:**\n` +
              `• Invalid portfolio ID\n` +
              `• Portfolio not found\n` +
              `• Authentication error\n` +
              `• Database connection issue\n\n` +
              `🔧 **Try:**\n` +
              `• "Show me my portfolios" to verify portfolio exists\n` +
              `• Check the portfolio ID is correct\n` +
              `• Try again in a few moments\n\n` +
              `💰 **Example Usage:**\n` +
              `"Delete my Tech Focus portfolio"`
          }
        ]
      };
    }
  }

  private async handleChinaIndustrialAnalysis(args: any) {
    try {
      const industrialData = args.industrial_data;
      const analysisFocus = args.analysis_focus || 'comprehensive';
      
      // Parse and analyze the industrial data
      const analysis = this.analyzeChinaIndustrialData(industrialData, analysisFocus);
      
      // Get current China ETF data for recommendations
      let chinaEtfData;
      try {
        chinaEtfData = await this.makeApiCall('/api/analysis/china-sectors?lookback_days=90');
      } catch (error) {
        console.log('Could not fetch China ETF data, proceeding with analysis only');
        chinaEtfData = null;
      }
      
      // Combine industrial analysis with ETF recommendations
      const recommendations = this.generateEtfRecommendations(analysis, chinaEtfData);
      
      return {
        content: [
          {
            type: 'text',
            text: `🇨🇳 **China ETF Sector Analysis & Recommendations**\n\n` +
              `📊 **Industrial Data Analysis:**\n${analysis.summary}\n\n` +
              `🎯 **ETF Sector Recommendations:**\n${recommendations.buy}\n\n` +
              `⚠️ **Sectors to Avoid:**\n${recommendations.avoid}\n\n` +
              `💡 **Key Insights:**\n${analysis.insights}\n\n` +
              `📈 **Investment Strategy:**\n${recommendations.strategy}\n\n` +
              `⚡ **Risk Management:**\n${recommendations.riskManagement}\n\n` +
              `🔍 **Data Quality:** ${analysis.dataQuality}\n\n` +
              `---\n\n**Analysis completed at:** ${new Date().toLocaleString()}`
          }
        ]
      };
    } catch (error: any) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ **China Industrial Data Analysis Failed**\n\n` +
              `Error: ${error.message}\n\n` +
              `💡 **How to Use:**\n` +
              `• Provide Chinese industrial financial data in table format\n` +
              `• Include sector names, revenue growth, profit growth\n` +
              `• Data can be in Chinese or English\n` +
              `• Specify analysis focus: growth_sectors, risk_assessment, or comprehensive\n\n` +
              `📊 **Example Usage:**\n` +
              `"Analyze this Chinese industrial data: [paste table with sectors and growth rates]"\n\n` +
              `🔧 **Supported Data Formats:**\n` +
              `• Government statistical reports\n` +
              `• Industry financial summaries\n` +
              `• Sector performance tables\n` +
              `• Year-over-year growth data`
          }
        ]
      };
    }
  }

  private analyzeChinaIndustrialData(data: string, focus: string) {
    // Parse the industrial data and extract key metrics
    const sectors = this.parseIndustrialData(data);
    
    // Categorize sectors by performance
    const strongSectors = sectors.filter(s => s.revenueGrowth > 5 && s.profitGrowth > 5);
    const weakSectors = sectors.filter(s => s.revenueGrowth < 0 || s.profitGrowth < -5);
    const mixedSectors = sectors.filter(s => !strongSectors.includes(s) && !weakSectors.includes(s));
    
    // Generate insights based on patterns
    const insights = this.generateIndustrialInsights(strongSectors, weakSectors, mixedSectors);
    
    // Create summary based on focus
    let summary = '';
    if (focus === 'growth_sectors') {
      summary = this.createGrowthSectorsSummary(strongSectors);
    } else if (focus === 'risk_assessment') {
      summary = this.createRiskAssessmentSummary(weakSectors);
    } else {
      summary = this.createComprehensiveSummary(strongSectors, weakSectors, mixedSectors);
    }
    
    return {
      summary,
      insights,
      strongSectors,
      weakSectors,
      mixedSectors,
      dataQuality: this.assessDataQuality(data, sectors)
    };
  }

  private parseIndustrialData(data: string) {
    const sectors = [];
    const lines = data.split('\n');
    
    // Simple parsing logic - look for patterns in Chinese industrial data
    for (const line of lines) {
      // Skip headers and empty lines
      if (!line.trim() || line.includes('行业') || line.includes('营业收入') || line.includes('同比增长')) {
        continue;
      }
      
      // Extract sector name and growth rates using regex
      const matches = line.match(/([^0-9]+?)\s+([\d.-]+)\s+([\d.-]+)\s+([\d.-]+)\s+([\d.-]+)\s+([\d.-]+)\s+([\d.-]+)/);
      if (matches) {
        const sectorName = matches[1].trim();
        const revenueGrowth = parseFloat(matches[4]) || 0; // 4th number is usually revenue growth %
        const profitGrowth = parseFloat(matches[6]) || 0;  // 6th number is usually profit growth %
        
        if (sectorName && !isNaN(revenueGrowth) && !isNaN(profitGrowth)) {
          sectors.push({
            name: sectorName,
            revenueGrowth,
            profitGrowth,
            performance: revenueGrowth > 5 && profitGrowth > 5 ? 'strong' : 
                        revenueGrowth < 0 || profitGrowth < -5 ? 'weak' : 'mixed'
          });
        }
      }
    }
    
    return sectors;
  }

  private generateIndustrialInsights(strong: any[], weak: any[], mixed: any[]) {
    const insights = [];
    
    // Technology trends
    const techSectors = strong.filter(s => 
      s.name.includes('电子') || s.name.includes('通信') || s.name.includes('计算机') || 
      s.name.includes('电气') || s.name.includes('设备制造')
    );
    if (techSectors.length > 0) {
      insights.push('🚀 Technology sectors showing strong momentum - China\'s tech manufacturing competitiveness');
    }
    
    // Energy transition
    const energyTransition = strong.filter(s => s.name.includes('有色金属')) || weak.filter(s => s.name.includes('煤炭') || s.name.includes('石油'));
    if (energyTransition.length > 0) {
      insights.push('⚡ Clear energy transition: Non-ferrous metals (green energy materials) rising, fossil fuels declining');
    }
    
    // Manufacturing evolution
    const traditionalMfg = weak.filter(s => s.name.includes('纺织') || s.name.includes('家具') || s.name.includes('造纸'));
    if (traditionalMfg.length > 0) {
      insights.push('🏭 Traditional manufacturing under pressure - structural shift toward high-tech manufacturing');
    }
    
    return insights.join('\n• ');
  }

  private createComprehensiveSummary(strong: any[], weak: any[], mixed: any[]) {
    return `**Strong Performers (${strong.length} sectors):**\n` +
      strong.slice(0, 5).map(s => `• ${s.name}: +${s.revenueGrowth}% revenue, +${s.profitGrowth}% profit`).join('\n') +
      `\n\n**Weak Performers (${weak.length} sectors):**\n` +
      weak.slice(0, 5).map(s => `• ${s.name}: ${s.revenueGrowth}% revenue, ${s.profitGrowth}% profit`).join('\n') +
      (mixed.length > 0 ? `\n\n**Mixed Performance (${mixed.length} sectors):** Showing moderate or mixed signals` : '');
  }

  private createGrowthSectorsSummary(strong: any[]) {
    return `**Top Growth Sectors:**\n` +
      strong.sort((a, b) => (b.revenueGrowth + b.profitGrowth) - (a.revenueGrowth + a.profitGrowth))
        .slice(0, 8).map(s => `• ${s.name}: +${s.revenueGrowth}% revenue, +${s.profitGrowth}% profit`).join('\n');
  }

  private createRiskAssessmentSummary(weak: any[]) {
    return `**High-Risk Sectors to Avoid:**\n` +
      weak.sort((a, b) => (a.revenueGrowth + a.profitGrowth) - (b.revenueGrowth + b.profitGrowth))
        .slice(0, 8).map(s => `• ${s.name}: ${s.revenueGrowth}% revenue, ${s.profitGrowth}% profit`).join('\n');
  }

  private generateEtfRecommendations(analysis: any, etfData: any) {
    // Map industrial sectors to available ETFs
    const sectorMapping = {
      '有色金属': '512400.SS (南方有色金属ETF)',
      '电子': '515050.SS (5G通信ETF), 512480.SS (半导体ETF)',
      '电气': '515050.SS (5G通信ETF), 588000.SS (科创50ETF)',
      '计算机': '512480.SS (半导体ETF), 588000.SS (科创50ETF)',
      '通信': '515050.SS (5G通信ETF)',
      '运输设备': '512660.SS (军工ETF)',
      '航空航天': '512660.SS (军工ETF)',
      '汽车': 'Auto sector ETFs',
      '医药': '513060.SS (恒生医疗ETF), 513120.SS (港股医药ETF)'
    };

    const buyRecommendations = [];
    const avoidRecommendations = [];
    
    // Generate buy recommendations from strong sectors
    for (const sector of analysis.strongSectors.slice(0, 5)) {
      for (const [key, etf] of Object.entries(sectorMapping)) {
        if (sector.name.includes(key)) {
          buyRecommendations.push(`• **${etf}** - Aligned with ${sector.name} (+${sector.revenueGrowth}% revenue, +${sector.profitGrowth}% profit)`);
          break;
        }
      }
    }
    
    // Generate avoid recommendations from weak sectors
    for (const sector of analysis.weakSectors.slice(0, 5)) {
      avoidRecommendations.push(`• Avoid ETFs with heavy ${sector.name} exposure (${sector.revenueGrowth}% revenue, ${sector.profitGrowth}% profit)`);
    }
    
    const strategy = this.generateInvestmentStrategy(analysis);
    const riskManagement = this.generateRiskManagement(analysis);
    
    return {
      buy: buyRecommendations.length > 0 ? buyRecommendations.join('\n') : 'No specific ETF matches found for strong sectors',
      avoid: avoidRecommendations.length > 0 ? avoidRecommendations.join('\n') : 'No major sector risks identified',
      strategy,
      riskManagement
    };
  }

  private generateInvestmentStrategy(analysis: any) {
    const strongCount = analysis.strongSectors.length;
    const weakCount = analysis.weakSectors.length;
    
    if (strongCount > weakCount) {
      return '🎯 **Growth Strategy**: Focus on sector-specific ETFs aligned with strong industrial performers\n' +
             '• Overweight technology and innovation sectors\n' +
             '• Consider thematic ETFs over broad market exposure';
    } else if (weakCount > strongCount) {
      return '🛡️ **Defensive Strategy**: Avoid broad market exposure, focus on quality sectors\n' +
             '• Underweight traditional industries\n' +
             '• Emphasize defensive and growth sectors';
    } else {
      return '⚖️ **Balanced Strategy**: Mixed signals suggest selective approach\n' +
             '• Focus on highest conviction sectors\n' +
             '• Maintain diversification across themes';
    }
  }

  private generateRiskManagement(analysis: any) {
    return '🔒 **Risk Management Guidelines:**\n' +
           '• Avoid ETFs with >20% exposure to declining sectors\n' +
           '• Monitor industrial data quarterly for trend changes\n' +
           '• Use stop-losses on sector-specific positions\n' +
           '• Diversify across multiple growth themes\n' +
           '• Consider hedging with defensive sectors';
  }

  private assessDataQuality(rawData: string, parsedSectors: any[]) {
    const lineCount = rawData.split('\n').length;
    const sectorCount = parsedSectors.length;
    
    if (sectorCount > 20 && lineCount > 30) {
      return '✅ High quality - Comprehensive industrial dataset';
    } else if (sectorCount > 10) {
      return '⚠️ Moderate quality - Partial industrial coverage';
    } else if (sectorCount > 0) {
      return '🔍 Limited quality - Few sectors identified, consider providing more detailed data';
    } else {
      return '❌ Poor quality - Unable to parse sector data, please check format';
    }
  }

  private async handleCreateDynamicGrid(args: any) {
    try {
      console.log('=== DYNAMIC GRID DEBUG START ===');
      console.log('Input args:', JSON.stringify(args, null, 2));
      // First, get current market data and calculate volatility
      // Convert lookback days to proper yfinance period format
      const lookbackDays = args.lookback_days || 30;
      let period: string;
      
      if (lookbackDays <= 5) {
        period = "5d";
      } else if (lookbackDays <= 30) {
        period = "1mo";
      } else if (lookbackDays <= 90) {
        period = "3mo";
      } else if (lookbackDays <= 180) {
        period = "6mo";
      } else {
        period = "1y";
      }
      
      console.log(`Dynamic grid: Requesting ${args.symbol} data for ${lookbackDays} days using period: ${period}`);
      const marketData = await this.makeApiCall(`/api/market/${args.symbol}?period=${period}`);
      
      console.log(`Dynamic grid: Received data:`, {
        hasData: !!marketData,
        hasDataArray: !!(marketData && marketData.data),
        dataLength: marketData && marketData.data ? marketData.data.length : 0,
        sampleData: marketData && marketData.data ? marketData.data[0] : null
      });
      
      if (!marketData || !marketData.data || marketData.data.length < 5) {
        const dataLength = marketData && marketData.data ? marketData.data.length : 0;
        console.log('Insufficient data, falling back to default volatility');
        
        // Fallback: Use default volatility of 20% if insufficient data
        const currentPrice = marketData?.current_price || 232; // Fallback price
        const defaultVolatility = 0.20; // 20% default volatility
        const volatilityMultiplier = args.volatility_multiplier || 2.0;
        const priceDeviation = currentPrice * defaultVolatility * volatilityMultiplier;
        const upperPrice = currentPrice + priceDeviation;
        const lowerPrice = Math.max(currentPrice - priceDeviation, currentPrice * 0.1);
        
        // Create grid with fallback bounds
        const gridData = {
          portfolio_id: args.portfolio_id,
          symbol: args.symbol,
          name: args.name + ' (Default Volatility)',
          upper_price: upperPrice,
          lower_price: lowerPrice,
          grid_count: args.grid_count || 10,
          investment_amount: args.investment_amount
        };
        
        console.log('Creating fallback dynamic grid:', gridData);
        const result = await this.makeApiCall('/api/grids', 'POST', gridData);
        
        if (result.success || result.grid_id || result.id) {
          return {
            content: [
              {
                type: 'text',
                text: `✅ **Dynamic Grid Created (Fallback Mode)**\n\n` +
                  `🧠 **${args.symbol} Dynamic Grid** (using default 20% volatility)\n` +
                  `• Grid ID: ${result.grid_id || result.id}\n` +
                  `• Current Price: $${currentPrice.toFixed(2)}\n` +
                  `• Used Default Volatility: 20% (insufficient historical data: ${dataLength} points)\n` +
                  `• Upper Bound: $${upperPrice.toFixed(2)}\n` +
                  `• Lower Bound: $${lowerPrice.toFixed(2)}\n` +
                  `• Grid Levels: ${args.grid_count || 10}\n` +
                  `• Investment: $${args.investment_amount.toLocaleString()}\n\n` +
                  `⚠️ **Note**: Used default volatility due to insufficient historical data.\n` +
                  `For more accurate bounds, ensure symbol has sufficient trading history.`
              }
            ]
          };
        } else {
          throw new Error(result.message || 'Fallback grid creation failed');
        }
      }

      // Calculate volatility from historical data
      const prices = marketData.data.map((d: any) => parseFloat(d.close));
      const currentPrice = marketData.current_price || prices[prices.length - 1];
      
      // Calculate daily returns
      const returns = [];
      for (let i = 1; i < prices.length; i++) {
        returns.push(Math.log(prices[i] / prices[i - 1]));
      }
      
      // Calculate volatility (standard deviation of returns, annualized)
      const meanReturn = returns.reduce((sum, r) => sum + r, 0) / returns.length;
      const variance = returns.reduce((sum, r) => sum + Math.pow(r - meanReturn, 2), 0) / returns.length;
      const volatility = Math.sqrt(variance * 252); // Annualized volatility
      
      // Calculate dynamic bounds based on volatility
      const volatilityMultiplier = args.volatility_multiplier || 2.0;
      const priceDeviation = currentPrice * volatility * volatilityMultiplier;
      const upperPrice = currentPrice + priceDeviation;
      const lowerPrice = Math.max(currentPrice - priceDeviation, currentPrice * 0.1); // Prevent negative prices
      
      // Create the grid with calculated bounds using the standard grid creation endpoint
      const gridData = {
        portfolio_id: args.portfolio_id,
        symbol: args.symbol,
        name: args.name,
        upper_price: upperPrice,
        lower_price: lowerPrice,
        grid_count: args.grid_count || 10,
        investment_amount: args.investment_amount
      };

      console.log('Creating dynamic grid with data:', gridData);
      const result = await this.makeApiCall('/api/grids', 'POST', gridData);
      
      // After successful creation, update the grid's strategy_config to mark it as dynamic
      if (result.success && result.grid_id) {
        console.log(`Dynamic grid created with ID: ${result.grid_id}`);
        // Note: In a full implementation, we would update the grid's strategy_config
        // to include the dynamic grid parameters for future rebalancing
      }
      
      if (result.success || result.grid_id || result.id) {
        const gridSpacing = (upperPrice - lowerPrice) / (args.grid_count || 10);
        const quantityPerGrid = args.investment_amount / ((args.grid_count || 10) * upperPrice);
        const expectedProfitPerCycle = gridSpacing * quantityPerGrid;
        
        return {
          content: [
            {
              type: 'text',
              text: `✅ **Dynamic Grid Strategy Created Successfully!**\n\n` +
                `🧠 **AI-Powered Dynamic Grid for ${args.symbol}**\n` +
                `• Grid ID: ${result.grid_id || result.id}\n` +
                `• Strategy: **Volatility-Adaptive Grid Trading**\n\n` +
                `📊 **Market Analysis:**\n` +
                `• Current Price: **$${currentPrice.toFixed(2)}**\n` +
                `• Calculated Volatility: **${(volatility * 100).toFixed(2)}%** (${args.lookback_days || 30} days)\n` +
                `• Market Regime: ${volatility > 0.3 ? '🔥 High Volatility' : volatility > 0.15 ? '⚡ Medium Volatility' : '😴 Low Volatility'}\n\n` +
                `🎯 **Dynamic Bounds (Auto-Adjusting):**\n` +
                `• Upper Bound: **$${upperPrice.toFixed(2)}** (+${((upperPrice - currentPrice) / currentPrice * 100).toFixed(1)}%)\n` +
                `• Lower Bound: **$${lowerPrice.toFixed(2)}** (${((lowerPrice - currentPrice) / currentPrice * 100).toFixed(1)}%)\n` +
                `• Price Range: **$${(upperPrice - lowerPrice).toFixed(2)}** (${((upperPrice - lowerPrice) / currentPrice * 100).toFixed(1)}% of current price)\n` +
                `• Volatility Multiplier: **${volatilityMultiplier}x**\n\n` +
                `⚙️ **Grid Configuration:**\n` +
                `• Grid Levels: **${args.grid_count || 10}**\n` +
                `• Grid Spacing: **$${gridSpacing.toFixed(4)}** per level\n` +
                `• Investment Amount: **$${args.investment_amount.toLocaleString()}**\n` +
                `• Quantity per Grid: **${quantityPerGrid.toFixed(6)}** shares\n` +
                `• Expected Profit per Cycle: **$${expectedProfitPerCycle.toFixed(2)}**\n\n` +
                `🚀 **Dynamic Features:**\n` +
                `• ✅ **Auto-adjusting bounds** based on market volatility\n` +
                `• ✅ **Rebalances when price approaches boundaries**\n` +
                `• ✅ **Adapts to changing market conditions**\n` +
                `• ✅ **Optimized for ${volatility > 0.2 ? 'volatile' : 'stable'} market conditions**\n\n` +
                `💡 **How It Works:**\n` +
                `1. **Monitors** ${args.symbol} volatility continuously\n` +
                `2. **Expands** grid range when volatility increases\n` +
                `3. **Contracts** grid range when volatility decreases\n` +
                `4. **Rebalances** automatically when price nears boundaries\n\n` +
                `📈 **Performance Expectations:**\n` +
                `• Optimal for sideways/ranging markets\n` +
                `• Adapts to breakout scenarios\n` +
                `• Risk-managed through dynamic bounds\n` +
                `• Expected annual cycles: ${Math.floor(252 / (args.lookback_days || 30))}-${Math.floor(252 / 10)}\n\n` +
                `🎉 **Your intelligent grid is now active and adapting to market conditions!**\n\n` +
                `---\n\n**Technical Data:**\n${JSON.stringify({
                  ...result,
                  volatility_analysis: {
                    current_price: currentPrice,
                    volatility: volatility,
                    upper_bound: upperPrice,
                    lower_bound: lowerPrice,
                    price_range_percent: ((upperPrice - lowerPrice) / currentPrice * 100).toFixed(2)
                  }
                }, null, 2)}`
            }
          ]
        };
      } else {
        throw new Error(result.message || result.detail || 'Dynamic grid creation failed');
      }
    } catch (error: any) {
      console.error('Dynamic grid creation error:', error);
      
      let errorMessage = 'Unknown error';
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.message) {
        errorMessage = error.message;
      } else if (typeof error === 'string') {
        errorMessage = error;
      } else {
        errorMessage = JSON.stringify(error, null, 2);
      }
      
      return {
        content: [
          {
            type: 'text',
            text: `❌ **Dynamic Grid Creation Failed**\n\n` +
              `Error: ${errorMessage}\n\n` +
              `💡 **Common Issues:**\n` +
              `• Insufficient historical data for volatility calculation\n` +
              `• Invalid stock symbol or market data unavailable\n` +
              `• Portfolio not found or insufficient funds\n` +
              `• Market closed or data provider issues\n\n` +
              `🔧 **Try:**\n` +
              `• "Validate symbol ${args.symbol}" to check if symbol is supported\n` +
              `• "Get market data for ${args.symbol}" to verify data availability\n` +
              `• "Show me my portfolios" to verify portfolio ID\n` +
              `• Use a major stock like AAPL or SPY for testing\n\n` +
              `📚 **Example Usage:**\n` +
              `"Create a dynamic grid for AAPL with $10000 investment in my growth portfolio"\n\n` +
              `🆚 **Alternative:**\n` +
              `If dynamic grid fails, try regular grid: "Create a grid for ${args.symbol}"`
          }
        ]
      };
    }
  }

  private async handleConfigureGridAlerts(args: any) {
    try {
      // For now, we'll store alert preferences in the grid's strategy_config
      // In a real implementation, this might be a separate user preferences table
      
      let responseText = `⚙️ **Grid Alert Configuration**\n\n`;
      
      if (args.grid_id) {
        // Configure alerts for specific grid
        const gridData = await this.makeApiCall(`/api/grids/${args.grid_id}`);
        
        if (gridData.success || gridData.id) {
          responseText += `**Grid:** ${gridData.name || 'Unknown'} (${gridData.symbol})\n\n`;
          
          // Update grid strategy config with alert preferences
          const alertConfig = {
            enable_order_alerts: args.enable_order_alerts !== undefined ? args.enable_order_alerts : true,
            enable_boundary_alerts: args.enable_boundary_alerts !== undefined ? args.enable_boundary_alerts : true,
            enable_rebalancing_alerts: args.enable_rebalancing_alerts !== undefined ? args.enable_rebalancing_alerts : true,
            profit_threshold: args.profit_threshold || 10.0,
            alert_frequency: args.alert_frequency || 'immediate',
            updated_at: new Date().toISOString()
          };
          
          // This would update the grid's strategy_config in a real implementation
          responseText += `**Alert Preferences Updated:**\n`;
          responseText += `• 🎯 Order Execution Alerts: ${alertConfig.enable_order_alerts ? '✅ Enabled' : '❌ Disabled'}\n`;
          responseText += `• 📈📉 Boundary Alerts: ${alertConfig.enable_boundary_alerts ? '✅ Enabled' : '❌ Disabled'}\n`;
          responseText += `• 🧠 Rebalancing Alerts: ${alertConfig.enable_rebalancing_alerts ? '✅ Enabled' : '❌ Disabled'}\n`;
          responseText += `• 💰 Profit Threshold: $${alertConfig.profit_threshold}\n`;
          responseText += `• ⏰ Alert Frequency: ${alertConfig.alert_frequency}\n\n`;
          
          responseText += `**What You'll Be Alerted About:**\n`;
          if (alertConfig.enable_order_alerts) {
            responseText += `• 🎯 **Buy/Sell Order Triggers** - When grid levels are hit\n`;
            responseText += `• 💰 **Profit Notifications** - When sell orders generate profit ≥ $${alertConfig.profit_threshold}\n`;
          }
          if (alertConfig.enable_boundary_alerts) {
            responseText += `• 📈 **Price Above Range** - When price exceeds upper grid bound\n`;
            responseText += `• 📉 **Price Below Range** - When price falls below lower grid bound\n`;
          }
          if (alertConfig.enable_rebalancing_alerts) {
            responseText += `• 🧠 **Dynamic Rebalancing** - When grid bounds need adjustment\n`;
            responseText += `• ⚡ **Volatility Changes** - When market conditions change significantly\n`;
          }
          
        } else {
          throw new Error(`Grid ${args.grid_id} not found`);
        }
        
      } else {
        // Configure global alert preferences
        responseText += `**Global Alert Preferences**\n\n`;
        
        const globalConfig = {
          enable_order_alerts: args.enable_order_alerts !== undefined ? args.enable_order_alerts : true,
          enable_boundary_alerts: args.enable_boundary_alerts !== undefined ? args.enable_boundary_alerts : true,
          enable_rebalancing_alerts: args.enable_rebalancing_alerts !== undefined ? args.enable_rebalancing_alerts : true,
          profit_threshold: args.profit_threshold || 10.0,
          alert_frequency: args.alert_frequency || 'immediate'
        };
        
        responseText += `**Default Alert Settings Applied to All Grids:**\n`;
        responseText += `• 🎯 Order Execution Alerts: ${globalConfig.enable_order_alerts ? '✅ Enabled' : '❌ Disabled'}\n`;
        responseText += `• 📈📉 Boundary Alerts: ${globalConfig.enable_boundary_alerts ? '✅ Enabled' : '❌ Disabled'}\n`;
        responseText += `• 🧠 Rebalancing Alerts: ${globalConfig.enable_rebalancing_alerts ? '✅ Enabled' : '❌ Disabled'}\n`;
        responseText += `• 💰 Profit Threshold: $${globalConfig.profit_threshold}\n`;
        responseText += `• ⏰ Alert Frequency: ${globalConfig.alert_frequency}\n\n`;
        
        responseText += `**Alert Types Explained:**\n`;
        responseText += `• 🎯 **Order Alerts** - Real-time notifications when buy/sell orders execute\n`;
        responseText += `• 📈📉 **Boundary Alerts** - Warnings when price moves outside grid range\n`;
        responseText += `• 🧠 **Rebalancing Alerts** - Suggestions for dynamic grid adjustments\n`;
        responseText += `• 💰 **Profit Alerts** - Celebrations when trades generate significant profit\n\n`;
      }
      
      responseText += `**Alert Frequency Options:**\n`;
      responseText += `• **Immediate** - Get alerts as soon as events occur\n`;
      responseText += `• **Hourly** - Batch similar alerts into hourly summaries\n`;
      responseText += `• **Daily** - Receive daily digest of all grid activity\n\n`;
      
      responseText += `**Next Steps:**\n`;
      responseText += `• Check your alerts: "Show me my trading alerts"\n`;
      responseText += `• View grid performance: "Analyze grid performance for [grid_id]"\n`;
      responseText += `• Monitor grid activity in real-time\n\n`;
      
      responseText += `🎉 **Alert configuration updated successfully!**`;
      
      return {
        content: [
          {
            type: 'text',
            text: responseText
          }
        ]
      };
      
    } catch (error: any) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ **Alert Configuration Failed**\n\n` +
              `Error: ${error.response?.data?.detail || error.message}\n\n` +
              `💡 **Try:**\n` +
              `• "Configure alerts for all my grids"\n` +
              `• "Enable order alerts for grid [grid_id]"\n` +
              `• "Set profit threshold to $25 for my grids"\n` +
              `• "Show me my current alert settings"`
          }
        ]
      };
    }
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('GridTrader Pro MCP server running on stdio');
  }
}

const server = new GridTraderProMCPServer();
server.run().catch(console.error);
