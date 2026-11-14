(() => {
    function normalizeSearchText(value) {
        return value
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .toLocaleLowerCase();
    }

    document.querySelectorAll(".buscador").forEach((input) => {
        const container = input.closest(".tabla-contenedor");
        const table = container?.querySelector("table");
        const body = table?.querySelector("tbody");

        if (!table || !body) {
            return;
        }

        const headers = Array.from(table.querySelectorAll("thead th"));
        const rows = Array.from(body.querySelectorAll("tr")).filter(
            (row) => !row.querySelector(".tabla-vacia")
        );
        const noResultsRow = document.createElement("tr");
        const noResultsCell = document.createElement("td");

        noResultsRow.className = "tabla-vacia";
        noResultsCell.colSpan = headers.length || 1;
        noResultsCell.textContent = "No se encontraron registros que coincidan con la búsqueda.";
        noResultsRow.append(noResultsCell);
        body.append(noResultsRow);
        noResultsRow.hidden = true;

        input.addEventListener("input", () => {
            const term = normalizeSearchText(input.value.trim());
            let visibleRows = 0;

            rows.forEach((row) => {
                const searchableText = Array.from(row.cells)
                    .filter((cell, index) => headers[index]?.textContent.trim().toLowerCase() !== "acciones")
                    .map((cell) => cell.textContent)
                    .join(" ");
                const matches = normalizeSearchText(searchableText).includes(term);

                row.hidden = !matches;
                if (matches) {
                    visibleRows += 1;
                }
            });

            noResultsRow.hidden = !term || visibleRows > 0 || rows.length === 0;
        });
    });
})();
