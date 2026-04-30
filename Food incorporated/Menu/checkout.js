// checkout.js — dummy payment page. Does NOT store or send card data.

function luhnCheck(num) {
    const digits = num.replace(/\s+/g, '').split('').reverse().map(d => parseInt(d, 10));
    if (digits.some(isNaN)) return false;
    let sum = 0;
    for (let i = 0; i < digits.length; i++) {
        let d = digits[i];
        if (i % 2 === 1) {
            d *= 2;
            if (d > 9) d -= 9;
        }
        sum += d;
    }
    return sum % 10 === 0;
}

window.addEventListener('DOMContentLoaded', () => {
    const orderBlock = document.getElementById('order-summary-block');
    const pending = sessionStorage.getItem('pendingOrder');
    let order = null;

    if (pending) {
        try {
            order = JSON.parse(pending);
        } catch (e) { order = null; }
    }

    if (!order) {
        orderBlock.innerHTML = '<p>No pending order found. <a href="menu.html">Return to menu</a>.</p>';
    } else {
        orderBlock.innerHTML = `<p>Order #${order.orderNumber} — Table ${order.tableNumber}</p>` +
            order.items.map(i => `<div style="display:flex;justify-content:space-between;"><span>${i.quantity}x ${i.name}</span><span>£${(i.subtotal).toFixed(2)}</span></div>`).join('') +
            `<p style="margin-top:8px;font-weight:600;">Total: £${order.total}</p>`;
    }

    const form = document.getElementById('checkout-form');
    const msg = document.getElementById('payment-message');
    const cancel = document.getElementById('cancel-pay');

    cancel.addEventListener('click', () => {
        // Return to menu without storing payment info
        window.location.href = 'menu.html';
    });

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        msg.textContent = '';

        const name = document.getElementById('card-name').value.trim();
        const number = document.getElementById('card-number').value.trim();
        const expiry = document.getElementById('card-expiry').value.trim();
        const cvc = document.getElementById('card-cvc').value.trim();

        // Basic validation
        if (!name || !number || !expiry || !cvc) {
            msg.textContent = 'Please fill all card fields.';
            return;
        }

        const normalizedNumber = number.replace(/[^0-9]/g, '');
        if (!luhnCheck(normalizedNumber)) {
            msg.textContent = 'Card number appears invalid.';
            return;
        }

        // Expiry MM/YY
        const m = expiry.match(/^(0[1-9]|1[0-2])\/(\d{2})$/);
        if (!m) {
            msg.textContent = 'Expiry must be in MM/YY format.';
            return;
        }
        const month = parseInt(m[1], 10);
        const year = parseInt('20' + m[2], 10);
        const now = new Date();
        const exp = new Date(year, month - 1, 1);
        if (exp < new Date(now.getFullYear(), now.getMonth(), 1)) {
            msg.textContent = 'Card appears expired.';
            return;
        }

        if (!/^\d{3,4}$/.test(cvc)) {
            msg.textContent = 'CVC must be 3 or 4 digits.';
            return;
        }

        // At this point, we treat the payment as successful for the dummy flow.
        // IMPORTANT: DO NOT store or send the raw card data anywhere.
        try {
            // Clear any references to card data in memory
            // (these are local variables; reassign to null to be explicit)
            // eslint-disable-next-line no-unused-vars
            let _cardName = null, _cardNumber = null, _cardExpiry = null, _cardCvc = null;
        } catch (e) {}

        // Remove the pending order (we've "paid" for it)
        try { sessionStorage.removeItem('pendingOrder'); } catch (e) {}

        msg.textContent = 'Payment successful! Thank you — returning to the menu...';

        // After a short pause, redirect back to menu
        setTimeout(() => {
            window.location.href = 'menu.html';
        }, 2200);
    });
});