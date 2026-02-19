// API Configuration
// Since Nginx proxies /api to Flask, we can use relative URLs
const API_BASE_URL = "/api";

// Global variables
let allEvents = [];
let filteredEvents = [];
let currentPage = 1;
const eventsPerPage = 12;
let currentView = "grid";
let currentStatus = "all";
let currentEvent = null;

// Initialize the application
document.addEventListener("DOMContentLoaded", () => {
	loadEvents();
	initializeEventListeners();
});

// Load events from API
async function loadEvents() {
	showLoading(true);

	try {
		// Use internal API endpoint that includes URLs
		const response = await fetch(`${API_BASE_URL}/internal/events`);

		if (!response.ok) {
			throw new Error("Failed to load events from API");
		}

		const data = await response.json();

		if (data.success) {
			allEvents = data.events.map((event) => ({
				...event,
				status: getEventStatus(event),
			}));

			filteredEvents = [...allEvents];

			populateFilters();
			updateEventCounts();
			displayEvents();
		} else {
			throw new Error(data.error || "Failed to load events");
		}
	} catch (error) {
		console.warn(
			"API unavailable, loading static data for UI preview:",
			error.message,
		);

		// Fallback to static mock data if available
		if (typeof STATIC_EVENTS !== "undefined" && STATIC_EVENTS.length > 0) {
			allEvents = STATIC_EVENTS.map((event) => ({
				...event,
				status: getEventStatus(event),
			}));

			filteredEvents = [...allEvents];

			populateFilters();
			updateEventCounts();
			displayEvents();
		} else {
			showNoResults(true);
			document.getElementById("loadingSpinner").innerHTML = `
                <i class="fas fa-exclamation-triangle"></i>
                <p>Failed to load events from database.</p>
                <p style="font-size: 0.9rem; margin-top: 10px;">Make sure the API server is running: python api_server.py</p>
            `;
		}
	} finally {
		showLoading(false);
	}
}

// Get event status based on dates
function getEventStatus(event) {
	const now = new Date();
	const startDate = event.date_time ? new Date(event.date_time) : null;
	const endDate = event.end_time ? new Date(event.end_time) : null;

	if (!startDate) return "upcoming";

	if (endDate) {
		if (now < startDate) return "upcoming";
		if (now >= startDate && now <= endDate) return "ongoing";
		if (now > endDate) return "ended";
	} else {
		if (now < startDate) return "upcoming";
		const dayAfterStart = new Date(startDate);
		dayAfterStart.setDate(dayAfterStart.getDate() + 1);
		if (now > dayAfterStart) return "ended";
		return "ongoing";
	}

	return "upcoming";
}

// Get image URL - use direct URL from event data or fallback to placeholder
function getImageUrl(event) {
	// If event has image_url, use it directly (loads from Luma CDN)
	if (
		event.image_url &&
		event.image_url !== "null" &&
		event.image_url !== "None"
	) {
		return event.image_url;
	}

	// Fallback to placeholder SVG
	return `data:image/svg+xml,${encodeURIComponent(`
        <svg xmlns="http://www.w3.org/2000/svg" width="400" height="220" viewBox="0 0 400 220">
            <defs>
                <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#1e00ff;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#5c4dff;stop-opacity:1" />
                </linearGradient>
            </defs>
            <rect width="400" height="220" fill="url(#grad)"/>
            <text x="50%" y="50%" font-family="Geist Sans, sans-serif" font-size="20" font-weight="bold" 
                  fill="white" text-anchor="middle" dominant-baseline="middle">
                Crypto Event
            </text>
        </svg>
    `)}`;
}

