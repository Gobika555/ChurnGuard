
function showMessage(element, message, type="") {
    if (!element) return;
    element.textContent = message;
    element.className = "form-message " + type;
}
document.addEventListener("DOMContentLoaded", () => {
    const signupForm = document.getElementById("signupForm");
    if (signupForm) signupForm.addEventListener("submit", async e => {
        e.preventDefault();
        const message = document.getElementById("signupMessage");
        showMessage(message, "Creating your account...", "loading");
        try {
            const response = await fetch("/signup", {
                method:"POST", headers:{"Content-Type":"application/json"}, credentials:"include",
                body:JSON.stringify({
                    username:document.getElementById("username").value.trim(),
                    email:document.getElementById("signupEmail").value.trim(),
                    password:document.getElementById("signupPassword").value
                })
            });
            const data = await response.json();
            if (response.ok && data.success) {
                showMessage(message, "Account created successfully. Redirecting...", "success");
                signupForm.reset();
                setTimeout(()=>window.location.href="/login.html",700);
            } else showMessage(message, data.message || "Unable to create account.", "error");
        } catch(err) { console.error(err); showMessage(message,"Unable to connect to ChurnGuard.","error"); }
    });

    const loginForm = document.getElementById("loginForm");
    if (loginForm) loginForm.addEventListener("submit", async e => {
        e.preventDefault();
        const message = document.getElementById("loginMessage");
        showMessage(message,"Signing you in...","loading");
        try {
            const response = await fetch("/login", {
                method:"POST", headers:{"Content-Type":"application/json"}, credentials:"include",
                body:JSON.stringify({
                    email:document.getElementById("email").value.trim(),
                    password:document.getElementById("password").value
                })
            });
            const data = await response.json();
            if (response.ok && data.success) {
                localStorage.setItem("user", JSON.stringify(data.user));
                showMessage(message,"Login successful. Redirecting...","success");
                setTimeout(()=>window.location.href="/dashboard.html",400);
            } else showMessage(message,data.message || "Invalid email or password.","error");
        } catch(err) { console.error(err); showMessage(message,"Unable to connect to ChurnGuard.","error"); }
    });
});
