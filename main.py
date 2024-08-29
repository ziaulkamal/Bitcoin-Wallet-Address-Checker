import os
import json
import random
import time
from bip_utils import Bip39SeedGenerator, Bip44Changes, Bip84, Bip84Coins
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

# Function to generate BIP84 (Bech32) address
def generate_bip84_address(phrase):
    # Generate seed from the mnemonic phrase
    seed_bytes = Bip39SeedGenerator(phrase).Generate()

    # Create BIP84 master key
    bip84_mst = Bip84.FromSeed(seed_bytes, Bip84Coins.BITCOIN)

    # Derive the key at path m/84'/0'/0'/0/0 (first address)
    bip84_acc = bip84_mst.Purpose().Coin().Account(0)
    bip84_change = bip84_acc.Change(Bip44Changes.CHAIN_EXT)
    bip84_addr = bip84_change.AddressIndex(0)

    # Return the address
    return bip84_addr.PublicKey().ToAddress()

# Function to generate 12-word mnemonic phrases using words from english.txt
def generate_mnemonic_from_file(suggested_phrases):
    if not os.path.exists(english_word_file):
        raise FileNotFoundError(f"{english_word_file} not found.")

    with open(english_word_file, 'r') as file:
        words = [line.strip() for line in file if line.strip()]

    # Ensure there are enough words in the file
    if len(words) < 12:
        raise ValueError(f"Not enough words in {english_word_file} to generate a 12-word phrase.")

    while True:
        # Generate a 12-word phrase from the words
        remaining_words_count = 12 - len(suggested_phrases)
        remaining_words = random.sample(words, remaining_words_count)
        phrase = ' '.join(suggested_phrases + remaining_words)

        try:
            # Validate the checksum of the generated phrase
            Bip39SeedGenerator(phrase).Generate()
            return phrase
        except MnemonicChecksumError:
            print(f"Checksum invalid for phrase: '{phrase}'. Retrying...")

# Function to process each mnemonic phrase without checking the balance
def process_phrase_non_check(phrase):
    phrase = phrase.strip()

    # Generate BIP84 address (Bech32)
    address = generate_bip84_address(phrase)

    # Create wallet info dictionary
    wallet_info = {
        "phrase": phrase,
        "address": address
    }

    return wallet_info

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

    # Load the data from the specified JSON file
    data = load_json_data(json_filename)
    
    # Lists to hold valid and zero balance results
    valid_results = []
    zero_results = []

    for item in data:
        address = item.get('address')
        phrase = item.get('phrase')
        
        # Print address being processed
        print(f"Processing address: {address}")

        try:
            # Fetch address details
            result = fetch_address_details(address)
            balance = result['balance']
            
            # Add phrase to the result
            result['phrase'] = phrase
            
            if balance == '0.00000000' or balance == 'N/A':
                zero_results.append(result)
                # Save zero balance result separately
                zero_filename = os.path.join(base_output_dir, 'blockchain', 'result', 'zero.json')
                save_results(zero_results, zero_filename)
                print(f"Failed: Balance for address {address} is zero or N/A.")
            else:
                valid_results.append(result)
                # Save valid balance result with address as filename
                address_filename = os.path.join(base_output_dir, 'blockchain', f'{address}.json')
                save_results(result, address_filename)
                print(f"Success: Balance for address {address} is {balance}.")
        except Exception as e:
            print(f"Error processing address {address}: {e}")

        # Wait before processing the next address
        time.sleep(random.uniform(2, 3))
    
    print(f"Results saved to {base_output_dir}/blockchain/{address}.json and {base_output_dir}/blockchain/result/zero.json")

# Menu for choosing between different options
print("Select an option:")
print("1: Use phrases from source.txt with balance check")
print("2: Check BTC Balance Blockchain from source result")
print("3: Use phrases from source.txt (non check)")
print("4: Generate BIP39 phrases from english.txt and BIP84 addresses (non check)")

option = input("Enter choice (1/2/3/4): ").strip()

# Ensure base output directory exists
if not os.path.exists(base_output_dir):
    os.makedirs(base_output_dir)

if option == '1':
    # Create directory for feature 1
    output_dir = ensure_output_dir_exists(1)
    print("Balance check functionality is not implemented in this example.")
elif option == '2':
    # Create directory for feature 2
    output_dir = ensure_output_dir_exists(2)
    json_filename = input("Enter the JSON filename from output/{feature} directory: ").strip()
    full_json_path = os.path.join('output', json_filename)
    if os.path.exists(full_json_path):
        process_feature_2(full_json_path)
    else:
        print(f"File {full_json_path} does not exist.")
elif option == '3':
    # Create directory for feature 3
    output_dir = ensure_output_dir_exists(3)
    if os.path.exists(source_file):
        with open(source_file, 'r') as file:
            phrases = file.readlines()

        results = []
        for phrase in phrases:
            result = process_phrase_non_check(phrase)
            results.append(result)

        save_results(results, os.path.join(output_dir, 'results.json'))
        print(f"BIP84 addresses have been generated and saved in {output_dir}/results.json.")
    else:
        print(f"File {source_file} not found.")
elif option == '4':
    # Create directory for feature 4
    output_dir = ensure_output_dir_exists(4)
    try:
        count = int(input("Enter the number of phrases to generate: ").strip())
        use_suggest = input("Do you want to use suggested phrases? (yes/no, default no): ").strip().lower()

        suggested_phrases = []
        if use_suggest == 'yes':
            suggest_phrase_count = int(input("Enter the number of suggested phrases (1-11): ").strip())
            if suggest_phrase_count < 1 or suggest_phrase_count > 11:
                raise ValueError("Suggested phrases must be between 1 and 11.")
            
            # Collect suggested phrases from user
            suggested_phrases = []
            for _ in range(suggest_phrase_count):
                phrase = input(f"Enter suggested phrase {_ + 1}: ").strip()
                suggested_phrases.append(phrase)

        results = []
        while len(results) < count:
            mnemonic_phrase = generate_mnemonic_from_file(suggested_phrases)
            result = process_phrase_non_check(mnemonic_phrase)
            results.append(result)
            print(f"Generated phrase {len(results)}: {mnemonic_phrase}")

            # Save results in real-time
            save_results(results, os.path.join(output_dir, 'results.json'))
            print(f"Results saved to {output_dir}/results.json")

        print(f"{count} BIP39 phrases and BIP84 addresses have been generated and saved in {output_dir}/results.json.")
    except ValueError as e:
        print(f"Invalid input: {e}")
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
else:
    print("Invalid choice.")
