document.addEventListener("DOMContentLoaded",()=>{document.querySelectorAll("[data-dismiss]").forEach(el=>el.addEventListener("click",()=>el.remove()));});
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".exercise-video-fullscreen").forEach(button => {
    button.addEventListener("click", async () => {
      const player = button.closest(".exercise-video");
      try {
        if (document.fullscreenElement) await document.exitFullscreen();
        else await player.requestFullscreen();
      } catch (error) {
        button.title = "Full screen is not available in this browser";
      }
    });
  });
});
document.addEventListener("DOMContentLoaded", () => {
  const root = document.documentElement;
  const toggles = document.querySelectorAll("[data-theme-toggle]");
  const currentTheme = () => root.dataset.theme || "light";
  const paint = () => {
    const dark = currentTheme() === "dark";
    toggles.forEach(button => {
      const icon = button.querySelector("[data-theme-icon]");
      const label = button.querySelector("[data-theme-label]");
      if (icon) icon.textContent = dark ? "☀" : "☾";
      if (label) label.textContent = dark ? "Light mode" : "Dark mode";
      button.setAttribute("aria-label", dark ? "Switch to light theme" : "Switch to dark theme");
      button.setAttribute("title", dark ? "Switch to light theme" : "Switch to dark theme");
    });
  };
  toggles.forEach(button => button.addEventListener("click", () => {
    const next = currentTheme() === "dark" ? "light" : "dark";
    root.dataset.theme = next;
    try { localStorage.setItem("calfit-theme", next); } catch (e) {}
    paint();
  }));
  paint();
});

document.addEventListener("DOMContentLoaded", () => {
  const fallback = "/static/images/exercise-fallback.svg";
  document.querySelectorAll("[data-exercise-image]").forEach(el => {
    const source = el.dataset.exerciseImage;
    if (!source) { el.style.backgroundImage = `url("${fallback}")`; return; }
    const probe = new Image();
    probe.onload = () => { el.style.backgroundImage = `url("${source}")`; };
    probe.onerror = () => { el.style.backgroundImage = `url("${fallback}")`; };
    probe.src = source;
  });
  document.querySelectorAll("img").forEach(img => {
    img.addEventListener("error", () => { img.onerror = null; img.src = fallback; });
  });
});
