import os
import random
import multiprocessing
from bitcoinlib.keys import Key, Address
from addressList.addresses import addresses
import mysql.connector
from database import create_table, insert_wallet_data

# ---------------- CONFIG ----------------
NUM_PROCESSES = multiprocessing.cpu_count()  # use all CPU cores
ADDRESS_FILE = "addressList/BTCAddressList.txt"
FOUND_FILE = "foundAddress.txt"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# ---------------------------------------

lock = multiprocessing.Lock()


def generate_random_32byte_array():
    return [random.randint(0, 255) for _ in range(32)]


def generate_random_wallet(private_key_hex):
    try:
        key = Key(import_key=private_key_hex, network='bitcoin')
        return {
            'private_key': key.wif(),
            'private_key_hex': key.private_hex,
            'public_key': key.public_hex,
            'address': key.address()
        }
    except Exception:
        return None


def load_file_to_set(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return set(line.strip() for line in file if line.strip())


def scanner_process(process_id, all_data_set):
    print(f"[Process-{process_id}] Started")

    while True:
        private_key_array = generate_random_32byte_array()
        private_key_hex = ''.join(f'{b:02x}' for b in private_key_array)

        wallet = generate_random_wallet(private_key_hex)
        if not wallet:
            continue
        # adrs ="173MqyKyBfomc3ry38hEolCmPiErGApk16"
        if wallet['address'] in all_data_set:
            with lock:
                with open(FOUND_FILE, "a") as file:
                    file.write(
                        "----------------------- CONGRATULATIONS -----------------------\n"
                        f"Private Key (WIF) : {wallet['private_key']}\n"
                        f"Private Key (hex) : {wallet['private_key_hex']}\n"
                        f"Public Key       : {wallet['public_key']}\n"
                        f"Bitcoin Address  : {wallet['address']}\n"
                        f"Network          : {Address(wallet['address']).network.name}\n"
                        "----------------------------------------------------------------\n"
                    )

                # Store data in database
                network_name = Address(wallet['address']).network.name
                insert_wallet_data(
                    wallet['private_key'],
                    wallet['private_key_hex'],
                    wallet['public_key'],
                    wallet['address'],
                    network_name
                )

            print(GREEN + f"[Process-{process_id}] 🎯 FOUND ADDRESS!")
            print(GREEN + wallet['address'])
            

        else:
            print(RED + f"[Process-{process_id}] Not found |" + YELLOW + f"{wallet['address']}")


def main():
    print("Loading address list...")
    btc_address_data_set = load_file_to_set(ADDRESS_FILE)
    all_data_set = btc_address_data_set.union(addresses)

    print(f"Total addresses loaded: {len(all_data_set)}")
    print("Initializing database...")
    if not create_table():
        print("Warning: Database initialization failed. Scanner will continue without database storage.")
    print(f"Starting {NUM_PROCESSES} processes...\n")

    processes = []
    for i in range(NUM_PROCESSES):
        p = multiprocessing.Process(
            target=scanner_process,
            args=(i + 1, all_data_set)
        )
        p.start()
        processes.append(p)

    for p in processes:
        p.join()


if __name__ == "__main__":
    main()
