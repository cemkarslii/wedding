(() => {
  "use strict";

  /* ── DOM ──────────────────────────────────────── */
  const $ = (s) => document.querySelector(s);
  const intro = $("#intro");
  const introVideo = $("#introVideo");
  const skipBtn = $("#skipBtn");
  const main = $("#main");
  const headerVideo = $("#headerVideo");
  const bgMusic = $("#bgMusic");
  const soundToggle = $("#soundToggle");

  let musicPlaying = false;
  let hasSkipped = false;

  /* ── Viewport Height Fix ───────────────────────── */
  const setVH = () => {
    document.documentElement.style.setProperty(
      "--vh",
      `${window.innerHeight * 0.01}px`,
    );
  };
  setVH();
  window.addEventListener("resize", setVH);
  window.addEventListener("orientationchange", () =>
    setTimeout(setVH, 150),
  );

  /* ── Music ─────────────────────────────────────── */
  const startMusic = () => {
    if (musicPlaying) return;
    bgMusic
      .play()
      .then(() => {
        musicPlaying = true;
        soundToggle.classList.add("is-playing");
        removeInteractionListeners();
      })
      .catch(() => {});
  };

  const toggleMusic = () => {
    if (!musicPlaying) {
      startMusic();
      return;
    }
    if (bgMusic.paused) {
      bgMusic.play();
      soundToggle.classList.add("is-playing");
    } else {
      bgMusic.pause();
      soundToggle.classList.remove("is-playing");
    }
  };

  /* Aggressively try to autoplay music */
  startMusic();
  const retryInterval = setInterval(() => {
    if (musicPlaying) {
      clearInterval(retryInterval);
      return;
    }
    startMusic();
  }, 500);
  setTimeout(() => clearInterval(retryInterval), 10000);

  /* Start music on ANY user interaction */
  const onInteraction = () => {
    startMusic();
  };
  const interactionEvents = [
    "touchstart",
    "touchend",
    "click",
    "mousedown",
    "mousemove",
    "scroll",
    "keydown",
  ];
  const removeInteractionListeners = () => {
    interactionEvents.forEach((evt) =>
      document.removeEventListener(evt, onInteraction, { capture: true }),
    );
  };
  interactionEvents.forEach((evt) =>
    document.addEventListener(evt, onInteraction, {
      capture: true,
      passive: true,
    }),
  );

  /* ── Skip Intro ────────────────────────────────── */
  const skipIntro = () => {
    if (hasSkipped) return;
    hasSkipped = true;
    startMusic();
    intro.classList.add("is-leaving");
    requestAnimationFrame(() => {
      main.classList.add("is-visible");
      headerVideo.play().catch(() => {});
      document.body.classList.add("scrollable");
    });
    setTimeout(() => {
      introVideo.pause();
      introVideo.removeAttribute("src");
      introVideo.load();
      intro.remove();
    }, 1800);
  };

  /* ── Events ────────────────────────────────────── */
  skipBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    skipIntro();
  });
  introVideo.addEventListener("ended", skipIntro);
  soundToggle.addEventListener("click", toggleMusic);

  /* ── Countdown ─────────────────────────────────── */
  const weddingDate = new Date("2026-09-26T15:00:00+03:00");
  const updateCountdown = () => {
    const now = Date.now();
    const diff = Math.max(0, weddingDate - now);
    const d = Math.floor(diff / 86400000);
    const h = Math.floor((diff % 86400000) / 3600000);
    const m = Math.floor((diff % 3600000) / 60000);
    const s = Math.floor((diff % 60000) / 1000);
    const pad = (n) => String(n).padStart(2, "0");
    $("#cdDays").textContent = d;
    $("#cdHours").textContent = pad(h);
    $("#cdMins").textContent = pad(m);
    $("#cdSecs").textContent = pad(s);
  };
  updateCountdown();
  setInterval(updateCountdown, 1000);

  /* ── Scroll Reveal ─────────────────────────────── */
  const revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-revealed");
          revealObserver.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.15, rootMargin: "0px 0px -40px 0px" },
  );

  document
    .querySelectorAll(".reveal")
    .forEach((el) => revealObserver.observe(el));

  /* ── Sound Toggle Light/Dark Adaption ──────────── */
  const heroSection = $(".hero");
  const toggleObserver = new IntersectionObserver(
    ([entry]) => {
      soundToggle.classList.toggle("on-light", !entry.isIntersecting);
    },
    { threshold: 0.3 },
  );
  if (heroSection) toggleObserver.observe(heroSection);

  /* ── Message Form ──────────────────────────────── */
  const form = $("#messageForm");
  const formSuccess = $("#formSuccess");
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    form.style.display = "none";
    formSuccess.classList.add("is-visible");
  });

  /* ── Photo Upload ──────────────────────────────── */
  const uploadArea = $("#photoUploadArea");
  const photoInput = $("#photoInput");
  const preview = $("#photoPreview");
  const shareBtn = $("#photoShareBtn");
  let uploadedFiles = [];

  uploadArea.addEventListener("click", () => photoInput.click());

  uploadArea.addEventListener("dragover", (e) => {
    e.preventDefault();
    uploadArea.classList.add("is-dragover");
  });
  uploadArea.addEventListener("dragleave", () =>
    uploadArea.classList.remove("is-dragover"),
  );
  uploadArea.addEventListener("drop", (e) => {
    e.preventDefault();
    uploadArea.classList.remove("is-dragover");
    handleFiles(e.dataTransfer.files);
  });

  photoInput.addEventListener("change", () =>
    handleFiles(photoInput.files),
  );

  const handleFiles = (files) => {
    Array.from(files).forEach((file) => {
      if (!file.type.startsWith("image/")) return;
      if (file.size > 10 * 1024 * 1024) return;
      uploadedFiles.push(file);
      const reader = new FileReader();
      reader.onload = (e) => {
        const div = document.createElement("div");
        div.className = "photos__preview-item";
        div.innerHTML = `
        <img src="${e.target.result}" alt="Fotoğraf" />
        <button class="photos__preview-item__remove" aria-label="Kaldır">×</button>
      `;
        div
          .querySelector(".photos__preview-item__remove")
          .addEventListener("click", () => {
            const idx = Array.from(preview.children).indexOf(div);
            uploadedFiles.splice(idx, 1);
            div.remove();
            if (uploadedFiles.length === 0)
              shareBtn.classList.remove("is-visible");
          });
        preview.appendChild(div);
        shareBtn.classList.add("is-visible");
      };
      reader.readAsDataURL(file);
    });
  };

  shareBtn.addEventListener("click", () => {
    shareBtn.textContent = "✓ Gönderildi!";
    shareBtn.style.background = "#4a9d5a";
    setTimeout(() => {
      shareBtn.textContent = "";
      shareBtn.innerHTML =
        '<svg viewBox="0 0 24 24"><path d="M22 2L11 13"/><path d="M22 2L15 22l-4-9-9-4z"/></svg> Fotoğrafları Gönder';
      shareBtn.style.background = "";
    }, 2500);
  });

  /* ── Visibility Change ─────────────────────────── */
  let wasPaused = false;
  document.addEventListener("visibilitychange", () => {
    if (!musicPlaying) return;
    if (document.hidden) {
      wasPaused = bgMusic.paused;
    } else if (!wasPaused) {
      bgMusic.play().catch(() => {});
    }
  });
})();
