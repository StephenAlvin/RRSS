// Sortable tables (via tablesort) and a quick filter box for large tables.
document$.subscribe(function () {
  var tables = document.querySelectorAll("article table:not([class])");
  tables.forEach(function (table) {
    if (!table.tablesortInstance) {
      table.tablesortInstance = new Tablesort(table);
    }
    var rows = table.tBodies[0] ? table.tBodies[0].rows.length : 0;
    if (rows > 30 && !table.previousElementSibling?.classList?.contains("table-filter")) {
      var input = document.createElement("input");
      input.type = "search";
      input.className = "table-filter";
      input.placeholder = "Filter this table…";
      input.setAttribute("aria-label", "Filter table");
      input.addEventListener("input", function () {
        var q = input.value.trim().toLowerCase();
        Array.prototype.forEach.call(table.tBodies[0].rows, function (row) {
          row.style.display = !q || row.textContent.toLowerCase().indexOf(q) !== -1 ? "" : "none";
        });
      });
      table.parentNode.insertBefore(input, table);
    }
  });
});
