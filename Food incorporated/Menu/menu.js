// ================================
// 1. GLOBAL SETTINGS & DATA
// ================================
let ASSIGNED_TABLE = null;  // Will be assigned from server
let ASSIGNED_STORE = "store1";  // Default store
const LIVE_SERVER_URL = "http://127.0.0.1:5000/orders";
const TABLE_API_URL = "http://127.0.0.1:5000/tables";

const images = [
    { src: "../Images/food1.jpg", alt: "Freshly battered cod with golden chunky chips" },
    { src: "../Images/food2.jpg", alt: "Steak and kidney pie served with rich brown gravy" },
    { src: "../Images/food3.jpg", alt: "Bowls of mushy peas and chip shop curry sauce" },
    { src: "../Images/food4.jpg", alt: "A cold glass of traditional fizzy lemonade" },
    { src: "../Images/food5.jpg", alt: "Freshly caught haddock" },
    { src: "../Images/food6.jpg", alt: "Crispy battered sausages" },
    { src: "../Images/food7.jpg", alt: "Traditional pickled eggs" },
    { src: "../Images/food8.jpg", alt: "Hot apple crumble" }
];

let currentImgIndex = 0;
let currentOrder = null;
let previouslyFocusedElement = null;

// ================================
// 2. THE SINGLE ONLOAD FUNCTION
// ================================
window.onload = async () => {
    // A. Check for cached table assignment
    const cachedTable = sessionStorage.getItem("assignedTable");
    const cachedStore = sessionStorage.getItem("assignedStore");
    
    if (cachedTable && cachedStore) {
        ASSIGNED_TABLE = parseInt(cachedTable);
        ASSIGNED_STORE = cachedStore;
        displayTable();
    } else {
        // Request new table assignment from server
        await assignTableFromServer();
    }

    // B. Auto-fill name from login
    const savedName = localStorage.getItem("customerName");
    const nameInput = document.getElementById("customer-name");
    if (savedName && nameInput) {
        nameInput.value = savedName;
    }

    // C. START THE CAROUSEL
    startCarousel();

    // D. Add accessible labels to quantity buttons
    document.querySelectorAll('.menu-item').forEach(item => {
        const nameEl = item.querySelector('h3');
        const name = nameEl ? nameEl.textContent.trim() : '';
        const inc = item.querySelector('.qty-btn.increase');
        const dec = item.querySelector('.qty-btn.decrease');
        if (inc) inc.setAttribute('aria-label', `Increase quantity of ${name}`);
        if (dec) dec.setAttribute('aria-label', `Decrease quantity of ${name}`);
    });
};

// ================================
// 2B. TABLE ASSIGNMENT FROM SERVER
// ================================
async function assignTableFromServer() {
    try {
        const customerEmail = localStorage.getItem("customerEmail") || "guest@example.com";
        const response = await fetch(`${TABLE_API_URL}/assign`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                storeId: ASSIGNED_STORE,
                customerEmail: customerEmail
            })
        });

        if (response.ok) {
            const data = await response.json();
            ASSIGNED_TABLE = data.tableId;
            ASSIGNED_STORE = data.storeId;
            sessionStorage.setItem("assignedTable", ASSIGNED_TABLE);
            sessionStorage.setItem("assignedStore", ASSIGNED_STORE);
            displayTable();
        } else {
            console.warn("No tables available, using fallback");
            ASSIGNED_TABLE = Math.floor(Math.random() * 10) + 1;
            displayTable();
        }
    } catch (error) {
        console.error("Error assigning table:", error);
        ASSIGNED_TABLE = Math.floor(Math.random() * 10) + 1;
        displayTable();
    }
}

function displayTable() {
    const tableEl = document.getElementById('display-table');
    if (tableEl) tableEl.textContent = ASSIGNED_TABLE;
}

// ================================
// 3. CAROUSEL LOGIC
// ================================
function startCarousel() {
    const carouselImg = document.getElementById("carousel-img");
    const announcer = document.getElementById("carousel-announcer");

    if (!carouselImg) return;

    function updateSlide() {
        carouselImg.style.opacity = 0; // Start fade out

        setTimeout(() => {
            const currentItem = images[currentImgIndex];
            
            // Change image and Alt text
            carouselImg.src = currentItem.src;
            carouselImg.alt = currentItem.alt;
            
            // Sync screen reader announcer
            if (announcer) announcer.textContent = `Now viewing: ${currentItem.alt}`;

            carouselImg.style.opacity = 1; // Fade back in

            // Move to next image index
            currentImgIndex = (currentImgIndex + 1) % images.length;
        }, 600); 
    }

    // Run immediately, then every 5 seconds
    updateSlide();
    setInterval(updateSlide, 5000);
}

