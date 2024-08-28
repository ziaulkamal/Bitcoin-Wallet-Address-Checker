import json
import os
from bitcoinlib.wallets import Wallet
from bitcoinlib.mnemonic import Mnemonic
from datetime import datetime

# Define the output file path
output_file = 'output/mnemonics.json'

# Function to generate a Bitcoin address from a mnemonic phrase
def get_address_from_mnemonic(mnemonic_phrase):
    try:
        # Create a unique wallet name using a timestamp
        wallet_name = f"TempWallet_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Create a wallet from the mnemonic phrase
        wallet = Wallet.create(name=wallet_name, keys=mnemonic_phrase, network='bitcoin', witness_type='legacy')
        return wallet.get_key().address
    except ValueError as e:
        print(f"Error generating address from mnemonic '{mnemonic_phrase}': {e}")
        return None

# Function to read existing results from the JSON file
def load_existing_results():
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            print("JSON file is corrupted or invalid. Starting with an empty list.")
            return []
    return []

# Function to ensure that the phrase is formatted correctly
def format_suggested_phrase(phrase, total_words):
    words = phrase.split()
    num_words = len(words)
    if num_words > total_words:
        raise ValueError("The suggested phrase is too long. It should be shorter than the total number of words.")
    elif num_words < total_words:
        # Add additional random words to complete the phrase
        mnemo = Mnemonic()
        additional_words = mnemo.generate(strength=(total_words - num_words) * 32).split()
        words.extend(additional_words[:total_words - num_words])
    return ' '.join(words)

# Function to generate and save mnemonics and addresses to JSON
def generate_and_save_mnemonics(count, suggested_phrase=None):
    mnemo = Mnemonic()
    results = load_existing_results()
    
    # Ensure output directory exists
    os.makedirs('output', exist_ok=True)
    
    while len(results) < count:
        if suggested_phrase:
            try:
                phrase = format_suggested_phrase(suggested_phrase, 12)  # Assuming 12 words for a standard mnemonic
            except ValueError as e:
                print(f"Error with suggested phrase: {e}")
                print("Generating a new phrase without suggestion...")
                suggested_phrase = None
                phrase = mnemo.generate()
        else:
            phrase = mnemo.generate()
        
        address = get_address_from_mnemonic(phrase)
        
        if address:
            results.append({
                "phrase": phrase,
                "address": address
            })
            print(f"Generated address {address} for phrase {phrase}")
            
            # Save results to JSON file in real-time
            with open(output_file, 'w') as file:
                json.dump(results, file, indent=4)
        else:
            print(f"Failed to generate a valid address for phrase '{phrase}'. Generating a new phrase...")
    
    print(f"Results saved to {output_file}")

# Main function to run the application
def main():
    try:
        count = int(input("Enter the number of mnemonic phrases to generate: ").strip())
        if count <= 0:
            raise ValueError("The number of mnemonics must be a positive integer.")
        
        use_suggestion = input("Do you want to use a suggested phrase? (yes/no): ").strip().lower() == 'yes'
        suggested_phrase = None
        if use_suggestion:
            suggested_phrase = input("Enter the suggested phrase: ").strip()
        
        generate_and_save_mnemonics(count, suggested_phrase)
    
    except ValueError as e:
        print(f"Invalid input: {e}")

if __name__ == "__main__":
    main()
