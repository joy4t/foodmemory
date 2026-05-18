// ═══════════════════════════════════════════
// FoodMemory — Chat Logic
// ═══════════════════════════════════════════

const API_URL = 'http://localhost:8000';
const USER_ID = 'arindam';

// ─── DOM Elements ───
const messagesContainer = document.getElementById('messages');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const menuToggle = document.getElementById('menuToggle');
const sidebar = document.querySelector('.sidebar');

// ─── State ───
let isProcessing = false;

// ─── Initialize ───
function init() {
    messageInput.addEventListener('input', handleInputChange);
    messageInput.addEventListener('keydown', handleKeyDown);
    sendBtn.addEventListener('click', sendMessage);
    menuToggle.addEventListener('click', toggleSidebar);

    // Quick action buttons
    document.querySelectorAll('.quick-btn, .chip').forEach(btn => {
        btn.addEventListener('click', () => {
            const msg = btn.getAttribute('data-msg');
            if (msg) {
                messageInput.value = msg;
                handleInputChange();
                sendMessage();
            }
        });
    });

    // Close sidebar on overlay click
    const overlay = document.createElement('div');
    overlay.className = 'sidebar-overlay';
    overlay.addEventListener('click', toggleSidebar);
    document.body.appendChild(overlay);

    messageInput.focus();
}

// ─── Input Handling ───
function handleInputChange() {
    sendBtn.disabled = !messageInput.value.trim() || isProcessing;

    // Auto-resize textarea
    messageInput.style.height = 'auto';
    messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + 'px';
}

function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        if (!sendBtn.disabled) sendMessage();
    }
}

// ─── Send Message ───
async function sendMessage() {
    const text = messageInput.value.trim();
    if (!text || isProcessing) return;

    isProcessing = true;
    sendBtn.disabled = true;

    // Add user message
    addMessage(text, 'user');

    // Clear input
    messageInput.value = '';
    messageInput.style.height = 'auto';

    // Show typing indicator
    const typingEl = showTyping();

    try {
        const response = await fetch(`${API_URL}/chat/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: USER_ID,
                message: text,
            }),
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();

        // Remove typing indicator
        typingEl.remove();

        // Add bot response
        addMessage(data.reply, 'bot', data.intent, data.data);

    } catch (error) {
        typingEl.remove();
        addMessage(
            "Oops, I couldn't reach the server. Make sure the backend is running on localhost:8000.",
            'bot',
            'error'
        );
        console.error('Chat error:', error);
    }

    isProcessing = false;
    handleInputChange();
    messageInput.focus();
}

// ─── Add Message to Chat ───
function addMessage(text, sender, intent = null, data = null) {
    const messageEl = document.createElement('div');
    messageEl.className = `message ${sender}-message`;

    const avatar = sender === 'bot' ? '🍕' : 'A';
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    let contentHtml = '';

    // Intent badge for bot messages
    if (sender === 'bot' && intent && intent !== 'error') {
        const intentLabels = {
            search_restaurant: '🔍 Restaurant Search',
            browse_menu: '📋 Menu',
            add_to_cart: '🛒 Cart',
            place_order: '✅ Order',
            rate_item: '⭐ Rating Saved',
            ask_recommendation: '💡 Recommendation',
            general_chat: '💬 Chat',
        };
        const label = intentLabels[intent] || intent;
        contentHtml += `<span class="intent-badge">${label}</span>`;
    }

    // Format the message text
    contentHtml += formatMessage(text);

    // Add restaurant cards if we have data
    if (data && data.restaurants && intent === 'search_restaurant') {
        contentHtml += renderRestaurantCards(data.restaurants);
    }

    messageEl.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
            <div class="message-bubble">${contentHtml}</div>
            <span class="message-time">${time}</span>
        </div>
    `;

    messagesContainer.appendChild(messageEl);
    scrollToBottom();
}

// ─── Format Message ───
function formatMessage(text) {
    // Convert markdown-like formatting to HTML
    let html = text
        // Bold
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        // Newlines to paragraphs
        .split('\n\n')
        .map(p => `<p>${p.replace(/\n/g, '<br>')}</p>`)
        .join('');

    return html;
}

// ─── Render Restaurant Cards ───
function renderRestaurantCards(restaurants) {
    if (!restaurants || restaurants.length === 0) return '';

    const cards = restaurants.slice(0, 5).map(r => {
        const cuisines = r.cuisine ? r.cuisine.join(', ') : '';
        return `
            <div class="restaurant-card" onclick="browseMenu('${r.name}')">
                <div class="restaurant-card-name">${r.name}</div>
                <div class="restaurant-card-meta">
                    ⭐ ${r.rating} · ${r.delivery_time} · ${r.area} · ${cuisines}
                </div>
            </div>
        `;
    }).join('');

    return `<div class="restaurant-cards">${cards}</div>`;
}

// ─── Browse Menu (from card click) ───
function browseMenu(restaurantName) {
    messageInput.value = `Show me ${restaurantName} menu`;
    handleInputChange();
    sendMessage();
}

// ─── Typing Indicator ───
function showTyping() {
    const typingEl = document.createElement('div');
    typingEl.className = 'message bot-message';
    typingEl.innerHTML = `
        <div class="message-avatar">🍕</div>
        <div class="message-content">
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>
    `;
    messagesContainer.appendChild(typingEl);
    scrollToBottom();
    return typingEl;
}

// ─── Scroll ───
function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// ─── Sidebar Toggle (mobile) ───
function toggleSidebar() {
    sidebar.classList.toggle('open');
    document.querySelector('.sidebar-overlay').classList.toggle('active');
}

// ─── Start ───
init();
