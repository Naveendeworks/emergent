# Order Management System - Backend Integration Contracts

## API Contracts

### Base URL
- All API endpoints prefixed with `/api`
- Backend URL: `process.env.REACT_APP_BACKEND_URL/api`

### Endpoints

#### 1. GET /api/orders
- **Purpose**: Fetch all orders
- **Response**: Array of order objects
- **Status Codes**: 200 (success), 500 (server error)

#### 2. POST /api/orders
- **Purpose**: Create new order
- **Body**: `{ customerName: string, items: [{ name: string, quantity: number }] }`
- **Response**: Created order object
- **Status Codes**: 201 (created), 400 (validation error), 500 (server error)

#### 3. PUT /api/orders/{id}/complete
- **Purpose**: Mark order as completed
- **Response**: Updated order object
- **Status Codes**: 200 (success), 404 (not found), 500 (server error)

#### 4. GET /api/orders/stats
- **Purpose**: Get order statistics
- **Response**: `{ pending: number, completed: number, total: number }`
- **Status Codes**: 200 (success), 500 (server error)

## Data Models

### Order Schema
```javascript
{
  _id: ObjectId,
  customerName: String (required),
  items: [{ 
    name: String (required), 
    quantity: Number (required, min: 1) 
  }],
  status: String (enum: ['pending', 'completed'], default: 'pending'),
  orderTime: Date (default: now),
  totalItems: Number (calculated field)
}
```

## Mock Data Replacement

### Current Mock Data in `/app/frontend/src/mock.js`:
- `mockOrders` array → Replace with API calls to `/api/orders`
- `completeOrder()` function → Replace with API call to `/api/orders/{id}/complete`
- `getPendingOrders()` → Filter from API response
- `getCompletedOrders()` → Filter from API response

### Frontend Integration Changes:

#### 1. OrderManager.jsx
- Replace `useState(mockOrders)` with `useState([])`
- Add `useEffect` to fetch orders on component mount
- Replace `handleCompleteOrder` to make API call
- Add loading states and error handling

#### 2. Remove Mock Dependencies
- Remove `import { mockOrders, completeOrder } from '../mock'`
- Keep `formatOrderTime` helper function

## Backend Implementation Plan

### 1. MongoDB Models
- Create `Order` model with Pydantic schemas
- Add validation for required fields
- Implement calculated fields (totalItems)

### 2. FastAPI Endpoints
- CRUD operations for orders
- Order completion logic
- Statistics endpoint
- Error handling and validation

### 3. Database Operations
- Create order with timestamp
- Update order status
- Query orders by status
- Aggregate statistics

## Frontend-Backend Integration Steps

### Phase 1: Replace Mock with API
1. Create API service functions in `frontend/src/services/api.js`
2. Update OrderManager.jsx to use API calls
3. Add error handling and loading states
4. Test order creation and completion

### Phase 2: Enhanced Features
1. Real-time updates (optional)
2. Order validation
3. Enhanced error messages
4. Performance optimizations

## Testing Strategy
1. Test backend endpoints with curl/postman
2. Test frontend API integration
3. Verify order completion workflow
4. Test error scenarios and edge cases