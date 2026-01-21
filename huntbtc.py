import os
import ecdsa
import hashlib
import base58
import requests

# c = 0
while 1==1 :
    # c=+1
    #Generate random private key (32 bytes)
    private_key = os.urandom(32).hex()
    # print("Private Key (hex):", private_key)

    #Get public key from private key (SECP256k1 curve)
    sk = ecdsa.SigningKey.from_string(bytes.fromhex(private_key), curve=ecdsa.SECP256k1)
    vk = sk.verifying_key

    public_key = b'\x04' + vk.to_string()  # uncompressed public key
    # print("Public Key:", public_key.hex())

    #Create Bitcoin address (P2PKH)
    sha256_bpk = hashlib.sha256(public_key).digest()
    ripemd160_bpk = hashlib.new('ripemd160', sha256_bpk).digest()
    network_byte = b'\x00' + ripemd160_bpk  # 0x00 = mainnet
    checksum = hashlib.sha256(hashlib.sha256(network_byte).digest()).digest()[:4]
    address_bytes = network_byte + checksum
    btc_address = base58.b58encode(address_bytes).decode()
    # print("Bitcoin Address:", btc_address)

    #Validate address format
    def is_valid_btc_address(addr):
        try:
            decoded = base58.b58decode(addr)
            if len(decoded) != 25:
                return False
            checksum = decoded[-4:]
            vh160 = decoded[:-4]
            hashed = hashlib.sha256(hashlib.sha256(vh160).digest()).digest()[:4]
            return checksum == hashed
        except Exception:
            return False
        
    # Check balance (Blockchain API)
    def get_balance(address):
        url = f"https://blockchain.info/q/addressbalance/{address}"
        try:
            resp = requests.get(url)
            if resp.status_code == 200:
                satoshis = int(resp.text)
                return satoshis / 1e8  # convert to BTC
            else:
                return 0
        except:
            return 0
        
    def load_file_to_set(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip()) # strip whitespace/newlines and ignore empty lines

    def search_value(value, data_set):
        return value in data_set
    
    btc_address_data_set = load_file_to_set("btcAddress.txt")
    
    # btcaddress ="12ga9e1rv213PpvxLTQCQUB9yuvuVUVefv"
    # if search_value(btcaddress,btc_address_data_set):
    #     print(btcaddress," is found")
    # else:
    #     print("Btc Address is not found")

    check_validity = is_valid_btc_address(btc_address)

    if check_validity == 1:
        print("----------------------------------------------------")
        print("✅ Valid Bitcoin Address Found!")
        print("Private Key (hex):", private_key)
        print("Public Key:", public_key.hex())
        print("Bitcoin Address:", btc_address)
        balance = get_balance(btc_address) 
        print("Balance :", balance, "BTC")
        print("----------------------------------------------------")
        try:
            if balance > 0 or search_value(btc_address,btc_address_data_set):
                with open("ValidBTCHasBalance.txt","a") as file:
                    file.write(
                        "----------------------------------------------------\n"
                        + "Private Key (hex) : " + private_key + "\n"
                        + "Public Key : " + public_key.hex() + "\n"
                        + "Bitcoin Address : " + btc_address + "\n"
                        + "Balance : " + str(balance) + " BTC\n"
                        + "----------------------------------------------------\n")
        except:
            print("something wrong!")
    else :
        print("❌ Invalid Bitcoin address generated")

