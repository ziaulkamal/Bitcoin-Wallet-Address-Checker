import os
import requests
import time
from supabase import create_client, Client
from dotenv import load_dotenv

# Memuat variabel lingkungan dari file .env
load_dotenv()

# Supabase configuration
url = os.getenv('SUPABASE_URL')  # Pastikan variabel lingkungan ini diset
key = os.getenv('SUPABASE_KEY')  # Pastikan variabel lingkungan ini diset

# Create Supabase client
supabase: Client = create_client(url, key)

# URL API untuk memeriksa saldo dari mempool.space
API_URL = 'https://mempool.space/api/address/'

def fetch_address_details(address):
    url = f"{API_URL}{address}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Akan memicu pengecualian untuk status code yang tidak berhasil
        data = response.json()
        funded_txo_sum = data['chain_stats']['funded_txo_sum']
        return {
            'address': address,
            'balance': funded_txo_sum / 1e8  # Konversi dari satoshi ke BTC
        }
    except requests.RequestException as e:
        print(f"Error fetching details for address {address}: {e}")
        return {
            'address': address,
            'balance': 'Error'
        }

def get_next_unused_address():
    try:
        # Ambil satu alamat dengan status 'use' = false
        response = supabase.table('chain_bip49').select('address', 'xprv', 'xpub').eq('use', False).order('id').limit(1).execute()
        data = response.data
        if data:
            return data[0]  # Ambil alamat pertama dari hasil
    except Exception as e:
        print(f"Error saat mengambil alamat yang tidak digunakan: {e}")
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
        if response.status_code != 201:
            raise Exception(f"Error inserting data into found_address: {response.status_code}")
        print(f"Alamat {address} berhasil disimpan ke found_address.")
    except Exception as e:
        print(f"Error saat menyimpan data: {e}")

def mark_address_as_used(address):
    try:
        response = supabase.table('chain_bip49').update({'use': True}).eq('address', address).execute()
        if response.status_code != 200:
            raise Exception(f"Error updating address: {response.status_code}")
        print(f"Alamat {address} telah diperbarui sebagai digunakan.")
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

        details = fetch_address_details(address)
        balance = details['balance']
        
        # Tandai alamat sebagai digunakan, terlepas dari hasilnya
        mark_address_as_used(address)

        time.sleep(1)  # Tidur selama 1 detik untuk menghindari batasan API
        
        if balance != 'Error' and balance > 0:
            print(f"Saldo untuk alamat {address} adalah {balance:.8f} BTC")
            save_found_address(address, xprv, xpub, balance)
        else:
            print(f"Saldo untuk alamat {address} tidak ditemukan atau nol.")
        
        # Optional sleep to avoid hitting API limits
        time.sleep(1)  # Menghindari batas API, sesuaikan sesuai kebutuhan

if __name__ == "__main__":
    main()
