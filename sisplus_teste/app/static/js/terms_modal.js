document.addEventListener("DOMContentLoaded", function () {
  const openBtn = document.getElementById("openTermsBtn");
  const modal = document.getElementById("termsModalOverlay");
  const checkbox = document.getElementById("termsAgreeCheckbox");
  const closeBtn = document.getElementById("closeTermsBtn");

  if (!openBtn || !modal || !checkbox || !closeBtn) return;

  openBtn.addEventListener("click", function () {
    modal.classList.add("open");
    modal.setAttribute("aria-hidden", "false");
  });

  checkbox.addEventListener("change", function () {
    if (checkbox.checked) {
      closeBtn.disabled = false;
      closeBtn.classList.add("enabled");
    } else {
      closeBtn.disabled = true;
      closeBtn.classList.remove("enabled");
    }
  });

  closeBtn.addEventListener("click", function () {
    if (!checkbox.checked) return;

    modal.classList.remove("open");
    modal.setAttribute("aria-hidden", "true");
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && modal.classList.contains("open")) {
      e.preventDefault();
    }
  });

  modal.addEventListener("click", function (e) {
    if (e.target === modal) {
      e.preventDefault();
    }
  });
});