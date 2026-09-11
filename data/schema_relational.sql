-- ============================================================================
-- SupportSense AI: Rich Relational Database Schema & Comprehensive Seed Data
-- Compatible with: PostgreSQL, MySQL 8+, and SQLite
-- ============================================================================

DROP TABLE IF EXISTS issues;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS agents;
DROP TABLE IF EXISTS customers;

-- 1. Customers Table
CREATE TABLE IF NOT EXISTS customers (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(30)
);

-- 2. Products Table
CREATE TABLE IF NOT EXISTS products (
    id VARCHAR(50) PRIMARY KEY,
    sku VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(150) NOT NULL,
    category VARCHAR(50),
    price_idr BIGINT DEFAULT 0
);

-- 3. Support Agents Table
CREATE TABLE IF NOT EXISTS agents (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL
);

-- 4. Orders Table
CREATE TABLE IF NOT EXISTS orders (
    id VARCHAR(50) PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    customer_id VARCHAR(50) REFERENCES customers(id),
    status VARCHAR(50) NOT NULL,
    tracking_number VARCHAR(100),
    carrier VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Order Items Table
CREATE TABLE IF NOT EXISTS order_items (
    id VARCHAR(50) PRIMARY KEY,
    order_id VARCHAR(50) REFERENCES orders(id),
    product_id VARCHAR(50) REFERENCES products(id),
    quantity INTEGER DEFAULT 1
);

-- 6. Issues / Complaints Table
CREATE TABLE IF NOT EXISTS issues (
    id VARCHAR(50) PRIMARY KEY,
    order_id VARCHAR(50) REFERENCES orders(id),
    issue_type VARCHAR(100) NOT NULL,
    issue_status VARCHAR(50) NOT NULL,
    assigned_agent_id VARCHAR(50) REFERENCES agents(id),
    notes TEXT
);

-- ============================================================================
-- 1. SEED DATA: CUSTOMERS (10 Pelanggan)
-- ============================================================================
INSERT INTO customers (id, name, email, phone) VALUES
('CUST-001', 'Andi Pratama', 'andi.pratama@example.com', '+6281234567801'),
('CUST-002', 'Dewi Lestari', 'dewi.lestari@example.com', '+6281234567802'),
('CUST-003', 'Bambang Suroso', 'bambang.suroso@example.com', '+6281234567803'),
('CUST-004', 'Jessica Chandra', 'jessica.chandra@example.com', '+6281234567804'),
('CUST-005', 'Ahmad Fauzi', 'ahmad.fauzi@example.com', '+6281234567805'),
('CUST-006', 'Maya Putri', 'maya.putri@example.com', '+6281234567806'),
('CUST-007', 'Michael Chen', 'michael.chen@example.com', '+6281234567807'),
('CUST-008', 'Rian Hidayat', 'rian.hidayat@example.com', '+6281234567808'),
('CUST-009', 'Nadia Safira', 'nadia.safira@example.com', '+6281234567809'),
('CUST-010', 'Hendra Kusuma', 'hendra.kusuma@example.com', '+6281234567810')
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, email = EXCLUDED.email, phone = EXCLUDED.phone;

-- ============================================================================
-- 2. SEED DATA: PRODUCTS (10 Produk Katalog)
-- ============================================================================
INSERT INTO products (id, sku, name, category, price_idr) VALUES
('PROD-001', 'SKU-WF-PRO', 'Ultra Wireless Headphones Pro', 'Audio', 1899000),
('PROD-002', 'SKU-KB-RGB', 'Pro Gaming Mechanical Keyboard RGB', 'Peripherals', 1250000),
('PROD-003', 'SKU-MS-MESH', 'Smart Home Mesh Wi-Fi 6 Hub', 'Networking', 2100000),
('PROD-004', 'SKU-CH-ERGO', 'Ergonomic Executive Office Chair V2', 'Furniture', 3499000),
('PROD-005', 'SKU-MN-34UW', '4K Ultra-Wide Monitor 34-Inch Curved', 'Displays', 7850000),
('PROD-006', 'SKU-PB-20K', 'Fast Charging Powerbank 20000mAh 65W', 'Accessories', 450000),
('PROD-007', 'SKU-WT-FIT', 'Smart Fitness Tracker Band Active', 'Wearables', 699000),
('PROD-008', 'SKU-EB-AIR', 'Noise-Cancelling True Wireless Earbuds Air', 'Audio', 1150000),
('PROD-009', 'SKU-SP-BTMAX', 'Portable Bluetooth Speaker Max Bass', 'Audio', 890000),
('PROD-010', 'SKU-HB-USBC', 'USB-C 10-in-1 Multi-Port Docking Hub', 'Accessories', 550000)
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, category = EXCLUDED.category, price_idr = EXCLUDED.price_idr;

-- ============================================================================
-- 3. SEED DATA: AGENTS (5 Agen CS Spesialis)
-- ============================================================================
INSERT INTO agents (id, name, role, email) VALUES
('AGENT-001', 'Budi Santoso', 'Senior Logistics Support Specialist', 'budi.santoso@company.com'),
('AGENT-002', 'Siti Rahma', 'Billing & Refund Escalation Specialist', 'siti.rahma@company.com'),
('AGENT-003', 'David Tan', 'Hardware & Technical Support Engineer', 'david.tan@company.com'),
('AGENT-004', 'Rina Wijaya', 'Customer Experience & VIP Lead', 'rina.wijaya@company.com'),
('AGENT-005', 'Kevin Pratama', 'Fraud Prevention & Security Specialist', 'kevin.pratama@company.com')
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, role = EXCLUDED.role, email = EXCLUDED.email;

-- ============================================================================
-- 4. SEED DATA: ORDERS (15 Pesanan dengan Ragam Status)
-- ============================================================================
INSERT INTO orders (id, order_number, customer_id, status, tracking_number, carrier) VALUES
('ORD-4521', '#4521', 'CUST-001', 'Shipping Delayed', 'TRK-FDX-9988', 'FedEx'),
('ORD-4522', '#4522', 'CUST-001', 'Delivered', 'TRK-DHL-1122', 'DHL Express'),
('ORD-4523', '#4523', 'CUST-002', 'Damaged in Transit', 'TRK-JNE-3344', 'JNE Express'),
('ORD-4524', '#4524', 'CUST-003', 'Return Processing', 'TRK-SCP-5566', 'SiCepat Reguler'),
('ORD-4525', '#4525', 'CUST-004', 'Held by Customs', 'TRK-FDX-7788', 'FedEx International'),
('ORD-4526', '#4526', 'CUST-005', 'Delivered', 'TRK-JNT-9900', 'J&T Express'),
('ORD-4527', '#4527', 'CUST-006', 'Defective Hardware Reported', 'TRK-DHL-2233', 'DHL Express'),
('ORD-4528', '#4528', 'CUST-007', 'Address Issue / Held at Hub', 'TRK-SCP-4455', 'SiCepat Cargo'),
('ORD-4529', '#4529', 'CUST-008', 'Out for Delivery', 'TRK-JNE-6677', 'JNE YES'),
('ORD-4530', '#4530', 'CUST-009', 'Missing Items in Package', 'TRK-ANTER-8899', 'AnterAja'),
('ORD-4531', '#4531', 'CUST-010', 'Delivered', 'TRK-JNT-1011', 'J&T Express'),
('ORD-4532', '#4532', 'CUST-002', 'Order Processing / Packing', 'TRK-PENDING-01', 'Internal Warehouse'),
('ORD-4533', '#4533', 'CUST-003', 'Refund Approved', 'TRK-REFUND-02', 'Finance Transfer'),
('ORD-4534', '#4534', 'CUST-005', 'Lost in Transit', 'TRK-FDX-1213', 'FedEx'),
('ORD-4535', '#4535', 'CUST-007', 'Delivered', 'TRK-SCP-1415', 'SiCepat Reguler')
ON CONFLICT (id) DO UPDATE SET status = EXCLUDED.status, tracking_number = EXCLUDED.tracking_number, carrier = EXCLUDED.carrier;

-- ============================================================================
-- 5. SEED DATA: ORDER ITEMS
-- ============================================================================
INSERT INTO order_items (id, order_id, product_id, quantity) VALUES
('ITEM-001', 'ORD-4521', 'PROD-001', 1),
('ITEM-002', 'ORD-4522', 'PROD-001', 1),
('ITEM-003', 'ORD-4523', 'PROD-005', 1),
('ITEM-004', 'ORD-4524', 'PROD-004', 1),
('ITEM-005', 'ORD-4525', 'PROD-003', 2),
('ITEM-006', 'ORD-4526', 'PROD-002', 1),
('ITEM-007', 'ORD-4527', 'PROD-002', 1),
('ITEM-008', 'ORD-4528', 'PROD-004', 1),
('ITEM-009', 'ORD-4529', 'PROD-006', 2),
('ITEM-010', 'ORD-4530', 'PROD-010', 1),
('ITEM-011', 'ORD-4531', 'PROD-007', 1),
('ITEM-012', 'ORD-4532', 'PROD-008', 1),
('ITEM-013', 'ORD-4533', 'PROD-009', 1),
('ITEM-014', 'ORD-4534', 'PROD-001', 1),
('ITEM-015', 'ORD-4535', 'PROD-006', 1)
ON CONFLICT (id) DO UPDATE SET quantity = EXCLUDED.quantity;

-- ============================================================================
-- 6. SEED DATA: ISSUES & SUPPORT COMPLAINTS
-- ============================================================================
INSERT INTO issues (id, order_id, issue_type, issue_status, assigned_agent_id, notes) VALUES
('ISSUE-001', 'ORD-4521', 'Shipping Delay', 'Investigating with Carrier', 'AGENT-001', 'Customer reported shipment stuck at transit hub since Monday.'),
('ISSUE-002', 'ORD-4523', 'Damaged Item on Arrival', 'Replacement RMA Issued', 'AGENT-003', 'Screen glass cracked during shipping. RMA return shipping label sent to customer.'),
('ISSUE-003', 'ORD-4524', 'Refund / Return Request', 'Awaiting Warehouse Inspection', 'AGENT-002', 'Customer initiated return within 30-day window due to ergonomic mismatch.'),
('ISSUE-004', 'ORD-4525', 'Customs Clearance Delay', 'Submitted Import Documentation', 'AGENT-001', 'Package held at Soekarno-Hatta Airport customs awaiting import duty verification.'),
('ISSUE-005', 'ORD-4527', 'Defective Hardware', 'Under Technical Diagnostic', 'AGENT-003', 'Mechanical keyboard keys W and Spacebar unresponsive out of the box.'),
('ISSUE-006', 'ORD-4528', 'Incorrect Delivery Address', 'Re-routing Delivery', 'AGENT-004', 'Customer updated apartment unit number; dispatched driver notification.'),
('ISSUE-007', 'ORD-4530', 'Missing Box Accessories', 'Supplementary Parcel Dispatched', 'AGENT-002', 'USB-C host cable was missing from package; replacement dispatched with SiCepat.'),
('ISSUE-008', 'ORD-4534', 'Package Lost by Courier', 'Insurance Claim & Full Refund', 'AGENT-002', 'Courier confirmed package lost at hub; full refund of Rp 1.899.000 approved.')
ON CONFLICT (id) DO UPDATE SET issue_type = EXCLUDED.issue_type, issue_status = EXCLUDED.issue_status, assigned_agent_id = EXCLUDED.assigned_agent_id, notes = EXCLUDED.notes;
