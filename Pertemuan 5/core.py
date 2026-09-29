import hashlib
import time
from datetime import datetime, timezone

# 1. Mendefinisikan Struktur Data Tunggal (Satu Blok)
class Block:
    def __init__(self, index, data, prev_hash):
        self.index = index
        self.timestamp = time.time()
        self.data = data
        self.previous_hash = prev_hash
        self.nonce = 0  # Digunakan untuk Proof of Work (jika diterapkan)
        self.hash = self.calculate_hash()

    @property
    def timestamp_readable(self):
        return datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S')

    def calculate_hash(self):
        value = str(self.index) + str(self.timestamp) + str(self.data) + str(self.previous_hash) + str(self.nonce)
        return hashlib.sha256(value.encode()).hexdigest()

    def mine_block(self, difficulty):
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()

            print(f"Block Mined! Nonce: {self.nonce} | Hash: {self.hash}")

# 2. Mendefinisikan Rantai Blok (Manajer Kumpulan Blok)
class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.difficulty = 3  

    def create_genesis_block(self):
        return Block(0, "Genesis Block - Rantai Dimulai", "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, new_block):
        new_block.previous_hash = self.get_latest_block().hash
        # ATRIBUT BARU: Panggil fungsi mining sebelum blok ditambahkan ke rantai
        new_block.mine_block(self.difficulty)
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
            if current_block.previous_hash != previous_block.hash:
                return False
        return True