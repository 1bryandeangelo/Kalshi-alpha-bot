import os
import requests
from datetime import datetime, timedelta
from anthropic import Anthropic
import time
import json

class KalshiAlphaBot:
“””
Automated Kalshi trading bot
Scans markets, researches with Claude, provides BUY/PASS recommendations

```
Focus: Economic data, politics, Fed decisions - researchable events
"""

def __init__(self):
    self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    self.claude = Anthropic(api_key=self.anthropic_key)
    
    # Kalshi API endpoints
    self.kalshi_api = "https://api.elections.kalshi.com/trade-api/v2"
    self.kalshi_email = os.getenv('KALSHI_EMAIL')
    self.kalshi_password = os.getenv('KALSHI_PASSWORD')
    
    # Authentication token (will be set on login)
    self.auth_token = None
    
def login_kalshi(self):
    """Authenticate with Kalshi API"""
    try:
        url = f"{self.kalshi_api}/login"
        payload = {
            "email": self.kalshi_email,
            "password": self.kalshi_password
        }
        
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        self.auth_token = data.get('token')
        
        if self.auth_token:
            print("✅ Authenticated with Kalshi")
            return True
        else:
            print("❌ Authentication failed - no token received")
            return False
            
    except Exception as e:
        print(f"❌ Kalshi login error: {e}")
        return False

def get_headers(self):
    """Get authenticated headers for API requests"""
    return {
        'Authorization': f'Bearer {self.auth_token}',
        'Content-Type': 'application/json'
    }

def get_active_markets(self):
    """Fetch active markets from Kalshi"""
    try:
        url = f"{self.kalshi_api}/markets"
        params = {
            'limit': 200,  # Get more markets
            'status': 'open'  # Only open markets
        }
        
        response = requests.get(url, headers=self.get_headers(), params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        markets = data.get('markets', [])
        
        print(f"✅ Found {len(markets)} active markets")
        return markets
        
    except Exception as e:
        print(f"❌ Error fetching markets: {e}")
        return []

def calculate_alpha_score(self, market):
    """
    Calculate alpha potential for Kalshi markets
    Focus on: researchable events, volume, time to resolution, odds
    """
    score = 0
    
    # Market category scoring (prefer researchable events)
    category = market.get('category', '').lower()
    ticker = market.get('ticker', '').lower()
    title = market.get('title', '').lower()
    
    # High-value categories (more researchable)
    if any(term in category or term in ticker or term in title for term in [
        'fed', 'interest', 'inflation', 'cpi', 'unemployment', 'jobs',
        'gdp', 'economy', 'congress', 'senate', 'election', 'vote'
    ]):
        score += 4
    
    # Medium-value categories
    elif any(term in category or term in ticker or term in title for term in [
        'politics', 'president', 'government', 'regulation', 'weather',
        'earnings', 'supreme', 'court'
    ]):
        score += 2
    
    # Skip sports/entertainment (too random)
    if any(term in category or term in ticker or term in title for term in [
        'nba', 'nfl', 'mlb', 'nhl', 'soccer', 'sports', 'game',
        'championship', 'super bowl', 'world series'
    ]):
        score -= 3
    
    # Volume score (liquidity matters)
    volume = float(market.get('volume', 0))
    if volume > 100000:
        score += 3
    elif volume > 50000:
        score += 2
    elif volume > 10000:
        score += 1
    
    # Open interest (how many contracts outstanding)
    open_interest = float(market.get('open_interest', 0))
    if open_interest > 50000:
        score += 2
    elif open_interest > 10000:
        score += 1
    
    # Time to resolution (prefer 1-4 weeks out)
    close_time = market.get('close_time')
    if close_time:
        try:
            close_date = datetime.fromisoformat(close_time.replace('Z', '+00:00'))
            days_until = (close_date - datetime.now().astimezone()).days
            
            if 7 <= days_until <= 60:  # 1 week to 2 months
                score += 2
            elif days_until < 7:  # Too soon (hard to research)
                score -= 1
            elif days_until > 180:  # Too far (too uncertain)
                score -= 1
        except:
            pass
    
    # Odds competitiveness (not too one-sided)
    yes_price = market.get('yes_bid', 0)
    no_price = market.get('no_bid', 0)
    
    # Convert cents to probability
    yes_prob = yes_price / 100 if yes_price else 0.5
    
    # Prefer competitive markets (20-80% range)
    if 0.20 <= yes_prob <= 0.80:
        score += 2
    
    return max(0, score)  # Don't allow negative scores

def filter_high_alpha_markets(self, markets, min_score=4):
    """Filter markets by alpha score"""
    scored_markets = []
    
    for market in markets:
        score = self.calculate_alpha_score(market)
        if score >= min_score:
            market['alpha_score'] = score
            scored_markets.append(market)
    
    # Sort by score descending
    scored_markets.sort(key=lambda x: x['alpha_score'], reverse=True)
    
    print(f"✅ Filtered to {len(scored_markets)} high-alpha markets (score >= {min_score})")
    return scored_markets

def research_and_validate(self, market):
    """
    Use Claude with web search to research and validate the market
    """
    
    title = market.get('title', '')
    ticker = market.get('ticker', '')
    category = market.get('category', '')
    yes_price = market.get('yes_bid', 0)
    no_price = market.get('no_bid', 0)
    volume = market.get('volume', 0)
    close_time = market.get('close_time', '')
    
    # Format close time
    close_date = "Unknown"
    try:
        close_dt = datetime.fromisoformat(close_time.replace('Z', '+00:00'))
        close_date = close_dt.strftime('%B %d, %Y')
    except:
        pass
    
    # Calculate implied probability
    yes_prob = yes_price / 100 if yes_price else 0
    no_prob = no_price / 100 if no_price else 0
    
    prompt = f"""You are an expert prediction market analyst researching Kalshi opportunities.
```

