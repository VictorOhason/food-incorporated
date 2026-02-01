// ================================
// GLOBAL STATE
// ================================
// Assign a random table number when they open the site
const ASSIGNED_TABLE = Math.floor(Math.random() * 20) + 1;
document.getElementById('display-table').textContent = ASSIGNED_TABLE;

let currentOrder = null;

// ================================
// 1. ADD / REMOVE LOGIC (+ and - buttons)
// ================================
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('qty-btn')) {
        const controls = e.target.closest('.item-controls');
        const qtySpan = controls.querySelector('.quantity');
        let qty = parseInt(qtySpan.textContent);

        if (e.target.classList.contains('increase')) {
            qty++;
        } else if (e.target.classList.contains('decrease')) {
            if (qty > 0) qty--; // Prevents negative numbers
        }

        qtySpan.textContent = qty;

        // Visual feedback: Change color if quantity > 0
        if (qty > 0) {
            qtySpan.style.color = "var(--british-red)";
            qtySpan.style.fontWeight = "bold";
        } else {
            qtySpan.style.color = "var(--text-dark)";
            qtySpan.style.fontWeight = "normal";
        }
    }
});

// ================================
// 2. SUBMIT → SHOW SUMMARY
// ================================
const form = document.getElementById("order-form");
const modal = document.getElementById("checkout-modal");
const summary = document.getElementById("order-summary");
const totalPriceEl = document.getElementById("total-price");
// Inside menu.js, when the page loads:
window.onload = () => {
    const savedName = localStorage.getItem("customerName");
    if (savedName) {
        document.getElementById("customer-name").value = savedName;
    }
};
form.addEventListener("submit", function (e) {
    e.preventDefault();
    
    const items = [];
    let grandTotal = 0;

    // Scan all menu items to see what was selected
    document.querySelectorAll(".menu-item").forEach(item => {
        const qty = parseInt(item.querySelector(".quantity").textContent);
        
        if (qty > 0) {
            const name = item.querySelector("h3").textContent;
            const price = parseFloat(item.querySelector(".price").textContent.replace('£', ''));
            const subtotal = price * qty;
            
            items.push({
                name: name,
                quantity: qty,
                subtotal: subtotal
            });
            grandTotal += subtotal;
        }
    });

    if (items.length === 0) {
        alert("Your basket is empty! Please add some fish and chips.");
        return;
    }

    // Save order data temporarily
    currentOrder = {
        orderNumber: Math.floor(1000 + Math.random() * 9000),
        tableNumber: ASSIGNED_TABLE,
        items: items,
        total: grandTotal.toFixed(2)
    };

    // Show the modal
    summary.innerHTML = items.map(i => `
        <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
            <span>${i.quantity}x ${i.name}</span>
            <span>£${i.subtotal.toFixed(2)}</span>
        </div>
    `).join('');
    
    totalPriceEl.textContent = grandTotal.toFixed(2);
    modal.classList.remove("hidden");
});

// ================================
// 3. CONFIRM → SEND TO PYTHON
// ================================
document.getElementById("confirm-order").addEventListener("click", () => {
    const customerName = document.getElementById("customer-name").value.trim();

    if (!customerName) {
        alert("Please enter your name so we know who the food is for!");
        return;
    }

    const finalPayload = {
        ...currentOrder,
        customerName: customerName
    };

    // Disable button to prevent double-ordering
    const btn = document.getElementById("confirm-order");
    btn.disabled = true;
    btn.textContent = "Sending...";

    fetch("http://localhost:5000/orders", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(finalPayload)
    })
    .then(res => {
        if (res.ok) {
            alert(`Thanks ${customerName}! Your order is being prepared for Table ${ASSIGNED_TABLE}.`);
            location.reload(); // Reset everything
        }
    })
    .catch(() => {
        alert("Error connecting to the kitchen. Is the server running?");
        btn.disabled = false;
        btn.textContent = "Send to Kitchen";
    });
});

// Close modal
document.getElementById("cancel-order").onclick = () => modal.classList.add("hidden");