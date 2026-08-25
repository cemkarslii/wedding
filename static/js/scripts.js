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
  const formError = $("#formError");
  const messageType = $("#id_message_type");
  const attendanceGroup = $("#attendanceGroup");
  const attendanceInput = $("#id_attendance");
  const formSubmit = form.querySelector("button[type='submit']");

  const toggleAttendance = () => {
    const isAttendance = messageType.value === "attendance_status";
    attendanceGroup.hidden = !isAttendance;
    attendanceInput.disabled = !isAttendance;
    attendanceInput.required = isAttendance;
  };

  toggleAttendance();
  messageType.addEventListener("change", toggleAttendance);

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    formError.hidden = true;
    formSubmit.disabled = true;
    form.setAttribute("aria-busy", "true");

    try {
      const response = await fetch(form.action, {
        method: "POST",
        body: new FormData(form),
        credentials: "same-origin",
        headers: {
          Accept: "application/json",
          "X-Requested-With": "XMLHttpRequest",
        },
      });
      let data;
      try {
        data = await response.json();
      } catch {
        throw new Error("Sunucudan geçerli bir yanıt alınamadı.");
      }

      if (!response.ok || !data.success) {
        const messages = Object.values(data.errors || {})
          .flat()
          .map((error) => error.message);
        throw new Error(messages[0] || "Mesaj gönderilemedi.");
      }

      form.style.display = "none";
      formSuccess.classList.add("is-visible");
    } catch (error) {
      formError.textContent =
        error.message || "Bir hata oluştu. Lütfen tekrar deneyin.";
      formError.hidden = false;
    } finally {
      formSubmit.disabled = false;
      form.removeAttribute("aria-busy");
    }
  });

  /* ── Photo Upload ──────────────────────────────── */
  const photoForm = $("#photoUploadForm");
  const uploadArea = $("#photoUploadArea");
  const photoInput = $("#photoInput");
  const preview = $("#photoPreview");
  const shareBtn = $("#photoShareBtn");
  const photoUploadError = $("#photoUploadError");
  const photoUploadSuccess = $("#photoUploadSuccess");
  let uploadedFiles = [];
  const maxPhotoSize = 10 * 1024 * 1024;
  const maxVideoSize = 100 * 1024 * 1024;
  const maxMediaCount = 10;
  const allowedImageTypes = ["image/jpeg", "image/png"];
  const allowedVideoTypes = ["video/mp4", "video/quicktime", "video/webm"];

  const showPhotoError = (message) => {
    photoUploadError.textContent = message;
    photoUploadError.hidden = false;
  };

  uploadArea.addEventListener("click", (e) => {
    if (e.target !== photoInput) photoInput.click();
  });

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

  photoInput.addEventListener("change", () => {
    handleFiles(photoInput.files);
    photoInput.value = "";
  });

  const handleFiles = (files) => {
    photoUploadError.hidden = true;
    photoUploadSuccess.hidden = true;
    Array.from(files).forEach((file) => {
      const isImage = allowedImageTypes.includes(file.type);
      const isVideo = allowedVideoTypes.includes(file.type);
      if (uploadedFiles.length >= maxMediaCount) {
        showPhotoError(`Tek seferde en fazla ${maxMediaCount} dosya seçebilirsiniz.`);
        return;
      }
      if (!isImage && !isVideo) {
        showPhotoError("Yalnızca JPG, PNG, MP4, MOV veya WebM seçebilirsiniz.");
        return;
      }
      if (isImage && file.size > maxPhotoSize) {
        showPhotoError(`${file.name} dosyası 10 MB sınırını aşıyor.`);
        return;
      }
      if (isVideo && file.size > maxVideoSize) {
        showPhotoError(`${file.name} dosyası 100 MB sınırını aşıyor.`);
        return;
      }
      uploadedFiles.push(file);
      const previewUrl = URL.createObjectURL(file);
      const div = document.createElement("div");
      div.className = "photos__preview-item";
      div.dataset.previewUrl = previewUrl;
      div.innerHTML = `
        ${isVideo ? '<video controls muted playsinline preload="metadata"></video>' : '<img alt="Fotoğraf önizlemesi" />'}
        <button class="photos__preview-item__remove" aria-label="Kaldır">×</button>
      `;
      div.querySelector(isVideo ? "video" : "img").src = previewUrl;
      div
        .querySelector(".photos__preview-item__remove")
        .addEventListener("click", () => {
          const idx = uploadedFiles.indexOf(file);
          if (idx !== -1) uploadedFiles.splice(idx, 1);
          URL.revokeObjectURL(previewUrl);
          div.remove();
          if (uploadedFiles.length === 0)
            shareBtn.classList.remove("is-visible");
        });
      preview.appendChild(div);
      shareBtn.classList.add("is-visible");
    });
  };

  photoForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (uploadedFiles.length === 0) {
      showPhotoError("Lütfen en az bir fotoğraf veya video seçin.");
      return;
    }

    photoUploadError.hidden = true;
    photoUploadSuccess.hidden = true;
    shareBtn.disabled = true;
    photoForm.setAttribute("aria-busy", "true");

    const formData = new FormData();
    formData.append(
      "csrfmiddlewaretoken",
      photoForm.querySelector("[name='csrfmiddlewaretoken']").value,
    );
    uploadedFiles.forEach((file) => formData.append("media_files", file));

    try {
      const response = await fetch(photoForm.action, {
        method: "POST",
        body: formData,
        credentials: "same-origin",
        headers: {
          Accept: "application/json",
          "X-Requested-With": "XMLHttpRequest",
        },
      });
      let data;
      try {
        data = await response.json();
      } catch {
        throw new Error("Sunucudan geçerli bir yanıt alınamadı.");
      }

      if (!response.ok || !data.success) {
        const messages = Object.values(data.errors || {})
          .flat()
          .map((error) => error.message);
        throw new Error(messages[0] || "Dosyalar yüklenemedi.");
      }

      uploadedFiles = [];
      preview.querySelectorAll("[data-preview-url]").forEach((item) => {
        URL.revokeObjectURL(item.dataset.previewUrl);
      });
      preview.replaceChildren();
      shareBtn.classList.remove("is-visible");
      photoUploadSuccess.textContent = `${data.uploaded_count} dosya başarıyla gönderildi. Teşekkür ederiz!`;
      photoUploadSuccess.hidden = false;
    } catch (error) {
      showPhotoError(
        error.message || "Bir hata oluştu. Lütfen tekrar deneyin.",
      );
    } finally {
      shareBtn.disabled = false;
      photoForm.removeAttribute("aria-busy");
    }
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