MARKET DETAILS:
Title: {title}
Category: {category}
Ticker: {ticker}

CURRENT MARKET ODDS:

- YES: {yes_prob:.1%} (${yes_price/100:.2f})
- NO: {no_prob:.1%} (${no_price/100:.2f})

MARKET INFO:

- Volume: ${volume:,.0f}
- Closes: {close_date}

YOUR TASK:
Research this market thoroughly using web search. This is a real-money trading opportunity.

RESEARCH:

1. Search for current, credible information about this event
1. Find expert predictions, polls, data, historical precedents
1. Identify key factors that will determine the outcome
1. Look for information the market might be missing or mispricing

ANALYZE:

1. What is the TRUE probability of YES based on your research?
1. Is the current market price ({yes_prob:.1%} YES) accurate?
1. Is there a clear mispricing opportunity?
1. What are the key risks or uncertainties?

PROVIDE YOUR ANALYSIS:

**RESEARCH SUMMARY:**
[3-4 sentences on what current sources say about this event]

**KEY FACTORS:**

- [Factor 1]
- [Factor 2]
- [Factor 3]

**TRUE PROBABILITY ESTIMATE:**
[Your best estimate: X% YES, based on research]

**MARKET ANALYSIS:**
Market says: {yes_prob:.1%} YES
Research suggests: [Your %] YES
Mispricing: [Explain if market is overpricing or underpricing]

**RECOMMENDATION:**
One of: BUY YES | BUY NO | PASS

**CONFIDENCE:**
One of: HIGH | MEDIUM | LOW

**POSITION SIZE:**
Based on confidence and edge: SMALL (1-2%) | MEDIUM (3-5%) | LARGE (5-10%) | PASS

**REASONING:**
[2-3 sentences: Why this recommendation? What’s the edge? What could go wrong?]

**SOURCES:**
[List URLs used in research]

Be critical. Only recommend BUY if there’s clear mispricing supported by evidence.
Most markets should be PASS - we’re looking for rare opportunities with edge.”””

