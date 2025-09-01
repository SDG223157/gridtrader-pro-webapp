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

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('GridTrader Pro MCP server running on stdio');
  }
}

const server = new GridTraderProMCPServer();
server.run().catch(console.error);
