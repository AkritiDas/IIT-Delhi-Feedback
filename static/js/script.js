/**
 * IIT Delhi Virtual Labs – Smart Feedback Portal
 * Frontend Interactivity and Dynamic Form Management
 */

document.addEventListener("DOMContentLoaded", function () {
    // ========================================================================
    // 1. Theme Management (Dark / Light Mode)
    // ========================================================================
    const themeToggleBtn = document.getElementById("themeToggleBtn");
    const currentTheme = localStorage.getItem("iitd_theme") || "light";

    function setTheme(theme) {
        document.documentElement.setAttribute("data-theme", theme);
        localStorage.setItem("iitd_theme", theme);
        if (themeToggleBtn) {
            const icon = themeToggleBtn.querySelector("i");
            if (icon) {
                icon.className = theme === "dark" ? "bi bi-sun-fill" : "bi bi-moon-stars-fill";
            }
        }
    }

    setTheme(currentTheme);

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener("click", function () {
            const activeTheme = document.documentElement.getAttribute("data-theme") || "light";
            setTheme(activeTheme === "dark" ? "light" : "dark");
        });
    }

    // ========================================================================
    // 2. Star Rating System
    // ========================================================================
    const ratingLabels = {
        1: "1/5 - Poor",
        2: "2/5 - Fair",
        3: "3/5 - Good",
        4: "4/5 - Very Good",
        5: "5/5 - Outstanding!"
    };

    const ratingCards = document.querySelectorAll(".rating-item-card");

    ratingCards.forEach(function (card) {
        const starContainer = card.querySelector(".star-container");
        const stars = card.querySelectorAll(".star-btn");
        const hiddenInput = card.querySelector(".rating-input");
        const valueBadge = card.querySelector(".rating-value-badge");

        function updateStarDisplay(val) {
            stars.forEach(function (star) {
                const sVal = parseInt(star.getAttribute("data-val"));
                if (sVal <= val) {
                    star.classList.add("active");
                    star.innerHTML = '<i class="bi bi-star-fill"></i>';
                } else {
                    star.classList.remove("active");
                    star.innerHTML = '<i class="bi bi-star"></i>';
                }
            });
            if (val > 0 && ratingLabels[val]) {
                valueBadge.textContent = ratingLabels[val];
            } else {
                valueBadge.textContent = "Not Rated";
            }
        }

        stars.forEach(function (star) {
            const val = parseInt(star.getAttribute("data-val"));

            // Hover effects
            star.addEventListener("mouseenter", function () {
                stars.forEach(function (s) {
                    const sv = parseInt(s.getAttribute("data-val"));
                    if (sv <= val) {
                        s.classList.add("hovered");
                        s.innerHTML = '<i class="bi bi-star-fill"></i>';
                    } else {
                        s.classList.remove("hovered");
                        s.innerHTML = '<i class="bi bi-star"></i>';
                    }
                });
                valueBadge.textContent = ratingLabels[val];
            });

            // Click selection
            star.addEventListener("click", function (e) {
                e.preventDefault();
                hiddenInput.value = val;
                updateStarDisplay(val);
                updateFormProgress();
            });
        });

        starContainer.addEventListener("mouseleave", function () {
            stars.forEach(s => s.classList.remove("hovered"));
            const currentVal = parseInt(hiddenInput.value) || 0;
            updateStarDisplay(currentVal);
        });

        // Keyboard navigation for accessibility
        stars.forEach(function (star) {
            star.addEventListener("keydown", function (e) {
                if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    star.click();
                }
            });
        });
    });

    // ========================================================================
    // 3. Anonymous Mode Toggle
    // ========================================================================
    const anonymousToggle = document.getElementById("anonymousToggle");
    const personalInfoSection = document.getElementById("personalInfoSection");
    const anonymousBanner = document.getElementById("anonymousBanner");

    if (anonymousToggle && personalInfoSection) {
        anonymousToggle.addEventListener("change", function () {
            if (this.checked) {
                personalInfoSection.style.display = "none";
                if (anonymousBanner) anonymousBanner.style.display = "block";
            } else {
                personalInfoSection.style.display = "block";
                if (anonymousBanner) anonymousBanner.style.display = "none";
            }
            updateFormProgress();
        });
    }

    // ========================================================================
    // 4. Issues Selection & Smart Conditional Questions
    // ========================================================================
    const issueCheckboxes = document.querySelectorAll(".issue-checkbox");
    const otherCheckbox = document.getElementById("issue_other");
    const otherIssueDescWrapper = document.getElementById("otherIssueDescWrapper");
    const conditionalTechBox = document.getElementById("conditionalTechBox");

    const technicalIssues = [
        "Experiment is not loading",
        "Simulation is not working",
        "Website is loading slowly",
        "Incorrect experiment output",
        "Audio or video not working",
        "Login or access problem",
        "Display or layout issues",
        "Mobile responsiveness problem",
        "Experiment results are inaccurate"
    ];

    function handleIssueChanges() {
        let hasTechnicalIssue = false;
        let isOtherSelected = false;

        issueCheckboxes.forEach(function (cb) {
            if (cb.checked) {
                const val = cb.value;
                if (technicalIssues.includes(val)) {
                    hasTechnicalIssue = true;
                }
                if (cb.id === "issue_other" || val === "Other") {
                    isOtherSelected = true;
                }
            }
        });

        // Show/hide "Other" description field
        if (otherIssueDescWrapper) {
            otherIssueDescWrapper.style.display = isOtherSelected ? "block" : "none";
        }

        // Show/hide Smart Conditional Technical Question Box
        if (conditionalTechBox) {
            if (hasTechnicalIssue) {
                conditionalTechBox.style.display = "block";
            } else {
                conditionalTechBox.style.display = "none";
            }
        }

        updateFormProgress();
    }

    issueCheckboxes.forEach(function (cb) {
        cb.addEventListener("change", handleIssueChanges);
    });

    // ========================================================================
    // 5. Live Character Counter for Experience Textarea
    // ========================================================================
    const experienceTextarea = document.getElementById("experience_description");
    const charCounter = document.getElementById("charCounter");
    const minCharNotice = document.getElementById("minCharNotice");

    if (experienceTextarea && charCounter) {
        experienceTextarea.addEventListener("input", function () {
            const len = this.value.length;
            charCounter.textContent = `${len} / 2000 characters`;

            if (len < 10) {
                charCounter.style.color = "#E65100";
                if (minCharNotice) minCharNotice.textContent = `(Min 10 chars required - ${10 - len} more needed)`;
            } else if (len > 1950) {
                charCounter.style.color = "#DC2626";
                if (minCharNotice) minCharNotice.textContent = "(Approaching limit)";
            } else {
                charCounter.style.color = "var(--text-muted)";
                if (minCharNotice) minCharNotice.textContent = "(Requirement met ✓)";
            }

            updateFormProgress();
        });
    }

    // ========================================================================
    // 6. Screenshot Drag & Drop with Real-time Previews
    // ========================================================================
    const dropzone = document.getElementById("screenshotDropzone");
    const fileInput = document.getElementById("screenshotInput");
    const previewGrid = document.getElementById("screenshotPreviewGrid");
    const uploadError = document.getElementById("uploadError");

    let uploadedFilesList = []; // Array of File objects

    const ALLOWED_EXTENSIONS = ["png", "jpg", "jpeg", "webp"];
    const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB

    function formatFileSize(bytes) {
        if (bytes < 1024) return bytes + " B";
        else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + " KB";
        else return (bytes / 1048576).toFixed(1) + " MB";
    }

    function renderPreviews() {
        if (!previewGrid) return;
        previewGrid.innerHTML = "";

        uploadedFilesList.forEach(function (file, index) {
            const card = document.createElement("div");
            card.className = "preview-card";

            const img = document.createElement("img");
            img.className = "preview-img";
            img.src = URL.createObjectURL(file);
            img.alt = file.name;

            const removeBtn = document.createElement("button");
            removeBtn.type = "button";
            removeBtn.className = "preview-remove-btn";
            removeBtn.innerHTML = '<i class="bi bi-x-lg"></i>';
            removeBtn.title = "Remove screenshot";
            removeBtn.addEventListener("click", function (e) {
                e.stopPropagation();
                uploadedFilesList.splice(index, 1);
                syncFileInput();
                renderPreviews();
            });

            const meta = document.createElement("div");
            meta.className = "preview-meta text-muted";
            meta.textContent = `${file.name} (${formatFileSize(file.size)})`;

            card.appendChild(img);
            card.appendChild(removeBtn);
            card.appendChild(meta);
            previewGrid.appendChild(card);
        });
    }

    function syncFileInput() {
        if (!fileInput) return;
        const dataTransfer = new DataTransfer();
        uploadedFilesList.forEach(file => dataTransfer.items.add(file));
        fileInput.files = dataTransfer.files;
    }

    function processSelectedFiles(files) {
        if (uploadError) uploadError.style.display = "none";

        Array.from(files).forEach(function (file) {
            const ext = file.name.split(".").pop().toLowerCase();
            if (!ALLOWED_EXTENSIONS.includes(ext)) {
                showUploadError(`'${file.name}' has invalid format. Only PNG, JPG, JPEG, and WEBP are allowed.`);
                return;
            }
            if (file.size > MAX_FILE_SIZE) {
                showUploadError(`'${file.name}' exceeds the maximum allowed size of 10 MB.`);
                return;
            }
            // Check if already added
            const exists = uploadedFilesList.some(f => f.name === file.name && f.size === file.size);
            if (!exists) {
                uploadedFilesList.push(file);
            }
        });

        syncFileInput();
        renderPreviews();
    }

    function showUploadError(msg) {
        if (uploadError) {
            uploadError.textContent = msg;
            uploadError.style.display = "block";
        }
    }

    if (dropzone && fileInput) {
        dropzone.addEventListener("click", function () {
            fileInput.click();
        });

        fileInput.addEventListener("change", function () {
            processSelectedFiles(this.files);
        });

        dropzone.addEventListener("dragover", function (e) {
            e.preventDefault();
            dropzone.classList.add("dragover");
        });

        dropzone.addEventListener("dragleave", function () {
            dropzone.classList.remove("dragover");
        });

        dropzone.addEventListener("drop", function (e) {
            e.preventDefault();
            dropzone.classList.remove("dragover");
            if (e.dataTransfer && e.dataTransfer.files.length > 0) {
                processSelectedFiles(e.dataTransfer.files);
            }
        });
    }

    // ========================================================================
    // 7. Dynamic Form Progress Bar
    // ========================================================================
    const progressFill = document.getElementById("formProgressFill");
    const progressText = document.getElementById("formProgressText");

    function updateFormProgress() {
        if (!progressFill || !progressText) return;

        let totalPoints = 0;
        const maxPoints = 8; // Key checkpoints

        const isAnon = anonymousToggle ? anonymousToggle.checked : false;

        // 1. Personal info (or automatic if anonymous)
        if (isAnon) {
            totalPoints += 1;
        } else {
            const name = document.getElementById("full_name")?.value.trim();
            const email = document.getElementById("email")?.value.trim();
            if (name && email && email.includes("@")) {
                totalPoints += 1;
            }
        }

        // 2. User type selected
        const userType = document.querySelector('input[name="user_type"]:checked');
        if (userType) totalPoints += 1;

        // 3. Subject selected
        const subject = document.getElementById("subject")?.value;
        if (subject) totalPoints += 1;

        // 4. Experiment name
        const expName = document.getElementById("experiment_name")?.value.trim();
        if (expName) totalPoints += 1;

        // 5. Star Ratings (all 4)
        const ov = parseInt(document.getElementById("overall_rating")?.value) || 0;
        const exp = parseInt(document.getElementById("experiment_rating")?.value) || 0;
        const nav = parseInt(document.getElementById("navigation_rating")?.value) || 0;
        const tech = parseInt(document.getElementById("technical_rating")?.value) || 0;
        if (ov > 0 && exp > 0 && nav > 0 && tech > 0) {
            totalPoints += 2;
        } else if (ov > 0 || exp > 0 || nav > 0 || tech > 0) {
            totalPoints += 1;
        }

        // 6. Experience description
        const descLen = experienceTextarea ? experienceTextarea.value.trim().length : 0;
        if (descLen >= 10) totalPoints += 1;

        // 7. Recommendation chosen
        const recom = document.querySelector('input[name="recommendation"]:checked');
        if (recom) totalPoints += 1;

        const percent = Math.min(100, Math.round((totalPoints / maxPoints) * 100));
        progressFill.style.width = `${percent}%`;
        progressText.textContent = `Form Completion: ${percent}%`;
    }

    // Attach change listeners to form inputs
    const formInputs = document.querySelectorAll(
        "#feedbackForm input, #feedbackForm select, #feedbackForm textarea"
    );
    formInputs.forEach(input => {
        input.addEventListener("input", updateFormProgress);
        input.addEventListener("change", updateFormProgress);
    });

    // Initial calculation
    updateFormProgress();

    // ========================================================================
    // 8. Feedback Preview Modal
    // ========================================================================
    const previewBtn = document.getElementById("btnPreviewFeedback");
    const previewModalEl = document.getElementById("feedbackPreviewModal");

    if (previewBtn && previewModalEl) {
        previewBtn.addEventListener("click", function () {
            const isAnon = anonymousToggle ? anonymousToggle.checked : false;

            document.getElementById("prevUser").textContent = isAnon
                ? "Anonymous User"
                : (document.getElementById("full_name")?.value || "Not provided");
            document.getElementById("prevEmail").textContent = isAnon
                ? "Hidden (Anonymous Mode)"
                : (document.getElementById("email")?.value || "Not provided");
            document.getElementById("prevSubject").textContent =
                document.getElementById("subject")?.value || "Not selected";
            document.getElementById("prevExperiment").textContent =
                document.getElementById("experiment_name")?.value || "Not provided";

            // Ratings summary
            const ov = document.getElementById("overall_rating")?.value || "0";
            const exp = document.getElementById("experiment_rating")?.value || "0";
            const nav = document.getElementById("navigation_rating")?.value || "0";
            const tech = document.getElementById("technical_rating")?.value || "0";

            document.getElementById("prevRatings").innerHTML = `
                <div class="row g-2">
                    <div class="col-6"><strong>Overall:</strong> ${ov}/5 ★</div>
                    <div class="col-6"><strong>Experiment:</strong> ${exp}/5 ★</div>
                    <div class="col-6"><strong>Navigation:</strong> ${nav}/5 ★</div>
                    <div class="col-6"><strong>Technical:</strong> ${tech}/5 ★</div>
                </div>
            `;

            // Issues summary
            const checkedIssues = Array.from(
                document.querySelectorAll(".issue-checkbox:checked")
            ).map(cb => cb.value);
            const issuesContainer = document.getElementById("prevIssues");
            if (checkedIssues.length > 0) {
                issuesContainer.innerHTML = checkedIssues
                    .map(i => `<span class="badge bg-light text-dark border me-1 mb-1">${i}</span>`)
                    .join("");
            } else {
                issuesContainer.textContent = "None reported";
            }

            // Description
            document.getElementById("prevDescription").textContent =
                experienceTextarea?.value || "Not provided";

            // Screenshots count
            document.getElementById("prevScreenshotsCount").textContent =
                `${uploadedFilesList.length} image(s) attached`;

            const modal = new bootstrap.Modal(previewModalEl);
            modal.show();
        });
    }

    // ========================================================================
    // 9. Reset Form with Confirmation
    // ========================================================================
    const resetFormBtn = document.getElementById("btnResetForm");
    const confirmResetBtn = document.getElementById("btnConfirmReset");
    const resetModalEl = document.getElementById("confirmResetModal");

    if (resetFormBtn && resetModalEl) {
        const resetModal = new bootstrap.Modal(resetModalEl);

        resetFormBtn.addEventListener("click", function () {
            resetModal.show();
        });

        if (confirmResetBtn) {
            confirmResetBtn.addEventListener("click", function () {
                const form = document.getElementById("feedbackForm");
                if (form) form.reset();

                // Clear ratings
                ratingCards.forEach(card => {
                    card.querySelector(".rating-input").value = "0";
                    card.querySelectorAll(".star-btn").forEach(s => {
                        s.classList.remove("active", "hovered");
                        s.innerHTML = '<i class="bi bi-star"></i>';
                    });
                    card.querySelector(".rating-value-badge").textContent = "Not Rated";
                });

                // Clear screenshots
                uploadedFilesList = [];
                syncFileInput();
                renderPreviews();

                // Reset conditional sections
                if (otherIssueDescWrapper) otherIssueDescWrapper.style.display = "none";
                if (conditionalTechBox) conditionalTechBox.style.display = "none";
                if (personalInfoSection) personalInfoSection.style.display = "block";
                if (anonymousBanner) anonymousBanner.style.display = "none";

                updateFormProgress();
                resetModal.hide();
                window.scrollTo({ top: 0, behavior: "smooth" });
            });
        }
    }

    // ========================================================================
    // 10. Form Submission & Client-side Validation
    // ========================================================================
    const feedbackForm = document.getElementById("feedbackForm");
    const submitBtn = document.getElementById("btnSubmitFeedback");
    const submitSpinner = document.getElementById("submitSpinner");
    const submitBtnText = document.getElementById("submitBtnText");
    const formAlertBox = document.getElementById("formAlertBox");

    function showFormAlert(message, type = "danger") {
        if (!formAlertBox) return;
        formAlertBox.className = `alert alert-${type} alert-dismissible fade show mt-3`;
        formAlertBox.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="bi bi-exclamation-triangle-fill me-2 fs-5"></i>
                <div>${message}</div>
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        formAlertBox.style.display = "block";
        formAlertBox.scrollIntoView({ behavior: "smooth", block: "center" });
    }

    if (feedbackForm) {
        feedbackForm.addEventListener("submit", async function (e) {
            e.preventDefault();

            // Client-side validation
            const isAnon = anonymousToggle ? anonymousToggle.checked : false;

            if (!isAnon) {
                const name = document.getElementById("full_name").value.trim();
                const email = document.getElementById("email").value.trim();
                if (!name) {
                    showFormAlert("Please provide your Full Name or enable Anonymous mode.");
                    document.getElementById("full_name").focus();
                    return;
                }
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!email || !emailRegex.test(email)) {
                    showFormAlert("Please provide a valid email address.");
                    document.getElementById("email").focus();
                    return;
                }
            }

            const subject = document.getElementById("subject").value;
            if (!subject) {
                showFormAlert("Please select a Laboratory / Subject.");
                document.getElementById("subject").focus();
                return;
            }

            const expName = document.getElementById("experiment_name").value.trim();
            if (!expName) {
                showFormAlert("Please enter the name of the Experiment.");
                document.getElementById("experiment_name").focus();
                return;
            }

            // Ratings check
            const ov = parseInt(document.getElementById("overall_rating").value) || 0;
            const exp = parseInt(document.getElementById("experiment_rating").value) || 0;
            const nav = parseInt(document.getElementById("navigation_rating").value) || 0;
            const tech = parseInt(document.getElementById("technical_rating").value) || 0;

            if (ov < 1 || exp < 1 || nav < 1 || tech < 1) {
                showFormAlert("Please select a star rating (1 to 5) for all four rating categories.");
                document.getElementById("starRatingSection").scrollIntoView({ behavior: "smooth" });
                return;
            }

            // Experience text check
            const desc = experienceTextarea.value.trim();
            if (!desc || desc.length < 10) {
                showFormAlert("Please share your experience description (minimum 10 characters required).");
                experienceTextarea.focus();
                return;
            }

            // Prepare FormData
            const formData = new FormData(feedbackForm);

            // Close any open modals
            const previewModalInstance = bootstrap.Modal.getInstance(previewModalEl);
            if (previewModalInstance) previewModalInstance.hide();

            // Disable submit button & show loading state
            submitBtn.disabled = true;
            if (submitSpinner) submitSpinner.classList.remove("d-none");
            if (submitBtnText) submitBtnText.textContent = "Submitting Feedback...";

            try {
                const response = await fetch("/api/feedback", {
                    method: "POST",
                    body: formData
                });

                const data = await response.json();

                if (response.ok && data.success) {
                    // Redirect to success receipt page
                    window.location.href = data.redirect_url;
                } else {
                    showFormAlert(data.message || "Failed to submit feedback. Please check required fields.");
                    submitBtn.disabled = false;
                    if (submitSpinner) submitSpinner.classList.add("d-none");
                    if (submitBtnText) submitBtnText.textContent = "SUBMIT FEEDBACK";
                }
            } catch (err) {
                console.error("Submission error:", err);
                showFormAlert("Network or communication error. Please verify your connection and try again.");
                submitBtn.disabled = false;
                if (submitSpinner) submitSpinner.classList.add("d-none");
                if (submitBtnText) submitBtnText.textContent = "SUBMIT FEEDBACK";
            }
        });
    }

    // Modal submit confirmation button (from preview modal)
    const btnSubmitFromPreview = document.getElementById("btnSubmitFromPreview");
    if (btnSubmitFromPreview && feedbackForm) {
        btnSubmitFromPreview.addEventListener("click", function () {
            feedbackForm.dispatchEvent(new Event("submit"));
        });
    }
});

