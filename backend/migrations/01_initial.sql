-- Create orders table if it doesn't exist
CREATE TABLE IF NOT EXISTS orders (
    id TEXT PRIMARY KEY,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'completed')),
    order_number TEXT UNIQUE NOT NULL,
    customer_name TEXT NOT NULL,
    payment_method TEXT NOT NULL CHECK (payment_method IN ('zelle', 'cashapp', 'cash')),
    order_time TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_time TIMESTAMPTZ,
    estimated_delivery_time TIMESTAMPTZ,
    actual_delivery_time TIMESTAMPTZ,
    delivery_minutes INTEGER DEFAULT 30,
    total_items INTEGER NOT NULL DEFAULT 0,
    total_amount DECIMAL(10,2) NOT NULL DEFAULT 0.0,
    items JSONB NOT NULL DEFAULT '[]'::jsonb CHECK (jsonb_array_length(items) > 0)
);

-- Create indexes if they don't exist
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_order_time ON orders(order_time);
CREATE INDEX IF NOT EXISTS idx_orders_order_number ON orders(order_number);

-- Create sequence if it doesn't exist
CREATE SEQUENCE IF NOT EXISTS order_number_seq
    START WITH 1001
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
