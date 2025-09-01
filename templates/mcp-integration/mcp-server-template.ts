/**
 * Universal MCP Server Template
 * Customize this template for any web application
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';
import axios from 'axios';

interface CreateItemRequest {  // Replace with your entity
  name: string;
  description?: string;
  // Add your specific fields
}

class YourAppMCPServer {  // Replace with your app name
  private server: Server;
  private apiUrl: string;
  private accessToken: string;

  constructor() {
    this.server = new Server(
      {
        name: 'your-app-mcp',  // Replace with your app name
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.apiUrl = process.env.YOUR_APP_API_URL || 'https://your-domain.com';  // Replace
    this.accessToken = process.env.YOUR_APP_ACCESS_TOKEN || '';  // Replace

    this.setupToolHandlers();
  }

  private async makeApiCall(endpoint: string, method = 'GET', data?: any) {
    try {
      const response = await axios({
        method,
        url: `${this.apiUrl}${endpoint}`,
        headers: {
          'Authorization': `Bearer ${this.accessToken}`,
          'Content-Type': 'application/json',
        },
        data,
      });
      return response.data;
    } catch (error: any) {
      console.error('API call failed:', error.response?.data || error.message);
      throw error;
    }
  }

  private setupToolHandlers() {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: 'get_data_list',  // Replace with your main data function
            description: 'Get list of your app data',
            inputSchema: {
              type: 'object',
              properties: {
                include_details: {
                  type: 'boolean',
                  description: 'Include detailed information',
                  default: true
                }
              }
            }
          },
          {
            name: 'get_items',  // Replace with your entities
            description: 'Get list of items',
            inputSchema: {
              type: 'object',
              properties: {
                limit: {
                  type: 'number',
                  description: 'Maximum number of items to return',
                  default: 10
                }
              }
            }
          },
          {
            name: 'create_item',  // Replace with your creation function
            description: 'Create a new item',
            inputSchema: {
              type: 'object',
              properties: {
                name: {
                  type: 'string',
                  description: 'Name of the item'
                },
                description: {
                  type: 'string',
                  description: 'Description of the item'
                }
                // Add your specific fields
              },
              required: ['name']
            }
          },
          {
            name: 'get_dashboard_summary',
            description: 'Get dashboard overview and summary statistics',
            inputSchema: {
              type: 'object',
              properties: {
                include_metrics: {
                  type: 'boolean',
                  description: 'Include detailed metrics',
                  default: true
                }
              }
            }
          },
          // Add more tools based on your app's functionality
        ],
      };
    });

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      switch (request.params.name) {
        case 'get_data_list':
          return await this.handleGetDataList(request.params.arguments);
        case 'get_items':
          return await this.handleGetItems(request.params.arguments);
        case 'create_item':
          return await this.handleCreateItem(request.params.arguments);
        case 'get_dashboard_summary':
          return await this.handleGetDashboardSummary(request.params.arguments);
        default:
          throw new Error(`Unknown tool: ${request.params.name}`);
      }
    });
  }

  private async handleGetDataList(args: any) {
    try {
      const data = await this.makeApiCall('/api/data');
      
      const summary = `📊 **Your App Data Overview**\n\n` +
        `Found ${data.items?.length || 0} items:\n\n`;
      
      let resultsText = summary;
      
      if (data.items && data.items.length > 0) {
        resultsText += data.items.map((item: any, index: number) => {
          return `**${index + 1}. ${item.name}**\n` +
            `   ID: ${item.id}\n` +
            `   Description: ${item.description || 'No description'}\n` +
            `   Created: ${new Date(item.created_at).toLocaleDateString()}\n`;
        }).join('\n');
      } else {
        resultsText += `No items found. Create your first item to get started!`;
      }
      
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
            text: `❌ Failed to get data: ${error.response?.data?.detail || error.message}`
          }
        ]
      };
    }
  }

  private async handleGetItems(args: any) {
    try {
      const data = await this.makeApiCall('/api/items');
      
      const items = data.items || [];
      let resultsText = `📋 **Your Items** (${items.length} total)\n\n`;
      
      if (items.length > 0) {
        resultsText += items.slice(0, args.limit || 10).map((item: any, index: number) => {
          return `**${index + 1}. ${item.name}**\n` +
            `   ID: ${item.id}\n` +
            `   Status: ${item.status || 'Active'}\n`;
        }).join('\n');
      } else {
        resultsText += `No items found. Create your first item!`;
      }
      
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
            text: `❌ Failed to get items: ${error.response?.data?.detail || error.message}`
          }
        ]
      };
    }
  }

  private async handleCreateItem(args: any) {
    try {
      const result = await this.makeApiCall('/api/items', 'POST', {
        name: args.name,
        description: args.description || ''
      });
      
      return {
        content: [
          {
            type: 'text',
            text: `✅ Successfully created item: **${args.name}**\n\n` +
                  `ID: ${result.id}\n` +
                  `Description: ${args.description || 'No description'}\n\n` +
                  `You can now manage this item through your app interface.`
          }
        ]
      };
    } catch (error: any) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ Failed to create item: ${error.response?.data?.detail || error.message}`
          }
        ]
      };
    }
  }

  private async handleGetDashboardSummary(args: any) {
    try {
      const data = await this.makeApiCall('/api/dashboard/summary');
      
      const resultsText = `📊 **Dashboard Summary**\n\n` +
        `👤 User: ${data.user_name || 'Unknown'}\n` +
        `📈 Total Items: ${data.total_items || 0}\n` +
        `🕒 Last Updated: ${new Date(data.last_updated).toLocaleString()}\n\n` +
        `**Quick Actions:**\n` +
        `• Ask: "Show me my items"\n` +
        `• Ask: "Create a new item called 'Test'"\n` +
        `• Ask: "What's my app summary?"`;
      
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
            text: `❌ Failed to get dashboard summary: ${error.response?.data?.detail || error.message}`
          }
        ]
      };
    }
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Your App MCP server running on stdio');
  }
}

const server = new YourAppMCPServer();
server.run().catch(console.error);
