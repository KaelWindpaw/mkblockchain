import hashlib
import time
from datetime import datetime, timezone

# 1. Mendefinisikan Struktur Data Tunggal (Satu Blok)
class Block:
    def __init__(self, index, data, prev_hash):
        self.index = index
        self.timestamp = time.time()
        self.data = data
        self.prev_hash = prev_hash
        self.hash = self.calculate_hash()

    @property
    def timestamp_readable(self):
        return datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S')

    def calculate_hash(self):
        block_string = str(self.index) + str(self.timestamp) + str(self.data) + str(self.prev_hash)
        return hashlib.sha256(block_string.encode()).hexdigest()

# 2. Mendefinisikan Rantai Blok (Manajer Kumpulan Blok)
class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        # Blok pertama selalu hardcoded
        genesis_block = Block(1, "Genesis Block (Awal Mula)", "0")
        self.chain.append(genesis_block)

    def add_block(self, data):
        # Mengambil hash dari blok terakhir sebagai pointer
        last_block = self.chain[-1]
        new_block = Block(last_block.index + 1, data, last_block.hash)
        self.chain.append(new_block)

    def is_chain_valid(self):
        # Loop dari blok ke-1 (setelah Genesis) sampai akhir
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            # Cek apakah hash saat ini valid
            if current_block.hash != current_block.calculate_hash():
                return False
            # Cek apakah pointer prev_hash merujuk ke blok sebelumnya dengan benar
            if current_block.prev_hash != previous_block.hash:
                return False
        return True