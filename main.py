import os
import json
import random
import time
from bip_utils import Bip39SeedGenerator, Bip44, Bip49, Bip84, Bip44Coins, Bip49Coins, Bip84Coins, Bip44Changes
from bip_utils.utils.mnemonic import MnemonicChecksumError
from blockchain import fetch_address_details

# File locations
source_file = 'source.txt'
english_word_file = 'english.txt'  # File untuk kata-kata BIP39
base_output_dir = 'output/'

# Function to ensure the output directory exists
def ensure_output_dir_exists(feature_number):
    directory = os.path.join(base_output_dir, str(feature_number))
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

# Ensure output directories for blockchain results
def ensure_blockchain_output_dirs():
    blockchain_dir = os.path.join(base_output_dir, 'blockchain')
    if not os.path.exists(blockchain_dir):
        os.makedirs(blockchain_dir)
    if not os.path.exists(os.path.join(blockchain_dir, 'result')):
        os.makedirs(os.path.join(blockchain_dir, 'result'))

# Function to generate BIP44 BTC address
def generate_bip44_btc_address(phrase):
    seed_bytes = Bip39SeedGenerator(phrase).Generate()
    bip44_mst = Bip44.FromSeed(seed_bytes, Bip44Coins.BITCOIN)
    bip44_acc = bip44_mst.Purpose().Coin().Account(0)
    bip44_change = bip44_acc.Change(Bip44Changes.CHAIN_EXT)
    bip44_addr = bip44_change.AddressIndex(0)
    return bip44_addr.PublicKey().ToAddress()

# Function to generate BIP49 BTC address
def generate_bip49_btc_address(phrase):
    seed_bytes = Bip39SeedGenerator(phrase).Generate()
    bip49_mst = Bip49.FromSeed(seed_bytes, Bip49Coins.BITCOIN)
    bip49_acc = bip49_mst.Purpose().Coin().Account(0)
    bip49_change = bip49_acc.Change(Bip44Changes.CHAIN_EXT)
    bip49_addr = bip49_change.AddressIndex(0)
    return bip49_addr.PublicKey().ToAddress()

# Function to generate BIP84 BTC address
def generate_bip84_btc_address(phrase):
    seed_bytes = Bip39SeedGenerator(phrase).Generate()
    bip84_mst = Bip84.FromSeed(seed_bytes, Bip84Coins.BITCOIN)
    bip84_acc = bip84_mst.Purpose().Coin().Account(0)
    bip84_change = bip84_acc.Change(Bip44Changes.CHAIN_EXT)
    bip84_addr = bip84_change.AddressIndex(0)
    return bip84_addr.PublicKey().ToAddress()

# Function to generate 12-word mnemonic phrases using words from english.txt
def generate_mnemonic_from_file(suggested_phrases):
    if not os.path.exists(english_word_file):
        raise FileNotFoundError(f"{english_word_file} not found.")

    with open(english_word_file, 'r') as file:
        words = [line.strip() for line in file if line.strip()]

    if len(words) < 12:
        raise ValueError(f"Not enough words in {english_word_file} to generate a 12-word phrase.")

    while True:
        remaining_words_count = 12 - len(suggested_phrases)
        remaining_words = random.sample(words, remaining_words_count)
        phrase = ' '.join(suggested_phrases + remaining_words)
        try:
            Bip39SeedGenerator(phrase).Generate()
            return phrase
        except MnemonicChecksumError:
            print(f"Checksum invalid for phrase: '{phrase}'. Retrying...")

# Function to process each mnemonic phrase without checking the balance
def process_phrase_non_check(phrase, address_type):
    phrase = phrase.strip()
    if not phrase:
        print("Empty phrase detected, skipping...")
        return None
    
    words_count = len(phrase.split())
    if words_count != 12:
        print(f"Invalid mnemonic phrase (should be 12 words): '{phrase}'. Skipping...")
        return None

    try:
        if address_type == 'BIP44':
            address = generate_bip44_btc_address(phrase)
        elif address_type == 'BIP49':
            address = generate_bip49_btc_address(phrase)
        elif address_type == 'BIP84':
            address = generate_bip84_btc_address(phrase)
        else:
            print("Unknown address type.")
            return None
        
        return {
            "phrase": phrase,
            "address": address
        }
    except MnemonicChecksumError:
        print(f"Invalid mnemonic phrase (checksum error): '{phrase}'. Skipping...")
        return None

# Function to save results to JSON file in real-time
def save_results(results, output_file):
    with open(output_file, 'w') as file:
        json.dump(results, file, indent=4)

# Function to load JSON data from file
def load_json_data(filename):
    with open(filename, 'r') as file:
        return json.load(file)

