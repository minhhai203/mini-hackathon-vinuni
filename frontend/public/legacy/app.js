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

    // --- 7. BOOKING BAR: DATE IN/OUT SYNC ---
    const dateDisplay = document.getElementById("dateDisplay");
    const checkInDateDisplay = document.getElementById("checkInDateDisplay");
    const checkOutDateDisplay = document.getElementById("checkOutDateDisplay");
    const inputCheckIn = document.getElementById("inputCheckIn");
    const inputCheckOut = document.getElementById("inputCheckOut");

    // Format dates to "DD THMM YYYY" (e.g. 04 TH06 2026)
    function formatDateString(dateVal) {
        if (!dateVal) return "";
        const dateObj = new Date(dateVal);
        const day = String(dateObj.getDate()).padStart(2, '0');
        const month = String(dateObj.getMonth() + 1).padStart(2, '0');
        const year = dateObj.getFullYear();
        return `${day} TH${month} ${year}`;
    }

    // Close dropdowns when clicking date inputs, and sync values on change
    inputCheckIn.addEventListener("click", (e) => {
        e.stopPropagation();
        closeAllDropdowns();
    });

    inputCheckOut.addEventListener("click", (e) => {
        e.stopPropagation();
        closeAllDropdowns();
    });

    inputCheckIn.addEventListener("change", () => {
        checkInDateDisplay.textContent = formatDateString(inputCheckIn.value);
    });

    inputCheckOut.addEventListener("change", () => {
        checkOutDateDisplay.textContent = formatDateString(inputCheckOut.value);
    });

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
    const plannerForm = document.getElementById("plannerForm");
    const plannerInput = document.getElementById("plannerInput");
    const plannerMessages = document.getElementById("plannerMessages");
    const plannerGenerateBtn = document.getElementById("plannerGenerateBtn");
    const plannerProgressRing = document.getElementById("plannerProgressRing");
    const plannerProgressText = document.getElementById("plannerProgressText");
    const plannerResultPanel = document.getElementById("plannerResultPanel");
    const plannerSteps = document.querySelectorAll(".planner-step");
    const plannerChips = document.querySelectorAll(".planner-chip");
    const destinationAiBtns = document.querySelectorAll(".card-ai-btn");
    const plannerFields = ["destination", "origin", "group", "dates", "priority"];
    let plannerProfile = {};
    let plannerBusy = false;

    plannerBackBtn.addEventListener("click", closePlannerPage);
    plannerCloseBtn.addEventListener("click", closePlannerPage);

    plannerForm.addEventListener("submit", () => {
        const query = plannerInput.value.trim();
        if (!query) return;
        plannerInput.value = "";
        runPlannerQuery(query);
    });

    plannerGenerateBtn.addEventListener("click", () => {
        const query = buildPlannerPrompt();
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
                    history: []
                })
            });

            if (!response.ok) {
                throw new Error(`Planner API error: ${response.status}`);
            }

            const data = await response.json();
            plannerProfile = { ...plannerProfile, ...(data.profile || {}) };
            removePlannerTyping();
            appendPlannerMessage(data.reply || "Mình đã ghi nhận. Bạn nói thêm một chút để mình chốt lịch nhé.", "bot", true);
            renderPlannerCards(data.cards || []);
            updatePlannerChecklist();
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
        const completed = plannerFields.filter(field => Boolean(plannerProfile[field])).length;
        plannerProgressRing.textContent = `${completed}/5`;
        plannerProgressText.textContent = `${completed} of 5 captured`;
        plannerSteps.forEach(step => {
            const field = step.getAttribute("data-field");
            const description = step.querySelector("p");
            if (plannerProfile[field]) {
                step.classList.add("completed");
                description.textContent = plannerProfile[field];
            } else {
                step.classList.remove("completed");
                description.textContent = getPlannerPlaceholder(field);
            }
        });
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

    function appendPlannerMessage(text, sender, allowHtml = false) {
        const message = document.createElement("div");
        message.className = `planner-msg ${sender === "user" ? "planner-user-msg" : "planner-bot-msg"}`;
        if (allowHtml) {
            message.innerHTML = text;
        } else {
            message.textContent = text;
        }
        plannerMessages.appendChild(message);
        plannerMessages.scrollTop = plannerMessages.scrollHeight;
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

    function renderPlannerCards(cards) {
        plannerResultPanel.querySelectorAll(".planner-result-card").forEach(card => card.remove());
        cards.slice(0, 3).forEach((card, index) => {
            const cardEl = document.createElement("div");
            cardEl.className = "planner-result-card";
            const badges = (card.context_badges || []).slice(0, 3).map(badge => `<span>${escapeHtml(badge)}</span>`).join("");
            cardEl.innerHTML = `
                <strong>${index + 1}. ${escapeHtml(card.option || "Vinpearl option")}</strong>
                <p>${escapeHtml(card.why_it_fits || "Phù hợp với profile chuyến đi.")}</p>
                <div>${badges}</div>
            `;
            plannerResultPanel.appendChild(cardEl);
        });
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
    const chatForm = document.getElementById("chatForm");
    const chatInput = document.getElementById("chatInput");
    const chatMessages = document.getElementById("chatMessages");
    const chatBody = document.getElementById("chatBody");
    const typingIndicator = document.getElementById("typingIndicator");
    const suggestBtns = document.querySelectorAll(".suggest-btn");
    const chatbotIconOpen = chatbotTriggerBtn.querySelector(".chatbot-icon-open");
    const chatbotIconClose = chatbotTriggerBtn.querySelector(".chatbot-icon-close");
    let chatProfile = {};
    const chatHistory = [];

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

    // Handle Form Submit
    chatForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const query = chatInput.value.trim();
        if (!query) return;

        appendMessage(query, "user");
        chatInput.value = "";

        handleBotResponse(query);
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
    function appendMessage(text, sender, allowHtml = false) {
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
        } catch (error) {
            typingIndicator.classList.remove("active");
            appendMessage(
                "Xin lỗi, hiện trợ lý AI chưa kết nối được backend. Bạn thử chạy lại server hoặc gửi lại câu hỏi sau nhé.",
                "bot"
            );
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
});
