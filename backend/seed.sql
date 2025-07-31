-- Initial admin user (password: memfamous2025)
INSERT INTO users (username, password_hash) 
VALUES ('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewLJsQJnr.OAFYdu')
ON CONFLICT (username) DO NOTHING;

-- Initial menu items
INSERT INTO menu_items (id, name, chef, sous_chef, category, price)
VALUES 
    ('dosa', 'Dosa', 'Sunoj', 'Rakesh', 'South Indian', 10.99),
    ('chicken_biryani', 'Chicken Biryani', 'Nachu', 'Sreedhar', 'Biryani', 12.99),
    ('goat_biryani', 'Goat Biryani', 'Mario', 'Rakesh', 'Biryani', 12.99),
    ('goat_curry', 'Goat Curry', 'Mario', NULL, 'Curry', 14.99),
    ('fish_pulusu', 'Fish Pulusu', 'Sunoj', NULL, 'Fish', 12.99),
    ('chicken_65', 'Chicken 65', 'Sunoj', 'Jnet', 'Starters', 9.99),
    ('idly', 'Idly', 'Jose', 'Ranjitha Mom', 'South Indian', 9.99),
    ('coffee', 'Coffee', 'Ravi Mom', NULL, 'Beverages', 3.00),
    ('chaat_items', 'Chaat Items', 'Bhavana', 'Abhiram', 'Chaat', 5.99),
    ('bajji', 'Bajji', 'Gupta', 'Akula', 'Snacks', 6.99),
    ('punugulu', 'Punugulu', 'Akula', 'Bhavana(Batter)', 'Snacks', 5.99),
    ('nellore_kaaram', 'Nellore Kaaram', 'Mridula', 'Sravani', 'Spicy', 10.99),
    ('paya_soup', 'Paya Soup', 'Sreedhar', 'Jnet', 'Soup', 8.99),
    ('keema', 'Keema', 'Sreedhar', 'Jnet', 'Meat', 15.99),
    ('tea', 'Tea', 'Dera', NULL, 'Beverages', 2.00),
    ('aloo_masala', 'Aloo Masala', 'Anusha Allu', NULL, 'Vegetarian', 6.99),
    ('fruits_cutting', 'Fruits Cutting', 'Kitchen Staff', NULL, 'Dessert', 5.99)
ON CONFLICT (id) DO UPDATE 
SET 
    name = EXCLUDED.name,
    chef = EXCLUDED.chef,
    sous_chef = EXCLUDED.sous_chef,
    category = EXCLUDED.category,
    price = EXCLUDED.price;

-- Sample order with items
INSERT INTO orders (
    id, 
    order_number, 
    customer_name, 
    items, 
    payment_method, 
    status, 
    order_time,
    total_items,
    total_amount
)
VALUES (
    uuid_generate_v4()::text,
    nextval('order_number_seq')::text,
    'Sample Customer',
    '[
        {
            "name": "Dosa",
            "quantity": 2,
            "price": 10.99,
            "subtotal": 21.98,
            "cooking_status": "not started"
        },
        {
            "name": "Coffee",
            "quantity": 1,
            "price": 3.00,
            "subtotal": 3.00,
            "cooking_status": "not started"
        }
    ]'::jsonb,
    'cash',
    'pending',
    CURRENT_TIMESTAMP,
    3,
    24.98
);

-- Sample notification for the order
INSERT INTO notifications (
    id,
    customer_name,
    message,
    order_id,
    is_active
)
SELECT 
    uuid_generate_v4()::text,
    'Sample Customer',
    'Your order has been received and is being prepared.',
    id,
    true
FROM orders
WHERE customer_name = 'Sample Customer'
LIMIT 1;
