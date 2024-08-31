
from supabase import create_client, Client
from dotenv import load_dotenv
import os

# Memuat variabel lingkungan dari file .env
load_dotenv()

# Supabase configuration
url = os.getenv('SUPABASE_URL')  # Ensure this environment variable is set
key = os.getenv('SUPABASE_KEY')  # Ensure this environment variable is set

# Create Supabase client
supabase: Client = create_client(url, key)

def save_to_supabase(data: dict):
    try:
        # Assuming 'data' is a dictionary and 'seeder_gen' is your table name
        response = supabase.table('seeder_gen').insert(data).execute()

        # Check if response has any errors
        if response.get('error'):
            raise Exception(f"Error inserting data: {response['error']}")
        
        print("Data inserted successfully:", response)
    
    except Exception as e:
        print(f"An error occurred: {e}")
        
def save_to_supabase_chain_bip49(data: dict):
    try:
        # Insert data into the 'chain_bip49' table
        response = supabase.table('chain_bip49').insert(data).execute()

        # Check if response has any errors
        if response.get('error'):
            raise Exception(f"Error inserting data: {response['error']}")
        
        # print("Data inserted successfully:", response)
    
    except Exception as e:
        print(f"Gagal Menyimpan.....")