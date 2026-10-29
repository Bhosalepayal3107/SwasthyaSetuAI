/**
 * SwasthyaSetu AI - Client Script
 * Handles file checklist previews, prompt chips, multi-step questionnaire interactions,
 * conditional questions, instant emergency medical modals, and recommendation drawers.
 */

document.addEventListener("DOMContentLoaded", () => {
  // ---------------------------------------------------------------------------
  // 1. Existing Document Centre upload preview (Preserved)
  // ---------------------------------------------------------------------------
  const docInput = document.getElementById("documents");
  const docFileList = document.getElementById("file-list");
  if (docInput && docFileList) {
    docInput.addEventListener("change", () => {
      const files = Array.from(docInput.files || []);
      docFileList.textContent = files.length
        ? files.map(f => `${f.name} (${Math.round(f.size / 1024)} KB)`).join(" · ")
        : "No files selected";
    });
  }

  // ---------------------------------------------------------------------------
  // 2. Existing Healthcare Assistant prompt chips (Preserved)
  // ---------------------------------------------------------------------------
  document.querySelectorAll("[data-prompt]").forEach(button => {
    button.addEventListener("click", () => {
      const question = document.getElementById("question");
      if (question) {
        question.value = button.dataset.prompt || "";
        question.focus();
      }
    });
  });

  // ---------------------------------------------------------------------------
  // 3. Multi-Step Questionnaire: Clean Selection State Synchronization
  // Uses native label/input behavior to prevent double-toggling
  // ---------------------------------------------------------------------------
  function syncSelectionClasses() {
    // Choice cards (radios & checkboxes)
    document.querySelectorAll(".choice-card").forEach(card => {
      const input = card.querySelector("input");
      if (input) {
        card.classList.toggle("selected", Boolean(input.checked));
      }
    });

    // Pill choices (radios)
    document.querySelectorAll(".pill-choice").forEach(pill => {
      const input = pill.querySelector("input");
      if (input) {
        pill.classList.toggle("selected", Boolean(input.checked));
      }
    });

    // Checkbox chips
    document.querySelectorAll(".checkbox-chip").forEach(chip => {
      const input = chip.querySelector("input");
      if (input) {
        chip.classList.toggle("selected", Boolean(input.checked));
      }
    });

    // Document matrix pills
    document.querySelectorAll(".doc-pill").forEach(docPill => {
      const input = docPill.querySelector("input");
      if (input) {
        docPill.classList.toggle("selected", Boolean(input.checked));
      }
    });
  }

  const questionnaireForm = document.getElementById("questionnaire-form");
  if (questionnaireForm) {
    questionnaireForm.addEventListener("change", () => {
      syncSelectionClasses();
    });

    // Initial sync on page render
    syncSelectionClasses();
  }

  // ---------------------------------------------------------------------------
  // 4. Conditional Form Fields: Beneficiary -> Patient Age (Step 1)
  // ---------------------------------------------------------------------------
  const beneficiaryRadios = document.querySelectorAll("input[name='beneficiary']");
  const patientAgeField = document.getElementById("patient-age-field");

  beneficiaryRadios.forEach(radio => {
    radio.addEventListener("change", () => {
      if (patientAgeField) {
        if (radio.value === "myself") {
          patientAgeField.style.display = "none";
        } else {
          patientAgeField.style.display = "block";
          const patientAgeInput = document.getElementById("patient_age");
          if (patientAgeInput && !patientAgeInput.value) {
            patientAgeInput.focus();
          }
        }
      }
    });
  });

  // ---------------------------------------------------------------------------
  // 5. Conditional Form Fields: Ration Card -> Category (Step 2)
  // ---------------------------------------------------------------------------
  const rationCardRadios = document.querySelectorAll("input[name='ration_card']");
  const rcTypeWrap = document.getElementById("rc-type-wrap");

  rationCardRadios.forEach(radio => {
    radio.addEventListener("change", () => {
      if (rcTypeWrap) {
        if (radio.value === "no") {
          rcTypeWrap.style.display = "none";
        } else {
          rcTypeWrap.style.display = "block";
        }
      }
    });
  });

  // ---------------------------------------------------------------------------
  // 6. CRITICAL EMERGENCY REQUIREMENT (Step 3)
  // Immediately show emergency modal if "Emergency treatment required now" is selected!
  // ---------------------------------------------------------------------------
  const emergencyModal = document.getElementById("emergency-modal");
  const dismissEmergencyBtn = document.getElementById("dismiss-emergency-modal");
  const treatmentStatusRadios = document.querySelectorAll("input[name='treatment_status']");

  treatmentStatusRadios.forEach(radio => {
    radio.addEventListener("change", () => {
      if (radio.value === "Emergency treatment required now" && emergencyModal) {
        emergencyModal.style.display = "grid";
        emergencyModal.setAttribute("aria-hidden", "false");
      }
    });
  });

  if (dismissEmergencyBtn && emergencyModal) {
    dismissEmergencyBtn.addEventListener("click", () => {
      emergencyModal.style.display = "none";
      emergencyModal.setAttribute("aria-hidden", "true");
    });

    // Close on backdrop click
    emergencyModal.addEventListener("click", (e) => {
      if (e.target === emergencyModal) {
        emergencyModal.style.display = "none";
        emergencyModal.setAttribute("aria-hidden", "true");
      }
    });
  }

  // ---------------------------------------------------------------------------
  // 7. Interactive Recommendation Modals ("Why this scheme?" & "Documents")
  // ---------------------------------------------------------------------------
  document.querySelectorAll(".open-modal-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const modalId = btn.dataset.modal;
      if (modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
          modal.style.display = "grid";
          modal.setAttribute("aria-hidden", "false");
        }
      }
    });
  });

  document.querySelectorAll(".close-modal-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const modalId = btn.dataset.close;
      if (modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
          modal.style.display = "none";
          modal.setAttribute("aria-hidden", "true");
        }
      }
    });
  });

  // Close any modal on backdrop click or ESC key
  document.querySelectorAll(".custom-modal-backdrop").forEach(backdrop => {
    backdrop.addEventListener("click", (e) => {
      if (e.target === backdrop) {
        backdrop.style.display = "none";
        backdrop.setAttribute("aria-hidden", "true");
      }
    });
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      if (emergencyModal && emergencyModal.style.display === "grid") {
        emergencyModal.style.display = "none";
      }
      document.querySelectorAll(".custom-modal-backdrop").forEach(modal => {
        if (modal.style.display === "grid") {
          modal.style.display = "none";
        }
      });
    }
  });

  // ---------------------------------------------------------------------------
  // 8. Client-Side Form Validation Guidance
  // Ensures seamless progression without blocking valid submissions
  // ---------------------------------------------------------------------------
  if (questionnaireForm) {
    questionnaireForm.addEventListener("submit", (e) => {
      const action = e.submitter ? e.submitter.value : "";
      if (action === "save") return; // Allow save without full validation

      const stepInput = questionnaireForm.querySelector("input[name='current_step']");
      const currentStep = stepInput ? parseInt(stepInput.value, 10) : 1;

      if (currentStep === 1) {
        const nameInput = document.getElementById("full_name");
        const ageInput = document.getElementById("age");
        const districtInput = document.getElementById("district");

        if (nameInput && (!nameInput.value.trim() || nameInput.value.trim().length < 2)) {
          e.preventDefault();
          nameInput.focus();
          return;
        }

        if (ageInput) {
          const ageVal = parseInt(ageInput.value, 10);
          if (isNaN(ageVal) || ageVal < 0 || ageVal > 120) {
            e.preventDefault();
            ageInput.focus();
            return;
          }
        }

        if (districtInput && !districtInput.value.trim()) {
          e.preventDefault();
          districtInput.focus();
          return;
        }
      } else if (currentStep === 3) {
        // Step 3 safety: Ensure at least one treatment and status are checked
        const checkedTreatments = questionnaireForm.querySelectorAll("input[name='treatments']:checked");
        if (checkedTreatments.length === 0) {
          const firstT = questionnaireForm.querySelector("input[name='treatments']");
          if (firstT) {
            firstT.checked = true;
          }
        }

        const checkedStatus = questionnaireForm.querySelector("input[name='treatment_status']:checked");
        if (!checkedStatus) {
          const defaultS = questionnaireForm.querySelector("input[name='treatment_status'][value='Doctor has recommended hospitalization']") ||
                           questionnaireForm.querySelector("input[name='treatment_status']");
          if (defaultS) {
            defaultS.checked = true;
          }
        }
        syncSelectionClasses();
      }
    });
  }
});