import os
import requests
from bitcoinlib.keys import Key
from bitcoinlib.keys import Address
from bitcoinlib.wallets import Wallet
from bitcoinlib.mnemonic import Mnemonic
from bitcoinlib.services.services import Service
import random
from addressList.addresses import addresses
from database import create_table, insert_wallet_data


def generate_random_32byte_array():
    return [random.randint(0, 255) for _ in range(32)]

# def random_generate():
#     for bytearrate in range(32):
#        random.randint(0,255)

def generate_random_wallet(private_key_bytes):
    try:
        # Generate random 32-byte private key
        # private_key_bytes = os.urandom(32)
        key = Key(import_key = private_key_bytes,network='bitcoin')
        return {
            'private_key': key.wif(),
            'private_key_hex': key.private_hex,
            'public_key': key.public_hex,
            'address': key.address()
        }
    except Exception as e:
        print("Invalid :",e)
        

def validate_address(address):
    try:
        service = Service(network='bitcoin')
        txs = service.gettransactions(address)
        if not txs:
            return False 
        else:
            return True
    except:
        return False 
    
def check_balance(address):
    try:
        url = f"https://blockstream.info/api/address/{address}"
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()
        confirmed = data['chain_stats']['funded_txo_sum'] - data['chain_stats']['spent_txo_sum']
        unconfirmed = data['mempool_stats']['funded_txo_sum'] - data['mempool_stats']['spent_txo_sum']
        total = (confirmed + unconfirmed) / 1e8  # convert satoshi to BTC
    except:
        return 0

def load_file_to_set(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return set(line.strip() for line in file if line.strip()) #strip whitespace/newlines and ignore empty lines

def search_value(value, data_set)->bool:
    return value in data_set


# btc_address_data_set = load_file_to_set("BTCAddressList.txt")

# print("length of new set :",len(btc_address_data_set))
# all_data_set = btc_address_data_set.union(addresses)
# print("length of old set :",len(all_data_set))

def scanner():
    while(True):
    
        all_data_set = load_file_to_set("addressList/BTCAddressList.txt")
            
        private_key_array = generate_random_32byte_array() # [97, 111, 222, 17, 231, 209, 215, 255, 49, 82, 8, 210, 125, 6, 89, 120, 221, 206, 102, 76, 154, 6, 197, 12, 215, 110, 13, 15, 124, 44, 146, 253] 
        private_key_hex = ''.join(f'{b:02x}' for b in private_key_array) #convert 32byte array to hex string
        wallet = generate_random_wallet(private_key_hex)
        
       
        if search_value(wallet['address'], all_data_set):
            with open("foundAddress.txt","a") as file:
                file.write(
                    "-----------------------congratulation-----------------------------\n"
                    + "Private Key (WIF) : " + wallet['private_key'] + "\n"
                    + "Private Key (hex) : " + wallet['private_key_hex'] + "\n"
                    + "Public Key : " + wallet['public_key'] + "\n"
                    + "Bitcoin Address : " + wallet['address'] + "\n"
                    + "Network : "+ str(Address(wallet['address']).network.name) + "\n"
                    # + "Balance : " + str(balance) + " BTC\n"
                    + "Search : " + "BTC Address is found"+ "\n"
                    + "---------------------congratulation-------------------------------\n")
                
                # Store data in database
            print("Initializing database...")
            if not create_table():
                print("Warning: Database initialization failed. Scanner will continue without database storage.")
                
            network_name = Address(wallet['address']).network.name
            insert_wallet_data(
                wallet['private_key'],
                wallet['private_key_hex'],
                wallet['public_key'],
                wallet['address'],
                network_name
            )
            print("congratulation BTC Addres is found")
            print("The Address is : ",wallet['address'])
        else:
            print("Not Found")
            print("Private Key (WIF):", wallet['private_key'])
            # # print("Private Key (hex):", wallet['private_key_hex'])
            # # print("Public Key:", wallet['public_key'])
            # print("BTC Address  : ",wallet['address'])


if __name__ == "__main__":
    scanner()