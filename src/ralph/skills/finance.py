import requests
from ralph.core import secrets
from pathlib import Path
import typer

def get_market_snapshot(symbols: list[str]) -> str:
    """
    Gets current price and change for a list of stocks using FMP.
    """
    api_key = secrets.fmp_key()
    if not api_key:
        return "FMP API key not found."
    
    symbols_str = ",".join(symbols)
    url = f"https://financialmodelingprep.com/api/v3/quote/{symbols_str}?apikey={api_key}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        report = []
        for stock in data:
            report.append(f"{stock['symbol']}: ${stock['price']} ({stock['changesPercentage']}%)")
        return "\n".join(report) if report else "No data found for symbols."
    except Exception as e:
        return f"Market check failed: {e}"

def get_company_news(symbol: str) -> str:
    """
    Gets latest news for a specific symbol using FMP.
    """
    api_key = secrets.fmp_key()
    url = f"https://financialmodelingprep.com/api/v3/stock_news?tickers={symbol}&limit=3&apikey={api_key}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return "\n".join([f"- {n['title']} ({n['url']})" for n in data])
    except Exception:
        return "News unavailable."

def analyze_portfolio():
    """
    Proactively checks the user's paper trading status on Alpaca.
    """
    api_key = secrets.alpaca_key()
    secret_key = secrets.alpaca_secret()
    base_url = secrets.get_secret("ALPACA_BASE_URL")
    
    headers = {
        "APCA-API-KEY-ID": api_key,
        "APCA-API-SECRET-KEY": secret_key
    }
    
    try:
        # Check Account
        acc_resp = requests.get(f"{base_url}/account", headers=headers)
        acc_resp.raise_for_status()
        acc_data = acc_resp.json()
        
        # Check Positions
        pos_resp = requests.get(f"{base_url}/positions", headers=headers)
        pos_resp.raise_for_status()
        positions = pos_resp.json()
        
        report = f"Balance: ${acc_data['cash']}\n"
        if positions:
            report += "Positions:\n"
            for p in positions:
                report += f"- {p['symbol']}: {p['qty']} shares @ ${p['current_price']}\n"
        else:
            report += "No active positions."
            
        return report
    except Exception as e:
        return f"Portfolio check failed: {e}"

