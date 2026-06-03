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

        // User Message
        appendMessage(query, "user");
        chatInput.value = "";
        
        // Trigger bot reply
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
    function appendMessage(text, sender) {
        const msgDiv = document.createElement("div");
        msgDiv.classList.add("message", sender === "user" ? "user-msg" : "bot-msg");
        msgDiv.innerHTML = `<div class="msg-bubble">${text}</div>`;
        chatMessages.appendChild(msgDiv);
        scrollChatToBottom();
    }

    // Bot Response Logic with Keywords Matching
    function handleBotResponse(query) {
        // Show Typing Indicator
        typingIndicator.classList.add("active");
        scrollChatToBottom();

        const lowerQuery = query.toLowerCase();
        let reply = "";

        // Keywords rules
        if (lowerQuery.includes("phú quốc") || lowerQuery.includes("phu quoc")) {
            reply = "🌴 <strong>Vinpearl Phú Quốc</strong> sở hữu quần thể nghỉ dưỡng khép kín đẳng cấp 5 sao tại Bãi Dài với các căn villa hồ bơi riêng biệt. Trải nghiệm không thể bỏ lỡ tại đây:<br>" +
                    "- Vui chơi tại <strong>VinWonders</strong> (Công viên chủ đề hàng đầu Việt Nam)<br>" +
                    "- Khám phá thế giới động vật bán hoang dã tại <strong>Vinpearl Safari</strong><br>" +
                    "- Tham quan thành phố không ngủ Grand World.<br><br>" +
                    "Bạn có muốn đặt phòng trực tiếp tại Vinpearl Phú Quốc hôm nay để được giảm giá 10% Pearl Club không?";
        } else if (lowerQuery.includes("nha trang")) {
            reply = "🌊 <strong>Vinpearl Nha Trang</strong> là thiên đường nghỉ dưỡng tọa lạc trên đảo Hòn Tre thơ mộng và các khách sạn trung tâm thành phố:<br>" +
                    "- Trải nghiệm cáp treo vượt biển kỳ vĩ dài hơn 3km.<br>" +
                    "- Công viên giải trí <strong>VinWonders Nha Trang</strong> với show diễn thực cảnh Tata Show độc bản.<br>" +
                    "- Hệ thống sân golf 18 hố Vinpearl Golf đầy thử thách.<br><br>" +
                    "Tôi có thể hỗ trợ kiểm tra giá phòng ưu đãi tại Nha Trang cho bạn ngay lúc này!";
        } else if (lowerQuery.includes("đà nẵng") || lowerQuery.includes("hội an") || lowerQuery.includes("nam hội an") || lowerQuery.includes("da nang") || lowerQuery.includes("hoi an")) {
            reply = "🏮 <strong>Vinpearl Nam Hội An</strong> là sự giao thoa hoàn hảo giữa di sản văn hóa và phong cách sống hiện đại:<br>" +
                    "- Nằm dọc bãi biển Bình Minh hoang sơ dài 1.3km.<br>" +
                    "- Gần khu bảo tồn văn hóa VinWonders Nam Hội An và Đảo Văn Hóa Dân Gian độc đáo.<br>" +
                    "- Sân golf 18 hố tiêu chuẩn Championship thiết kế bởi IMG.<br><br>" +
                    "Bạn có muốn tôi tư vấn gói combo trọn gói gồm vé máy bay và phòng khách sạn Nam Hội An không?";
        } else if (lowerQuery.includes("hạ long") || lowerQuery.includes("ha long")) {
            reply = "🏰 <strong>Vinpearl Resort & Spa Hạ Long</strong> là lâu đài nghỉ dưỡng tráng lệ 4 mặt hướng biển độc bản giữa lòng Vịnh kỳ quan:<br>" +
                    "- Thiết kế lấy cảm hứng từ Nhà hát thành phố Rennes (Pháp) vô cùng sang trọng.<br>" +
                    "- Hồ bơi ngoài trời siêu rộng ngắm hoàng hôn vịnh biển.<br>" +
                    "- Cách Hà Nội chỉ 2 giờ lái xe qua cao tốc.<br><br>" +
                    "Hạ Long hiện đang có ưu đãi combo hè <strong>Family Summer Fun</strong> giảm tới 30%, bạn có muốn tìm hiểu?";
        } else if (lowerQuery.includes("khuyến mãi") || lowerQuery.includes("ưu đãi") || lowerQuery.includes("combo") || lowerQuery.includes("giá")) {
            reply = "🔥 <strong>Ưu đãi cực hot hiện tại của Vinpearl:</strong><br>" +
                    "1. <strong>Pearl Luxury Escape</strong>: Combo Vé máy bay khứ hồi + phòng 3N2Đ Vinpearl Phú Quốc chỉ từ 4.500.000đ/khách.<br>" +
                    "2. <strong>Early Bird Booking</strong>: Đặt trước phòng 30 ngày giảm ngay 20% giá phòng trên toàn hệ thống.<br>" +
                    "3. <strong>Pearl Club Exclusive</strong>: Đăng ký thành viên nhận thêm 10% giảm giá trực tiếp và tích điểm nâng hạng phòng.<br><br>" +
                    "Bạn muốn tìm hiểu kỹ hơn về chương trình ưu đãi nào?";
        } else if (lowerQuery.includes("vinwonders") || lowerQuery.includes("vé") || lowerQuery.includes("safari") || lowerQuery.includes("chơi")) {
            reply = "🎡 <strong>Hệ thống vui chơi giải trí VinWonders:</strong><br>" +
                    "- Đặt vé trực tuyến nhanh chóng, không cần xếp hàng, nhận mã QR vào cổng ngay lập tức.<br>" +
                    "- Hỗ trợ mua vé combo lẻ hoặc tích hợp cùng phòng lưu trú nghỉ dưỡng với giá tốt hơn.<br><br>" +
                    "Bạn có muốn tham khảo bảng giá vé vui chơi VinWonders tại Phú Quốc, Nha Trang hay Nam Hội An không?";
        } else {
            reply = "Cảm ơn câu hỏi của bạn! Trợ lý ảo Vinpearl AI sẵn sàng tư vấn cho bạn các thông tin sau:<br>" +
                    "1. 🌴 Địa điểm du lịch (Phú Quốc, Nha Trang, Hội An, Hạ Long).<br>" +
                    "2. 🔥 Các chương trình Khuyến mãi/Combo Hot.<br>" +
                    "3. 🎡 Mua vé vui chơi giải trí VinWonders & Safari.<br><br>" +
                    "Bạn hãy nhập từ khóa địa điểm hoặc dịch vụ bạn muốn tìm hiểu nhé!";
        }

        // Simulate network delay for typing indicator (800ms to 1500ms)
        const delay = Math.random() * 700 + 800; 
        setTimeout(() => {
            typingIndicator.classList.remove("active");
            appendMessage(reply, "bot");
        }, delay);
    }
});
