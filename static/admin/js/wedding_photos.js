(() => {
  "use strict";

  const storageKey = "weddingPhotoAdminView";

  const setView = (view) => {
    const isGrid = view === "grid";
    document.body.classList.toggle("wedding-photo-grid", isGrid);
    document.querySelectorAll("[data-photo-view]").forEach((button) => {
      const isActive = button.dataset.photoView === view;
      button.classList.toggle("is-active", isActive);
      button.setAttribute("aria-pressed", String(isActive));
    });
    try {
      localStorage.setItem(storageKey, view);
    } catch {}
  };

  document.addEventListener("DOMContentLoaded", () => {
    const mediaDialog = document.createElement("dialog");
    mediaDialog.className = "wedding-media-dialog";
    mediaDialog.setAttribute("aria-label", "Medya önizlemesi");
    mediaDialog.innerHTML = `
      <button type="button" class="wedding-media-dialog__close" aria-label="Kapat">×</button>
      <div class="wedding-media-dialog__content"></div>
    `;
    document.body.appendChild(mediaDialog);

    const dialogContent = mediaDialog.querySelector(
      ".wedding-media-dialog__content",
    );
    const closeDialog = () => mediaDialog.close();

    const openMediaDialog = (trigger) => {
      dialogContent.replaceChildren();
      const media = document.createElement(
        trigger.dataset.mediaType === "video" ? "video" : "img",
      );
      media.src = trigger.dataset.mediaUrl;
      if (media instanceof HTMLVideoElement) {
        media.controls = true;
        media.autoplay = true;
        media.playsInline = true;
      } else {
        media.alt = trigger.getAttribute("aria-label") || "Görsel önizlemesi";
      }
      dialogContent.appendChild(media);
      mediaDialog.showModal();
    };

    document.addEventListener("click", (event) => {
      const trigger = event.target.closest(".media-dialog-trigger");
      if (trigger) {
        event.preventDefault();
        event.stopPropagation();
        openMediaDialog(trigger);
        return;
      }

      const primaryPreview = event.target.closest(".media-preview-primary");
      if (!primaryPreview) return;
      event.preventDefault();
      event.stopPropagation();
      if (document.body.classList.contains("wedding-photo-grid")) {
        primaryPreview
          .closest("tr")
          ?.querySelector("input.action-select")
          ?.click();
      } else {
        openMediaDialog(primaryPreview);
      }
    });

    mediaDialog
      .querySelector(".wedding-media-dialog__close")
      .addEventListener("click", closeDialog);
    mediaDialog.addEventListener("click", (event) => {
      if (event.target === mediaDialog) closeDialog();
    });
    mediaDialog.addEventListener("close", () => {
      dialogContent.querySelector("video")?.pause();
      dialogContent.replaceChildren();
    });

    const buttons = document.querySelectorAll("[data-photo-view]");
    if (!buttons.length) return;

    let initialView = "list";
    try {
      initialView = localStorage.getItem(storageKey) || initialView;
    } catch {}
    setView(initialView === "grid" ? "grid" : "list");

    buttons.forEach((button) => {
      button.addEventListener("click", () => setView(button.dataset.photoView));
    });

    const selectAllButton = document.querySelector("[data-select-all-photos]");
    const downloadButton = document.querySelector("[data-download-selected]");
    const changeListForm = document.querySelector("#changelist-form");
    let allSelected = false;

    const updateSelectedCard = (checkbox) => {
      checkbox
        .closest("tr")
        ?.classList.toggle("is-media-selected", checkbox.checked);
    };
    changeListForm
      .querySelectorAll("input.action-select")
      .forEach((checkbox) => {
        updateSelectedCard(checkbox);
        checkbox.addEventListener("change", () => updateSelectedCard(checkbox));
      });

    selectAllButton?.addEventListener("click", () => {
      allSelected = !allSelected;
      const selectionBoxes = changeListForm.querySelectorAll(
        "input.action-select",
      );
      selectionBoxes.forEach((checkbox) => {
        checkbox.checked = allSelected;
        checkbox.dispatchEvent(new Event("change", { bubbles: true }));
      });

      const pageToggle = changeListForm.querySelector("#action-toggle");
      if (pageToggle) pageToggle.checked = allSelected;
      const selectAcross = changeListForm.querySelector(
        "input[name='select_across']",
      );
      if (selectAcross) selectAcross.value = allSelected ? "1" : "0";
      selectAllButton.textContent = allSelected
        ? "Seçimi kaldır"
        : "Tümünü seç";
    });

    downloadButton?.addEventListener("click", () => {
      const selectedPhotos = changeListForm.querySelectorAll(
        "input.action-select:checked",
      );
      if (!selectedPhotos.length) {
        window.alert("Lütfen indirmek için en az bir dosya seçin.");
        return;
      }

      const actionSelect = changeListForm.querySelector(
        "select[name='action']",
      );
      actionSelect.value = "download_selected_photos";
      changeListForm.requestSubmit();
    });
  });
})();
