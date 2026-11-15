(() => {
    const formControls = "input, select, textarea";
    const fieldLabel = (field) => {
        if (field.labels && field.labels.length) {
            return Array.from(field.labels)
                .map((label) => label.textContent.trim())
                .filter(Boolean)
                .join(" ");
        }
        const container = field.closest(".campo-form") || field.closest(".campo");
        const nearbyLabel = container && container.querySelector("label");
        return (nearbyLabel && nearbyLabel.textContent.trim())
            || field.getAttribute("aria-label")
            || field.name
            || "este campo";
    };

    document.addEventListener("invalid", (event) => {
        const field = event.target;
        if (!field.matches(formControls)) {
            return;
        }

        const label = fieldLabel(field);
        const validity = field.validity;
        let message = `Revisa el campo "${label}" e intenta de nuevo.`;
        if (validity.valueMissing) {
            message = `Completa el campo "${label}" para continuar.`;
        } else if (validity.typeMismatch && field.type === "email") {
            message = `Escribe un correo válido en el campo "${label}" (por ejemplo, nombre@empresa.com).`;
        } else if (validity.patternMismatch) {
            message = field.title || `Revisa el formato del campo "${label}".`;
        } else if (validity.tooLong) {
            message = `El campo "${label}" excede la cantidad máxima de caracteres permitida.`;
        } else if (validity.rangeOverflow) {
            message = `El valor de "${label}" no puede ser mayor que ${field.max}.`;
        } else if (validity.rangeUnderflow) {
            message = `El valor de "${label}" no puede ser menor que ${field.min}.`;
        } else if (validity.stepMismatch || validity.badInput) {
            message = `Revisa el valor ingresado en "${label}". Usa el formato indicado.`;
        }
        field.setCustomValidity(message);
    }, true);

    document.addEventListener("input", (event) => {
        const field = event.target;
        if (!field.matches(formControls)) {
            return;
        }
        if (field.name === "telefono") {
            field.value = field.value.replace(/\D/g, "").slice(0, 10);
        }
        field.setCustomValidity("");
    });

    document.addEventListener("change", (event) => {
        const field = event.target;
        if (field.matches(formControls)) {
            field.setCustomValidity("");
        }
    });

    const thirtyMinutes = 30 * 60 * 1000;
    let inactivityTimer;

    const logout = () => {
        window.location.assign("/logout");
    };

    const resetInactivityTimer = () => {
        window.clearTimeout(inactivityTimer);
        inactivityTimer = window.setTimeout(logout, thirtyMinutes);
    };

    ["keydown", "mousedown", "pointerdown", "scroll", "touchstart"].forEach((eventName) => {
        window.addEventListener(eventName, resetInactivityTimer, { passive: true });
    });
    resetInactivityTimer();
})();
