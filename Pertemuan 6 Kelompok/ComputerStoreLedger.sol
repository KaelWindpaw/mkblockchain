// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title  ComputerStoreLedger
 * @notice Versi Solidity dari databasecore.py (Block + Blockchain) untuk toko komputer.
 *         Siap di-compile & di-deploy di Remix IDE.
 *
 * Pemetaan dari versi Python:
 *   Block            -> struct LedgerBlock
 *   Blockchain       -> contract ComputerStoreLedger
 *   create_genesis   -> constructor()
 *   add_block()      -> recordSale()
 *   tamper_block()   -> tamperBlockForDemo()   (HANYA untuk simulasi/edukasi)
 *   is_chain_valid() -> isChainValid() / verifyChain()
 *   stok_produk      -> products[id].stock
 *
 * Catatan: Proof of Work (nonce/difficulty) tidak diperlukan karena
 * konsensus sudah ditangani oleh jaringan Ethereum itu sendiri.
 * Hash memakai keccak256 (pengganti SHA-256 di Python).
 */
contract ComputerStoreLedger {
    // ------------------------------------------------------------------
    //  Struktur data
    // ------------------------------------------------------------------
    struct Product {
        string category;
        string name;
        uint256 price;   // dalam Rupiah (bilangan bulat)
        uint256 stock;
        bool active;
    }

    struct Accessory {
        string name;
        uint256 price;   // dalam Rupiah
        bool active;
    }

    /// Input transaksi (dibungkus struct agar mudah dipanggil & hemat stack)
    struct SaleInput {
        string buyer;
        uint256 productId;
        uint256 quantity;
        uint256[] accessoryIds;
        string seller;
        string location;
    }

    /// Data transaksi yang disimpan di dalam blok
    struct Sale {
        string buyer;
        uint256 productId;
        string productName;
        uint256 quantity;
        string accessories;
        uint256 total;
        string seller;
        uint256 stockBefore;
        uint256 stockAfter;
        string location;
    }

    /// Padanan class Block di Python
    struct LedgerBlock {
        uint256 index;
        uint256 timestamp;
        Sale sale;
        bytes32 prevHash;
        bytes32 hash;
    }

    // ------------------------------------------------------------------
    //  State
    // ------------------------------------------------------------------
    address public owner;
    mapping(address => bool) public isStaff; // kasir/admin yang boleh mencatat transaksi

    LedgerBlock[] private chain;

    mapping(uint256 => Product) public products;
    uint256 public productCount;

    mapping(uint256 => Accessory) public accessories;
    uint256 public accessoryCount;

    bool public demoTamperEnabled = true;
    bool public sampleSeeded;

    // ------------------------------------------------------------------
    //  Events
    // ------------------------------------------------------------------
    event BlockAdded(uint256 indexed index, bytes32 hash, address indexed recordedBy);
    event ProductAdded(uint256 indexed productId, string name, uint256 price, uint256 stock);
    event AccessoryAdded(uint256 indexed accessoryId, string name, uint256 price);
    event Restocked(uint256 indexed productId, uint256 amount, uint256 newStock);
    event StaffUpdated(address indexed account, bool allowed);
    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);
    event BlockTampered(uint256 indexed index);

    // ------------------------------------------------------------------
    //  Modifier
    // ------------------------------------------------------------------
    modifier onlyOwner() {
        require(msg.sender == owner, "Hanya owner");
        _;
    }

    modifier onlyStaff() {
        require(msg.sender == owner || isStaff[msg.sender], "Hanya owner/staff");
        _;
    }

    // ------------------------------------------------------------------
    //  Constructor (Genesis Block)
    // ------------------------------------------------------------------
    constructor() {
        owner = msg.sender;
        isStaff[msg.sender] = true;

        Sale memory s;
        s.buyer = "Genesis Block (Awal Mula)";

        uint256 ts = block.timestamp;
        LedgerBlock storage g = chain.push();
        g.index = 1;
        g.timestamp = ts;
        g.sale = s;
        g.prevHash = bytes32(0);
        g.hash = _hashBlock(1, ts, s, bytes32(0));

        emit BlockAdded(1, g.hash, msg.sender);
    }

    // ------------------------------------------------------------------
    //  Administrasi
    // ------------------------------------------------------------------
    function setStaff(address account, bool allowed) external onlyOwner {
        isStaff[account] = allowed;
        emit StaffUpdated(account, allowed);
    }

    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "Alamat tidak valid");
        emit OwnershipTransferred(owner, newOwner);
        owner = newOwner;
        isStaff[newOwner] = true;
    }

    function addProduct(
        string calldata category,
        string calldata name,
        uint256 price,
        uint256 stock
    ) external onlyOwner returns (uint256 productId) {
        productId = _addProduct(category, name, price, stock);
    }

    function addAccessory(string calldata name, uint256 price)
        external
        onlyOwner
        returns (uint256 accessoryId)
    {
        accessoryId = _addAccessory(name, price);
    }

    function restock(uint256 productId, uint256 amount) external onlyStaff {
        require(_validProduct(productId), "Produk tidak ditemukan");
        require(amount > 0, "Jumlah harus > 0");
        products[productId].stock += amount;
        emit Restocked(productId, amount, products[productId].stock);
    }

    function setProductPrice(uint256 productId, uint256 newPrice) external onlyOwner {
        require(_validProduct(productId), "Produk tidak ditemukan");
        products[productId].price = newPrice;
    }

    function setProductActive(uint256 productId, bool active) external onlyOwner {
        require(_validProduct(productId), "Produk tidak ditemukan");
        products[productId].active = active;
    }

    /// Mengisi beberapa data contoh (diambil dari katalog Furrapp.py) untuk testing cepat.
    function seedSampleCatalog() external onlyOwner {
        require(!sampleSeeded, "Sudah di-seed");
        sampleSeeded = true;

        _addProduct("Motherboard", "AMD AM4 - B550", 1750000, 10);
        _addProduct("CPU", "AMD Ryzen 5 5600", 1850000, 10);
        _addProduct("RAM", "DDR4 16GB", 650000, 20);
        _addProduct("GPU", "NVIDIA RTX 4060 (40 Series)", 5200000, 5);
        _addProduct("PSU", "650W 80+ Bronze", 950000, 8);
        _addProduct("Storage", "SSD NVMe Gen4 2TB", 2250000, 6);

        _addAccessory("Kabel HDMI", 100000);
        _addAccessory("Mousepad", 75000);
        _addAccessory("Flashdisk 64GB", 90000);
        _addAccessory("Thermal Paste", 75000);
        _addAccessory("Kabel Power", 50000);
    }

    // ------------------------------------------------------------------
    //  Transaksi (padanan add_block)
    // ------------------------------------------------------------------
    /**
     * @notice Mencatat penjualan sebagai blok baru & mengurangi stok.
     * Contoh input di Remix (satu tuple):
     *   ["Budi", 1, 2, [1,2], "Admin Andi", "Cirebon"]
     */
    function recordSale(SaleInput calldata input)
        external
        onlyStaff
        returns (uint256 blockIndex)
    {
        require(bytes(input.buyer).length > 0, "Nama pembeli kosong");
        require(bytes(input.seller).length > 0, "Nama penjual kosong");
        require(bytes(input.location).length > 0, "Lokasi kosong");
        require(input.quantity > 0, "Jumlah harus > 0");
        require(_validProduct(input.productId), "Produk tidak ditemukan");

        Product storage p = products[input.productId];
        require(p.active, "Produk tidak aktif");
        require(input.quantity <= p.stock, "Stok tidak cukup");

        (uint256 accTotal, string memory accNames) = _accessoryInfo(input.accessoryIds);

        uint256 stockBefore = p.stock;
        p.stock = stockBefore - input.quantity;

        Sale memory s;
        s.buyer = input.buyer;
        s.productId = input.productId;
        s.productName = p.name;
        s.quantity = input.quantity;
        s.accessories = accNames;
        s.total = (p.price + accTotal) * input.quantity;
        s.seller = input.seller;
        s.stockBefore = stockBefore;
        s.stockAfter = p.stock;
        s.location = input.location;

        blockIndex = _appendBlock(s);
    }

    // ------------------------------------------------------------------
    //  Validasi rantai (padanan is_chain_valid)
    // ------------------------------------------------------------------
    /// @return valid true jika seluruh rantai konsisten
    /// @return firstInvalidIndex nomor blok pertama yang rusak (0 jika valid)
    function verifyChain() public view returns (bool valid, uint256 firstInvalidIndex) {
        uint256 len = chain.length;
        for (uint256 i = 0; i < len; i++) {
            LedgerBlock storage b = chain[i];

            // 1. Hash tersimpan harus sama dengan hash hasil hitung ulang
            if (b.hash != _hashBlock(b.index, b.timestamp, b.sale, b.prevHash)) {
                return (false, b.index);
            }
            // 2. Pointer prev_hash harus merujuk ke blok sebelumnya
            if (i == 0) {
                if (b.prevHash != bytes32(0)) return (false, b.index);
            } else if (b.prevHash != chain[i - 1].hash) {
                return (false, b.index);
            }
        }
        return (true, 0);
    }

    function isChainValid() external view returns (bool) {
        (bool valid, ) = verifyChain();
        return valid;
    }

    // ------------------------------------------------------------------
    //  Simulasi serangan (padanan tamper_block) - HANYA UNTUK DEMO
    // ------------------------------------------------------------------
    /// Mengubah nama pembeli tanpa menghitung ulang hash, sehingga verifyChain() gagal.
    /// Di blockchain sungguhan data lama tidak bisa diubah; fungsi ini hanya untuk edukasi.
    function tamperBlockForDemo(uint256 index, string calldata newBuyer) external onlyOwner {
        require(demoTamperEnabled, "Mode demo dimatikan");
        require(index > 1 && index <= chain.length, "Blok tidak dapat dirusak");
        chain[index - 1].sale.buyer = newBuyer;
        emit BlockTampered(index);
    }

    /// Matikan fitur tamper secara permanen sebelum dipakai produksi.
    function disableDemoTamper() external onlyOwner {
        demoTamperEnabled = false;
    }

    // ------------------------------------------------------------------
    //  Fungsi baca (view)
    // ------------------------------------------------------------------
    function getChainLength() external view returns (uint256) {
        return chain.length;
    }

    /// index dimulai dari 1 (sama seperti versi Python)
    function getBlock(uint256 index) external view returns (LedgerBlock memory) {
        require(index >= 1 && index <= chain.length, "Blok tidak ada");
        return chain[index - 1];
    }

    function getLatestBlock() external view returns (LedgerBlock memory) {
        return chain[chain.length - 1];
    }

    /// Hitung ulang hash sebuah blok (berguna untuk membandingkan dengan hash tersimpan)
    function calculateHash(uint256 index) external view returns (bytes32) {
        require(index >= 1 && index <= chain.length, "Blok tidak ada");
        LedgerBlock storage b = chain[index - 1];
        return _hashBlock(b.index, b.timestamp, b.sale, b.prevHash);
    }

    function getStock(uint256 productId) external view returns (uint256) {
        require(_validProduct(productId), "Produk tidak ditemukan");
        return products[productId].stock;
    }

    /// Hitung estimasi total tanpa mencatat transaksi
    function previewTotal(
        uint256 productId,
        uint256 quantity,
        uint256[] calldata accessoryIds
    ) external view returns (uint256) {
        require(_validProduct(productId), "Produk tidak ditemukan");
        (uint256 accTotal, ) = _accessoryInfo(accessoryIds);
        return (products[productId].price + accTotal) * quantity;
    }

    // ------------------------------------------------------------------
    //  Internal
    // ------------------------------------------------------------------
    function _hashBlock(
        uint256 index,
        uint256 timestamp,
        Sale memory sale,
        bytes32 prevHash
    ) internal pure returns (bytes32) {
        return keccak256(abi.encode(index, timestamp, sale, prevHash));
    }

    function _appendBlock(Sale memory s) internal returns (uint256 newIndex) {
        bytes32 prevHash = chain[chain.length - 1].hash;
        newIndex = chain[chain.length - 1].index + 1;
        uint256 ts = block.timestamp;
        bytes32 h = _hashBlock(newIndex, ts, s, prevHash);

        LedgerBlock storage nb = chain.push();
        nb.index = newIndex;
        nb.timestamp = ts;
        nb.sale = s;
        nb.prevHash = prevHash;
        nb.hash = h;

        emit BlockAdded(newIndex, h, msg.sender);
    }

    function _accessoryInfo(uint256[] calldata ids)
        internal
        view
        returns (uint256 sum, string memory names)
    {
        if (ids.length == 0) {
            return (0, "Tidak ada");
        }
        for (uint256 i = 0; i < ids.length; i++) {
            uint256 id = ids[i];
            require(id >= 1 && id <= accessoryCount, "Aksesori tidak ditemukan");
            Accessory storage a = accessories[id];
            require(a.active, "Aksesori tidak aktif");
            sum += a.price;
            names = (i == 0) ? a.name : string.concat(names, ", ", a.name);
        }
    }

    function _validProduct(uint256 id) internal view returns (bool) {
        return id >= 1 && id <= productCount;
    }

    function _addProduct(
        string memory category,
        string memory name,
        uint256 price,
        uint256 stock
    ) internal returns (uint256 productId) {
        require(bytes(name).length > 0, "Nama produk kosong");
        require(price > 0, "Harga harus > 0");
        productId = ++productCount;
        products[productId] = Product(category, name, price, stock, true);
        emit ProductAdded(productId, name, price, stock);
    }

    function _addAccessory(string memory name, uint256 price)
        internal
        returns (uint256 accessoryId)
    {
        require(bytes(name).length > 0, "Nama aksesori kosong");
        require(price > 0, "Harga harus > 0");
        accessoryId = ++accessoryCount;
        accessories[accessoryId] = Accessory(name, price, true);
        emit AccessoryAdded(accessoryId, name, price);
    }
}
