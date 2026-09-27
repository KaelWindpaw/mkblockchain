import hashlib
import time
from datetime import datetime, timezone

# 1. Mendefinisikan Struktur Data Tunggal (Satu Blok)
class Block:
    def __init__(self, index, data, prev_hash, difficulty=3):
        self.index = index
        self.timestamp = time.time()
        self.data = data
        self.prev_hash = prev_hash
        self.nonce = 0
        self.difficulty = difficulty
        self.hash = self.mine_block()

    @property
    def timestamp_readable(self):
        return datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S')

    def calculate_hash(self):
        block_string = (
            str(self.index)
            + str(self.timestamp)
            + str(self.data)
            + str(self.prev_hash)
            + str(self.nonce)
        )
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self):
        target = "0" * self.difficulty
        while True:
            block_hash = self.calculate_hash()
            if block_hash.startswith(target):
                return block_hash
            self.nonce += 1

# 2. Mendefinisikan Rantai Blok (Manajer Kumpulan Blok)
class Blockchain:
    def __init__(self, difficulty=3):
        self.chain = []
        self.difficulty = difficulty
        self.create_genesis_block()

    def create_genesis_block(self):
        # Blok pertama selalu hardcoded
        genesis_block = Block(1, "Genesis Block (Awal Mula)", "0", self.difficulty)
        self.chain.append(genesis_block)

    def add_block(self, data):
        # Mengambil hash dari blok terakhir sebagai pointer
        last_block = self.chain[-1]
        new_block = Block(
            last_block.index + 1,
            data,
            last_block.hash,
            self.difficulty,
        )
        self.chain.append(new_block)

    def tamper_block(self, index, tampered_data):
        """Mengubah payload tanpa mining ulang untuk mensimulasikan serangan."""
        if index <= 1 or index > len(self.chain):
            raise ValueError("Blok yang dipilih tidak dapat dirusak.")
        self.chain[index - 1].data = tampered_data

    def is_chain_valid(self):
        # Loop dari blok ke-1 (setelah Genesis) sampai akhir
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            # Cek apakah hash saat ini valid
            if current_block.hash != current_block.calculate_hash():
                return False
            # Cek apakah hash memenuhi Proof of Work
            if not current_block.hash.startswith("0" * current_block.difficulty):
                return False
            # Cek apakah pointer prev_hash merujuk ke blok sebelumnya dengan benar
            if current_block.prev_hash != previous_block.hash:
                return False
        return True