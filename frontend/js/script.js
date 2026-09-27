document.addEventListener("DOMContentLoaded", () => {
    const menu = document.getElementById("mobileMenu");
    const sidebar = document.getElementById("sidebar");
    if (menu && sidebar) menu.addEventListener("click", () => sidebar.classList.toggle("open"));
    document.querySelectorAll(".sidebar-menu a").forEach(link => {
        if (link.getAttribute("href") === window.location.pathname) link.classList.add("active");
    });
    const logout = document.getElementById("logoutButton");
    if (logout) logout.addEventListener("click", async () => {
        logout.disabled = true;
        try { await fetch("/logout", {method:"POST", credentials:"include"}); }
        catch (e) { console.error("Logout error", e); }
        localStorage.removeItem("user");
        window.location.href = "/login.html";
    });
});
