const filterToggle = document.getElementById("filterToggle");
const filterForm = document.getElementById("filterForm");

if (filterToggle && filterForm) {
    filterToggle.addEventListener("click", function () {
        filterForm.classList.toggle("filter-closed");

        filterToggle.classList.toggle(
            "filter-open",
            !filterForm.classList.contains("filter-closed")
        );
    });
}