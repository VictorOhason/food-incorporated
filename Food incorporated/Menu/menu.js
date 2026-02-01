// ================================
// GLOBAL STATE & SETUP
// ================================
const ASSIGNED_TABLE = Math.floor(Math.random() * 20) + 1;

// Replace this with your actual URL once you create the service on Render.com
const LIVE_SERVER_URL = "https://your-app-name.onrender.com/orders";

window.onload = () => {
    // 1. Display assigned table
    const tableEl = document.getElementById('display-table');
    if (tableEl) tableEl.textContent = ASSIGNED_TABLE;

    // 2. Auto-fill name from login
    const savedName = localStorage.getItem("customerName");
    if (savedName) {
        document.getElementById("customer-name").value = savedName;
    }
};

let currentOrder = null;

// ================================
// 1. ADD / REMOVE LOGIC (+ and -)
// ================================
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('qty-btn')) {
        const controls = e.target.closest('.item-controls');
        const qtySpan = controls.querySelector('.quantity');
        let qty = parseInt(qtySpan.textContent);

        if (e.target.classList.contains('increase')) {
            qty++;
        } else if (e.target.classList.contains('decrease') && qty > 0) {
            qty--;
        }

        qtySpan.textContent = qty;

        // Visual feedback
        qtySpan.style.color = qty > 0 ? "#c8102e" : "#1a1a1a";
        qtySpan.style.fontWeight = qty > 0 ? "bold" : "normal";
    }
});

// ================================
// 2. SUBMIT → SHOW MODAL SUMMARY
// ================================
const form = document.getElementById("order-form");
const modal = document.getElementById("checkout-modal");
const summary = document.getElementById("order-summary");
const totalPriceEl = document.getElementById("total-price");

form.addEventListener("submit", function (e) {
    e.preventDefault();
    
    const items = [];
    let grandTotal = 0;

    document.querySelectorAll(".menu-item").forEach(item => {
        const qty = parseInt(item.querySelector(".quantity").textContent);
        if (qty > 0) {
            const name = item.querySelector("h3").textContent;
            const price = parseFloat(item.querySelector(".price").textContent.replace('£', ''));
            items.push({ name, quantity: qty, subtotal: price * qty });
            grandTotal += (price * qty);
        }
    });

    if (items.length === 0) {
        alert("Please select at least one item.");
        return;
    }

    currentOrder = {
        orderNumber: Math.floor(1000 + Math.random() * 9000),
        tableNumber: ASSIGNED_TABLE,
        items: items,
        total: grandTotal.toFixed(2)
    };

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
// 3. CONFIRM → SEND TO LIVE SERVER
// ================================
document.getElementById("confirm-order").addEventListener("click", () => {
    const customerName = document.getElementById("customer-name").value.trim();

    if (!customerName) {
        alert("Please enter your name!");
        return;
    }

    const finalPayload = {
        ...currentOrder,
        customerName: customerName
    };

    // Disable button to prevent double clicks
    const btn = document.getElementById("confirm-order");
    btn.disabled = true;
    btn.textContent = "Sending to Kitchen...";

    // Use the LIVE_SERVER_URL variable defined at the top
    fetch(LIVE_SERVER_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(finalPayload)
    })
    .then(res => {
        if (res.ok) {
            alert(`Order Sent! Table ${ASSIGNED_TABLE} is ready for you, ${customerName}.`);
            location.reload(); 
        } else {
            throw new Error("Server error");
        }
    })
    .catch(() => {
        alert("Could not reach the kitchen. Is the Render server awake?");
        btn.disabled = false;
        btn.textContent = "Confirm Order";
    });
});

// Close modal
document.getElementById("cancel-order").onclick = () => modal.classList.add("hidden");