# Claude API Cost Guide

## Current Implementation Costs

### Claude Sonnet 4 Pricing
- **Input tokens**: $3.00 per million tokens
- **Output tokens**: $15.00 per million tokens

### Actual Usage per Contract

Based on testing with sample contracts:

| Contract Type | Input Tokens | Output Tokens | Cost per Contract |
|--------------|--------------|---------------|-------------------|
| Bulk Carrier (001) | ~2,434 | ~703 | **$0.018** |
| Tanker (002) | ~3,000-3,500 | ~700-800 | **$0.020-0.023** |
| Container (003) | ~3,500-4,000 | ~700-800 | **$0.023-0.025** |

**Average cost per contract: ~$0.02 (2 cents)**

### Batch Processing Costs

| Number of Contracts | Estimated Total Cost |
|---------------------|---------------------|
| 10 contracts | $0.20 |
| 50 contracts | $1.00 |
| 100 contracts | $2.00 |
| 500 contracts | $10.00 |
| 1,000 contracts | $20.00 |

## Cost Optimization Features

### 1. Reduced max_tokens
- Changed from 4000 to 2000 tokens
- Saves ~$0.015 per contract if full tokens were used
- Still sufficient for structured extraction

### 2. Retry Logic with Backoff
- Only retries on actual errors
- Exponential backoff prevents rapid retries
- Default: 3 attempts maximum

### 3. Real-time Cost Tracking
The system displays actual costs for each extraction:
```
  - Actual tokens: 2434 input, 703 output
  - Estimated cost: $0.0178
```

## Cost Control Recommendations

### For Testing (Your Current Use)
1. **Test with single contracts first**
   ```python
   python test_with_cost_tracking.py  # ~$0.02
   ```

2. **Limit batch processing during development**
   ```python
   # Process only first N files
   pdf_files = list(CONTRACTS_DIR.glob("*.pdf"))[:3]
   ```

3. **Use the test scripts** - they show costs before committing to batch processing

### For Production Use

1. **Batch Processing Strategy**
   - Process contracts in small batches
   - Monitor cumulative costs
   - Set a daily/monthly budget limit

2. **Add Budget Guards** (optional)
   ```python
   DAILY_BUDGET_USD = 5.00  # Set your limit
   daily_spent = 0.0

   if daily_spent + estimated_cost > DAILY_BUDGET_USD:
       raise Exception("Daily budget limit reached")
   ```

3. **Cache Results**
   - Save extracted data to avoid re-processing
   - The current system already does this (Excel files)

## Error Handling & Retries

### Retry Scenarios
The system automatically retries (up to 3 times) on:
- Network errors
- API temporary unavailability
- JSON parsing errors
- Invalid responses

### Cost of Retries
- **First attempt fails**: Full token cost charged
- **Second attempt**: Additional ~$0.02 charged
- **Third attempt**: Additional ~$0.02 charged

**Maximum cost with retries: ~$0.06 per contract** (rare)

## Cost Comparison

### Alternative Approaches

| Method | Cost per Contract | Accuracy | Speed |
|--------|------------------|----------|-------|
| **Claude Sonnet 4** | **$0.02** | **Very High** | **Fast (2-5s)** |
| Claude Haiku | $0.001 | Medium | Very Fast |
| Manual entry | $5-10 (labor) | High | Slow (10-20 min) |
| Traditional NLP | Setup cost $$$ | Medium | Fast |

**Claude Sonnet 4 offers best accuracy-to-cost ratio for complex documents**

## Monitoring Usage

### Real-time Monitoring
The system prints costs for each contract:
```
Processing contract: tcp_contract_001.pdf
  - Estimated input tokens: ~1292
  - Actual tokens: 2434 input, 703 output
  - Estimated cost: $0.0178
```

### Total Usage Tracking
Check your Anthropic dashboard:
- https://console.anthropic.com/
- View usage statistics
- Set up billing alerts

## Example Cost Scenarios

### Scenario 1: Small Law Firm
- **Volume**: 20 contracts/month
- **Cost**: $0.40/month
- **Savings vs manual**: ~$100-200/month

### Scenario 2: Shipping Company
- **Volume**: 100 contracts/month
- **Cost**: $2.00/month
- **Savings vs manual**: ~$500-1000/month

### Scenario 3: Large Broker
- **Volume**: 500 contracts/month
- **Cost**: $10.00/month
- **Savings vs manual**: ~$2500-5000/month

## API Rate Limits

Claude API limits (as of Dec 2024):
- **Requests per minute**: 50
- **Tokens per minute**: 40,000
- **Tokens per day**: 1,000,000

For processing contracts:
- **Safe rate**: ~20 contracts/minute
- **Daily capacity**: ~50,000 contracts/day (far exceeds typical needs)

## Cost Reduction Tips

### 1. Pre-filter PDFs
Only process relevant pages if contracts have appendices:
```python
# Extract only first 10 pages
text = extract_text_from_pdf(pdf_path, max_pages=10)
```

### 2. Use Haiku for Simple Contracts
For very simple contracts, consider Claude Haiku (~$0.001/contract)

### 3. Batch Similar Contracts
Process contracts from same template together for efficiency

### 4. Cache Common Clauses
Store and reuse standard clauses (future enhancement)

## Budget Planning

### Conservative Estimate
- Add 50% buffer for retries and errors
- Example: 100 contracts = $2.00 × 1.5 = **$3.00 budget**

### Recommended Monthly Budgets

| Use Case | Contracts/Month | Recommended Budget |
|----------|-----------------|-------------------|
| Testing | 10-50 | $2-5 |
| Small Business | 50-200 | $5-10 |
| Medium Business | 200-1000 | $10-30 |
| Enterprise | 1000+ | $30-100 |

## Current Status

**Your implementation includes:**
- ✅ Real-time cost tracking
- ✅ Automatic retry with backoff (max 3 attempts)
- ✅ Error handling for API failures
- ✅ Token usage optimization (2000 max_tokens)
- ✅ Detailed logging of costs

**Safety Features:**
- Fails gracefully on errors
- Displays costs before batch processing
- Test scripts available for validation

## Questions?

**Q: What if I hit my budget limit?**
A: Set up billing alerts in Anthropic console, or add budget checks in code

**Q: Can I reduce costs further?**
A: Yes - reduce max_tokens, use Claude Haiku, or process fewer fields

**Q: What about rate limiting?**
A: Current implementation processes ~1 contract every 2-5 seconds, well within limits

**Q: How do I track total monthly costs?**
A: Check Anthropic console dashboard for real-time usage and billing
