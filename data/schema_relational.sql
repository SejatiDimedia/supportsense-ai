-- ============================================================================
-- SupportSense AI: Rich Relational Database Schema & Comprehensive Seed Data
-- Compatible with: PostgreSQL, MySQL 8+, and SQLite
-- ============================================================================

DROP TABLE IF EXISTS support_documents;
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
('ITEM-015', 'ORD-4535', 'PROD-006', 1),
('ITEM-016', 'ORD-4525', 'PROD-004', 1)
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


-- ============================================================================
-- 7. SUPPORT DOCUMENTS TABLE (RAG Knowledge Base in PostgreSQL)
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_documents (
    id VARCHAR(100) PRIMARY KEY,
    source VARCHAR(100) NOT NULL,
    category VARCHAR(100) NOT NULL,
    section VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO support_documents (id, source, category, section, content) VALUES
('faq.md_000', 'faq.md', 'FAQ', 'What are your customer support operating hours?', '## What are your customer support operating hours?
Our support team is available Monday through Friday, from 9:00 AM to 6:00 PM EST. Inquiries submitted outside these hours or during public holidays will be reviewed on the next business day.'),
('faq.md_001', 'faq.md', 'FAQ', 'How can I track my general inquiry or support ticket?', '## How can I track my general inquiry or support ticket?
Every inquiry logged in our system is assigned a unique reference ID. You can check the status at any time by asking our support assistant with your order number or reference ID, or by checking your registered email.'),
('faq.md_002', 'faq.md', 'FAQ', 'How long does standard shipping take?', '## How long does standard shipping take?
Standard domestic shipping usually takes between 3 to 5 business days. Express shipping takes 1 to 2 business days. Tracking numbers are generated and emailed as soon as the package leaves our warehouse.'),
('faq.md_003', 'faq.md', 'FAQ', 'Can I change my delivery address after placing an order?', '## Can I change my delivery address after placing an order?
Address changes are permitted within 2 hours of order placement. Once an order enters the fulfillment stage or has been picked up by the carrier, the address cannot be modified directly, and a redirect request must be filed through our support team.'),
('faq.md_004', 'faq.md', 'FAQ', 'How do I update my profile details?', '## How do I update my profile details?
You can update your personal contact details, email address, and notification preferences by logging into your account dashboard under "Account Settings".'),
('faq.md_005', 'faq.md', 'FAQ', 'What should I do if I suspect unauthorized activity on my account?', '## What should I do if I suspect unauthorized activity on my account?
Please immediately request a password reset via the login screen. For safety reasons, automated agents and standard representatives cannot directly view, alter, or bypass your password credentials. Suspicious activity reports are automatically escalated to our Security & Fraud Prevention team.'),
('policy.md_000', 'policy.md', 'Policy', 'Eligibility for Refunds', '## Eligibility for Refunds
We offer a 30-day money-back guarantee on all eligible products purchased directly from our official store. To qualify for a full refund:
- The return request must be initiated within 30 calendar days from the delivery date.
- Items must be returned in their original packaging, in new or unused condition, complete with all accessories, manuals, and documentation.
- Proof of purchase (Order number and receipt) is required.'),
('policy.md_001', 'policy.md', 'Policy', 'Refund Processing Timeline', '## Refund Processing Timeline
Once our warehouse inspects and verifies the returned items (usually within 2 to 4 business days of receipt):
- Approved refunds are credited back to the original payment method.
- Credit card refunds take 5 to 10 business days to reflect on your statement depending on your banking provider.
- Shipping fees are non-refundable unless the return is due to our error or product defect.'),
('policy.md_002', 'policy.md', 'Policy', 'Immediate Action Protocol', '## Immediate Action Protocol
If your package or item arrives damaged, dented, broken, or defective:
- You must report the damage within 48 hours of delivery.
- Please provide clear photos or a short video demonstrating the packaging and product defect.
- A replacement item will be expedited to you at zero additional cost, or a full refund will be initiated if a replacement is unavailable.
- A dedicated Customer Support Representative will be assigned to coordinate the carrier claim and courier pickup of the damaged item.'),
('policy.md_003', 'policy.md', 'Policy', 'Cancellation Window', '## Cancellation Window
Orders can be canceled free of charge before they enter the shipping and dispatch phase (typically within 1 to 2 hours of payment). Once shipped, the order cannot be recalled from transit and must follow the standard 30-day return process upon receipt.'),
('product_manual.md_000', 'product_manual.md', 'Manual', 'Warranty Length', '## Warranty Length
All hardware products purchased from our authorized channels come with a comprehensive Limited Manufacturer Warranty:
- **Standard Electronics & Smart Devices**: 24 months (2 years) from the date of purchase.
- **Accessories & Cables**: 12 months (1 year) from the date of purchase.
- **Consumables & Wearables**: 6 months limited coverage.'),
('product_manual.md_001', 'product_manual.md', 'Manual', 'What is Covered', '## What is Covered
- Mechanical, electrical, and internal component failures occurring during standard and proper usage.
- Manufacturing flaws, dead pixels (more than 3), and firmware anomalies not caused by user modification.
- Repair labor and genuine replacement parts.'),
('product_manual.md_002', 'product_manual.md', 'Manual', 'What is Not Covered', '## What is Not Covered
- Accidental drops, physical impact, liquid submersion, fire damage, or theft.
- Unauthorized disassembly, third-party repairs, or jailbreaking/rooting firmware modifications.
- Normal cosmetic wear and tear (scratches, dents, fading).'),
('product_manual.md_003', 'product_manual.md', 'Manual', 'How to File a Claim', '## How to File a Claim
To file a warranty service request:
1. Locate your original order number (e.g., #4521) and the device serial number located on the underside or packaging.
2. Contact our support team via live chat or submit a ticket detailing the symptom.
3. Our technical team will issue a Prepaid Return Merchandise Authorization (RMA) shipping label.
4. Repack the device securely and drop it off at an authorized carrier drop-point.
5. Repairs or replacements are processed and shipped back within 7 to 10 business days.')
ON CONFLICT (id) DO UPDATE SET 
    source = EXCLUDED.source, 
    category = EXCLUDED.category, 
    section = EXCLUDED.section, 
    content = EXCLUDED.content;