// Create event card HTML
function createEventCard(event) {
	const statusClass = `status-${event.status}`;
	const statusText =
		event.status.charAt(0).toUpperCase() + event.status.slice(1);

	const tags = event.category_tags
		? event.category_tags
				.split(",")
				.filter((tag) => tag.trim())
				.slice(0, 3)
				.map(
					(tag) =>
						`<span class="event-tag-small">${capitalizeWords(tag.trim())}</span>`,
				)
				.join("")
		: "";

	const imageUrl = getImageUrl(event);
	const dateStr = formatEventDate(event.date_time);
	const timeStr = formatEventTime(event.date_time, event.end_time);
	const venue = escapeHtml(event.venue || "Location TBA");
	const organizer = escapeHtml(event.organizer || "");

	return `
        <div class="event-card" data-id="${event.external_id}">
            <div class="event-image-container" style="--card-img-url: url('${imageUrl}')">
                <img src="${imageUrl}"
                     alt="${escapeHtml(event.title)}"
                     class="event-image"
                     loading="lazy">
                <div class="event-card-badges">
                    <div class="event-status-badge ${statusClass}">${statusText}</div>
                </div>
            </div>
            <div class="event-content">
                <div class="event-date-line">${dateStr} · ${timeStr}</div>
                <h3 class="event-title">${escapeHtml(event.title || "Untitled Event")}</h3>
                ${organizer ? `<div class="event-organizer-line">by <strong>${organizer}</strong></div>` : ""}
                <div class="event-info">
                    <div class="info-row">
                        <span>${venue}</span>
                    </div>
                </div>
				<div class="event-tags-inline">
                    ${tags}
                </div>
            </div>
        </div>
    `;
}

// Rest of the JavaScript functions (same as before)
function populateFilters() {
	const locations = [
		...new Set(allEvents.map((e) => extractLocation(e.venue)).filter(Boolean)),
	];
	const locationFilter = document.getElementById("locationFilter");
	locations.sort().forEach((location) => {
		const option = document.createElement("option");
		option.value = location;
		option.textContent = location;
		locationFilter.appendChild(option);
	});

	const types = new Set();
	allEvents.forEach((event) => {
		if (event.category_tags) {
			event.category_tags.split(",").forEach((tag) => {
				const cleanTag = tag.trim();
				if (cleanTag) types.add(cleanTag);
			});
		}
	});

	const typeFilter = document.getElementById("typeFilter");
	[...types].sort().forEach((type) => {
		const option = document.createElement("option");
		option.value = type;
		option.textContent = capitalizeWords(type);
		typeFilter.appendChild(option);
	});
}

function extractLocation(venue) {
	if (!venue) return null;
	const parts = venue.split(",");
	return parts.length > 1 ? parts[parts.length - 1].trim() : venue.trim();
}

function capitalizeWords(str) {
	return str
		.split(/[\s-_]/)
		.map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
		.join(" ");
}

function initializeEventListeners() {
	document
		.getElementById("locationFilter")
		.addEventListener("change", applyFilters);
	document
		.getElementById("dateFilter")
		.addEventListener("change", applyFilters);
	document
		.getElementById("typeFilter")
		.addEventListener("change", applyFilters);
	document
		.getElementById("resetFilters")
		.addEventListener("click", resetFilters);

	document.querySelectorAll(".tab-btn").forEach((btn) => {
		btn.addEventListener("click", () => {
			document
				.querySelectorAll(".tab-btn")
				.forEach((b) => b.classList.remove("active"));
			btn.classList.add("active");
			currentStatus = btn.dataset.status;
			currentPage = 1;
			applyFilters();
		});
	});

	document
		.getElementById("searchInput")
		.addEventListener("input", debounce(applyFilters, 300));

	document.querySelectorAll(".view-btn").forEach((btn) => {
		btn.addEventListener("click", () => {
			document
				.querySelectorAll(".view-btn")
				.forEach((b) => b.classList.remove("active"));
			btn.classList.add("active");
			currentView = btn.dataset.view;
			const grid = document.getElementById("eventsGrid");
			if (currentView === "list") {
				grid.classList.add("list-view");
			} else {
				grid.classList.remove("list-view");
			}
		});
	});

	document
		.getElementById("closeModal")
		.addEventListener("click", closeEventModal);
	document
		.getElementById("closeShareModal")
		.addEventListener("click", closeShareModal);
	document
		.getElementById("closeCalendarModal")
		.addEventListener("click", closeCalendarModal);
	document
		.getElementById("modalShareBtn")
		.addEventListener("click", openShareModal);
	document
		.getElementById("modalCalendarBtn")
		.addEventListener("click", openCalendarModal);
	document
		.getElementById("copyLinkBtn")
		.addEventListener("click", copyShareLink);

	document
		.getElementById("calendarGoogle")
		.addEventListener("click", () => addToCalendarService("google"));
	document
		.getElementById("calendarOutlook")
		.addEventListener("click", () => addToCalendarService("outlook"));
	document
		.getElementById("calendarApple")
		.addEventListener("click", () => addToCalendarService("apple"));
	document
		.getElementById("calendarICS")
		.addEventListener("click", () => addToCalendarService("ics"));

	document
		.getElementById("shareTwitter")
		.addEventListener("click", () => shareOn("twitter"));
	document
		.getElementById("shareLinkedIn")
		.addEventListener("click", () => shareOn("linkedin"));
	document
		.getElementById("shareWhatsApp")
		.addEventListener("click", () => shareOn("whatsapp"));
	document
		.getElementById("shareFacebook")
		.addEventListener("click", () => shareOn("facebook"));
	document
		.getElementById("shareEmail")
		.addEventListener("click", () => shareOn("email"));

	document.getElementById("eventModal").addEventListener("click", (e) => {
		if (e.target.id === "eventModal") closeEventModal();
	});
	document.getElementById("shareModal").addEventListener("click", (e) => {
		if (e.target.id === "shareModal") closeShareModal();
	});
	document.getElementById("calendarModal").addEventListener("click", (e) => {
		if (e.target.id === "calendarModal") closeCalendarModal();
	});

	document.getElementById("listEventBtn").addEventListener("click", () => {
		window.location.href = "list_event.html";
	});
}

