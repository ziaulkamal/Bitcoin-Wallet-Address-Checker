import requests

def fetch_address_details(address):
    url = f"https://mempool.space/api/address/{address}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        funded_txo_sum = data['chain_stats']['funded_txo_sum']
        return {
            'address': address,
            'balance': funded_txo_sum / 1e8  # Convert from Satoshis to BTC
        }
    except Exception as e:
        print(f"Error fetching details for address {address}: {e}")
        return {
            'address': address,
            'balance': 'Error'
        }
