-- Clear existing orders (optional, comment out if you want to keep existing orders)
-- TRUNCATE orders;

-- Reset the order number sequence
ALTER SEQUENCE order_number_seq RESTART WITH 1001;

-- Sample orders data with authentic menu items
INSERT INTO orders (
    id,
    status,
    order_number,
    customer_name,
    payment_method,
    order_time,
    estimated_delivery_time,
    total_items,
    total_amount,
    items,
    completed_time,
    actual_delivery_time
) VALUES 
-- South Indian Breakfast Order (5 minutes ago)
(
    '1',
    'pending',
    '1001',
    'Raj Kumar',
    'zelle',
    NOW() - INTERVAL '5 minutes',
    NOW() + INTERVAL '25 minutes',
    4,
    41.96,
    '[
        {
            "name": "Dosa",
            "quantity": 2,
            "price": 10.99,
            "subtotal": 21.98,
            "cooking_status": "not started"
        },
        {
            "name": "Idly",
            "quantity": 1,
            "price": 9.99,
            "subtotal": 9.99,
            "cooking_status": "not started"
        },
        {
            "name": "Coffee",
            "quantity": 2,
            "price": 3.00,
            "subtotal": 6.00,
            "cooking_status": "not started"
        },
        {
            "name": "Nellore Kaaram",
            "quantity": 1,
            "price": 3.99,
            "subtotal": 3.99,
            "cooking_status": "not started"
        }
    ]'::jsonb,
    NULL,
    NULL
),
-- Biryani Special Order (15 minutes ago)
(
    '2',
    'pending',
    '1002',
    'Sarah Williams',
    'cashapp',
    NOW() - INTERVAL '15 minutes',
    NOW() + INTERVAL '15 minutes',
    3,
    40.97,
    '[
        {
            "name": "Chicken Biryani",
            "quantity": 2,
            "price": 12.99,
            "subtotal": 25.98,
            "cooking_status": "cooking"
        },
        {
            "name": "Goat Biryani",
            "quantity": 1,
            "price": 12.99,
            "subtotal": 12.99,
            "cooking_status": "not started"
        },
        {
            "name": "Tea",
            "quantity": 1,
            "price": 2.00,
            "subtotal": 2.00,
            "cooking_status": "finished"
        }
    ]'::jsonb,
    NULL,
    NULL
),
-- Completed Non-Vegetarian Special (2 minutes ago)
(
    '3',
    'completed',
    '1003',
    'John Smith',
    'cash',
    NOW() - INTERVAL '32 minutes',
    NOW() - INTERVAL '2 minutes',
    4,
    49.96,
    '[
        {
            "name": "Goat Curry",
            "quantity": 2,
            "price": 14.99,
            "subtotal": 29.98,
            "cooking_status": "finished"
        },
        {
            "name": "Chicken 65",
            "quantity": 1,
            "price": 9.99,
            "subtotal": 9.99,
            "cooking_status": "finished"
        },
        {
            "name": "Paya Soup",
            "quantity": 1,
            "price": 8.99,
            "subtotal": 8.99,
            "cooking_status": "finished"
        }
    ]'::jsonb,
    NOW() - INTERVAL '2 minutes',
    NOW() - INTERVAL '2 minutes'
),
-- Family Party Order (just placed)
(
    '4',
    'pending',
    '1004',
    'Priya Patel',
    'zelle',
    NOW() - INTERVAL '2 minutes',
    NOW() + INTERVAL '45 minutes',
    12,
    88.89,
    '[
        {
            "name": "Dosa",
            "quantity": 3,
            "price": 10.99,
            "subtotal": 32.97,
            "cooking_status": "not started"
        },
        {
            "name": "Chicken 65",
            "quantity": 2,
            "price": 9.99,
            "subtotal": 19.98,
            "cooking_status": "not started"
        },
        {
            "name": "Chaat Items",
            "quantity": 3,
            "price": 5.99,
            "subtotal": 17.97,
            "cooking_status": "not started"
        },
        {
            "name": "Punugulu",
            "quantity": 2,
            "price": 5.99,
            "subtotal": 11.98,
            "cooking_status": "not started"
        },
        {
            "name": "Tea",
            "quantity": 3,
            "price": 2.00,
            "subtotal": 6.00,
            "cooking_status": "not started"
        }
    ]'::jsonb,
    NULL,
    NULL
),
-- Earlier completed order with mix of items
(
    '5',
    'completed',
    '1005',
    'Maya Rodriguez',
    'cashapp',
    NOW() - INTERVAL '1 hour 30 minutes',
    NOW() - INTERVAL '1 hour',
    6,
    51.94,
    '[
        {
            "name": "Fish Pulusu",
            "quantity": 1,
            "price": 12.99,
            "subtotal": 12.99,
            "cooking_status": "finished"
        },
        {
            "name": "Keema",
            "quantity": 1,
            "price": 15.99,
            "subtotal": 15.99,
            "cooking_status": "finished"
        },
        {
            "name": "Aloo Masala",
            "quantity": 2,
            "price": 6.99,
            "subtotal": 13.98,
            "cooking_status": "finished"
        },
        {
            "name": "Fruits Cutting",
            "quantity": 1,
            "price": 5.99,
            "subtotal": 5.99,
            "cooking_status": "finished"
        },
        {
            "name": "Coffee",
            "quantity": 1,
            "price": 3.00,
            "subtotal": 3.00,
            "cooking_status": "finished"
        }
    ]'::jsonb,
    NOW() - INTERVAL '1 hour',
    NOW() - INTERVAL '1 hour'
);
