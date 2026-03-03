function toggleMenu() {
    const sidebar = document.getElementById("sidebar");
    const overlay = document.getElementById("overlay");
    if(sidebar.style.width == "280px") {
        sidebar.style.width = "0";
        overlay.style.display = "none";
    } else {
        sidebar.style.width = "280px";
        overlay.style.display = "block";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("menu-toggle").addEventListener("click", toggleMenu);
    document.getElementById("overlay").addEventListener("click", toggleMenu);

    const closeBtn = document.querySelector(".closeBtn");
    if(closeBtn) closeBtn.addEventListener("click", toggleMenu);
});