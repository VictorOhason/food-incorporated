document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("loginForm");
    const emailInput = document.getElementById("username");
    const passwordInput = document.getElementById("password");

    // 1. HANDLE REGULAR FORM LOGIN
    form.addEventListener("submit", (e) => {
        e.preventDefault();
        
        const email = emailInput.value.trim();
        const password = passwordInput.value.trim();

        if (email && password) {
            // In a real app, you'd verify this with your server.py
            console.log("Login Success. Redirecting...");
            window.location.href = "menu.html"; // CONNECTS TO MENU
        } else {
            alert("Please fill in all fields.");
        }
    });
});

// 2. HANDLE REAL GOOGLE LOGIN RESPONSE
function handleCredentialResponse(response) {
    // response.credential is a "JWT Token" containing the user's Google info
    console.log("Encoded JWT ID token: " + response.credential);
    
    // Redirect to the menu after successful Google Sign-in
    alert("Google Login Successful!");
    // Inside your login success logic:
    localStorage.setItem("customerName", email.split('@')[0]); // Save part of the email as the name
    window.location.href = "menu.html";
    window.location.href = "menu.html"; 
}