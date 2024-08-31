import os
import requests
from supabase import create_client, Client
from dotenv import load_dotenv

# Memuat variabel lingkungan dari file .env
load_dotenv()

# Supabase configuration
url = os.getenv('SUPABASE_URL')  # Pastikan variabel lingkungan ini diset
key = os.getenv('SUPABASE_KEY')  # Pastikan variabel lingkungan ini diset

# Create Supabase client
supabase: Client = create_client(url, key)

# URL API untuk memeriksa saldo dari blockchain.info (atau gunakan API lain yang sesuai)
API_URL = 'https://blockchain.info/q/addressbalance/'

def get_balance(address):
    try:
        response = requests.get(f'{API_URL}{address}')
        response.raise_for_status()  # Akan memicu pengecualian untuk status code yang tidak berhasil
        balance_satoshis = int(response.text)  # Saldo dalam satoshi
        balance_btc = balance_satoshis / 1e8  # Konversi dari satoshi ke BTC
        return balance_btc
    except requests.RequestException as e:
        print(f"Error saat memeriksa saldo: {e}")
        return None

def get_next_unused_address():
    response = supabase.table('chain_bip49').select('address', 'xprv', 'xpub').eq('use', False).order('created_at', ascending=True).limit(1).execute()
    if response.data:
        return response.data[0]
    return None

def save_found_address(address, xprv, xpub, balance):
    try:
        data = {
            "address": address,
            "xprv": xprv,
            "xpub": xpub,
            "balance": balance
        }
        response = supabase.table('found_address').insert(data).execute()
        if response.error:
            raise Exception(f"Error inserting data into found_address: {response.error}")
        print(f"Alamat {address} berhasil disimpan ke found_address.")
    except Exception as e:
        print(f"Error saat menyimpan data: {e}")

def mark_address_as_used(address):
    try:
        response = supabase.table('chain_bip49').update({'use': True}).eq('address', address).execute()
        if response.error:
            raise Exception(f"Error updating address: {response.error}")
    except Exception as e:
        print(f"Error saat memperbarui status alamat: {e}")

def main():
    print("Bitcoin Address Balance Checker")
    print("============================\n")
    
    while True:
        entry = get_next_unused_address()
        if not entry:
            print("Semua alamat telah digunakan atau tidak ada alamat yang tersedia.")
            break

        address = entry['address']
        xprv = entry['xprv']
        xpub = entry['xpub']

        print(f"Memeriksa saldo untuk alamat {address}...")
        balance = get_balance(address)
        if balance is not None and balance > 0:
            print(f"Saldo untuk alamat {address} adalah {balance:.8f} BTC")
            save_found_address(address, xprv, xpub, balance)
            mark_address_as_used(address)
            print(f"Alamat {address} telah diperbarui sebagai digunakan.")
        else:
            print(f"Saldo untuk alamat {address} tidak ditemukan atau nol.")
        
        # Optional sleep to avoid hitting API limits
        # time.sleep(1)  # Sleep for 1 second

if __name__ == "__main__":
    main()
