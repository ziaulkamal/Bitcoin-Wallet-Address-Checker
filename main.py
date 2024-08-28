import requests
import json
import os
import time
from bitcoinlib.wallets import Wallet, wallet_delete_if_exists
from bitcoinlib.mnemonic import Mnemonic
import random

# File locations
output_file = 'wallet_results.json'
source_file = 'source.txt'
proxy_file = 'proxy.txt'

# List to store valid wallet information
valid_wallets = []

# Function to load proxy list from file
def load_proxies():
    if os.path.exists(proxy_file):
        with open(proxy_file, 'r') as file:
            proxies = [line.strip() for line in file if line.strip()]
        return proxies
    return []

# Function to process each mnemonic phrase
def process_phrase(phrase, use_proxy):
    phrase = phrase.strip()
    wallet_name = 'UniqueWallet_' + phrase.split()[0]

    # Delete wallet if it already exists
    wallet_delete_if_exists(wallet_name)

    try:
        # Create wallet from mnemonic phrase
        wallet = Wallet.create(wallet_name, keys=phrase, network='bitcoin', witness_type='legacy')
        
        # Get the first BTC address from the wallet
        address = wallet.get_key().address

        # Load proxies if using proxy
        proxies = load_proxies() if use_proxy else []

        # Function to get wallet info from BlockCypher API with proxy support
        def get_wallet_info(address):
            attempts = 0
            max_attempts = len(proxies) if proxies else 1
            while attempts < max_attempts:
                proxy = random.choice(proxies) if proxies else None
                proxies_dict = {'http': f'http://{proxy}', 'https': f'http://{proxy}'} if proxy else None
                try:
                    response = requests.get(f'https://api.blockcypher.com/v1/btc/main/addrs/{address}', proxies=proxies_dict, timeout=3)
                    
                    if response.status_code == 200:
                        print(f"Success with proxy {proxy}" if proxy else "Success")
                        return response.json()
                    elif response.status_code == 429:
                        # Wait before retrying
                        print(f"Rate limit exceeded for {address}. Waiting 3 seconds before retrying...")
                        time.sleep(3)
                    else:
                        response.raise_for_status()  # Handle other status codes
                
                except requests.RequestException as e:
                    print(f"Request error with proxy {proxy}: {e}" if proxy else f"Request error: {e}")
                    attempts += 1
                    if attempts < max_attempts:
                        print(f"Retrying with next proxy... ({attempts}/{max_attempts})")
                        time.sleep(3)  # Wait before retrying with the next proxy
                    else:
                        print("All proxies failed. Skipping this address.")
                        return None

            return None  # If all attempts fail

        # Get wallet info from BlockCypher API
        result = get_wallet_info(address)

        if result:
            # Extract required information
            wallet_info = {
                "phrase": phrase,
                "address": result.get("address"),
                "total_received": result.get("total_received"),
                "total_sent": result.get("total_sent"),
                "balance": result.get("balance"),
                "unconfirmed_balance": result.get("unconfirmed_balance"),
                "final_balance": result.get("final_balance")
            }
            
            # Save only if balance is greater than 0
            if wallet_info['balance'] > 0:
                valid_wallets.append(wallet_info)
                print(f"BTC address for phrase '{phrase}': {result.get('address')} successfully saved.")
                
                # Save results to JSON file in real-time
                save_results(valid_wallets)
        
        # Wait before processing the next address
        time.sleep(3)
    
    except ValueError as e:
        if "Invalid checksum" in str(e):
            print(f"Checksum error for phrase '{phrase}'. Skipping this wallet creation.")
        else:
            # Handle other errors or re-raise
            raise e

# Function to generate a random mnemonic phrase
def generate_mnemonic():
    mnemo = Mnemonic()
    return mnemo.generate()

# Function to load existing results from JSON file
def load_existing_results():
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r') as json_file:
                content = json_file.read().strip()
                if content:
                    return json.loads(content)
                else:
                    return []  # Return an empty list if file is empty
        except json.JSONDecodeError:
            print("JSON file is corrupted or has invalid format. Creating a new file.")
            return []
    return []

# Function to save results to JSON file
def save_results(results):
    with open(output_file, 'w') as json_file:
        json.dump(results, json_file, indent=4)

# Menu for choosing between source.txt or random mnemonic phrases and proxy option
print("Select an option:")
print("1: Use phrases from source.txt")
print("2: Generate random mnemonic phrases")

option = input("Enter choice (1/2): ").strip()

if option == '1':
    # Read phrases from source.txt
    if os.path.exists(source_file):
        use_proxy = input("Do you want to use proxy? (yes/no): ").strip().lower() == 'yes'
        with open(source_file, 'r') as file:
            phrases = file.readlines()
    else:
        print(f"File {source_file} not found.")
        phrases = []
elif option == '2':
    # Input number of mnemonics to generate
    try:
        count = int(input("Enter number of mnemonic phrases to generate: ").strip())
        phrases = [generate_mnemonic() for _ in range(count)]
        print(f"{count} random mnemonic phrases generated.")
        for phrase in phrases:
            print(f"Mnemonic phrase: {phrase}")
        use_proxy = input("Do you want to use proxy? (yes/no): ").strip().lower() == 'yes'
    except ValueError:
        print("Number of mnemonic phrases must be a number.")
        phrases = []
else:
    print("Invalid choice.")
    phrases = []
    use_proxy = False

# Process mnemonic phrases if any
if phrases:
    # Load existing results
    existing_results = load_existing_results()

    for phrase in phrases:
        process_phrase(phrase, use_proxy)

    # Combine new results with existing ones
    all_results = existing_results + valid_wallets

    # Save valid results to JSON file
    save_results(all_results)

    print(f"Valid wallet results saved in file {output_file}.")
else:
    print("No mnemonic phrases to process.")
