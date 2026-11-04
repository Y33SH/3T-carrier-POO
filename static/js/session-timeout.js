(() => {
    const twelveHours = 12 * 60 * 60 * 1000;
    let inactivityTimer;

    const logout = () => {
        window.location.assign("/logout");
    };

    const resetInactivityTimer = () => {
        window.clearTimeout(inactivityTimer);
        inactivityTimer = window.setTimeout(logout, twelveHours);
    };

    ["keydown", "mousedown", "pointerdown", "scroll", "touchstart"].forEach((eventName) => {
        window.addEventListener(eventName, resetInactivityTimer, { passive: true });
    });
    resetInactivityTimer();

    fetch("/session-deadline", { credentials: "same-origin" })
        .then((response) => {
            if (!response.ok) {
                throw new Error(`No se pudo consultar el cierre de sesión (${response.status}).`);
            }
            return response.json();
        })
        .then(({ expires_at: expiresAt }) => {
            const millisecondsUntilMidnight = expiresAt * 1000 - Date.now();
            if (millisecondsUntilMidnight <= 0) {
                logout();
                return;
            }
            window.setTimeout(logout, millisecondsUntilMidnight);
        })
        .catch((error) => {
            console.error("No se pudo programar el cierre de sesión de medianoche.", error);
        });
})();
