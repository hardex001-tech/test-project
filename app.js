const views = document.querySelectorAll(".view");
const navItems = document.querySelectorAll(".nav-item");
const crumb = document.querySelector("#pageCrumb");
const sidebar = document.querySelector("#sidebar");
const toast = document.querySelector("#toast");

function showView(name) {
  views.forEach((view) => view.classList.toggle("active", view.dataset.page === name));
  navItems.forEach((item) => item.classList.toggle("active", item.dataset.view === name));
  crumb.textContent = name.charAt(0).toUpperCase() + name.slice(1);
  sidebar.classList.remove("open");
  window.scrollTo({ top: 0, behavior: "smooth" });
}

document.querySelectorAll("[data-view], [data-view-target]").forEach((element) => {
  element.addEventListener("click", () => showView(element.dataset.view || element.dataset.viewTarget));
});

document.querySelector("#menuToggle").addEventListener("click", () => sidebar.classList.toggle("open"));

function showToast(message) {
  toast.firstChild.textContent = message + " ";
  toast.classList.add("show");
  window.setTimeout(() => toast.classList.remove("show"), 2800);
}

document.querySelector("#createInvoice").addEventListener("click", () => showToast("Invoice draft created"));
document.querySelector("#createInvoiceAlt").addEventListener("click", () => showToast("Invoice draft created"));
document.querySelector("#saveSettings").addEventListener("click", () => showToast("Settings saved successfully"));

const invoiceRows = [...document.querySelectorAll("#invoiceTable tbody tr")];
const invoiceSearch = document.querySelector("#invoiceSearch");
let invoiceFilter = "all";

function filterInvoices() {
  const query = invoiceSearch.value.toLowerCase();
  invoiceRows.forEach((row) => {
    const matchesStatus = invoiceFilter === "all" || row.dataset.status === invoiceFilter;
    row.hidden = !matchesStatus || !row.textContent.toLowerCase().includes(query);
  });
}

document.querySelectorAll(".filter").forEach((filter) => {
  filter.addEventListener("click", () => {
    document.querySelectorAll(".filter").forEach((item) => item.classList.remove("active"));
    filter.classList.add("active");
    invoiceFilter = filter.dataset.filter;
    filterInvoices();
  });
});
invoiceSearch.addEventListener("input", filterInvoices);

const customerSearch = document.querySelector("#customerSearch");
customerSearch.addEventListener("input", () => {
  const query = customerSearch.value.toLowerCase();
  document.querySelectorAll(".customer-card").forEach((card) => {
    card.hidden = !card.textContent.toLowerCase().includes(query);
  });
});
