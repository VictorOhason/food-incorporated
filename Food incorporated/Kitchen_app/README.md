# Food Inc - Backend Server

A Flask-based REST API backend for managing restaurant orders, tables, and inventory. Designed to connect to any server and database.

## Features

**Multi-Database Support**
- SQLite (local development)
- PostgreSQL (production)
- MySQL
- Extensible to other databases via SQLAlchemy

**Flexible CORS Configuration**
- Connect from any frontend server
- Configurable per environment
- Supports multiple origins

**Full API Endpoints**
- Orders management (create, retrieve, update status)
- Stock/Inventory management
- Table assignment (2 stores with 10 tables each)
- Automatic table state transitions
- Health check endpoint

**Automatic Data Persistence**
- Database initialization on startup
- Sample data loaded automatically
- Background task for table status management

---

## Quick Start

### 1. Install Dependencies
```bash
cd Kitchen_app
pip install -r requirements.txt
```

### 2. Configure (Optional)
Default configuration works out-of-box with SQLite. To customize:
```bash
# Edit .env
DATABASE_URL=sqlite:///foodinc.db  # Default
ALLOWED_ORIGINS=*                   # Accept all origins
PORT=5000
DEBUG=True
```

### 3. Run the Server
```bash
python server.py
```

Expected output:
```
Initializing database with default data
Database initialized successfully
* Running on http://0.0.0.0:5000
```

### 4. Verify Health
```bash
curl http://localhost:5000/health
```

---

## API Endpoints

### Health Check
```
GET /health
```
Response: `{"status": "healthy"}`

### Orders
```
GET /orders
POST /orders
PATCH /orders/<order_id>/status
```

### Stock
```
GET /stock
POST /stock/update
```

### Tables
```
GET /tables
GET /tables/<store_id>
POST /tables/assign
PATCH /tables/<store_id>/<table_id>/free
```

---

## Database Setup

### For Development (SQLite - Default)
No setup needed! Just run `python server.py`

### For Production (PostgreSQL)
See [DATABASE_SETUP.md](DATABASE_SETUP.md) for detailed instructions.

Examples:
```bash
# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/foodinc

# MySQL
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/foodinc

# Heroku PostgreSQL
DATABASE_URL=<auto-set by Heroku>
```

---

## Connecting from Other Servers

### CORS Configuration
By default, the server accepts requests from any origin. For production, restrict to specific servers:

```bash
# .env
ALLOWED_ORIGINS=https://menu.foodinc.com,https://kitchen.foodinc.com,https://admin.foodinc.com
```

### Frontend Example (JavaScript)
```javascript
const response = await fetch('http://api-server:5000/tables/assign', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    storeId: 'store1',
    customerEmail: 'user@example.com'
  })
});
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///foodinc.db` | Database connection string |
| `ALLOWED_ORIGINS` | `*` | CORS allowed origins (comma-separated) |
| `PORT` | `5000` | Server port |
| `DEBUG` | `False` | Enable Flask debug mode |

---

## Database Models

### Store
- `id`: Primary key
- `store_id`: Unique identifier (e.g., "store1")
- `name`: Store name
- `location`: Store location

### Table
- `id`: Primary key
- `store_id`: Foreign key to Store
- `table_id`: Table number (1-10 per store)
- `status`: "free" or "occupied"
- `assigned_to`: Customer email when occupied
- `occupied_since`: Timestamp when occupied

### StockItem
- `id`: Primary key
- `name`: Item name
- `quantity`: Current stock
- `unit`: Unit of measurement (kg, pcs, liters, etc.)

### Order
- `id`: Primary key
- `order_number`: Unique order number
- `store_id`: Foreign key to Store
- `table_number`: Table number
- `customer_name`: Customer name
- `customer_email`: Customer email
- `status`: "pending", "preparing", or "ready"
- `items`: JSON array of ordered items
- `total`: Order total price
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

---

## Deployment

### Heroku
```bash
# Create app with PostgreSQL addon
heroku create your-app
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set ALLOWED_ORIGINS="https://your-domain.com"

# Push code
git push heroku main
```

### AWS/DigitalOcean/Other VPS
```bash
# Install Python 3.8+
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://..."
export ALLOWED_ORIGINS="https://your-domain.com"

# Run with production server
gunicorn server:app --bind 0.0.0.0:5000 --workers 4
```

---

## Troubleshooting

### Database connection error
- Check `DATABASE_URL` is set correctly
- Verify database exists and credentials are correct
- See [DATABASE_SETUP.md](DATABASE_SETUP.md)

### CORS errors in browser
- Check `ALLOWED_ORIGINS` includes your frontend domain
- For development: set `ALLOWED_ORIGINS=*`

### Port already in use
```bash
# Change PORT in .env or
python server.py  # Will use next available port
```

### Tables not initializing
Delete `foodinc.db` (SQLite) or the database itself and restart the server.

---

## Development

### Running with Debug Mode
```bash
DEBUG=True python server.py
```

### Testing Endpoints
```bash
# Get all tables
curl http://localhost:5000/tables

# Assign a table
curl -X POST http://localhost:5000/tables/assign \
  -H "Content-Type: application/json" \
  -d '{"storeId":"store1","customerEmail":"test@example.com"}'

# Get health status
curl http://localhost:5000/health
```

---

## License

Food Inc - All Rights Reserved
