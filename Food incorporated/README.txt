Food Incorporated - Project Overview

This document explains the purpose of each major file in the workspace, how the application works, and the common issues to watch for.

---

1) Project Structure

Admin_Login/
  index.html       - login page for customers/staff.
  script.js        - email-only login flow, saves customer name/email to localStorage, and redirects to menu.
  style.css        - visual styling for the login page.

Images/
  (image files)    - asset folder containing food images used by the menu carousel.

Kitchen_app/
  server.py        - main Flask backend application.
  models.py        - SQLAlchemy database model definitions for stores, tables, stock, and orders.
  Procfile         - optional deployment config for services like Heroku.
  qt6-old-app.txt  - legacy PyQt UI draft file; not part of current web app runtime.
  requirements.txt - Python dependency list for backend runtime.
  app.py           - likely another backend or app entrypoint; not part of the main current flow.
  api.py           - additional backend API helper or stub file; not part of the primary current flow.
  widgets/         - custom UI widgets for old Qt application.

Menu/
  menu.html        - customer menu page used to select items and place orders.
  menu.js          - frontend menu behavior, table assignment, carousel, item quantity, order summary, and order submission logic.
  menu.css         - styling for menu page.
  checkout.html    - order review/checkout page for finalizing orders.
  checkout.js      - frontend checkout behavior for order submission and handling.

favicon.ico        - browser favicon used by HTML pages.
create_favicon.py  - script to generate or manage the favicon file.
"Tutorial for FoodInc.mp4" - video file, likely a project walkthrough or demo.

---

2) Backend: Kitchen_app/server.py

Purpose: Provides a REST API, database initialization, and table lifecycle management.

Key sections and functions:

- load_dotenv() and config setup
  * Loads environment variables from a .env file if present.
  * DATABASE_URL is used to configure SQLAlchemy.
  * Supports SQLite by default and adjusts `postgres://` URLs to `postgresql://`.
  * CORS is enabled for the allowed origins list.

- init_db()
  * Creates database tables for stores, tables, stock_items, and orders.
  * Seeds default stores, 10 tables per store, and stock inventory only when the database is initially empty.
  * This function runs on startup to ensure a working database.

- /health
  * Basic health check endpoint.
  * Returns status and message so load balancers or monitoring can confirm the backend is running.

- /stock
  * GET `/stock`: returns current kitchen inventory.
  * POST `/stock/update`: updates a stock item's quantity by ID.
  * Validation ensures the requested stock item exists.

- /orders
  * GET `/orders`: returns all saved order records.
  * POST `/orders`: creates a new order.
    - Requires `orderNumber` and `tableNumber`.
    - Stores order fields, items, and total.
    - Decrements matching stock items for each order item using a simple fuzzy name match.
    - Commits the order and inventory updates together.

- /orders/<order_id>/status
  * PATCH updates the status of an existing order.
  * Looks up the order by `order_number`.

- /tables
  * GET `/tables`: returns table state for every store.
  * GET `/tables/<store_id>`: returns tables for one store only.
  * POST `/tables/assign`: reserves the next free table in a store.
    - Requests should include `storeId` and optionally `customerEmail`.
    - Marks the found table `occupied`, saves the assigned email, and sets `occupied_since`.
    - Returns 409 when no free tables are available.
  * PATCH `/tables/<store_id>/<table_id>/free`: marks a table free again.
    - Clears `assigned_to` and `occupied_since`.

- Background cleanup worker
  * `check_occupied_tables()` runs every 60 seconds.
  * It frees tables that have been occupied longer than 30 minutes.
  * This thread is started automatically when the app launches.

- Application startup
  * `init_db()` is called when the module is executed directly.
  * The Flask app listens on `0.0.0.0` and uses `PORT` and `DEBUG` from environment variables.

Common backend issues:
  * `DATABASE_URL` misconfiguration.
  * Wrong host/port if frontend uses `http://127.0.0.1:5000` but backend is running elsewhere.
  * CORS settings blocking the frontend if `ALLOWED_ORIGINS` is not set correctly.
  * Database not seeded because `init_db()` was not run or the database file is not writable.
  * Order stock decrement logic may not match names exactly, creating inconsistent inventory updates.
  * Duplicate `orderNumber` values can fail if an order with the same number already exists.

---

3) Backend Models: Kitchen_app/models.py

Purpose: Defines the persistent data schema for the backend.

Models:

- Store
  * `store_id`: external store identifier, e.g. `store1`.
  * `name` and `location`
  * Relationships to `Table` and `Order`.

- Table
  * `table_id`: table number inside a store.
  * `status`: `free` or `occupied`.
  * `assigned_to`: email of the customer currently using the table.
  * `occupied_since`: timestamp when the table was assigned.
  * Unique constraint on `(store_id, table_id)`.