# Main function for feature 2
def process_feature_2(json_filename):
    ensure_blockchain_output_dirs()
    data = load_json_data(json_filename)
    valid_results = []
    zero_results = []

    for item in data:
        address = item.get('address')
        phrase = item.get('phrase')
        print(f"Processing address: {address}")

        try:
            result = fetch_address_details(address)
            balance = result['balance']
            result['phrase'] = phrase
            
            if balance == 0 or balance == 'Error':
                zero_results.append(result)
                zero_filename = os.path.join(base_output_dir, 'blockchain', 'result', 'zero.json')
                save_results(zero_results, zero_filename)
                print(f"Failed: Balance for address {address} is zero or Error.")
            else:
                valid_results.append(result)
                address_filename = os.path.join(base_output_dir, 'blockchain', f'{address}.json')
                save_results(result, address_filename)
                print(f"Success: Balance for address {address} is {balance}.")
        except Exception as e:
            print(f"Error processing address {address}: {e}")

        time.sleep(random.uniform(2, 3))
    
    print(f"Results saved to {base_output_dir}/blockchain/{address}.json and {base_output_dir}/blockchain/result/zero.json")

# Main function for feature 3
def process_feature_3():
    address_type_map = {
        '1': 'BIP44',
        '2': 'BIP49',
        '3': 'BIP84'
    }

    print("Select address type:")
    print("1: BIP44 BTC Address")
    print("2: BIP49 BTC Address")
    print("3: BIP84 BTC Address")
    
    address_type_choice = input("Enter choice (1/2/3): ").strip()
    address_type = address_type_map.get(address_type_choice)
    
    if not address_type:
        print("Invalid choice.")
        return

    if not os.path.exists(source_file):
        print(f"{source_file} not found.")
        return

    with open(source_file, 'r') as file:
        phrases = [line.strip() for line in file if line.strip()]

    results = []
    for phrase in phrases:
        result = process_phrase_non_check(phrase, address_type)
        if result:
            results.append(result)
            print(f"Processed phrase: {phrase}")

    results_filename = f"{address_type}_source_results.json"
    save_results(results, os.path.join(ensure_output_dir_exists(3), results_filename))
    print(f"Results saved to {os.path.join(ensure_output_dir_exists(3), results_filename)}")

# Main function for feature 4
def process_feature_4():
    ensure_output_dir_exists(4)
    print("Select address type:")
    print("1: BIP44 BTC Address")
    print("2: BIP49 BTC Address")
    print("3: BIP84 BTC Address")
    
    address_type_map = {
        '1': 'BIP44',
        '2': 'BIP49',
        '3': 'BIP84'
    }
    
    address_type_choice = input("Enter choice (1/2/3): ").strip()
    address_type = address_type_map.get(address_type_choice)
    
    if not address_type:
        print("Invalid choice.")
        return
    
    count = int(input("Enter the number of phrases to generate: ").strip())
    use_suggest = input("Do you want to use suggested phrases? (yes/no, default no): ").strip().lower()

    suggested_phrases = []
    if use_suggest == 'yes':
        suggest_phrase_count = int(input("Enter the number of suggested phrases (1-11): ").strip())
        if suggest_phrase_count < 1 or suggest_phrase_count > 11:
            raise ValueError("Suggested phrases must be between 1 and 11.")
        
        for _ in range(suggest_phrase_count):
            phrase = input(f"Enter suggested phrase {_ + 1}: ").strip()
            suggested_phrases.append(phrase)

    results = []
    for _ in range(count):
        mnemonic = generate_mnemonic_from_file(suggested_phrases)
        result = process_phrase_non_check(mnemonic, address_type)
        if result:
            results.append(result)
            print(f"Generated mnemonic: {mnemonic}")
    
    output_file = os.path.join(ensure_output_dir_exists(4), f"{address_type}_generated_phrases.json")
    save_results(results, output_file)
    print(f"Results saved to {output_file}")

# Main function
def main():
    print("Select an option:")
    print("1: Use phrases from source.txt with balance check")
    print("2: Check BTC Balance Blockchain from source result")
    print("3: Use phrases from source.txt (non check)")
    print("4: Generate BIP39 phrases and addresses (non check)")

    choice = input("Enter choice (1/2/3/4): ").strip()

    if choice == '1':
        # Implement feature 1 here if needed
        pass
    elif choice == '2':
        json_filename = input("Enter the JSON filename from output/ directory: ").strip()
        process_feature_2(os.path.join(base_output_dir, json_filename))
    elif choice == '3':
        process_feature_3()
    elif choice == '4':
        process_feature_4()
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()
