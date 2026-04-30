document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("loginForm");
    const emailInput = document.getElementById("username");
    const socialBtn = document.querySelector(".social-btn");

    // Helper: Validate email format
    const isValidEmail = (email) => {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    };

    // 1. SOCIAL LOGIN HANDLER
    if (socialBtn) {
        socialBtn.addEventListener("click", (e) => {
            e.preventDefault();
            alert("Google sign-in integration coming soon!");
        });
    }

    // 2. FORM SUBMIT & REDIRECT
    form.addEventListener("submit", (e) => {
        e.preventDefault();

        const submitBtn = form.querySelector('input[type="submit"]');
        const email = emailInput.value.trim();

        // Validate email is filled
        if (!email) {
            alert("Please enter your email address.");
            return;
        }

        // Validate email format
        if (!isValidEmail(email)) {
            alert("Please enter a valid email address.");
            return;
        }

        // Disable submit button to prevent duplicate submissions
        submitBtn.disabled = true;
        submitBtn.value = "Signing in...";

        try {
            // Save the email to LocalStorage so the menu can greet them
            const nameForMenu = email.split('@')[0];
            localStorage.setItem("customerName", nameForMenu);
            localStorage.setItem("customerEmail", email);
        } catch (error) {
            console.error("Failed to save to localStorage:", error);
            alert("Storage unavailable. Please check your privacy settings.");
            return;
        }

        // SUCCESS: Redirect to menu
        const menuPath = "../Menu/menu.html";
        try {
            window.location.href = menuPath;
        } catch (error) {
            console.error("Navigation failed:", error);
            alert("Unable to navigate. Please ensure the Menu folder exists.");
        }
    });
});