import os
import random
from bip_utils import Bip39SeedGenerator, Bip44, Bip49, Bip84, Bip44Coins, Bip49Coins, Bip84Coins, Bip44Changes
from bip_utils.utils.mnemonic import MnemonicChecksumError
from supabase_utils import save_to_supabase

# File locations
source_file = 'source.txt'
english_word_file = 'english.txt'  # Ensure this is defined

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
            print(f"Checksum invalid. Retrying...")

# Function to process each mnemonic phrase and save to Supabase
def process_phrase_and_save(phrase, address_type, feature):
    phrase = phrase.strip()
    if not phrase:
        print("Empty phrase detected, skipping...")
        return
    
    words_count = len(phrase.split())
    if words_count != 12:
        print(f"Invalid mnemonic phrase (should be 12 words): . Skipping...")
        return

    try:
        if address_type == 'BIP44':
            address = generate_bip44_btc_address(phrase)
        elif address_type == 'BIP49':
            address = generate_bip49_btc_address(phrase)
        elif address_type == 'BIP84':
            address = generate_bip84_btc_address(phrase)
        else:
            print("Unknown address type.")
            return
        
        data = {
            "type": address_type,
            "phrase": phrase,
            "address": address,
            "feature": feature,
            "use": False
        }
        save_to_supabase(data)  # Ensure this function is correctly defined in supabase_utils.py
        print(f"Saved : {address}")
    
    except MnemonicChecksumError:
        print(f"Skip Invalid mnemonic phrase (checksum error)")

# Main function for feature 1
def process_feature_1():
    if not os.path.exists(source_file):
        print(f"{source_file} not found.")
        return

    with open(source_file, 'r') as file:
        phrases = [line.strip() for line in file if line.strip()]

    for phrase in phrases:
        process_phrase_and_save(phrase, 'BIP44', '1')  # Assuming '1' is for feature 1
        print(f"Processed phrase: .........")

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

    for phrase in phrases:
        process_phrase_and_save(phrase, address_type, '3')
        print(f"Processed phrase: .........")

# Main function for feature 4
def process_feature_4():
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

    for _ in range(count):
        mnemonic = generate_mnemonic_from_file(suggested_phrases)
        process_phrase_and_save(mnemonic, address_type, '4')
        print(f"Generated mnemonic: ........")

# Main function
def main():
    while True:
        print("\nSelect an option:")
        print("1: Use phrases from source.txt with balance check")
        print("2: Check BTC Balance Blockchain from source result")
        print("3: Use phrases from source.txt (non check)")
        print("4: Generate BIP39 phrases and addresses (non check)")
        print("5: Exit")

        choice = input("Enter choice (1/2/3/4/5): ").strip()

        if choice == '1':
            process_feature_1()
        elif choice == '2':
            print("Feature 2 is not implemented in this version.")
        elif choice == '3':
            process_feature_3()
        elif choice == '4':
            process_feature_4()
        elif choice == '5':
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
