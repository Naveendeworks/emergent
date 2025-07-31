-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop tables if they exist
DROP TABLE IF EXISTS notifications;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS menu_items;
DROP TABLE IF EXISTS users;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Create menu_items table
CREATE TABLE IF NOT EXISTS menu_items (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    chef TEXT NOT NULL,
    sous_chef TEXT,
    category TEXT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    available BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Create orders table
CREATE TABLE IF NOT EXISTS orders (
    id TEXT PRIMARY KEY,
    order_number TEXT UNIQUE NOT NULL,
    customer_name TEXT NOT NULL,
    items JSONB NOT NULL CHECK (jsonb_array_length(items) > 0),
    payment_method TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    order_time TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_time TIMESTAMPTZ,
    estimated_delivery_time TIMESTAMPTZ,
    actual_delivery_time TIMESTAMPTZ,
    delivery_minutes INTEGER DEFAULT 30,
    total_items INTEGER DEFAULT 0,
    total_amount DECIMAL(10,2) DEFAULT 0.0,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_payment CHECK (payment_method IN ('zelle', 'cashapp', 'cash')),
    CONSTRAINT valid_status CHECK (status IN ('pending', 'completed'))
);

-- Create notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id TEXT PRIMARY KEY,
    customer_name TEXT NOT NULL,
    message TEXT NOT NULL,
    order_id TEXT REFERENCES orders(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_menu_items_category ON menu_items(category);
CREATE INDEX IF NOT EXISTS idx_menu_items_available ON menu_items(available);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_order_time ON orders(order_time);
CREATE INDEX IF NOT EXISTS idx_orders_payment_method ON orders(payment_method);
CREATE INDEX IF NOT EXISTS idx_notifications_order_id ON notifications(order_id);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at);
CREATE INDEX IF NOT EXISTS idx_notifications_is_active ON notifications(is_active);

-- Create sequence for order numbers
CREATE SEQUENCE IF NOT EXISTS order_number_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

-- Add comment
COMMENT ON TABLE orders IS 'Stores all order information with items as JSONB';
COMMENT ON TABLE notifications IS 'Stores notifications for orders with read status';
COMMENT ON TABLE menu_items IS 'Stores menu items with availability status';
COMMENT ON TABLE users IS 'Stores user authentication information';