function applyFilters() {
	const locationFilter = document.getElementById("locationFilter").value;
	const dateFilter = document.getElementById("dateFilter").value;
	const typeFilter = document.getElementById("typeFilter").value;
	const searchQuery = document
		.getElementById("searchInput")
		.value.toLowerCase();

	filteredEvents = allEvents.filter((event) => {
		if (currentStatus !== "all" && event.status !== currentStatus) return false;
		if (
			locationFilter &&
			!extractLocation(event.venue)?.includes(locationFilter)
		)
			return false;
		if (dateFilter && event.status !== dateFilter) return false;
		if (typeFilter && !event.category_tags?.includes(typeFilter)) return false;

		if (searchQuery) {
			const searchableText = [
				event.title,
				event.description,
				event.venue,
				event.organizer,
				event.category_tags,
			]
				.filter(Boolean)
				.join(" ")
				.toLowerCase();

			if (!searchableText.includes(searchQuery)) return false;
		}

		return true;
	});

	currentPage = 1;
	updateEventCounts();
	displayEvents();
}

function resetFilters() {
	document.getElementById("locationFilter").value = "";
	document.getElementById("dateFilter").value = "";
	document.getElementById("typeFilter").value = "";
	document.getElementById("searchInput").value = "";
	currentStatus = "all";

	document.querySelectorAll(".tab-btn").forEach((btn) => {
		btn.classList.toggle("active", btn.dataset.status === "all");
	});

	applyFilters();
}

function updateEventCounts() {
	const counts = {
		all: allEvents.length,
		upcoming: allEvents.filter((e) => e.status === "upcoming").length,
		ongoing: allEvents.filter((e) => e.status === "ongoing").length,
		ended: allEvents.filter((e) => e.status === "ended").length,
	};

	document.getElementById("countAll").textContent = counts.all;
	document.getElementById("countUpcoming").textContent = counts.upcoming;
	document.getElementById("countOngoing").textContent = counts.ongoing;
	document.getElementById("countEnded").textContent = counts.ended;
}

function displayEvents() {
	const grid = document.getElementById("eventsGrid");
	const startIndex = (currentPage - 1) * eventsPerPage;
	const endIndex = startIndex + eventsPerPage;
	const eventsToShow = filteredEvents.slice(startIndex, endIndex);

	if (eventsToShow.length === 0) {
		grid.innerHTML = "";
		showNoResults(true);
		return;
	}

	showNoResults(false);

	grid.innerHTML = eventsToShow.map((event) => createEventCard(event)).join("");

	document.querySelectorAll(".event-card").forEach((card, index) => {
		card.addEventListener("click", () => {
			openEventModal(eventsToShow[index]);
		});
	});

	renderPagination();
}

