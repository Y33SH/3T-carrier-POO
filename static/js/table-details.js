(() => {
    let dialog;
    let details;

    function getDialog() {
        if (dialog) {
            return dialog;
        }
 
        dialog = document.createElement("dialog");
        dialog.className = "modal-detalle";

        const header = document.createElement("div");
        header.className = "modal-detalle-header";

        const title = document.createElement("h2");
        title.textContent = "Detalle";

        const closeButton = document.createElement("button");
        closeButton.type = "button";
        closeButton.className = "btn-cerrar-modal";
        closeButton.setAttribute("aria-label", "Cerrar");
        closeButton.textContent = "×";
        closeButton.addEventListener("click", () => dialog.close());

        header.append(title, closeButton);
        details = document.createElement("dl");
        details.className = "modal-detalle-lista";
        dialog.append(header, details);
        document.body.append(dialog);
        return dialog;
    }

    function addDetail(label, value) {
        const text = (value || "").trim();
        if (!text || text === "—") {
            return;
        }

        const term = document.createElement("dt");
        term.textContent = label;
        const description = document.createElement("dd");
        description.textContent = text;
        details.append(term, description);
    }

    function showTableDetails(row) {
        const headers = Array.from(row.closest("table").querySelectorAll("thead th"));
        const cells = Array.from(row.children);
        headers.forEach((header, index) => {
            if (header.textContent.trim().toLowerCase() !== "acciones" && cells[index]) {
                addDetail(header.textContent, cells[index].innerText);
            }
        });
    }

    function showTrackingDetails(card) {
        addDetail("Unidad", card.querySelector(".unidad-tracking-header h3")?.innerText);
        addDetail("Pedido", card.querySelector(".unidad-tracking-header p")?.innerText.replace(/^Pedido:\s*/, ""));
        addDetail("Estado", card.querySelector(".unidad-tracking-header .estado-activo")?.innerText);

        card.querySelectorAll(".tracking-datos > div").forEach((item) => {
            addDetail(item.querySelector("span")?.innerText, item.querySelector("strong")?.innerText);
        });

        card.querySelectorAll(".ruta-punto").forEach((point) => {
            addDetail(point.querySelector("small")?.innerText, point.querySelector("p")?.innerText);
        });

        const footer = card.querySelector(".tracking-footer");
        if (footer) {
            addDetail("Última actualización", footer.innerText.replace("Ver detalle", "").replace("Última actualización:", ""));
        }
    }

    document.addEventListener("click", (event) => {
        const button = event.target.closest("button.btn-tabla");
        if (!button || !/^ver(\s|$)/i.test(button.textContent.trim())) {
            return;
        }

        const modal = getDialog();
        details.replaceChildren();

        const row = button.closest("tr");
        const trackingCard = button.closest(".unidad-tracking");
        if (row) {
            showTableDetails(row);
        } else if (trackingCard) {
            showTrackingDetails(trackingCard);
        }

        if (!details.children.length) {
            addDetail("Información", "No hay información adicional disponible para este registro.");
        }

        if (!modal.open) {
            modal.showModal();
        }
    });
})();
