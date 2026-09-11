-- ============================================================================
-- SupportSense AI: Relational Database Schema & Seed Data
-- Kompatibel dengan: PostgreSQL, MySQL 8+, dan SQLite
-- ============================================================================

-- 1. Tabel Pelanggan (Customers)
CREATE TABLE IF NOT EXISTS customers (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(30)
);

-- 2. Tabel Produk (Products)
CREATE TABLE IF NOT EXISTS products (
    id VARCHAR(50) PRIMARY KEY,
    sku VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(150) NOT NULL,
    category VARCHAR(50)
);

-- 3. Tabel Petugas Support (Agents)
CREATE TABLE IF NOT EXISTS agents (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL
);

-- 4. Tabel Pesanan (Orders)
CREATE TABLE IF NOT EXISTS orders (
    id VARCHAR(50) PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    customer_id VARCHAR(50) REFERENCES customers(id),
    status VARCHAR(50) NOT NULL,
    tracking_number VARCHAR(100),
    carrier VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Tabel Item Pesanan (Order Items)
CREATE TABLE IF NOT EXISTS order_items (
    id VARCHAR(50) PRIMARY KEY,
    order_id VARCHAR(50) REFERENCES orders(id),
    product_id VARCHAR(50) REFERENCES products(id),
    quantity INTEGER DEFAULT 1
);

-- 6. Tabel Komplain/Kasus (Issues)
CREATE TABLE IF NOT EXISTS issues (
    id VARCHAR(50) PRIMARY KEY,
    order_id VARCHAR(50) REFERENCES orders(id),
    issue_type VARCHAR(100) NOT NULL,
    issue_status VARCHAR(50) NOT NULL,
    assigned_agent_id VARCHAR(50) REFERENCES agents(id),
    notes TEXT
);

-- ============================================================================
-- SEED DATA (Data Contoh yang Sama Persis dengan KAG Graph)
-- ============================================================================

-- Insert Customers
INSERT INTO customers (id, name, email, phone) VALUES
('CUST-001', 'Andi Pratama', 'andi.pratama@example.com', '+6281234567890');

-- Insert Products
INSERT INTO products (id, sku, name, category) VALUES
('PROD-001', 'SKU-WF-PRO', 'Ultra Wireless Headphones Pro', 'Electronics');

-- Insert Agents
INSERT INTO agents (id, name, role, email) VALUES
('AGENT-001', 'Budi Santoso', 'Senior Logistics Support Specialist', 'budi.santoso@company.com');

-- Insert Orders (#4521 bermasalah, #4522 sudah sampai)
INSERT INTO orders (id, order_number, customer_id, status, tracking_number, carrier) VALUES
('ORD-4521', '#4521', 'CUST-001', 'Shipping Delayed', 'TRK-FDX-9988', 'FedEx'),
('ORD-4522', '#4522', 'CUST-001', 'Delivered', 'TRK-DHL-1122', 'DHL Express');

-- Insert Order Items
INSERT INTO order_items (id, order_id, product_id, quantity) VALUES
('ITEM-001', 'ORD-4521', 'PROD-001', 1),
('ITEM-002', 'ORD-4522', 'PROD-001', 1);

-- Insert Issues (Order #4521 ditangani oleh Agent Budi)
INSERT INTO issues (id, order_id, issue_type, issue_status, assigned_agent_id, notes) VALUES
('ISSUE-001', 'ORD-4521', 'Shipping Delay', 'Investigating with Carrier', 'AGENT-001', 'Customer reported package stuck at transit hub');
