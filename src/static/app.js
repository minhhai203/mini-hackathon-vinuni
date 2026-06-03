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
    
    // --- 11. AI CHATBOT LOGIC ---
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
});
