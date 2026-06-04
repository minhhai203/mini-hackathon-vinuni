// ==========================================================================
// VINPEARL CLONE - INTERACTION LOGIC
// ==========================================================================

document.addEventListener("DOMContentLoaded", () => {
    
    // --- 1. STICKY HEADER & UTILITY BAR EFFECT ---
    const mainHeader = document.getElementById("mainHeader");
    const topUtilityBar = document.getElementById("topUtilityBar");
    
    window.addEventListener("scroll", () => {
        if (window.scrollY > 50) {
            mainHeader.classList.add("sticky-active");
        } else {
            mainHeader.classList.remove("sticky-active");
        }
    });

    // --- 2. LANGUAGE SELECTOR DROPDOWN ---
    const langDropdownTrigger = document.getElementById("langDropdownTrigger");
    const langDropdownMenu = document.getElementById("langDropdownMenu");
    
    langDropdownTrigger.addEventListener("click", (e) => {
        e.stopPropagation();
        langDropdownMenu.classList.toggle("show");
    });

    // --- 3. MOBILE MENU TOGGLE ---
    const mobileMenuToggleBtn = document.getElementById("mobileMenuToggleBtn");
    const navMenu = document.getElementById("navMenu");
    
    mobileMenuToggleBtn.addEventListener("click", () => {
        mobileMenuToggleBtn.classList.toggle("active");
        navMenu.classList.toggle("show");
    });
    
    // Close mobile menu when clicking nav links
    const navLinks = document.querySelectorAll(".nav-link");
    navLinks.forEach(link => {
        link.addEventListener("click", () => {
            mobileMenuToggleBtn.classList.remove("active");
            navMenu.classList.remove("show");
        });
    });

    // --- 4. HERO SLIDER ---
    const slides = document.querySelectorAll(".slide");
    const dots = document.querySelectorAll(".dot");
    const prevBtn = document.getElementById("slidePrevBtn");
    const nextBtn = document.getElementById("slideNextBtn");
    let currentSlide = 0;
    let slideInterval;
    
    function showSlide(index) {
        slides.forEach(slide => slide.classList.remove("active"));
        dots.forEach(dot => dot.classList.remove("active"));
        
        currentSlide = (index + slides.length) % slides.length;
        
        slides[currentSlide].classList.add("active");
        dots[currentSlide].classList.add("active");
    }
    
    function nextSlide() {
        showSlide(currentSlide + 1);
    }
    
    function prevSlide() {
        showSlide(currentSlide - 1);
    }
    
    function startSlideShow() {
        stopSlideShow();
        slideInterval = setInterval(nextSlide, 5000);
    }
    
    function stopSlideShow() {
        if (slideInterval) clearInterval(slideInterval);
    }
    
    // Slide Button Events
    nextBtn.addEventListener("click", () => {
        nextSlide();
        startSlideShow(); // Reset timer
    });
    
    prevBtn.addEventListener("click", () => {
        prevSlide();
        startSlideShow(); // Reset timer
    });
    
    // Dots click events
    dots.forEach(dot => {
        dot.addEventListener("click", (e) => {
            const index = parseInt(e.target.getAttribute("data-index"));
            showSlide(index);
            startSlideShow(); // Reset timer
        });
    });
    
    // Initialise slider
    startSlideShow();

    // --- 5. BOOKING BAR: TABS LOGIC ---
    const bookingTabBtns = document.querySelectorAll(".booking-tab-btn");
    const inputDestination = document.getElementById("inputDestination");
    const fieldDestinationLabel = document.querySelector("#fieldDestination .field-label");
    
    bookingTabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            bookingTabBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            
            const tabType = btn.getAttribute("data-tab");
            if (tabType === "planner") {
                closeAllDropdowns();
                openPlannerPage();
                return;
            }
            
            // Adjust form values and placeholder depending on tab type
            if (tabType === "hotel") {
                fieldDestinationLabel.innerHTML = `<i class="fa-solid fa-location-dot icon-gold"></i> Điểm đến / Khách sạn`;
                inputDestination.value = "Phú Quốc";
                inputDestination.placeholder = "Chọn điểm đến hoặc khách sạn...";
            } else if (tabType === "ticket") {
                fieldDestinationLabel.innerHTML = `<i class="fa-solid fa-ticket icon-gold"></i> Khu vui chơi giải trí`;
                inputDestination.value = "VinWonders Phú Quốc";
                inputDestination.placeholder = "Chọn khu vui chơi VinWonders...";
            } else if (tabType === "tour") {
                fieldDestinationLabel.innerHTML = `<i class="fa-solid fa-compass icon-gold"></i> Tour & Trải nghiệm`;
                inputDestination.value = "Combo Tour Hòn Khô Nha Trang";
                inputDestination.placeholder = "Chọn tour trải nghiệm...";
            }
        });
    });

    // --- 6. BOOKING BAR: DESTINATION DROPDOWN ---
    const fieldDestination = document.getElementById("fieldDestination");
    const dropdownDestination = document.getElementById("dropdownDestination");
    
    inputDestination.addEventListener("click", (e) => {
        e.stopPropagation();
        closeAllDropdowns();
        dropdownDestination.classList.toggle("show");
    });
    
    const destItems = dropdownDestination.querySelectorAll(".dropdown-list li");
    destItems.forEach(item => {
        item.addEventListener("click", (e) => {
            e.stopPropagation();
            destItems.forEach(i => i.classList.remove("selected"));
            item.classList.add("selected");
            
            inputDestination.value = item.getAttribute("data-value");
            dropdownDestination.classList.remove("show");
        });
    });

    // --- 7. BOOKING BAR: CUSTOM CALENDAR DATE PICKER ---
    const checkInDateDisplay = document.getElementById("checkInDateDisplay");
    const checkOutDateDisplay = document.getElementById("checkOutDateDisplay");
    const datePickerTrigger = document.getElementById("datePickerTrigger");
    const calendarDropdown = document.getElementById("calendarDropdown");
    const calendarGrid = document.getElementById("calendarGrid");
    const calMonthLabel = document.getElementById("calMonthLabel");
    const calPrevBtn = document.getElementById("calPrevBtn");
    const calNextBtn = document.getElementById("calNextBtn");
    const calHint = document.getElementById("calHint");
    const calApplyBtn = document.getElementById("calApplyBtn");

    const MONTHS_VI = ["Tháng 1","Tháng 2","Tháng 3","Tháng 4","Tháng 5","Tháng 6",
                       "Tháng 7","Tháng 8","Tháng 9","Tháng 10","Tháng 11","Tháng 12"];

    const calToday = new Date();
    calToday.setHours(0, 0, 0, 0);

    const calState = {
        viewYear: 2026,
        viewMonth: 5, // June (0-indexed)
        checkIn: new Date(2026, 5, 4),
        checkOut: new Date(2026, 5, 5),
        selecting: null // 'start' | 'end' | null
    };

    function formatCalDate(d) {
        if (!d) return "---";
        const day = String(d.getDate()).padStart(2, '0');
        const month = String(d.getMonth() + 1).padStart(2, '0');
        return `${day} TH${month} ${d.getFullYear()}`;
    }

    function sameDay(a, b) {
        return a && b && a.getFullYear() === b.getFullYear()
            && a.getMonth() === b.getMonth() && a.getDate() === b.getDate();
    }

    function renderCalendar() {
        const { viewYear, viewMonth, checkIn, checkOut } = calState;
        calMonthLabel.textContent = `${MONTHS_VI[viewMonth]} ${viewYear}`;

        const firstDay = new Date(viewYear, viewMonth, 1);
        let startOffset = firstDay.getDay() - 1;
        if (startOffset < 0) startOffset = 6;

        const daysInMonth = new Date(viewYear, viewMonth + 1, 0).getDate();
        calendarGrid.innerHTML = '';

        for (let i = 0; i < startOffset; i++) {
            const empty = document.createElement('button');
            empty.type = 'button';
            empty.className = 'cal-day empty';
            calendarGrid.appendChild(empty);
        }

        for (let d = 1; d <= daysInMonth; d++) {
            const date = new Date(viewYear, viewMonth, d);
            date.setHours(0, 0, 0, 0);
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'cal-day';
            btn.textContent = d;
            btn.dataset.ts = date.getTime();

            if (date < calToday) {
                btn.classList.add('disabled');
            } else {
                if (sameDay(date, calToday)) btn.classList.add('today');
                if (checkIn && sameDay(date, checkIn)) btn.classList.add('selected-start');
                if (checkOut && sameDay(date, checkOut)) btn.classList.add('selected-end');
                if (checkIn && checkOut && date > checkIn && date < checkOut) btn.classList.add('in-range');

                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    onDayClick(new Date(parseInt(btn.dataset.ts)));
                });
            }

            calendarGrid.appendChild(btn);
        }
    }

    function onDayClick(date) {
        if (calState.selecting === 'end' && calState.checkIn && date > calState.checkIn) {
            calState.checkOut = date;
            calState.selecting = null;
            checkOutDateDisplay.textContent = formatCalDate(date);
            calHint.textContent = `Nhận: ${formatCalDate(calState.checkIn)} · Trả: ${formatCalDate(date)}`;
        } else {
            calState.checkIn = date;
            calState.checkOut = null;
            calState.selecting = 'end';
            checkInDateDisplay.textContent = formatCalDate(date);
            checkOutDateDisplay.textContent = '---';
            calHint.textContent = 'Chọn ngày trả phòng';
        }
        renderCalendar();
    }

    datePickerTrigger.addEventListener('click', (e) => {
        e.stopPropagation();
        closeAllDropdowns();
        calState.selecting = 'start';
        calHint.textContent = 'Chọn ngày nhận phòng';
        const isOpen = calendarDropdown.classList.toggle('show');
        if (isOpen) {
            const ref = calState.checkIn || calToday;
            calState.viewYear = ref.getFullYear();
            calState.viewMonth = ref.getMonth();
            renderCalendar();
        }
    });

    calPrevBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        calState.viewMonth--;
        if (calState.viewMonth < 0) { calState.viewMonth = 11; calState.viewYear--; }
        renderCalendar();
    });

    calNextBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        calState.viewMonth++;
        if (calState.viewMonth > 11) { calState.viewMonth = 0; calState.viewYear++; }
        renderCalendar();
    });

    calApplyBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        calendarDropdown.classList.remove('show');
        calState.selecting = null;
        if (calState.checkIn) checkInDateDisplay.textContent = formatCalDate(calState.checkIn);
        if (calState.checkOut) checkOutDateDisplay.textContent = formatCalDate(calState.checkOut);
    });

    calendarDropdown.addEventListener('click', (e) => e.stopPropagation());

    // --- 8. BOOKING BAR: GUESTS DROPDOWN SELECTOR ---
    const inputGuests = document.getElementById("inputGuests");
    const dropdownGuests = document.getElementById("dropdownGuests");
    const fieldGuests = document.getElementById("fieldGuests");
    
    inputGuests.addEventListener("click", (e) => {
        e.stopPropagation();
        closeAllDropdowns();
        dropdownGuests.classList.toggle("show");
    });
    
    // Guests Counters logic
    setupCounter("Rooms", 1, 8);
    setupCounter("Adults", 2, 20);
    setupCounter("Kids", 0, 10);
    
    function setupCounter(idPrefix, minVal, maxVal) {
        const minusBtn = document.getElementById(`btn${idPrefix}Minus`);
        const plusBtn = document.getElementById(`btn${idPrefix}Plus`);
        const valSpan = document.getElementById(`val${idPrefix}`);
        
        minusBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            let val = parseInt(valSpan.textContent);
            if (val > minVal) {
                val--;
                valSpan.textContent = val;
            }
        });
        
        plusBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            let val = parseInt(valSpan.textContent);
            if (val < maxVal) {
                val++;
                valSpan.textContent = val;
            }
        });
    }
    
    const btnApplyGuests = document.getElementById("btnApplyGuests");
    btnApplyGuests.addEventListener("click", (e) => {
        e.stopPropagation();
        const rooms = document.getElementById("valRooms").textContent;
        const adults = document.getElementById("valAdults").textContent;
        const kids = document.getElementById("valKids").textContent;
        
        inputGuests.value = `${adults} người lớn, ${kids} trẻ em, ${rooms} phòng`;
        dropdownGuests.classList.remove("show");
    });

    // Helper to close all dropdowns
    function closeAllDropdowns() {
        langDropdownMenu.classList.remove("show");
        dropdownDestination.classList.remove("show");
        dropdownGuests.classList.remove("show");
        calendarDropdown.classList.remove("show");
    }
    
    // Close dropdowns when clicking outside
    document.addEventListener("click", () => {
        closeAllDropdowns();
    });

    // --- 9. ECOSYSTEM TABS TOGGLING ---
    const expTabBtns = document.querySelectorAll(".exp-tab-btn");
    const expPanels = document.querySelectorAll(".exp-panel");
    
    expTabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            expTabBtns.forEach(b => b.classList.remove("active"));
            expPanels.forEach(p => p.classList.remove("active"));
            
            btn.classList.add("active");
            const expType = btn.getAttribute("data-exp");
            
            // Map data-exp back to id of panel
            const targetPanelId = "expPanel" + expType.charAt(0).toUpperCase() + expType.slice(1);
            document.getElementById(targetPanelId).classList.add("active");
        });
    });

    // --- 10. SCROLL ENTANCE ANIMATION (SCROLL-FADE) ---
    const animatedElements = document.querySelectorAll(".animate-scroll");
    
    const appearanceObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("appeared");
                observer.unobserve(entry.target); // Trigger once
            }
        });
    }, {
        threshold: 0.15
    });
    animatedElements.forEach(element => appearanceObserver.observe(element));

    // --- 11. AI TRIP PLANNER PAGE ---
    const plannerPage = document.getElementById("plannerPage");
    const plannerBackBtn = document.getElementById("plannerBackBtn");
    const plannerCloseBtn = document.getElementById("plannerCloseBtn");
    const plannerClearBtn = document.getElementById("plannerClearBtn");
    const plannerTraceBtn = document.getElementById("plannerTraceBtn");
    const plannerForm = document.getElementById("plannerForm");
    const plannerInput = document.getElementById("plannerInput");
    const plannerMessages = document.getElementById("plannerMessages");
    const plannerGenerateBtn = document.getElementById("plannerGenerateBtn");
    const plannerProgressRing = document.getElementById("plannerProgressRing");
    const plannerProgressText = document.getElementById("plannerProgressText");
    const plannerResultPanel = document.getElementById("plannerResultPanel");
    const plannerResultIcon = document.getElementById("plannerResultIcon");
    const plannerResultTitle = document.getElementById("plannerResultTitle");
    const plannerResultText = document.getElementById("plannerResultText");
    const plannerSteps = document.querySelectorAll(".planner-step");
    const plannerChips = document.querySelectorAll(".planner-chip");
    const destinationAiBtns = document.querySelectorAll(".card-ai-btn");
    const plannerFields = ["destination", "origin", "group", "dates", "priority"];
    const plannerStorageKey = "vinpearl_ai_planner_state_v1";
    const chatStorageKey = "vinpearl_ai_widget_state_v1";
    const defaultPlannerLog = [
        {
            sender: "bot",
            allowHtml: true,
            text: "<p><strong>Đi chơi nhưng chưa biết muốn gì cũng được.</strong></p><p>Mình sẽ hỏi vài điều cơ bản rồi gợi ý điểm đến, chỗ ở và lịch vui chơi hợp với bạn.</p>"
        }
    ];
    const defaultChatLog = [
        {
            sender: "bot",
            allowHtml: true,
            text: "Xin chào! Tôi là Trợ lý Ảo <strong>Vinpearl AI</strong>. Tôi có thể tư vấn các địa điểm du lịch nghỉ dưỡng, khách sạn, vé vui chơi VinWonders tại Phú Quốc, Nha Trang, Đà Nẵng, Hạ Long. Bạn đang lên kế hoạch du lịch ở đâu?"
        }
    ];
    let plannerProfile = {};
    let plannerHistory = [];
    let plannerChatLog = [...defaultPlannerLog];
    let plannerBusy = false;
    let previousCompletedFields = new Set();

    resetStoredChatOnReload();

    plannerBackBtn.addEventListener("click", closePlannerPage);
    plannerCloseBtn.addEventListener("click", closePlannerPage);
    plannerClearBtn.addEventListener("click", clearPlannerHistory);
    plannerTraceBtn.addEventListener("click", () => toggleTraceMode(plannerPage, plannerTraceBtn));

    plannerForm.addEventListener("submit", (event) => {
        event.preventDefault();
        const query = plannerInput.value.trim();
        if (!query) return;
        plannerInput.value = "";
        autoSizeTextInput(plannerInput);
        runPlannerQuery(query);
    });

    plannerInput.addEventListener("input", () => autoSizeTextInput(plannerInput));
    plannerInput.addEventListener("keydown", (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            plannerForm.requestSubmit();
        }
    });

    plannerGenerateBtn.addEventListener("click", () => {
        if (!isPlannerComplete()) return;
        const query = buildPlannerPlanPrompt();
        runPlannerQuery(query);
    });

    plannerChips.forEach(chip => {
        chip.addEventListener("click", () => {
            const query = chip.getAttribute("data-planner-chip");
            runPlannerQuery(query);
        });
    });

    destinationAiBtns.forEach(button => {
        button.addEventListener("click", (event) => {
            event.preventDefault();
            event.stopPropagation();
            const destination = button.getAttribute("data-planner-destination");
            openPlannerPage(destination);
        });
    });

    function openPlannerPage(destination = "") {
        if (destination) {
            plannerProfile.destination = destination;
            appendPlannerMessage(`Mình đang xem ${destination}. Hãy giúp tôi lên lịch đi chơi phù hợp.`, "user");
            appendPlannerMessage(`Đã ghim điểm đến ${destination}. Bạn có thể nói thêm đi mấy người, đi mấy ngày, ngân sách hoặc kiểu chuyến đi bạn thích.`, "bot");
            updatePlannerChecklist();
        }
        plannerPage.classList.add("show");
        plannerPage.setAttribute("aria-hidden", "false");
        document.body.classList.add("planner-open");
        setTimeout(() => plannerInput.focus(), 120);
    }

    function closePlannerPage() {
        plannerPage.classList.remove("show");
        plannerPage.setAttribute("aria-hidden", "true");
        document.body.classList.remove("planner-open");
    }

    async function runPlannerQuery(query) {
        if (plannerBusy) return;
        plannerBusy = true;
        plannerResultPanel.classList.add("planner-loading");
        appendPlannerMessage(query, "user");
        plannerProfile = { ...plannerProfile, ...parsePlannerHints(query) };
        updatePlannerChecklist();
        appendPlannerTyping();

        try {
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    message: query,
                    profile: plannerProfile,
                    history: plannerHistory.slice(-8)
                })
            });

            if (!response.ok) {
                throw new Error(`Planner API error: ${response.status}`);
            }

            const data = await response.json();
            plannerProfile = { ...plannerProfile, ...(data.profile || {}) };
            plannerHistory.push({ role: "user", content: query });
            plannerHistory.push({ role: "assistant", content: data.reply || "" });
            removePlannerTyping();
            appendPlannerMessage(data.reply || "Mình đã ghi nhận. Bạn nói thêm một chút để mình chốt lịch nhé.", "bot", true);
            renderPlannerCards(data.cards || []);
            updatePlannerChecklist();
            savePlannerState();
        } catch (error) {
            removePlannerTyping();
            appendPlannerMessage("Hiện planner chưa kết nối được backend. Bạn kiểm tra FastAPI rồi thử lại nhé.", "bot");
        } finally {
            plannerBusy = false;
            plannerResultPanel.classList.remove("planner-loading");
        }
    }

    function buildPlannerPrompt() {
        const missing = plannerFields.filter(field => !plannerProfile[field]);
        if (missing.length) {
            return "Tôi còn mơ hồ, hãy hỏi ngắn để làm rõ chuyến đi Vinpearl phù hợp nhất cho tôi.";
        }
        return [
            `Tư vấn lịch đi chơi Vinpearl cho tôi.`,
            `Điểm đến: ${plannerProfile.destination}.`,
            plannerProfile.origin ? `Xuất phát: ${plannerProfile.origin}.` : "",
            plannerProfile.group ? `Nhóm đi: ${plannerProfile.group}.` : "",
            plannerProfile.dates ? `Thời gian: ${plannerProfile.dates}.` : "",
            plannerProfile.budget ? `Ngân sách: ${plannerProfile.budget}.` : "",
            plannerProfile.priority ? `Ưu tiên: ${plannerProfile.priority}.` : ""
        ].filter(Boolean).join(" ");
    }

    function buildPlannerPlanPrompt() {
        return [
            "Tôi đã chuẩn bị đủ thông tin. Hãy thiết kế một plan đi chơi Vinpearl cá nhân hóa, dễ đọc, ưu tiên phương án phù hợp nhất trước rồi mới đưa lựa chọn dự phòng.",
            `Điểm đến: ${plannerProfile.destination}.`,
            `Xuất phát: ${plannerProfile.origin}.`,
            `Nhóm đi: ${plannerProfile.group}.`,
            `Thời gian: ${plannerProfile.dates}.`,
            plannerProfile.budget ? `Ngân sách: ${plannerProfile.budget}.` : "",
            `Ưu tiên: ${plannerProfile.priority}.`,
            "Trả lời bằng tiếng Việt thân thiện, có lịch trình gợi ý theo buổi, lưu ý thời tiết nếu có, và không làm người dùng bị rối vì quá nhiều lựa chọn."
        ].filter(Boolean).join(" ");
    }

    function parsePlannerHints(text) {
        const normalized = normalizeForMatch(text);
        const updates = {};
        const destinations = [
            ["Phú Quốc", ["phu quoc", "phú quốc"]],
            ["Nha Trang", ["nha trang"]],
            ["Hạ Long", ["ha long", "hạ long"]],
            ["Nam Hội An", ["nam hoi an", "nam hội an", "hoi an", "hội an", "da nang", "đà nẵng"]]
        ];
        const origins = [
            ["Hà Nội", ["ha noi", "hà nội"]],
            ["TP. Hồ Chí Minh", ["ho chi minh", "hồ chí minh", "sai gon", "sài gòn", "tphcm"]],
            ["Đà Nẵng", ["da nang", "đà nẵng"]]
        ];
        const priorities = [
            ["vui chơi cho trẻ em", ["tre em", "trẻ em", "vinwonders", "safari", "vui choi", "vui chơi"]],
            ["nghỉ biển", ["bien", "biển", "beach", "bai bien", "bãi biển"]],
            ["spa và nghỉ dưỡng nhẹ", ["spa", "nghi duong", "nghỉ dưỡng", "chill", "lich nhe", "lịch nhẹ"]],
            ["ẩm thực và lịch nhẹ", ["am thuc", "ẩm thực", "an uong", "ăn uống", "nha hang", "nhà hàng"]],
            ["tham quan và khám phá", ["tham quan", "kham pha", "khám phá", "di chuyen", "di chuyển", "trai nghiem", "trải nghiệm"]],
            ["tiết kiệm chi phí", ["gia re", "giá rẻ", "tiet kiem", "tiết kiệm", "budget thap", "budget thấp"]]
        ];

        const destinationMatch = destinations.find(([, aliases]) => aliases.some(alias => normalized.includes(normalizeForMatch(alias))));
        if (destinationMatch) updates.destination = destinationMatch[0];

        const originMatch = origins.find(([, aliases]) => aliases.some(alias => normalized.includes(normalizeForMatch(alias))));
        if (originMatch) updates.origin = originMatch[0];

        if (/(người|nguoi|bé|be|trẻ em|tre em|gia đình|gia dinh|cặp đôi|cap doi|người yêu|nguoi yeu|couple|bạn bè|ban be)/i.test(text)) {
            updates.group = text;
        }
        if (/(ngày|ngay|đêm|dem|tuần|tuan|tháng|thang|2026|2027)/i.test(text)) {
            updates.dates = text;
        }
        if (/(triệu|trieu|budget|ngân sách|ngan sach|vnd|vnđ|đồng)/i.test(text)) {
            updates.budget = text;
        }

        const priorityMatches = priorities
            .filter(([, aliases]) => aliases.some(alias => normalized.includes(normalizeForMatch(alias))))
            .map(([priority]) => priority);
        if (priorityMatches.length) {
            updates.priority = [...new Set(priorityMatches)].join(", ");
        }
        return updates;
    }

    function updatePlannerChecklist() {
        const completedFields = plannerFields.filter(field => Boolean(plannerProfile[field]));
        const completed = completedFields.length;
        plannerProgressRing.textContent = `${completed}/5`;
        plannerProgressText.textContent = `${completed} of 5 captured`;
        plannerSteps.forEach(step => {
            const field = step.getAttribute("data-field");
            const description = step.querySelector("p");
            if (plannerProfile[field]) {
                step.classList.add("completed");
                if (!previousCompletedFields.has(field)) {
                    step.classList.add("just-completed");
                    plannerProgressRing.classList.remove("progress-bump");
                    void plannerProgressRing.offsetWidth;
                    plannerProgressRing.classList.add("progress-bump");
                    window.setTimeout(() => step.classList.remove("just-completed"), 760);
                }
                description.textContent = plannerProfile[field];
            } else {
                step.classList.remove("completed", "just-completed");
                description.textContent = getPlannerPlaceholder(field);
            }
        });
        previousCompletedFields = new Set(completedFields);
        updatePlannerResultPanel(completed);
    }

    function isPlannerComplete() {
        return plannerFields.every(field => Boolean(plannerProfile[field]));
    }

    function updatePlannerResultPanel(completed) {
        const missingCount = plannerFields.length - completed;
        const ready = missingCount === 0;
        plannerResultPanel.classList.toggle("planner-result-ready", ready);
        plannerResultPanel.classList.toggle("planner-result-locked", !ready);
        plannerGenerateBtn.hidden = !ready;
        plannerGenerateBtn.disabled = !ready;

        if (ready) {
            plannerResultIcon.innerHTML = '<i class="fa-solid fa-circle-check"></i>';
            plannerResultTitle.textContent = "Đủ đồ nghề rồi, chuyến này bắt đầu ra dáng";
            plannerResultText.textContent = "Bạn đã chuẩn bị đủ thông tin để mình thiết kế plan đi chơi riêng cho bạn.";
            return;
        }

        plannerResultIcon.innerHTML = '<i class="fa-solid fa-list-check"></i>';
        plannerResultTitle.textContent = missingCount === 1 ? "Sắp xong rồi, còn một ý nhỏ" : `Mình hỏi thêm ${missingCount} ý nữa nhé`;
        plannerResultText.textContent = "Bạn cứ nhắn như đang kể chuyến đi mong muốn. Càng rõ gu, mình càng dễ chốt plan hợp bạn.";
    }

    function getPlannerPlaceholder(field) {
        const placeholders = {
            destination: "Mình sẽ gợi ý nếu bạn chưa có điểm đến",
            origin: "Để ước lượng độ tiện di chuyển",
            group: "Gia đình, cặp đôi, bạn bè hay công ty",
            dates: "Ngày cụ thể hoặc số đêm dự kiến",
            priority: "Vui chơi, nghỉ biển, spa, ăn uống hay lịch nhẹ"
        };
        return placeholders[field] || "Cho mình thêm một chút thông tin";
    }

    function appendPlannerMessage(text, sender, allowHtml = false, persist = true) {
        const message = document.createElement("div");
        message.className = `planner-msg ${sender === "user" ? "planner-user-msg" : "planner-bot-msg"}`;
        if (allowHtml) {
            message.innerHTML = text;
        } else {
            message.textContent = text;
        }
        plannerMessages.appendChild(message);
        plannerMessages.scrollTop = plannerMessages.scrollHeight;
        if (persist) {
            plannerChatLog.push({ text, sender, allowHtml });
            savePlannerState();
        }
    }

    function appendPlannerTyping() {
        const typing = document.createElement("div");
        typing.className = "planner-msg planner-bot-msg";
        typing.id = "plannerTyping";
        typing.textContent = "AI đang ghép nhu cầu với dữ liệu Vinpearl...";
        plannerMessages.appendChild(typing);
        plannerMessages.scrollTop = plannerMessages.scrollHeight;
    }

    function removePlannerTyping() {
        const typing = document.getElementById("plannerTyping");
        if (typing) typing.remove();
    }

    function renderPlannerLog() {
        plannerMessages.innerHTML = "";
        plannerChatLog.forEach(message => appendPlannerMessage(message.text, message.sender, message.allowHtml, false));
    }

    function savePlannerState() {
        writeBrowserState(plannerStorageKey, {
            profile: plannerProfile,
            history: plannerHistory,
            messages: plannerChatLog
        });
    }

    function restorePlannerState() {
        const saved = readBrowserState(plannerStorageKey);
        if (!saved) {
            plannerProfile = {};
            plannerHistory = [];
            previousCompletedFields = new Set();
            plannerChatLog = [...defaultPlannerLog];
            renderPlannerLog();
            updatePlannerChecklist();
            return;
        }
        plannerProfile = saved.profile || {};
        plannerHistory = Array.isArray(saved.history) ? saved.history : [];
        previousCompletedFields = new Set(plannerFields.filter(field => Boolean(plannerProfile[field])));
        plannerChatLog = Array.isArray(saved.messages) && saved.messages.length ? saved.messages : [...defaultPlannerLog];
        renderPlannerLog();
        updatePlannerChecklist();
    }

    function clearPlannerHistory() {
        plannerProfile = {};
        plannerHistory = [];
        previousCompletedFields = new Set();
        plannerChatLog = [...defaultPlannerLog];
        removeBrowserState(plannerStorageKey);
        renderPlannerLog();
        renderPlannerCards([]);
        updatePlannerChecklist();
    }

    function renderPlannerCards(cards) {
        plannerResultPanel.querySelectorAll(".planner-result-card").forEach(card => card.remove());
        // Recommendations are rendered inside the chat answer; the board stays focused on trip readiness.
    }

    function normalizeForMatch(text) {
        return String(text || "")
            .toLowerCase()
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .replace(/đ/g, "d");
    }

    function escapeHtml(text) {
        const div = document.createElement("div");
        div.textContent = String(text || "");
        return div.innerHTML;
    }
    
    // --- 12. AI CHATBOT LOGIC ---
    const chatbotTriggerBtn = document.getElementById("chatbotTriggerBtn");
    const chatWindow = document.getElementById("chatWindow");
    const chatCloseBtn = document.getElementById("chatCloseBtn");
    const chatClearBtn = document.getElementById("chatClearBtn");
    const chatTraceBtn = document.getElementById("chatTraceBtn");
    const chatForm = document.getElementById("chatForm");
    const chatInput = document.getElementById("chatInput");
    const chatMessages = document.getElementById("chatMessages");
    const chatBody = document.getElementById("chatBody");
    const typingIndicator = document.getElementById("typingIndicator");
    const suggestBtns = document.querySelectorAll(".suggest-btn");
    const chatbotIconOpen = chatbotTriggerBtn.querySelector(".chatbot-icon-open");
    const chatbotIconClose = chatbotTriggerBtn.querySelector(".chatbot-icon-close");
    let chatProfile = {};
    let chatHistory = [];
    let chatLog = [...defaultChatLog];

    // Toggle Chat Window
    chatbotTriggerBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        chatWindow.classList.toggle("show");
        const isOpen = chatWindow.classList.contains("show");
        
        if (isOpen) {
            chatbotIconOpen.style.display = "none";
            chatbotIconClose.style.display = "block";
            chatInput.focus();
            scrollChatToBottom();
        } else {
            chatbotIconOpen.style.display = "block";
            chatbotIconClose.style.display = "none";
        }
    });

    chatCloseBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        chatWindow.classList.remove("show");
        chatbotIconOpen.style.display = "block";
        chatbotIconClose.style.display = "none";
    });

    chatClearBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        clearChatHistory();
    });

    chatTraceBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        toggleTraceMode(chatWindow, chatTraceBtn);
    });

    // Close chat if clicked outside chat window (excluding trigger button)
    document.addEventListener("click", (e) => {
        if (!chatWindow.contains(e.target) && !chatbotTriggerBtn.contains(e.target)) {
            chatWindow.classList.remove("show");
            chatbotIconOpen.style.display = "block";
            chatbotIconClose.style.display = "none";
        }
    });

    // Prevent closing when clicking inside chat window
    chatWindow.addEventListener("click", (e) => {
        e.stopPropagation();
    });

    // Scroll chat to bottom
    function scrollChatToBottom() {
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    function autoSizeTextInput(input) {
        input.style.height = "auto";
        input.style.height = `${Math.min(input.scrollHeight, 118)}px`;
    }

    // Handle Form Submit
    chatForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const query = chatInput.value.trim();
        if (!query) return;

        appendMessage(query, "user");
        chatInput.value = "";
        autoSizeTextInput(chatInput);

        handleBotResponse(query);
    });

    chatInput.addEventListener("input", () => autoSizeTextInput(chatInput));
    chatInput.addEventListener("keydown", (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            chatForm.requestSubmit();
        }
    });

    // Handle Suggestion Buttons
    suggestBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const query = btn.getAttribute("data-query");
            appendMessage(query, "user");
            handleBotResponse(query);
        });
    });

    // Append Message to UI
    function appendMessage(text, sender, allowHtml = false, persist = true) {
        const msgDiv = document.createElement("div");
        msgDiv.classList.add("message", sender === "user" ? "user-msg" : "bot-msg");
        const bubble = document.createElement("div");
        bubble.classList.add("msg-bubble");
        if (allowHtml) {
            bubble.innerHTML = text;
        } else {
            bubble.textContent = text;
        }
        msgDiv.appendChild(bubble);
        chatMessages.appendChild(msgDiv);
        scrollChatToBottom();
        if (persist) {
            chatLog.push({ text, sender, allowHtml });
            saveChatState();
        }
    }

    async function handleBotResponse(query) {
        typingIndicator.classList.add("active");
        scrollChatToBottom();

        try {
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    message: query,
                    profile: chatProfile,
                    history: chatHistory.slice(-8)
                })
            });

            if (!response.ok) {
                throw new Error(`Chat API error: ${response.status}`);
            }

            const data = await response.json();
            chatProfile = data.profile || {};
            chatHistory.push({ role: "user", content: query });
            chatHistory.push({ role: "assistant", content: data.reply });
            typingIndicator.classList.remove("active");
            applyChatTheme(data.ui_theme);
            appendMessage(data.reply, "bot", true);
            updateQuickSuggestions(data.suggestions || []);
            saveChatState();
        } catch (error) {
            typingIndicator.classList.remove("active");
            appendMessage(
                "Xin lỗi, hiện trợ lý AI chưa kết nối được backend. Bạn thử chạy lại server hoặc gửi lại câu hỏi sau nhé.",
                "bot"
            );
        }
    }

    function renderChatLog() {
        chatMessages.innerHTML = "";
        chatLog.forEach(message => appendMessage(message.text, message.sender, message.allowHtml, false));
        scrollChatToBottom();
    }

    function saveChatState() {
        writeBrowserState(chatStorageKey, {
            profile: chatProfile,
            history: chatHistory,
            messages: chatLog
        });
    }

    function restoreChatState() {
        const saved = readBrowserState(chatStorageKey);
        if (!saved) {
            chatLog = [...defaultChatLog];
            renderChatLog();
            return;
        }
        chatProfile = saved.profile || {};
        chatHistory = Array.isArray(saved.history) ? saved.history : [];
        chatLog = Array.isArray(saved.messages) && saved.messages.length ? saved.messages : [...defaultChatLog];
        renderChatLog();
    }

    function clearChatHistory() {
        chatProfile = {};
        chatHistory = [];
        chatLog = [...defaultChatLog];
        removeBrowserState(chatStorageKey);
        renderChatLog();
        updateQuickSuggestions(["Tư vấn Phú Quốc", "Tư vấn Nha Trang", "So sánh các điểm đến Vinpearl"]);
    }

    function readBrowserState(key) {
        try {
            return JSON.parse(localStorage.getItem(key) || "null");
        } catch (error) {
            removeBrowserState(key);
            return null;
        }
    }

    function writeBrowserState(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
            // Storage can be disabled in private mode; the chat still works in memory.
        }
    }

    function removeBrowserState(key) {
        try {
            localStorage.removeItem(key);
        } catch (error) {
            // Storage can be disabled in private mode.
        }
    }

    function resetStoredChatOnReload() {
        const navigationEntry = performance.getEntriesByType("navigation")[0];
        const isReload = navigationEntry ? navigationEntry.type === "reload" : performance.navigation?.type === 1;
        if (isReload) {
            removeBrowserState(plannerStorageKey);
            removeBrowserState(chatStorageKey);
        }
    }

    function updateQuickSuggestions(suggestions) {
        if (!suggestions.length) return;
        suggestBtns.forEach((btn, index) => {
            if (suggestions[index]) {
                btn.textContent = suggestions[index];
                btn.setAttribute("data-query", suggestions[index]);
            }
        });
    }

    function applyChatTheme(themeName) {
        const themes = ["theme-default", "theme-beach", "theme-sea", "theme-bay", "theme-heritage"];
        chatWindow.classList.remove(...themes);
        chatWindow.classList.add(themes.includes(themeName) ? themeName : "theme-default");
    }

    function toggleTraceMode(container, button) {
        const enabled = container.classList.toggle("trace-mode");
        button.classList.toggle("active", enabled);
        button.setAttribute("aria-label", enabled ? "Tắt trace mode" : "Bật trace mode");
        button.setAttribute("title", enabled ? "Trace mode đang bật" : "Trace mode");
    }

    // --- 13. BOOKING SEARCH RESULTS PAGE ---
    const resultsPage         = document.getElementById("resultsPage");
    const resultsBackBtn      = document.getElementById("resultsBackBtn");
    const resultsModifyBtn    = document.getElementById("resultsModifyBtn");
    const resultsGrid         = document.getElementById("resultsGrid");
    const resultsEmpty        = document.getElementById("resultsEmpty");
    const resultsResetBtn     = document.getElementById("resultsResetBtn");
    const resultsTitleEl      = document.getElementById("resultsTitle");
    const resultsSubtitleEl   = document.getElementById("resultsSubtitle");
    const resultsSummaryDest  = document.getElementById("resultsSummaryDest");
    const resultsSummaryDates = document.getElementById("resultsSummaryDates");
    const resultsSummaryGuests= document.getElementById("resultsSummaryGuests");
    const amenityFilterChips  = document.querySelectorAll(".results-amenity-chip");

    // Destination input value → JSON destination key
    const DEST_INPUT_TO_KEY = {
        "Phú Quốc":                        ["Phu Quoc"],
        "Nha Trang":                        ["Nha Trang"],
        "Đà Nẵng - Hội An":                ["Nam Hoi An"],
        "Hạ Long":                          ["Ha Long"],
        "Hải Phòng":                        [],
        "VinWonders Phú Quốc":             ["Phu Quoc"],
        "Combo Tour Hòn Khô Nha Trang":    ["Nha Trang"],
    };

    // Tab → categories to include
    const TAB_CATEGORY_MAP = {
        "hotel":  ["hotel"],
        "ticket": ["experience"],
        "tour":   ["experience"],
        "planner":["hotel", "experience"],
    };

    // Extra filter for ticket tab (must have theme_park or kids)
    function tabFilter(item, tab) {
        if (tab === "ticket") {
            return (item.amenities || []).some(a => ["theme_park", "kids"].includes(a));
        }
        return true;
    }

    const TAB_TITLE_MAP = {
        "hotel":  "Khách sạn & Resort",
        "ticket": "Vé vui chơi VinWonders",
        "tour":   "Tour & Trải nghiệm",
        "planner":"Gợi ý Vinpearl",
    };

    let resultsAllItems = [];   // full filtered list (no amenity filter)
    let activeAmenityFilter = "all";

    // Hook the booking form submit button
    document.getElementById("formHotel").addEventListener("submit", handleBookingSearch);

    async function handleBookingSearch(e) {
        e.preventDefault();

        const destination = document.getElementById("inputDestination").value.trim();
        const checkIn     = document.getElementById("checkInDateDisplay").textContent.trim();
        const checkOut    = document.getElementById("checkOutDateDisplay").textContent.trim();
        const guests      = document.getElementById("inputGuests").value.trim();
        const activeTab   = document.querySelector(".booking-tab-btn.active")?.getAttribute("data-tab") || "hotel";

        // Update top-bar summary
        resultsSummaryDest.textContent  = destination || "Tất cả điểm đến";
        resultsSummaryDates.textContent = `${checkIn} → ${checkOut}`;
        resultsSummaryGuests.textContent = guests;

        // Load + filter data
        const items = await loadSearchData();

        const destKeys = DEST_INPUT_TO_KEY[destination] ?? null; // null = no dest filter
        const allowedCats = TAB_CATEGORY_MAP[activeTab] || ["hotel"];

        resultsAllItems = items.filter(item => {
            if (item.category === "homepage") return false;
            if (!allowedCats.includes(item.category)) return false;
            if (!tabFilter(item, activeTab)) return false;
            if (destKeys !== null && destKeys.length > 0) {
                const itemDests = item.destinations || [];
                if (!itemDests.some(d => destKeys.includes(d))) return false;
            }
            return true;
        });

        // Reset amenity filter
        activeAmenityFilter = "all";
        amenityFilterChips.forEach(c => c.classList.toggle("active", c.getAttribute("data-amenity") === "all"));

        // Build section title
        const destLabel = destination || "Tất cả điểm đến";
        resultsTitleEl.textContent = TAB_TITLE_MAP[activeTab] || "Kết quả tìm kiếm";
        resultsSubtitleEl.textContent = `${destLabel} · ${resultsAllItems.length} kết quả`;

        renderResultCards(resultsAllItems);
        openResultsPage();
    }

    function applyAmenityFilter(amenity) {
        activeAmenityFilter = amenity;
        let filtered = resultsAllItems;
        if (amenity !== "all") {
            filtered = resultsAllItems.filter(item => (item.amenities || []).includes(amenity));
        }
        resultsSubtitleEl.textContent = resultsSubtitleEl.textContent.replace(/·.*kết quả/, `· ${filtered.length} kết quả`);
        renderResultCards(filtered);
    }

    amenityFilterChips.forEach(chip => {
        chip.addEventListener("click", () => {
            amenityFilterChips.forEach(c => c.classList.remove("active"));
            chip.classList.add("active");
            applyAmenityFilter(chip.getAttribute("data-amenity"));
        });
    });

    function renderResultCards(items) {
        resultsGrid.innerHTML = "";

        if (items.length === 0) {
            resultsEmpty.style.display = "";
            resultsGrid.style.display = "none";
            return;
        }

        resultsEmpty.style.display = "none";
        resultsGrid.style.display = "";

        const AMENITY_ICONS = {
            "spa":        '<i class="fa-solid fa-spa"></i>',
            "pool":       '<i class="fa-solid fa-water-ladder"></i>',
            "beach":      '<i class="fa-solid fa-umbrella-beach"></i>',
            "restaurant": '<i class="fa-solid fa-utensils"></i>',
            "kids":       '<i class="fa-solid fa-children"></i>',
            "golf":       '<i class="fa-solid fa-golf-ball-tee"></i>',
            "villa":      '<i class="fa-solid fa-house"></i>',
            "theme_park": '<i class="fa-solid fa-ferris-wheel"></i>',
        };

        resultsGrid.innerHTML = items.map(item => {
            const imgUrl    = item.image_url || "assets/hero-1.png";
            const catLabel  = CAT_LABELS[item.category] || item.category;
            const destLabel = (item.destinations || []).map(d => DEST_LABELS[d] || d).join(", ");
            const isGold    = item.category === "offer";
            const confHigh  = item.confidence === "high";

            const amenityTags = (item.amenities || []).slice(0, 4).map(a =>
                `<span class="result-amenity-tag">${AMENITY_ICONS[a] || ""} ${escapeHtml(AMENITY_VI[a] || a)}</span>`
            ).join("");

            return `
            <div class="result-card animate-scroll">
                <div class="result-card-image" style="background-image:url('${escapeHtml(imgUrl)}')">
                    <span class="result-card-category-badge ${isGold ? "badge-gold" : ""}">${escapeHtml(catLabel)}</span>
                </div>
                <div class="result-card-content">
                    ${destLabel ? `<div class="result-card-dest"><i class="fa-solid fa-location-dot"></i> ${escapeHtml(destLabel)}</div>` : ""}
                    <div class="result-card-name">${escapeHtml(item.name || "")}</div>
                    <div class="result-card-amenities">${amenityTags}</div>
                    <div class="result-card-summary">${escapeHtml(item.summary || "")}</div>
                    <div class="result-card-footer">
                        <span class="result-card-confidence ${confHigh ? "high" : ""}">
                            ${confHigh ? '<i class="fa-solid fa-circle-check"></i> Xác nhận chính thức' : '<i class="fa-regular fa-clock"></i> Cần xác nhận'}
                        </span>
                        <a class="result-card-cta" href="${escapeHtml(item.url || "#")}" target="_blank" rel="noopener">
                            Xem chi tiết <i class="fa-solid fa-arrow-right"></i>
                        </a>
                    </div>
                </div>
            </div>`;
        }).join("");

        // Trigger scroll animations for newly added cards
        document.querySelectorAll("#resultsGrid .animate-scroll").forEach(el => {
            appearanceObserver.observe(el);
        });
    }

    function openResultsPage() {
        resultsPage.classList.add("show");
        resultsPage.setAttribute("aria-hidden", "false");
        document.body.classList.add("planner-open"); // reuse overflow lock
        resultsPage.querySelector(".results-body").scrollTop = 0;
    }

    function closeResultsPage() {
        resultsPage.classList.remove("show");
        resultsPage.setAttribute("aria-hidden", "true");
        document.body.classList.remove("planner-open");
    }

    resultsBackBtn.addEventListener("click", closeResultsPage);

    resultsModifyBtn.addEventListener("click", () => {
        closeResultsPage();
        setTimeout(() => document.getElementById("booking-section").scrollIntoView({ behavior: "smooth" }), 320);
    });

    resultsResetBtn.addEventListener("click", () => {
        activeAmenityFilter = "all";
        amenityFilterChips.forEach(c => c.classList.toggle("active", c.getAttribute("data-amenity") === "all"));
        renderResultCards(resultsAllItems);
    });

    // --- 14. SEARCH MODAL ---
    const searchOverlay     = document.getElementById("searchOverlay");
    const searchModalInput  = document.getElementById("searchModalInput");
    const searchClearBtn    = document.getElementById("searchClearBtn");
    const searchCloseBtn    = document.getElementById("searchCloseBtn");
    const searchFilterChips = document.querySelectorAll(".search-filter-chip");
    const searchEmptyState  = document.getElementById("searchEmptyState");
    const searchResultsWrapper = document.getElementById("searchResultsWrapper");
    const searchResultsGrid = document.getElementById("searchResultsGrid");
    const searchResultCount = document.getElementById("searchResultCount");
    const searchNoResults   = document.getElementById("searchNoResults");
    const searchNoResultsQuery = document.getElementById("searchNoResultsQuery");
    const searchQuickTags   = document.querySelectorAll(".search-quick-tag");

    let searchData = null;
    let activeFilter = "all";

    const DEST_LABELS = {
        "Phu Quoc":  "Phú Quốc",
        "Nha Trang": "Nha Trang",
        "Ha Long":   "Hạ Long",
        "Nam Hoi An":"Nam Hội An",
        "Bac Ninh":  "Bắc Ninh",
        "Ha Tinh":   "Hà Tĩnh",
        "Nghe An":   "Nghệ An",
    };

    const CAT_LABELS = {
        "hotel":      "Khách sạn",
        "experience": "Trải nghiệm",
        "offer":      "Ưu đãi",
        "news":       "Tin tức",
        "homepage":   "Trang chủ",
    };

    const AMENITY_VI = {
        "spa":        "Spa",
        "pool":       "Hồ bơi",
        "beach":      "Bãi biển",
        "restaurant": "Ẩm thực",
        "kids":       "Gia đình",
        "golf":       "Golf",
        "villa":      "Biệt thự",
        "theme_park": "VinWonders",
    };

    const BEST_FOR_VI = {
        "family_with_children":    "Gia đình có bé",
        "beach_holiday":           "Nghỉ biển",
        "relaxed_couple_or_family":"Nghỉ dưỡng nhẹ",
        "short_trip_from_hanoi":   "Gần Hà Nội",
        "premium_or_private_stay": "Cao cấp / Riêng tư",
        "golf_trip":               "Golf",
        "business_or_short_trip":  "Công tác",
        "budget_friendly_stay":    "Tiết kiệm",
        "city_beach_stay":         "Biển phố thị",
        "culture_light_activity":  "Văn hóa",
        "deal_hunter":             "Săn ưu đãi",
        "inspiration":             "Cảm hứng du lịch",
    };

    async function loadSearchData() {
        if (searchData) return searchData;
        try {
            const res = await fetch("search-data.json");
            searchData = await res.json();
        } catch {
            searchData = [];
        }
        return searchData;
    }

    function openSearchModal() {
        searchOverlay.classList.add("show");
        searchOverlay.setAttribute("aria-hidden", "false");
        document.body.style.overflow = "hidden";
        setTimeout(() => searchModalInput.focus(), 80);
        loadSearchData();
    }

    function closeSearchModal() {
        searchOverlay.classList.remove("show");
        searchOverlay.setAttribute("aria-hidden", "true");
        document.body.style.overflow = "";
        searchModalInput.value = "";
        searchClearBtn.style.display = "none";
        resetSearchView();
    }

    function resetSearchView() {
        searchEmptyState.style.display = "";
        searchResultsWrapper.style.display = "none";
        searchNoResults.style.display = "none";
    }

    document.getElementById("searchTriggerBtn").addEventListener("click", openSearchModal);
    searchCloseBtn.addEventListener("click", closeSearchModal);
    searchOverlay.addEventListener("click", (e) => {
        if (e.target === searchOverlay) closeSearchModal();
    });
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && searchOverlay.classList.contains("show")) closeSearchModal();
    });

    searchFilterChips.forEach(chip => {
        chip.addEventListener("click", () => {
            searchFilterChips.forEach(c => c.classList.remove("active"));
            chip.classList.add("active");
            activeFilter = chip.getAttribute("data-filter");
            const query = searchModalInput.value.trim();
            if (query) runSearch(query);
        });
    });

    searchQuickTags.forEach(tag => {
        tag.addEventListener("click", () => {
            const query = tag.getAttribute("data-query");
            searchModalInput.value = query;
            searchClearBtn.style.display = "flex";
            runSearch(query);
        });
    });

    searchModalInput.addEventListener("input", () => {
        const query = searchModalInput.value;
        searchClearBtn.style.display = query ? "flex" : "none";
        if (query.trim()) {
            runSearch(query.trim());
        } else {
            resetSearchView();
        }
    });

    searchClearBtn.addEventListener("click", () => {
        searchModalInput.value = "";
        searchClearBtn.style.display = "none";
        resetSearchView();
        searchModalInput.focus();
    });

    async function runSearch(query) {
        const items = await loadSearchData();
        const norm = normalizeForMatch(query);

        const filtered = items.filter(item => {
            if (item.category === "homepage") return false;
            if (activeFilter !== "all" && item.category !== activeFilter) return false;

            const name    = normalizeForMatch(item.name || "");
            const summary = normalizeForMatch(item.summary || "");
            const dests   = (item.destinations || []).map(d => normalizeForMatch(DEST_LABELS[d] || d)).join(" ");
            const amenities = (item.amenities || []).map(a => normalizeForMatch(AMENITY_VI[a] || a)).join(" ");
            const bestFor = (item.best_for || []).map(b => normalizeForMatch(BEST_FOR_VI[b] || b)).join(" ");
            const category = normalizeForMatch(CAT_LABELS[item.category] || item.category || "");

            const haystack = [name, summary, dests, amenities, bestFor, category].join(" ");
            return norm.split(/\s+/).every(word => haystack.includes(word));
        });

        renderSearchResults(filtered, query);
    }

    function renderSearchResults(items, query) {
        if (items.length === 0) {
            searchEmptyState.style.display = "none";
            searchResultsWrapper.style.display = "none";
            searchNoResults.style.display = "";
            searchNoResultsQuery.textContent = query;
            return;
        }

        searchEmptyState.style.display = "none";
        searchNoResults.style.display = "none";
        searchResultsWrapper.style.display = "";

        searchResultCount.textContent = `Tìm thấy ${items.length} kết quả`;

        searchResultsGrid.innerHTML = items.map(item => {
            const imgUrl = item.image_url || "assets/hero-1.png";
            const catLabel = CAT_LABELS[item.category] || item.category;
            const destLabels = (item.destinations || []).map(d => DEST_LABELS[d] || d).join(", ");
            const amenityBadges = (item.amenities || []).slice(0, 3)
                .map(a => `<span class="search-result-badge">${escapeHtml(AMENITY_VI[a] || a)}</span>`)
                .join("");

            return `
                <a class="search-result-card" href="${escapeHtml(item.url || '#')}" target="_blank" rel="noopener">
                    <div class="search-result-thumb" style="background-image:url('${escapeHtml(imgUrl)}')"></div>
                    <div class="search-result-info">
                        <div class="search-result-name">${escapeHtml(item.name || "")}</div>
                        <div class="search-result-summary">${escapeHtml(item.summary || "")}</div>
                        <div class="search-result-badges">
                            <span class="search-result-badge badge-category">${escapeHtml(catLabel)}</span>
                            ${destLabels ? `<span class="search-result-badge badge-dest"><i class="fa-solid fa-location-dot"></i> ${escapeHtml(destLabels)}</span>` : ""}
                            ${amenityBadges}
                        </div>
                    </div>
                    <i class="fa-solid fa-arrow-right search-result-arrow"></i>
                </a>`;
        }).join("");
    }
    restorePlannerState();
    restoreChatState();
});
