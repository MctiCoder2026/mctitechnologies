document.addEventListener("DOMContentLoaded", function () {
    const sidebar = document.querySelector(".sidebar");

    if (!sidebar) {
        return;
    }

    const toggle = document.createElement("button");
    toggle.type = "button";
    toggle.className = "mobile-sidebar-toggle";
    toggle.setAttribute("aria-label", "Open staff menu");
    toggle.setAttribute("aria-expanded", "false");
    toggle.innerHTML =
        "<span></span><span></span><span></span>";

    const overlay = document.createElement("button");
    overlay.type = "button";
    overlay.className = "mobile-sidebar-overlay";
    overlay.setAttribute("aria-label", "Close staff menu");

    document.body.appendChild(toggle);
    document.body.appendChild(overlay);

    function closeMenu() {
        sidebar.classList.remove("mobile-open");
        toggle.classList.remove("active");
        overlay.classList.remove("active");
        document.body.classList.remove("staff-menu-open");
        toggle.setAttribute("aria-expanded", "false");
        toggle.setAttribute("aria-label", "Open staff menu");
    }

    function openMenu() {
        sidebar.classList.add("mobile-open");
        toggle.classList.add("active");
        overlay.classList.add("active");
        document.body.classList.add("staff-menu-open");
        toggle.setAttribute("aria-expanded", "true");
        toggle.setAttribute("aria-label", "Close staff menu");
    }

    toggle.addEventListener("click", function () {
        if (sidebar.classList.contains("mobile-open")) {
            closeMenu();
        } else {
            openMenu();
        }
    });

    overlay.addEventListener("click", closeMenu);

    sidebar.querySelectorAll("a").forEach(function (link) {
        link.addEventListener("click", closeMenu);
    });

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            closeMenu();
        }
    });

    window.addEventListener("resize", function () {
        if (window.innerWidth > 900) {
            closeMenu();
        }
    });
});