- StockItem
  * `name`, `quantity`, `unit`
  * Used by the kitchen inventory API.

- Order
  * `order_number`: unique order id used by application flow.
  * `table_number`, `customer_name`, `customer_email`
  * `status`: order lifecycle state.
  * `items`: JSON payload of the ordered items.
  * `total`: order total amount.

Each model includes `to_dict()` for JSON serialization.

Common model issues:
  * If the `store_id` or `table_id` fields are inconsistent between frontend and backend, table assignment will fail.
  * `items` stored as JSON must be valid JSON; invalid payloads may break order creation.
  * `order_number` collisions can prevent new orders from being saved.

---

4) Frontend: Admin_Login/script.js

Purpose: simple login experience using email only.

Key behavior:
  * Validates that an email is present and in the correct format.
  * Stores `customerName` and `customerEmail` in localStorage.
  * Redirects to `../Menu/menu.html` after login.
  * Includes a placeholder social login button with a future stub.

Common issues:
  * localStorage blocked by browser privacy settings causes sign-in failure.
  * Missing or incorrect path to `../Menu/menu.html` prevents redirect.
  * Invalid email entry triggers validation alerts.

---

5) Frontend: Menu/menu.js

Purpose: handles table assignment, menu interactions, order summary, and order submission.

Key functions and areas:

- Global configuration
  * `ASSIGNED_TABLE` / `ASSIGNED_STORE`
  * `LIVE_SERVER_URL` and `TABLE_API_URL` point to backend endpoints.

- `window.onload`
  * Checks `sessionStorage` for a cached table assignment.
  * If none exists, calls `assignTableFromServer()`.
  * Restores the saved customer name in the menu form.
  * Starts the image carousel.
  * Adds aria labels to quantity buttons.

- `assignTableFromServer()`
  * Posts to `/tables/assign` and stores the result in sessionStorage.
  * Falls back to a random table if assignment fails.

- `displayTable()`
  * Updates the UI with the current assigned table.

- `startCarousel()`
  * Rotates food images every 5 seconds.
  * Updates alt text and announcements for accessibility.

- Quantity button handling
  * Increases or decreases item quantities.
  * Changes quantity styling when item count is above zero.

- Form submit handling
  * Builds an order summary from selected items.
  * Performs validation to ensure at least one item is selected.
  * Generates a random `orderNumber` and stores order details in `currentOrder`.
  * Opens a modal for confirmation.

- Modal accessibility
  * `openModal()` and `closeModal()` manage focus and visibility.
  * Escape closes the modal.
  * Tab key focus is trapped inside the modal.

Common frontend issues:
  * If the server is not running, `/tables/assign` will fail and the page uses a fallback table.
  * Cross-origin issues when backend and frontend are served from different hosts.
  * Missing DOM elements in HTML can break menu.js if selectors return null.
  * The frontend uses `sessionStorage` for table state and `localStorage` for identity, so browser storage must be enabled.
  * `orderNumber` is generated randomly by the frontend and may collide with existing backend records.

---

6) General Application Flow

1. User opens `Admin_Login/index.html`.
2. They enter an email and submit the form.
3. `script.js` stores the user email and name locally.
4. The browser redirects to `Menu/menu.html`.
5. `menu.js` assigns or restores a table from the backend.
6. The user selects menu items and submits the order.
7. The frontend sends the order payload to `Kitchen_app/server.py` via `/orders`.
8. The backend saves the order, updates stock, and stores table assignment state.
9. The background thread periodically frees tables held longer than 30 minutes.

---

7) Deployment and Environment Notes

- Use `.env` in `Kitchen_app` to define:
  * `DATABASE_URL` for the SQLAlchemy database.
  * `PORT` for the Flask server.
  * `DEBUG` to enable debug mode.
  * `ALLOWED_ORIGINS` for CORS origin control.

- Default database is SQLite at `sqlite:///foodinc.db`.
- For PostgreSQL, set `DATABASE_URL=postgresql://user:pass@host:port/dbname`.
- Ensure the backend is launched from `Kitchen_app` if relative imports are used.

Common deployment issues:
  * `postgres://` URIs must be converted to `postgresql://`.
  * `ALLOWED_ORIGINS` must include the frontend origin or else CORS blocks requests.
  * If the app starts without `init_db()`, the tables may not exist.
  * Running backend from the wrong working directory can break relative imports.

---

8) Notes on Legacy/Unused Files

- `Kitchen_app/qt6-old-app.txt` is a legacy PyQt draft and not used by the current web-based menu/order system.
- `create_favicon.py` is a utility script for the favicon and is not part of regular runtime.
- `Tutorial for FoodInc.mp4` is a demo/tutorial asset and does not affect application logic.

---

Use this file as a quick reference for how the app is organized, which backend routes support each feature, and what to verify when the system does not behave as expected.