function openEventModal(event) {
	currentEvent = event;

	const modal = document.getElementById("eventModal");
	const statusClass = `status-${event.status}`;
	const statusText =
		event.status.charAt(0).toUpperCase() + event.status.slice(1);

	const imageUrl = getImageUrl(currentEvent);
	const modalImage = document.getElementById("modalImage");
	modalImage.src = imageUrl;

	const badge = document.getElementById("modalStatusBadge");
	badge.className = `modal-status-badge ${statusClass}`;
	badge.textContent = statusText;

	document.getElementById("modalTitle").textContent =
		event.title || "Untitled Event";
	document.getElementById("modalVenue").textContent =
		event.venue || "Location TBA";

	const viewMapLink = document.getElementById("modalViewMap");
	if (event.venue) {
		viewMapLink.href = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(event.venue)}`;
		viewMapLink.style.display = "inline-block";
	} else {
		viewMapLink.style.display = "none";
	}

	const dateStr = formatEventDateRange(event.date_time, event.end_time);
	document.getElementById("modalDate").textContent = dateStr;

	const timeStr = formatEventTime(event.date_time, event.end_time);
	document.getElementById("modalTime").textContent = timeStr;

	const organizerContainer = document.getElementById("modalOrganizerContainer");
	if (event.organizer) {
		document.getElementById("modalOrganizer").innerHTML = `
            <strong>${escapeHtml(event.organizer)}</strong>
        `;
		organizerContainer.style.display = "flex";
	} else {
		organizerContainer.style.display = "none";
	}

	const tagsContainer = document.getElementById("modalTags");
	if (event.category_tags) {
		const tags = event.category_tags
			.split(",")
			.filter((tag) => tag.trim())
			.map(
				(tag) =>
					`<span class="modal-tag">#${capitalizeWords(tag.trim())}</span>`,
			)
			.join("");
		tagsContainer.innerHTML = tags;
	} else {
		tagsContainer.innerHTML = "";
	}

	const ticketBtn = document.getElementById("modalTicketBtn");
	if (event.ticket_url) {
		ticketBtn.href = event.ticket_url;
		ticketBtn.style.display = "inline-flex";
	} else {
		ticketBtn.style.display = "none";
	}

	modal.classList.add("active");
	document.body.style.overflow = "hidden";
}

function formatEventDate(dateStr) {
	if (!dateStr) return "Date TBA";
	try {
		const date = new Date(dateStr);
		return date.toLocaleDateString("en-US", {
			month: "short",
			day: "numeric",
			year: "numeric",
		});
	} catch {
		return "Date TBA";
	}
}

function formatEventTime(startStr, endStr) {
	if (!startStr) return "Time TBA";
	try {
		const start = new Date(startStr);
		const startTime = start.toLocaleTimeString("en-US", {
			hour: "numeric",
			minute: "2-digit",
			hour12: true,
		});

		if (endStr) {
			const end = new Date(endStr);
			const endTime = end.toLocaleTimeString("en-US", {
				hour: "numeric",
				minute: "2-digit",
				hour12: true,
			});
			return `${startTime} - ${endTime}`;
		}

		return startTime;
	} catch {
		return "Time TBA";
	}
}

function formatEventDateRange(startStr, endStr) {
	if (!startStr) return "Date TBA";
	try {
		const start = new Date(startStr);
		const startFormatted = start.toLocaleDateString("en-US", {
			month: "short",
			day: "numeric",
			year: "numeric",
		});

		if (endStr) {
			const end = new Date(endStr);
			const endFormatted = end.toLocaleDateString("en-US", {
				month: "short",
				day: "numeric",
				year: "numeric",
			});

			if (startFormatted !== endFormatted) {
				return `${startFormatted} - ${endFormatted}`;
			}
		}

		return startFormatted;
	} catch {
		return "Date TBA";
	}
}

function closeEventModal() {
	document.getElementById("eventModal").classList.remove("active");
	document.body.style.overflow = "";
}

function openShareModal() {
	if (!currentEvent) return;

	const shareLink = currentEvent.ticket_url || window.location.href;
	document.getElementById("shareLink").value = shareLink;

	document.getElementById("shareModal").classList.add("active");
}

function closeShareModal() {
	document.getElementById("shareModal").classList.remove("active");
}