```
    try:
        message = self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            tools=[{
                "type": "web_search_20250305",
                "name": "web_search"
            }],
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Extract response
        full_response = ""
        for block in message.content:
            if hasattr(block, 'text'):
                full_response += block.text
        
        # Parse recommendation
        recommendation = "PASS"
        if "BUY YES" in full_response.upper():
            recommendation = "BUY YES"
        elif "BUY NO" in full_response.upper():
            recommendation = "BUY NO"
        
        # Parse confidence
        confidence = "UNKNOWN"
        if "HIGH" in full_response.upper():
            confidence = "HIGH"
        elif "MEDIUM" in full_response.upper():
            confidence = "MEDIUM"
        elif "LOW" in full_response.upper():
            confidence = "LOW"
        
        return {
            'analysis': full_response,
            'recommendation': recommendation,
            'confidence': confidence,
            'success': True
        }
        
    except Exception as e:
        print(f"❌ Error with Claude analysis: {e}")
        return {
            'analysis': f"Error: {str(e)}",
            'recommendation': "PASS",
            'confidence': "UNKNOWN",
            'success': False
        }

def run_daily_scan(self, top_n=10, min_alpha_score=4):
    """
    Main workflow: authenticate, scan, filter, research, validate
    """
    
    print(f"\n{'='*70}")
    print(f"🎯 KALSHI ALPHA BOT")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")
    
    # Step 1: Authenticate
    if not self.login_kalshi():
        print("❌ Authentication failed. Check credentials.")
        return []
    
    # Step 2: Get active markets
    print("\n📊 Fetching active markets...")
    markets = self.get_active_markets()
    if not markets:
        print("❌ No markets found. Exiting.")
        return []
    
    # Step 3: Filter for high-alpha opportunities
    print(f"\n🔍 Filtering for alpha opportunities (min score: {min_alpha_score})...")
    high_alpha = self.filter_high_alpha_markets(markets, min_score=min_alpha_score)
    
    if not high_alpha:
        print(f"❌ No markets with alpha score >= {min_alpha_score}")
        return []
    
    # Step 4: Research top N markets
    top_markets = high_alpha[:top_n]
    print(f"\n🎯 Researching top {len(top_markets)} markets...\n")
    
    results = []
    
    for i, market in enumerate(top_markets, 1):
        title = market.get('title', 'Unknown')[:70]
        print(f"[{i}/{len(top_markets)}] {title}...")
        
        # Research and validate
        analysis = self.research_and_validate(market)
        
        if not analysis['success']:
            print(f"  ⚠️  Analysis failed")
            continue
        
        # Only include actionable plays
        if analysis['recommendation'] != 'PASS':
            print(f"  ✅ {analysis['recommendation']} | {analysis['confidence']} confidence")
            results.append({
                'market': market,
                'analysis': analysis
            })
        else:
            print(f"  ⏭️  PASS")
        
        # Rate limiting
        if i < len(top_markets):
            time.sleep(2)
    
    # Step 5: Generate report
    print(f"\n📝 Generating report...")
    self.generate_report(results)
    
    return results

def generate_report(self, results):
    """Generate actionable trading report"""
    
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"kalshi_report_{timestamp}.txt"
    filepath = f"/tmp/{filename}"
    
    report = []
    report.append("="*80)
    report.append(f"KALSHI ALPHA TRADING REPORT")
    report.append(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("="*80)
    report.append(f"\n💰 Found {len(results)} actionable opportunities\n")
    
    if len(results) == 0:
        report.append("No BUY recommendations today.")
        report.append("\nAll markets analyzed were fairly priced or lacked clear edge.")
        report.append("\nThis is normal - most markets are efficient.")
        report.append("Keep scanning daily for rare mispricing opportunities.")
    
    for i, result in enumerate(results, 1):
        market = result['market']
        analysis = result['analysis']
        
        title = market.get('title', 'N/A')
        ticker = market.get('ticker', 'N/A')
        yes_price = market.get('yes_bid', 0)
        no_price = market.get('no_bid', 0)
        volume = market.get('volume', 0)
        close_time = market.get('close_time', '')
        
        # Format close time
        close_date = "Unknown"
        try:
            close_dt = datetime.fromisoformat(close_time.replace('Z', '+00:00'))
            close_date = close_dt.strftime('%B %d, %Y')
            days_until = (close_dt - datetime.now().astimezone()).days
            close_date += f" ({days_until} days)"
        except:
            pass
        
        report.append(f"\n{'─'*80}")
        report.append(f"OPPORTUNITY #{i}: {analysis['recommendation']}")
        report.append(f"Confidence: {analysis['confidence']} | Alpha Score: {market.get('alpha_score', 0)}")
        report.append(f"{'─'*80}")
        report.append(f"\n📋 MARKET: {title}")
        report.append(f"Ticker: {ticker}")
        report.append(f"\n📊 CURRENT ODDS:")
        report.append(f"  • YES: {yes_price/100:.1%} (${yes_price/100:.2f})")
        report.append(f"  • NO: {no_price/100:.1%} (${no_price/100:.2f})")
        report.append(f"\n📈 MARKET DATA:")
        report.append(f"  • Volume: ${volume:,.0f}")
        report.append(f"  • Closes: {close_date}")
        report.append(f"\n🔍 ANALYSIS:")
        report.append(analysis['analysis'])
        report.append(f"\n{'─'*80}\n")
    
    report_text = "\n".join(report)
    
    # Save to file
    try:
        with open(filepath, 'w') as f:
            f.write(report_text)
        print(f"✅ Report saved: {filepath}")
    except Exception as e:
        print(f"⚠️  Could not save: {e}")
    
    # Print to console
    print(f"\n{report_text}")
    
    return filepath
```

def main():
“”“Main entry point”””
bot = KalshiAlphaBot()

```
# Run scan
# Customize: top_n (markets to analyze), min_alpha_score (filtering threshold)
results = bot.run_daily_scan(top_n=10, min_alpha_score=4)

print(f"\n✅ Scan complete! Found {len(results)} actionable plays.")

return len(results)
```

if **name** == “**main**”:
main()
