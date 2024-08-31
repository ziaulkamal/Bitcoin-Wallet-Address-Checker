import os
import random
from bip_utils import Bip39SeedGenerator, Bip39MnemonicValidator, Bip49, Bip49Coins, Bip44Changes
from supabase_utils import save_to_supabase_chain_bip49  # Import fungsi baru

# Lokasi file english.txt
english_word_file = 'english.txt'

# Fungsi untuk membaca daftar kata BIP-39 dari file
def load_bip39_words():
    if not os.path.exists(english_word_file):
        raise FileNotFoundError(f"{english_word_file} tidak ditemukan.")
    
    with open(english_word_file, 'r') as file:
        words = [line.strip() for line in file if line.strip()]
    
    if len(words) < 2048:
        raise ValueError("Jumlah kata dalam english.txt kurang dari 2048.")
    
    return words

# Fungsi untuk menghasilkan mnemonic secara acak dan menyimpan yang valid ke Supabase
def generate_and_save_mnemonics(words, count):
    valid_count = 0
    while valid_count < count:
        mnemonic_words = random.sample(words, 12)  # Mengambil 12 kata secara acak
        mnemonic = ' '.join(mnemonic_words)
        try:
            # Validasi mnemonic
            Bip39MnemonicValidator().Validate(mnemonic)
            # Jika valid, simpan ke Supabase
            xprv, xpub, address = generate_bip49_xprv_xpub_p2sh(mnemonic)
            data = {
                "xprv": xprv,
                "xpub": xpub,
                "phrases": mnemonic,
                "address": address
            }
            save_to_supabase_chain_bip49(data)
            print(f"Ditemukan {address}")
            valid_count += 1
        except Exception as e:
            print(f"Ulang Kembali ....")

# Fungsi untuk menghasilkan xprv, xpub, dan P2SH address menggunakan BIP49
def generate_bip49_xprv_xpub_p2sh(mnemonic):
    seed_bytes = Bip39SeedGenerator(mnemonic).Generate()
    bip49_mst = Bip49.FromSeed(seed_bytes, Bip49Coins.BITCOIN)
    bip49_acc = bip49_mst.Purpose().Coin().Account(0)
    xprv = bip49_acc.PrivateKey().ToExtended()
    xpub = bip49_acc.PublicKey().ToExtended()
    bip49_change = bip49_acc.Change(Bip44Changes.CHAIN_EXT)
    bip49_addr = bip49_change.AddressIndex(0)
    p2sh_address = bip49_addr.PublicKey().ToAddress()
    return xprv, xpub, p2sh_address

def main():
    print("BIP49 P2SH-P2WPKH Generator")
    print("============================\n")
    
    # Load BIP-39 words from file
    try:
        words = load_bip39_words()
    except Exception as e:
        print(f"Error loading BIP-39 words: {e}")
        return
    
    try:
        num_entries = int(input("Masukkan jumlah entri yang ingin dihasilkan: ").strip())
    except ValueError:
        print("Jumlah entri tidak valid. Harus berupa angka.")
        return

    if num_entries <= 0:
        print("Jumlah entri harus lebih dari 0.")
        return
    
    print(f"\nGenerating {num_entries} entries...\n")
    generate_and_save_mnemonics(words, num_entries)

if __name__ == "__main__":
    main()