function copyShareLink() {
	const input = document.getElementById("shareLink");
	input.select();
	document.execCommand("copy");

	const btn = document.getElementById("copyLinkBtn");
	const originalText = btn.innerHTML;
	btn.innerHTML = '<i class="fas fa-check"></i> Copied!';

	setTimeout(() => {
		btn.innerHTML = originalText;
	}, 2000);
}

function shareOn(platform) {
	if (!currentEvent) return;

	const url = encodeURIComponent(
		currentEvent.ticket_url || window.location.href,
	);
	const title = encodeURIComponent(currentEvent.title || "Crypto Event");
	const text = encodeURIComponent(
		`Check out this event: ${currentEvent.title}`,
	);

	let shareUrl = "";

	switch (platform) {
		case "twitter":
			shareUrl = `https://twitter.com/intent/tweet?text=${text}&url=${url}`;
			break;
		case "linkedin":
			shareUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${url}`;
			break;
		case "whatsapp":
			shareUrl = `https://wa.me/?text=${text}%20${url}`;
			break;
		case "facebook":
			shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${url}`;
			break;
		case "email":
			shareUrl = `mailto:?subject=${title}&body=${text}%20${url}`;
			break;
	}

	if (shareUrl) {
		window.open(shareUrl, "_blank", "width=600,height=400");
	}
}

function openCalendarModal() {
	if (!currentEvent) return;
	document.getElementById("calendarModal").classList.add("active");
}

function closeCalendarModal() {
	document.getElementById("calendarModal").classList.remove("active");
}

function addToCalendarService(service) {
	if (!currentEvent) return;

	const event = currentEvent;
	const title = event.title || "Crypto Event";
	const description = event.description || "";
	const location = event.venue || "";
	const organizer = event.organizer || "";

	// Parse dates
	let startDate, endDate;
	try {
		startDate = event.date_time ? new Date(event.date_time) : null;
		endDate = event.end_time ? new Date(event.end_time) : null;
	} catch (e) {
		alert("Invalid date format. Cannot add to calendar.");
		return;
	}

	if (!startDate) {
		alert("Event date is missing. Cannot add to calendar.");
		return;
	}

	// If no end date, set end date to 1 hour after start
	if (!endDate) {
		endDate = new Date(startDate);
		endDate.setHours(endDate.getHours() + 1);
	}

	// Format dates for iCalendar (YYYYMMDDTHHmmssZ)
	function formatICSDate(date) {
		const year = date.getUTCFullYear();
		const month = String(date.getUTCMonth() + 1).padStart(2, "0");
		const day = String(date.getUTCDate()).padStart(2, "0");
		const hours = String(date.getUTCHours()).padStart(2, "0");
		const minutes = String(date.getUTCMinutes()).padStart(2, "0");
		const seconds = String(date.getUTCSeconds()).padStart(2, "0");
		return `${year}${month}${day}T${hours}${minutes}${seconds}Z`;
	}

	// Format dates for calendar URLs
	function formatURLDate(date) {
		return date.toISOString().replace(/[-:]/g, "").split(".")[0] + "Z";
	}

	const startICS = formatICSDate(startDate);
	const endICS = formatICSDate(endDate);
	const startURL = formatURLDate(startDate);
	const endURL = formatURLDate(endDate);

	// Create .ics file content
	function generateICS() {
		const icsContent = [
			"BEGIN:VCALENDAR",
			"VERSION:2.0",
			"PRODID:-//Crypto Events//EN",
			"CALSCALE:GREGORIAN",
			"METHOD:PUBLISH",
			"BEGIN:VEVENT",
			`UID:${event.external_id || Date.now()}@cryptoevents.com`,
			`DTSTART:${startICS}`,
			`DTEND:${endICS}`,
			`DTSTAMP:${formatICSDate(new Date())}`,
			`SUMMARY:${escapeICS(title)}`,
			description
				? `DESCRIPTION:${escapeICS(description).substring(0, 500)}`
				: "",
			location ? `LOCATION:${escapeICS(location)}` : "",
			organizer ? `ORGANIZER:CN=${escapeICS(organizer)}` : "",
			event.ticket_url ? `URL:${event.ticket_url}` : "",
			"STATUS:CONFIRMED",
			"SEQUENCE:0",
			"BEGIN:VALARM",
			"TRIGGER:-PT1H",
			"ACTION:DISPLAY",
			`DESCRIPTION:Reminder: ${escapeICS(title)}`,
			"END:VALARM",
			"END:VEVENT",
			"END:VCALENDAR",
		]
			.filter((line) => line !== "")
			.join("\r\n");
		return icsContent;
	}

	function escapeICS(text) {
		return text
			.replace(/\\/g, "\\\\")
			.replace(/;/g, "\\;")
			.replace(/,/g, "\\,")
			.replace(/\n/g, "\\n");
	}

	let url = "";

	switch (service) {
		case "google":
			url = `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${encodeURIComponent(title)}&dates=${startURL}/${endURL}&details=${encodeURIComponent(description)}&location=${encodeURIComponent(location)}`;
			window.open(url, "_blank");
			closeCalendarModal();
			break;

		case "outlook":
			url = `https://outlook.live.com/calendar/0/deeplink/compose?subject=${encodeURIComponent(title)}&startdt=${startDate.toISOString()}&enddt=${endDate.toISOString()}&body=${encodeURIComponent(description)}&location=${encodeURIComponent(location)}`;
			window.open(url, "_blank");
			closeCalendarModal();
			break;

		case "apple":
			// Apple Calendar uses .ics file
			const icsContent = generateICS();
			const blob = new Blob([icsContent], {
				type: "text/calendar;charset=utf-8",
			});
			const blobUrl = window.URL.createObjectURL(blob);
			const link = document.createElement("a");
			link.href = blobUrl;
			link.setAttribute("download", `${title.replace(/[^a-z0-9]/gi, "_")}.ics`);
			document.body.appendChild(link);
			link.click();
			document.body.removeChild(link);
			window.URL.revokeObjectURL(blobUrl);
			closeCalendarModal();
			break;

		case "ics":
			// Download .ics file
			const ics = generateICS();
			const icsBlob = new Blob([ics], { type: "text/calendar;charset=utf-8" });
			const icsUrl = window.URL.createObjectURL(icsBlob);
			const icsLink = document.createElement("a");
			icsLink.href = icsUrl;
			icsLink.setAttribute(
				"download",
				`${title.replace(/[^a-z0-9]/gi, "_")}.ics`,
			);
			document.body.appendChild(icsLink);
			icsLink.click();
			document.body.removeChild(icsLink);
			window.URL.revokeObjectURL(icsUrl);
			closeCalendarModal();
			break;
	}
}

