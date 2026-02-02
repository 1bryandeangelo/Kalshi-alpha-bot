# Kalshi Alpha Bot

**Automated prediction market scanner for Kalshi - Find edge through research, not gambling.**

## What It Does

- 🔍 Scans all active Kalshi markets daily
- 📊 Filters for high-alpha opportunities (Fed decisions, economic data, elections)
- 🧠 Researches each market with Claude + web search
- 🎯 Provides BUY YES / BUY NO / PASS recommendations
- 💪 Focuses on researchable events, NOT sports betting

## Why Kalshi?

✅ **Legal & regulated** (CFTC-approved in US)  
✅ **No waitlist** - trade immediately ($100 to start)  
✅ **Better markets** - Economic data, Fed decisions, politics  
✅ **Real edge potential** - Research-based opportunities

vs Polymarket (700k+ waitlist, mostly sports betting)

## Cost

**~$20/month:**

- Claude API: ~$18-20/month
- Render hosting: FREE
- Kalshi: FREE (just your trading capital)

## Quick Setup

1. **Create Kalshi account**: https://kalshi.com (fund with $100+)
1. **Get Claude API key**: https://console.anthropic.com
1. **Push to GitHub**: Upload these files
1. **Deploy to Render**: Cron job, schedule `0 14 * * *`
1. **Add env vars**: ANTHROPIC_API_KEY, KALSHI_EMAIL, KALSHI_PASSWORD
1. **Test**: Click “Trigger Run” in Render

**Full instructions**: See KALSHI_DEPLOYMENT.md

## What You Get

Daily report with actionable opportunities:

```
OPPORTUNITY #1: BUY YES
Confidence: HIGH | Alpha Score: 8

📋 MARKET: Will the Fed raise rates in March?

📊 CURRENT ODDS:
  • YES: 72% ($0.72)
  • NO: 28% ($0.28)

🔍 ANALYSIS:
[Claude's research summary]
[Key factors]
[True probability estimate]
[Edge calculation]
[Position sizing recommendation]
[Sources with links]
```

## Files

- `kalshi_bot.py` - Main bot
- `test_kalshi_bot.py` - Test setup
- `render.yaml` - Render deployment config
- `.env.example` - Environment variables
- `KALSHI_DEPLOYMENT.md` - Complete guide
- `README.md` - This file

## Alpha Scoring

Markets scored 0-10+ based on:

- **Category** (+4): Fed, inflation, elections, economic data
- **Volume** (+3): >$100k highly liquid
- **Time horizon** (+2): 1 week to 2 months (research window)
- **Odds** (+2): 20-80% competitive (not one-sided)
- **Sports penalty** (-3): Avoids NBA, NFL, etc.

Only markets scoring 4+ are analyzed.

## Strategy

**Position Sizing:**

- HIGH confidence: 5-10% of bankroll
- MEDIUM confidence: 2-5% of bankroll
- LOW confidence: 1-2% or skip

**Focus Markets:**

- ✅ Fed decisions
- ✅ CPI/inflation data
- ✅ Unemployment reports
- ✅ Elections with polling
- ✅ Congressional votes
- ❌ Sports (no edge)
- ❌ Crypto prices (too volatile)

## Expected Results

**Reality:**

- Most markets → PASS (correctly priced)
- 1-3 opportunities per week is good
- Target 55-60% win rate
- Small edge compounds over time

**With $100 starting capital:**

- Good outcome: $150-200 after 6 months
- Requires discipline and tracking

## Test Locally

```bash
pip install -r requirements.txt
cp .env.example .env
# Add your credentials to .env
python test_kalshi_bot.py
python kalshi_bot.py
```

## Customization

**Change schedule** (render.yaml):

```yaml
schedule: "0 14 * * *"  # Daily 10 AM EST
schedule: "0 14 * * 1-5"  # Weekdays only
```

**Focus categories** (kalshi_bot.py):

```python
# Only Fed/economic markets
if 'fed' in title or 'inflation' in title:
    score += 5
```

**Adjust risk** (prompt in research_and_validate):

```python
"Only recommend BUY if edge >15%"  # More conservative
```

## iPad Friendly

Once deployed:

- Bot runs automatically daily
- Check Render logs from Safari
- Trade on Kalshi app/website
- No computer needed!

## Important Notes

⚠️ **Not guaranteed profit** - Markets are efficient  
⚠️ **Start small** - Paper trade first, then 1-2% positions  
⚠️ **Track results** - Spreadsheet of all recommendations  
⚠️ **Your judgment** - Bot is a tool, not financial advice  
⚠️ **Check legality** - Available in most US states

## Support

- **Kalshi**: https://kalshi.com/help
- **Claude API**: https://docs.anthropic.com
- **Render**: https://render.com/docs
- **Deployment**: See KALSHI_DEPLOYMENT.md

-----

**Built with Claude. Researched with care. Traded with discipline.**

Find edge through research, not luck. 🎯
