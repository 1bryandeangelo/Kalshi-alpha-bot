#!/usr/bin/env python3
“””
Test script for Kalshi Alpha Bot
“””

import os
import sys

def test_setup():
“”“Check environment”””
print(”\n” + “=”*60)
print(“TESTING KALSHI BOT SETUP”)
print(”=”*60 + “\n”)

```
required = {
    'ANTHROPIC_API_KEY': 'Claude API',
    'KALSHI_EMAIL': 'Kalshi email',
    'KALSHI_PASSWORD': 'Kalshi password'
}

all_good = True
for key, desc in required.items():
    value = os.getenv(key)
    if value:
        if 'PASSWORD' in key:
            print(f"  ✅ {desc}: ********")
        else:
            print(f"  ✅ {desc}: {value[:15]}...")
    else:
        print(f"  ❌ {desc}: NOT SET")
        all_good = False

print()
return all_good
```

def test_dependencies():
“”“Test packages”””
print(“Testing dependencies…”)

```
try:
    import anthropic
    print("  ✅ anthropic")
except:
    print("  ❌ anthropic - Run: pip install anthropic")
    return False

try:
    import requests
    print("  ✅ requests")
except:
    print("  ❌ requests - Run: pip install requests")
    return False

print()
return True
```

def test_kalshi_api():
“”“Test Kalshi authentication”””
print(“Testing Kalshi API…”)

```
try:
    from kalshi_bot import KalshiAlphaBot
    
    bot = KalshiAlphaBot()
    
    if bot.login_kalshi():
        print("  ✅ Kalshi authentication successful\n")
        
        # Try fetching markets
        markets = bot.get_active_markets()
        if markets:
            print(f"  ✅ Found {len(markets)} active markets")
            print(f"  Sample: {markets[0].get('title', 'N/A')[:60]}...\n")
            return True
        else:
            print("  ⚠️  No markets returned\n")
            return False
    else:
        print("  ❌ Authentication failed\n")
        return False
        
except Exception as e:
    print(f"  ❌ Error: {e}\n")
    return False
```

def test_claude():
“”“Test Claude API”””
print(“Testing Claude API…”)

```
try:
    from anthropic import Anthropic
    
    client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=20,
        messages=[{"role": "user", "content": "Say 'Ready'"}]
    )
    
    print(f"  ✅ Claude: {message.content[0].text}\n")
    return True
    
except Exception as e:
    print(f"  ❌ Error: {e}\n")
    return False
```

def main():
“”“Run tests”””
print(”\n🔍 KALSHI ALPHA BOT - SETUP TEST\n”)

```
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

results = {
    'Environment': test_setup(),
    'Dependencies': test_dependencies(),
    'Claude API': test_claude(),
    'Kalshi API': test_kalshi_api()
}

print("="*60)
print("RESULTS")
print("="*60 + "\n")

for name, passed in results.items():
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"  {name}: {status}")

all_passed = all(results.values())

print()
if all_passed:
    print("🎉 ALL TESTS PASSED!")
    print("\nNext steps:")
    print("  1. Run: python kalshi_bot.py")
    print("  2. Paper trade for 1-2 weeks")
    print("  3. Deploy to Render (see KALSHI_DEPLOYMENT.md)")
else:
    print("⚠️  Fix issues above.")

print()
return 0 if all_passed else 1
```

if **name** == “**main**”:
sys.exit(main())
