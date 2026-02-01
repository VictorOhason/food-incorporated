document.addEventListener("DOMContentLoaded", () => {
    const toggleBtn = document.querySelector(".toggle-password");
    const passwordInput = document.getElementById("password");
    const form = document.getElementById("loginForm");
    const emailInput = document.getElementById("username");

    // 1. PASSWORD TOGGLE
    if (toggleBtn) {
        toggleBtn.addEventListener("click", () => {
            const isHidden = passwordInput.type === "password";
            passwordInput.type = isHidden ? "text" : "password";
            toggleBtn.textContent = isHidden ? "🙈" : "👁️";
        });
    }

    // 2. FORM SUBMIT & REDIRECT
    form.addEventListener("submit", (e) => {
        e.preventDefault();

        const email = emailInput.value.trim();
        const password = passwordInput.value.trim();

        if (!email || !password) {
            alert("Please fill in all fields.");
            return;
        }

        // Save the username to LocalStorage so the menu can greet them
        const nameForMenu = email.split('@')[0];
        localStorage.setItem("customerName", nameForMenu);

        // SUCCESS: Redirect to menu
        window.location.href = "menu.html"; 
    });
});