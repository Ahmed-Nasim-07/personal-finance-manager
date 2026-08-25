/* =========================================================
   PURITY FINANCE — SHARED JAVASCRIPT
   ========================================================= */

const html = document.documentElement;

const themeToggle =
    document.getElementById("themeToggle");

const sidebar =
    document.getElementById("sidebar");

const sidebarOpen =
    document.getElementById("sidebarOpen");

const sidebarClose =
    document.getElementById("sidebarClose");

const sidebarOverlay =
    document.getElementById("sidebarOverlay");


/* =========================================================
   THEME
   ========================================================= */

function updateThemeIcon() {

    if (!themeToggle) {
        return;
    }

    const icon =
        themeToggle.querySelector("i");

    if (html.dataset.theme === "dark") {

        icon.className =
            "fa-solid fa-sun";

        themeToggle.setAttribute(
            "aria-label",
            "Switch to light mode"
        );

    } else {

        icon.className =
            "fa-solid fa-moon";

        themeToggle.setAttribute(
            "aria-label",
            "Switch to dark mode"
        );
    }
}


function setTheme(theme) {

    html.dataset.theme = theme;

    localStorage.setItem(
        "finance-theme",
        theme
    );

    updateThemeIcon();
}


/* Load saved theme */

const savedTheme =
    localStorage.getItem("finance-theme");

if (
    savedTheme === "light" ||
    savedTheme === "dark"
) {

    setTheme(savedTheme);

} else {

    setTheme("dark");

}


/* Toggle theme */

if (themeToggle) {

    themeToggle.addEventListener(
        "click",
        () => {

            const currentTheme =
                html.dataset.theme;

            const newTheme =
                currentTheme === "dark"
                    ? "light"
                    : "dark";

            setTheme(newTheme);

        }
    );

}


/* =========================================================
   MOBILE SIDEBAR
   ========================================================= */

function openSidebar() {

    if (!sidebar) {
        return;
    }

    sidebar.classList.add("open");

    sidebarOverlay.classList.add("active");

    document.body.style.overflow =
        "hidden";
}


function closeSidebar() {

    if (!sidebar) {
        return;
    }

    sidebar.classList.remove("open");

    sidebarOverlay.classList.remove("active");

    document.body.style.overflow = "";
}


if (sidebarOpen) {

    sidebarOpen.addEventListener(
        "click",
        openSidebar
    );

}


if (sidebarClose) {

    sidebarClose.addEventListener(
        "click",
        closeSidebar
    );

}


if (sidebarOverlay) {

    sidebarOverlay.addEventListener(
        "click",
        closeSidebar
    );

}


/* Close sidebar after navigation */

const navLinks =
    document.querySelectorAll(".nav-item");

navLinks.forEach((link) => {

    link.addEventListener(
        "click",
        () => {

            if (window.innerWidth <= 800) {
                closeSidebar();
            }

        }
    );

});