// ================================
// 4. ORDERING LOGIC (Quantity Buttons)
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
        qtySpan.style.color = qty > 0 ? "#c8102e" : "#1a1a1a";
        qtySpan.style.fontWeight = qty > 0 ? "bold" : "normal";
    }
});

// ================================
// 5. FORM SUBMIT (Show Summary)
// ================================
const form = document.getElementById("order-form");
const modal = document.getElementById("checkout-modal");
const summary = document.getElementById("order-summary");
const totalPriceEl = document.getElementById("total-price");

if (form) {
    form.addEventListener("submit", function (e) {
        e.preventDefault();

        if (!summary || !totalPriceEl || !modal) {
            alert('Page missing required elements.');
            return;
        }

        const items = [];
        let grandTotal = 0;

        document.querySelectorAll(".menu-item").forEach(item => {
            const qtyEl = item.querySelector(".quantity");
            const qty = qtyEl ? parseInt(qtyEl.textContent) || 0 : 0;
            if (qty > 0) {
                const name = item.querySelector("h3").textContent;
                const priceText = item.querySelector(".price").textContent.replace('£', '');
                const price = parseFloat(priceText) || 0;
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
        // Open accessible modal
        if (modal) openModal();
    });
}

function openModal() {
    if (!modal) return;
    previouslyFocusedElement = document.activeElement;
    modal.classList.remove('hidden');
    modal.setAttribute('aria-hidden', 'false');
    const nameInputEl = document.getElementById('customer-name');
    if (nameInputEl) nameInputEl.focus();
}

function closeModal() {
    if (!modal) return;
    modal.classList.add('hidden');
    modal.setAttribute('aria-hidden', 'true');
    if (previouslyFocusedElement && typeof previouslyFocusedElement.focus === 'function') {
        previouslyFocusedElement.focus();
    }
}

// Global keyboard handler: Escape closes modal; Tab is trapped within modal when open
document.addEventListener('keydown', (e) => {
    if (!modal) return;
    const isOpen = !modal.classList.contains('hidden');
    if (e.key === 'Escape' && isOpen) {
        e.preventDefault();
        closeModal();
        return;
    }

    if (e.key === 'Tab' && isOpen) {
        const focusableSelectors = 'a[href], area[href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), button:not([disabled]), [tabindex]:not([tabindex="-1"])';
        const focusable = Array.from(modal.querySelectorAll(focusableSelectors)).filter(el => el.offsetParent !== null);
        if (focusable.length === 0) return;
        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        if (e.shiftKey && document.activeElement === first) {
            e.preventDefault();
            last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
            e.preventDefault();
            first.focus();
        }
    }
});

// ================================
// 6. CONFIRM ORDER
// ================================
const confirmBtn = document.getElementById("confirm-order");
if (confirmBtn) {
    confirmBtn.addEventListener("click", () => {
        const customerInput = document.getElementById("customer-name");
        const customerName = customerInput ? customerInput.value.trim() : '';

        if (!customerName) {
            alert("Please enter your name!");
            return;
        }

        if (!currentOrder) {
            alert('No order to send.');
            return;
        }

        const finalPayload = { ...currentOrder, customerName: customerName };

        confirmBtn.disabled = true;
        const originalText = confirmBtn.textContent;
        confirmBtn.textContent = "Sending to Kitchen...";

        // POST the order to the backend server (no payment data involved)
        fetch(LIVE_SERVER_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(finalPayload)
        })
        .then(res => {
            if (!res.ok) throw new Error('Server returned error');
            // Optionally read response JSON if available
            return res.json().catch(() => null);
        })
        .then((serverData) => {
            // Persist order (non-sensitive) for checkout page
            try {
                // If server returned an order id, prefer that
                if (serverData && serverData.orderNumber) finalPayload.orderNumber = serverData.orderNumber;
                sessionStorage.setItem('pendingOrder', JSON.stringify(finalPayload));
            } catch (e) {}

            try { localStorage.setItem('customerName', customerName); } catch (e) {}

            confirmBtn.textContent = 'Sent — Redirecting...';
            // Short delay so user sees confirmation, then go to checkout
            setTimeout(() => window.location.href = 'checkout.html', 600);
        })
        .catch((err) => {
            alert('Could not send order to the kitchen. Please try again.');
            confirmBtn.disabled = false;
            confirmBtn.textContent = originalText || 'Send to Kitchen';
        });
    });
}

// Close modal (guarded)
const cancelBtn = document.getElementById("cancel-order");
if (cancelBtn) cancelBtn.onclick = () => closeModal();