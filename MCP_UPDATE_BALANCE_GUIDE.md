# 💰 Update Balance Tool - GridTrader Pro MCP

## Overview
The `update_balance` tool allows you to update portfolio cash balances directly from Cursor using natural language commands.

## Usage Examples

### Basic Balance Update
```
Update my portfolio balance to $50000
```

### Balance Update with Notes
```
Update portfolio 3d378b4f-d66e-48b7-9617-25f37d074546 balance to $75000 with note "Bank deposit received"
```

### Interest Earned Update
```
Set my JC portfolio cash balance to $8500000 with note "Interest earned from savings"
```

## Tool Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `portfolio_id` | string | ✅ | Portfolio ID to update |
| `new_cash_balance` | number | ✅ | New cash balance amount |
| `notes` | string | ❌ | Optional notes explaining the update |

## Response Details

### Success Response
- ✅ Previous and new balance amounts
- 💰 Balance change calculation
- 📊 Updated total portfolio value
- 📝 Audit trail transaction created
- 🎯 Next steps suggestions

### Error Handling
- Invalid portfolio ID detection
- Negative balance prevention
- Authentication error handling
- Clear troubleshooting guidance

## Behind the Scenes

1. **API Call**: `POST /api/portfolios/{portfolio_id}/update-cash`
2. **Validation**: Checks portfolio ownership and balance validity
3. **Audit Trail**: Creates transaction record with timestamp
4. **Portfolio Update**: Recalculates total portfolio value
5. **Response**: Returns detailed success/failure information

## Integration with Other Tools

Combine with other MCP tools for complete portfolio management:

```
Show me all my portfolios
Update my main portfolio balance to $100000 with note "Quarterly bonus"
Show me portfolio details for my updated portfolio
```

## Security Features

- ✅ API token authentication
- ✅ Portfolio ownership verification
- ✅ Input validation and sanitization
- ✅ Detailed audit logging
- ✅ Transaction history tracking

## Tips for Best Results

1. **Use descriptive notes** to track balance changes
2. **Check portfolio ID** with "Show me all my portfolios" first
3. **Verify results** with portfolio details after update
4. **Include context** in notes for better audit trail

---

🚀 **Ready to use!** Just restart your MCP server and start updating balances with natural language commands.