function renderPagination() {
	const totalPages = Math.ceil(filteredEvents.length / eventsPerPage);
	const pagination = document.getElementById("pagination");

	if (totalPages <= 1) {
		pagination.innerHTML = "";
		return;
	}

	let html = "";

	html += `<button class="page-btn" ${currentPage === 1 ? "disabled" : ""} onclick="changePage(${currentPage - 1})">
        <i class="fas fa-chevron-left"></i>
    </button>`;

	for (let i = 1; i <= totalPages; i++) {
		if (
			i === 1 ||
			i === totalPages ||
			(i >= currentPage - 1 && i <= currentPage + 1)
		) {
			html += `<button class="page-btn ${i === currentPage ? "active" : ""}" onclick="changePage(${i})">${i}</button>`;
		} else if (i === currentPage - 2 || i === currentPage + 2) {
			html += `<button class="page-btn" disabled>...</button>`;
		}
	}

	html += `<button class="page-btn" ${currentPage === totalPages ? "disabled" : ""} onclick="changePage(${currentPage + 1})">
        <i class="fas fa-chevron-right"></i>
    </button>`;

	pagination.innerHTML = html;
}

function changePage(page) {
	currentPage = page;
	displayEvents();
	window.scrollTo({ top: 0, behavior: "smooth" });
}

function showLoading(show) {
	document.getElementById("loadingSpinner").style.display = show
		? "block"
		: "none";
}

function showNoResults(show) {
	document.getElementById("noResults").style.display = show ? "block" : "none";
}

function escapeHtml(text) {
	const div = document.createElement("div");
	div.textContent = text;
	return div.innerHTML;
}

function debounce(func, wait) {
	let timeout;
	return function executedFunction(...args) {
		const later = () => {
			clearTimeout(timeout);
			func(...args);
		};
		clearTimeout(timeout);
		timeout = setTimeout(later, wait);
	};
}
