document.addEventListener("DOMContentLoaded", () => {
  const ttlMinutes = Number(window.SISPLUS_SESSION_TTL_MINUTES || 30);
  const idleLimitMs = ttlMinutes * 60 * 1000;
  const heartbeatIntervalMs = 4 * 60 * 1000;

  console.log("TTL bruto:", window.SISPLUS_SESSION_TTL_MINUTES);
  console.log("TTL convertido:", ttlMinutes);
  console.log("Idle em ms:", idleLimitMs);

  let lastActivityAt = Date.now();
  let lastHeartbeatAt = 0;

  const markActivity = () => {
    lastActivityAt = Date.now();
    maybeHeartbeat();
  };

  const maybeHeartbeat = () => {
    const now = Date.now();
    if (now - lastHeartbeatAt < heartbeatIntervalMs) return;
    lastHeartbeatAt = now;
    fetch("/auth/heartbeat", {
      method: "POST",
      credentials: "same-origin",
      headers: { "X-Requested-With": "XMLHttpRequest" },
    }).catch(() => {});
  };

  const enforceIdleTimeout = () => {
    if (Date.now() - lastActivityAt >= idleLimitMs) {
      window.location.href = "/auth/logout?reason=expired";
    }
  };

  ["click", "mousemove", "keydown", "scroll", "touchstart"].forEach((eventName) => {
    window.addEventListener(eventName, markActivity, { passive: true });
  });

  setInterval(enforceIdleTimeout, 30 * 1000);
  setInterval(maybeHeartbeat, heartbeatIntervalMs);
});
