(function () {
    // API Configuration - Use production URL when not on localhost
    const API_BASE = (typeof window !== 'undefined' && window.location.hostname === 'localhost') 
        ? 'http://localhost:5000/api' 
        : 'https://your-render-app.onrender.com/api'; // Replace with your Render backend URL

    const form = document.getElementById('listEventForm');
    const steps = document.querySelectorAll('.form-step');
    const sidebarSteps = document.querySelectorAll('.sidebar-step');
    const formSuccess = document.getElementById('formSuccess');
    const formError = document.getElementById('formError');
    const formErrorMessage = document.getElementById('formErrorMessage');
    const dismissError = document.getElementById('dismissError');

    // Preview elements
    const previewTitle = document.getElementById('previewTitle');
    const previewType = document.getElementById('previewType');
    const previewDate = document.getElementById('previewDate');
    const previewVenue = document.getElementById('previewVenue');
    const previewBannerImg = document.getElementById('previewBannerImg');
    const previewBannerPlaceholder = document.getElementById('previewBannerPlaceholder');

    let currentStep = 1;
    /** Effective banner image: data URL (from file upload) or https URL (from paste). Stored as link in user collection. */
    let effectiveBannerUrl = '';
    const totalSteps = 7;

    // Data collections for complex sections
    const tickets = [];
    const sponsors = [];
    const partners = [];
    const faqs = [];
    const contents = [];

    function getActiveStepButtons() {
        const activeStep = document.querySelector('.form-step.active');
        if (!activeStep) return null;
        return {
            prev: activeStep.querySelector('.wizard-btn-prev'),
            next: activeStep.querySelector('.wizard-btn-next'),
            submit: activeStep.querySelector('.wizard-btn-submit')
        };
    }

    function goToStep(step) {
        currentStep = Math.max(1, Math.min(totalSteps, step));

        steps.forEach(function (s) {
            s.classList.toggle('active', parseInt(s.dataset.step, 10) === currentStep);
        });

        sidebarSteps.forEach(function (s) {
            const n = parseInt(s.dataset.step, 10);
            s.classList.toggle('active', n === currentStep);
        });

        // Update button visibility in active step
        const buttons = getActiveStepButtons();
        if (buttons) {
            if (buttons.prev) {
                buttons.prev.style.visibility = currentStep > 1 ? 'visible' : 'hidden';
            }
            if (buttons.next) {
                buttons.next.style.display = currentStep < totalSteps ? 'inline-flex' : 'none';
            }
            if (buttons.submit) {
                buttons.submit.style.display = currentStep === totalSteps ? 'inline-flex' : 'none';
            }
        }
    }

    function validateStep(step) {
        if (step === 1) {
            const title = document.getElementById('title');
            const startDate = document.getElementById('start_date');
            const eventType = document.getElementById('event_type');

            if (!title || !title.value.trim()) {
                if (title) { title.focus(); title.reportValidity && title.reportValidity(); }
                return false;
            }
            if (!startDate || !startDate.value.trim()) {
                if (startDate) { startDate.focus(); startDate.reportValidity && startDate.reportValidity(); }
                return false;
            }
            if (!eventType || !eventType.value.trim()) {
                if (eventType) { eventType.focus(); eventType.reportValidity && eventType.reportValidity(); }
                return false;
            }
            return true;
        }
        return true;
    }

    function buildDateTime(dateStr, timeStr, dateOnly) {
        if (!dateStr) return null;
        const date = dateStr.trim();
        if (dateOnly) {
            return date + 'T00:00:00';
        }
        const time = (timeStr || '').trim();
        if (time) return date + 'T' + time + ':00';
        return date + 'T00:00:00';
    }

    function collectPayload() {
        const startDate = document.getElementById('start_date').value;
        const endDate = document.getElementById('end_date').value;
        const startTime = document.getElementById('start_time').value;
        const endTimeInput = document.getElementById('end_time_input').value;
        const dateOnly = document.getElementById('date_only').checked;

        const dateTime = buildDateTime(startDate, startTime, dateOnly);
        const endTime = (endDate || startDate) ? buildDateTime(endDate || startDate, endTimeInput || startTime, dateOnly) : null;

        // organizer_details object
        const organizerDetails = {
            name: document.getElementById('org_name').value.trim() || null,
            email: document.getElementById('org_email').value.trim() || null,
            company: document.getElementById('org_company').value.trim() || null,
            website: document.getElementById('org_website').value.trim() || null,
            social: {
                twitter: document.getElementById('org_twitter').value.trim() || null,
                facebook: document.getElementById('org_facebook').value.trim() || null,
                telegram: document.getElementById('org_telegram').value.trim() || null,
                linkedin: document.getElementById('org_linkedin').value.trim() || null
            }
        };

        return {
            title: document.getElementById('title').value.trim(),
            description: document.getElementById('description').value.trim() || null,
            event_type: document.getElementById('event_type').value || null,
            venue: document.getElementById('venue').value.trim() || null,
            date_time: dateTime,
            end_time: endTime,
            image_url: effectiveBannerUrl || document.getElementById('image_url').value.trim() || null,
            organizer: organizerDetails.company || organizerDetails.name || null,
            ticket_url: document.getElementById('ticket_url').value.trim() ||
                        document.getElementById('ticket_url_step').value.trim() || null,
            category_tags: document.getElementById('category_tags').value.trim() || null,

            // Extended structured data
            organizer_details: organizerDetails,
            tickets: tickets,
            sponsors: sponsors,
            partners: partners,
            faqs: faqs,
            contents: contents
        };
    }

    function showSuccess() {
        form.style.display = 'none';
        formError.style.display = 'none';
        formSuccess.style.display = 'block';
    }

    function showError(msg) {
        formErrorMessage.textContent = msg || 'Could not save your event. Please try again.';
        formError.style.display = 'block';
    }

    function hideError() {
        formError.style.display = 'none';
    }

    // Preview updates
    function updatePreview() {
        const title = document.getElementById('title').value.trim();
        const eventType = document.getElementById('event_type').value || 'Conference';
        const venue = document.getElementById('venue').value.trim();
        const city = document.getElementById('city').value.trim();
        const country = document.getElementById('country').value.trim();
        const startDate = document.getElementById('start_date').value;
        const endDate = document.getElementById('end_date').value;

        previewTitle.textContent = title || 'Event Title';
        previewType.textContent = (eventType || 'Conference').toUpperCase();

        if (startDate) {
            const start = new Date(startDate);
            let text = start.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
            if (endDate) {
                const end = new Date(endDate);
                const endText = end.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
                text = text + ' - ' + endText;
            }
            previewDate.textContent = text;
        } else {
            previewDate.textContent = 'Date will appear here';
        }

        const parts = [];
        if (venue) parts.push(venue);
        if (city) parts.push(city);
        if (country) parts.push(country);
        previewVenue.textContent = parts.length ? parts.join(', ') : 'Venue will appear here';
    }

    ['title', 'event_type', 'venue', 'city', 'country', 'start_date', 'end_date'].forEach(function (id) {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('input', updatePreview);
            el.addEventListener('change', updatePreview);
        }
    });

    function updatePreviewBanner() {
        var urlInput = document.getElementById('image_url');
        var url = effectiveBannerUrl || (urlInput && urlInput.value.trim()) || '';
        if (previewBannerImg) {
            if (url) {
                previewBannerImg.src = url;
                previewBannerImg.style.display = 'block';
            } else {
                previewBannerImg.src = '';
                previewBannerImg.style.display = 'none';
            }
        }
        if (previewBannerPlaceholder) {
            previewBannerPlaceholder.style.display = url ? 'none' : 'flex';
        }
    }

    function setBannerFromFile(file) {
        if (!file || !file.type.match(/^image\/(jpeg|png|gif|webp)$/)) return;
        if (file.size > 5 * 1024 * 1024) { alert('Image must be under 5MB.'); return; }
        const reader = new FileReader();
        reader.onload = function () {
            effectiveBannerUrl = reader.result;
            var urlInput = document.getElementById('image_url');
            if (urlInput) urlInput.value = '';
            var fileInput = document.getElementById('banner_file');
            if (fileInput) fileInput.value = '';
            updatePreviewBanner();
        };
        reader.readAsDataURL(file);
    }

    var bannerDropzone = document.getElementById('bannerDropzone');
    var bannerFileInput = document.getElementById('banner_file');
    var imageUrlInput = document.getElementById('image_url');

    if (bannerDropzone && bannerFileInput) {
        // File input now overlays the dropzone, so clicks should work directly
        // But add a fallback click handler for the dropzone area
        bannerDropzone.addEventListener('click', function (e) {
            // Don't trigger if clicking on URL input
            if (imageUrlInput && (e.target === imageUrlInput || e.target.closest('input[type="url"]'))) {
                return;
            }
            // Don't trigger if clicking directly on file input (it handles itself)
            if (e.target === bannerFileInput) {
                return;
            }
            // For clicks on dropzone content, trigger file input
            if (e.target.closest('.banner-dropzone-inner') || e.target.closest('.banner-or')) {
                bannerFileInput.click();
            }
        });
        
        // Prevent URL input clicks from bubbling
        if (imageUrlInput) {
            imageUrlInput.addEventListener('click', function (e) {
                e.stopPropagation();
            });
            imageUrlInput.addEventListener('mousedown', function (e) {
                e.stopPropagation();
            });
        }
        
        // Drag and drop handlers
        bannerDropzone.addEventListener('dragover', function (e) {
            e.preventDefault();
            e.stopPropagation();
            bannerDropzone.classList.add('drag-over');
        });
        bannerDropzone.addEventListener('dragleave', function (e) {
            e.preventDefault();
            e.stopPropagation();
            bannerDropzone.classList.remove('drag-over');
        });
        bannerDropzone.addEventListener('drop', function (e) {
            e.preventDefault();
            e.stopPropagation();
            bannerDropzone.classList.remove('drag-over');
            var files = e.dataTransfer && e.dataTransfer.files;
            if (files && files.length) setBannerFromFile(files[0]);
        });
    }

    if (bannerFileInput) {
        bannerFileInput.addEventListener('change', function () {
            var files = this.files;
            if (files && files.length) setBannerFromFile(files[0]);
        });
    }

    if (imageUrlInput) {
        imageUrlInput.addEventListener('input', function () {
            var v = this.value.trim();
            effectiveBannerUrl = v || '';
            if (v && bannerFileInput) bannerFileInput.value = '';
            updatePreviewBanner();
        });
        imageUrlInput.addEventListener('change', function () {
            var v = this.value.trim();
            effectiveBannerUrl = v || '';
            if (v && bannerFileInput) bannerFileInput.value = '';
            updatePreviewBanner();
        });
    }

    updatePreviewBanner();

    // Date-only toggle
    const dateOnlyEl = document.getElementById('date_only');
    const timeRow = document.getElementById('timeRow');
    if (dateOnlyEl && timeRow) {
        dateOnlyEl.addEventListener('change', function () {
            timeRow.style.display = dateOnlyEl.checked ? 'none' : 'grid';
        });
    }

    // End date min
    const startDateEl = document.getElementById('start_date');
    const endDateEl = document.getElementById('end_date');
    if (startDateEl && endDateEl) {
        startDateEl.addEventListener('change', function () {
            endDateEl.min = startDateEl.value || '';
            updatePreview();
        });
    }

    // Sidebar click navigation
    sidebarSteps.forEach(function (btn) {
        btn.addEventListener('click', function () {
            const step = parseInt(btn.dataset.step, 10);
            // Only allow going forward if current step is valid
            if (step > currentStep && !validateStep(currentStep)) return;
            goToStep(step);
        });
    });

    // Use event delegation for buttons in each step
    form.addEventListener('click', function (e) {
        if (e.target.classList.contains('wizard-btn-prev')) {
            e.preventDefault();
            if (currentStep > 1) goToStep(currentStep - 1);
        } else if (e.target.classList.contains('wizard-btn-next')) {
            e.preventDefault();
            if (!validateStep(currentStep)) return;
            if (currentStep < totalSteps) goToStep(currentStep + 1);
        }
    });

    dismissError.addEventListener('click', hideError);

    // Helpers to add items to lists
    function addPill(listEl, emptyEl, label, storeArray, obj) {
        storeArray.push(obj);
        if (emptyEl) emptyEl.style.display = 'none';
        const li = document.createElement('li');
        li.textContent = label;
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'pill-remove';
        btn.textContent = '×';
        btn.addEventListener('click', function () {
            const idx = storeArray.indexOf(obj);
            if (idx >= 0) storeArray.splice(idx, 1);
            li.remove();
            if (storeArray.length === 0 && emptyEl) emptyEl.style.display = 'block';
        });
        li.appendChild(btn);
        listEl.appendChild(li);
    }

    // Tickets
    const addTicketBtn = document.getElementById('addTicketBtn');
    if (addTicketBtn) {
        addTicketBtn.addEventListener('click', function () {
            const nameEl = document.getElementById('ticket_name');
            const typeEl = document.getElementById('ticket_type');
            if (!nameEl || !nameEl.value.trim()) {
                if (nameEl) { nameEl.focus(); nameEl.reportValidity && nameEl.reportValidity(); }
                return;
            }
            const obj = {
                name: nameEl.value.trim(),
                type: typeEl ? typeEl.value : 'Free',
                description: document.getElementById('ticket_description').value.trim() || null,
                quantity: document.getElementById('ticket_quantity').value || null,
                price: document.getElementById('ticket_price').value || null,
                sales_start: document.getElementById('ticket_sales_start').value || null,
                sales_end: document.getElementById('ticket_sales_end').value || null,
                url: document.getElementById('ticket_url_step').value.trim() || null
            };
            addPill(
                document.getElementById('ticketsList'),
                document.getElementById('ticketsEmpty'),
                obj.name + ' (' + obj.type + ')',
                tickets,
                obj
            );
            nameEl.value = '';
        });
    }

    // Sponsors
    const addSponsorBtn = document.getElementById('addSponsorBtn');
    if (addSponsorBtn) {
        addSponsorBtn.addEventListener('click', function () {
            const nameEl = document.getElementById('sponsor_name');
            if (!nameEl || !nameEl.value.trim()) {
                if (nameEl) { nameEl.focus(); nameEl.reportValidity && nameEl.reportValidity(); }
                return;
            }
            const obj = {
                name: nameEl.value.trim(),
                tier: document.getElementById('sponsor_tier').value.trim() || null,
                logo_url: document.getElementById('sponsor_logo').value.trim() || null,
                website: document.getElementById('sponsor_website').value.trim() || null
            };
            addPill(
                document.getElementById('sponsorsList'),
                document.getElementById('sponsorsEmpty'),
                obj.name + (obj.tier ? ' – ' + obj.tier : ''),
                sponsors,
                obj
            );
            nameEl.value = '';
        });
    }

    // Partners
    const addPartnerBtn = document.getElementById('addPartnerBtn');
    if (addPartnerBtn) {
        addPartnerBtn.addEventListener('click', function () {
            const nameEl = document.getElementById('partner_name');
            if (!nameEl || !nameEl.value.trim()) {
                if (nameEl) { nameEl.focus(); nameEl.reportValidity && nameEl.reportValidity(); }
                return;
            }
            const obj = {
                name: nameEl.value.trim(),
                type: document.getElementById('partner_type').value.trim() || null,
                logo_url: document.getElementById('partner_logo').value.trim() || null,
                website: document.getElementById('partner_website').value.trim() || null
            };
            addPill(
                document.getElementById('partnersList'),
                document.getElementById('partnersEmpty'),
                obj.name + (obj.type ? ' – ' + obj.type : ''),
                partners,
                obj
            );
            nameEl.value = '';
        });
    }

    // FAQs
    const addFaqBtn = document.getElementById('addFaqBtn');
    if (addFaqBtn) {
        addFaqBtn.addEventListener('click', function () {
            const qEl = document.getElementById('faq_question');
            const aEl = document.getElementById('faq_answer');
            if (!qEl || !qEl.value.trim() || !aEl || !aEl.value.trim()) {
                if (qEl && !qEl.value.trim()) { qEl.focus(); qEl.reportValidity && qEl.reportValidity(); }
                else if (aEl) { aEl.focus(); aEl.reportValidity && aEl.reportValidity(); }
                return;
            }
            const obj = {
                question: qEl.value.trim(),
                answer: aEl.value.trim()
            };
            addPill(
                document.getElementById('faqsList'),
                document.getElementById('faqsEmpty'),
                obj.question,
                faqs,
                obj
            );
            qEl.value = '';
            aEl.value = '';
        });
    }

    // Contents
    const addContentBtn = document.getElementById('addContentBtn');
    if (addContentBtn) {
        addContentBtn.addEventListener('click', function () {
            const hEl = document.getElementById('content_heading');
            const bEl = document.getElementById('content_body');
            const alignEl = document.getElementById('content_alignment');
            if (!hEl || !hEl.value.trim() || !bEl || !bEl.value.trim()) {
                if (hEl && !hEl.value.trim()) { hEl.focus(); hEl.reportValidity && hEl.reportValidity(); }
                else if (bEl) { bEl.focus(); bEl.reportValidity && bEl.reportValidity(); }
                return;
            }
            const obj = {
                heading: hEl.value.trim(),
                body: bEl.value.trim(),
                alignment: alignEl ? alignEl.value : 'left'
            };
            addPill(
                document.getElementById('contentsList'),
                document.getElementById('contentsEmpty'),
                obj.heading,
                contents,
                obj
            );
            hEl.value = '';
            bEl.value = '';
        });
    }

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        if (!validateStep(1)) {
            goToStep(1);
            return;
        }

        const payload = collectPayload();
        const buttons = getActiveStepButtons();
        const submitBtn = buttons ? buttons.submit : null;
        if (!submitBtn) {
            showError('Submit button not found');
            return;
        }
        const origText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Submitting...';
        hideError();

        fetch(API_BASE + '/user/list-event', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
            .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, json: j }; }); })
            .then(function (res) {
                if (res.ok && res.json.success) {
                    showSuccess();
                } else {
                    showError(res.json.error || 'Failed to list event.');
                }
            })
            .catch(function (err) {
                showError(err && err.message ? err.message : 'Network error. Is the API server running?');
            })
            .finally(function () {
                submitBtn.disabled = false;
                submitBtn.innerHTML = origText;
            });
    });

    // Init
    goToStep(1);
    updatePreview();
})();
