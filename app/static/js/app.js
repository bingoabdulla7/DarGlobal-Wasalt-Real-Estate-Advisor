// DarGlobal & Wasalt Real Estate AI Advisor — Client Script

document.addEventListener("DOMContentLoaded", () => {
  const messagesContainer = document.getElementById("messages-container");
  const welcomeHero = document.getElementById("welcome-hero");
  const chatScroller = document.getElementById("chat-scroller");
  const chatForm = document.getElementById("chat-form");
  const userInput = document.getElementById("user-input");
  const sendButton = document.getElementById("send-button");
  const modelSelect = document.getElementById("model-select");
  const footerStatus = document.getElementById("footer-status");
  const btnClearChat = document.getElementById("btn-clear-chat");

  // Modal elements
  const btnOpenExplorer = document.getElementById("btn-open-explorer");
  const btnCloseExplorer = document.getElementById("btn-close-explorer");
  const explorerModal = document.getElementById("explorer-modal");
  const modalPropertiesGrid = document.getElementById("modal-properties-grid");
  const modalSearch = document.getElementById("modal-search");
  const filterBtns = document.querySelectorAll(".filter-btn");

  let conversationHistory = [];
  let allPropertiesCache = [];
  let currentFilterSource = "all";

  // Auto-resize textarea
  userInput.addEventListener("input", () => {
    userInput.style.height = "auto";
    userInput.style.height = Math.min(userInput.scrollHeight, 140) + "px";
  });

  // Enter to send (Shift+Enter for newline)
  userInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      chatForm.dispatchEvent(new Event("submit"));
    }
  });

  // Prompt suggestion chips
  document.querySelectorAll(".prompt-chip").forEach((btn) => {
    btn.addEventListener("click", () => {
      const promptText = btn.querySelector(".text-sm").innerText.replace(/[""]/g, "").trim();
      userInput.value = promptText;
      chatForm.dispatchEvent(new Event("submit"));
    });
  });

  // Scroll to bottom
  function scrollToBottom() {
    chatScroller.scrollTo({
      top: chatScroller.scrollHeight,
      behavior: "smooth",
    });
  }

  // Escape HTML
  function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  // Append user message
  function appendUserMessage(text) {
    if (welcomeHero) welcomeHero.style.display = "none";

    const msgDiv = document.createElement("div");
    msgDiv.className = "flex items-start justify-end space-x-3";
    msgDiv.innerHTML = `
      <div class="max-w-[85%] md:max-w-[75%] rounded-2xl rounded-tr-none px-4 py-3 bg-gradient-to-r from-amber-600/90 to-amber-700/90 text-white shadow-lg text-sm md:text-base leading-relaxed">
        ${escapeHtml(text)}
      </div>
      <div class="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center flex-none text-slate-300 text-xs">
        <i class="fa-solid fa-user"></i>
      </div>
    `;
    messagesContainer.appendChild(msgDiv);
    scrollToBottom();
  }

  // Append typing indicator
  function appendTypingIndicator() {
    const indicatorDiv = document.createElement("div");
    indicatorDiv.id = "typing-indicator";
    indicatorDiv.className = "flex items-start space-x-3";
    indicatorDiv.innerHTML = `
      <div class="w-8 h-8 rounded-full bg-gradient-to-br from-amber-500 to-amber-700 flex items-center justify-center flex-none text-black font-bold text-xs shadow-md">
        DG
      </div>
      <div class="rounded-2xl rounded-tl-none px-4 py-3 bg-slate-900 border border-slate-800 text-slate-400 text-sm flex items-center space-x-2">
        <span class="w-2 h-2 rounded-full bg-amber-400 animate-bounce" style="animation-delay: 0ms;"></span>
        <span class="w-2 h-2 rounded-full bg-amber-400 animate-bounce" style="animation-delay: 150ms;"></span>
        <span class="w-2 h-2 rounded-full bg-amber-400 animate-bounce" style="animation-delay: 300ms;"></span>
        <span class="text-xs text-slate-400 ml-2">Advisor analyzing portfolio data...</span>
      </div>
    `;
    messagesContainer.appendChild(indicatorDiv);
    scrollToBottom();
    return indicatorDiv;
  }

  // Remove typing indicator
  function removeTypingIndicator() {
    const el = document.getElementById("typing-indicator");
    if (el) el.remove();
  }

  // Render Property Card HTML
  function renderPropertyCard(prop) {
    const isDG = prop.source === "DarGlobal";
    const badgeColor = isDG 
      ? "bg-amber-950/80 text-amber-300 border-amber-500/40" 
      : "bg-emerald-950/80 text-emerald-300 border-emerald-500/40";
    const sourceLabel = isDG ? "DarGlobal Luxury" : "Wasalt Verified";
    const defaultImg = isDG
      ? "https://cdn.darglobal.co.uk/TTD_exterior_02_bd7d425e3c.webp"
      : "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=600&q=80";
    const imgUrl = prop.image_url || defaultImg;

    return `
      <div class="property-card rounded-xl bg-slate-900 border border-slate-800 overflow-hidden flex flex-col h-full shadow-lg">
        <div class="relative h-32 w-full bg-slate-950 overflow-hidden">
          <img 
            src="${imgUrl}" 
            alt="${escapeHtml(prop.title)}" 
            class="w-full h-full object-cover transition-transform duration-500 hover:scale-105"
            onerror="this.src='${defaultImg}'"
          />
          <div class="absolute top-2 left-2">
            <span class="text-[10px] font-bold px-2 py-0.5 rounded-full border backdrop-blur-md ${badgeColor}">
              ${sourceLabel}
            </span>
          </div>
        </div>

        <div class="p-3 flex-1 flex flex-col justify-between space-y-2">
          <div>
            <h4 class="font-semibold text-xs md:text-sm text-white line-clamp-1" title="${escapeHtml(prop.title)}">
              ${escapeHtml(prop.title)}
            </h4>
            <p class="text-[11px] text-slate-400 flex items-center mt-0.5">
              <i class="fa-solid fa-location-dot text-amber-400 mr-1 text-[10px]"></i>
              <span class="truncate">${escapeHtml(prop.location || "International")}</span>
            </p>
          </div>

          <div class="flex items-center justify-between text-[11px] text-slate-300 pt-1 border-t border-slate-800">
            <span class="text-amber-300 font-semibold truncate">${escapeHtml(prop.price || "Price on Application")}</span>
            ${prop.bedrooms ? `<span class="text-slate-400 flex items-center"><i class="fa-solid fa-bed mr-1 text-[10px]"></i>${prop.bedrooms} Bed</span>` : ""}
          </div>

          <a 
            href="${prop.url}" 
            target="_blank" 
            rel="noopener noreferrer" 
            class="block text-center w-full py-1.5 px-2 rounded-lg bg-slate-800 hover:bg-amber-500 hover:text-black text-amber-300 text-xs font-medium transition duration-200"
          >
            View Listing <i class="fa-solid fa-arrow-up-right-from-square ml-1 text-[10px]"></i>
          </a>
        </div>
      </div>
    `;
  }

  // Append assistant message
  function appendAssistantMessage(data) {
    const msgDiv = document.createElement("div");
    msgDiv.className = "flex items-start space-x-3";

    // Format markdown
    const formattedHtml = marked.parse(data.reply || "");

    // Property cards HTML if available
    let cardsHtml = "";
    if (data.properties && data.properties.length > 0) {
      cardsHtml = `
        <div class="mt-4 pt-3 border-t border-slate-800">
          <div class="text-xs font-semibold uppercase tracking-wider text-amber-400 mb-2 flex items-center">
            <i class="fa-solid fa-gem mr-1.5"></i> Featured Portfolio Matches (${data.properties.length})
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            ${data.properties.map(renderPropertyCard).join("")}
          </div>
        </div>
      `;
    }

    msgDiv.innerHTML = `
      <div class="w-8 h-8 rounded-full bg-gradient-to-br from-amber-500 to-amber-700 flex items-center justify-center flex-none text-black font-bold text-xs shadow-md">
        DG
      </div>
      <div class="max-w-[85%] md:max-w-[80%] rounded-2xl rounded-tl-none px-4 py-3.5 bg-slate-900 border border-amber-500/20 text-slate-100 shadow-xl">
        <div class="prose-luxury">
          ${formattedHtml}
        </div>
        ${cardsHtml}
        <div class="mt-2.5 pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-500">
          <span class="flex items-center">
            <i class="fa-solid fa-bolt text-amber-400 mr-1"></i>
            <span class="truncate">Model: ${escapeHtml(data.model_used || "OpenRouter Free")}</span>
          </span>
          <button class="copy-btn text-slate-500 hover:text-slate-300 ml-2" title="Copy response">
            <i class="fa-regular fa-copy"></i>
          </button>
        </div>
      </div>
    `;

    // Copy button handler
    msgDiv.querySelector(".copy-btn").addEventListener("click", function() {
      navigator.clipboard.writeText(data.reply || "");
      this.innerHTML = '<i class="fa-solid fa-check text-emerald-400"></i>';
      setTimeout(() => { this.innerHTML = '<i class="fa-regular fa-copy"></i>'; }, 2000);
    });

    messagesContainer.appendChild(msgDiv);
    scrollToBottom();
  }

  // Handle Form Submit
  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const query = userInput.value.trim();
    if (!query) return;

    // Clear input
    userInput.value = "";
    userInput.style.height = "auto";
    sendButton.disabled = true;

    // Add user message to UI and history
    appendUserMessage(query);
    conversationHistory.push({ role: "user", content: query });

    // Show typing indicator
    appendTypingIndicator();

    try {
      const selectedModel = modelSelect.value;
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: conversationHistory,
          model: selectedModel,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }

      const data = await response.json();
      removeTypingIndicator();

      appendAssistantMessage(data);
      conversationHistory.push({ role: "assistant", content: data.reply });

      // Update footer model indicator
      if (footerStatus && data.model_used) {
        footerStatus.innerHTML = `
          <span class="inline-block w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
          <span>Active: ${escapeHtml(data.model_used)}</span>
        `;
      }
    } catch (err) {
      removeTypingIndicator();
      console.error(err);
      appendAssistantMessage({
        reply: "Sorry, I encountered an issue connecting to the inference engine. Please try sending your inquiry again or selecting an alternate free model from the dropdown.",
        model_used: "error",
        properties: [],
      });
    } finally {
      sendButton.disabled = false;
      userInput.focus();
    }
  });

  // Clear chat
  btnClearChat.addEventListener("click", () => {
    conversationHistory = [];
    messagesContainer.innerHTML = "";
    if (welcomeHero) {
      welcomeHero.style.display = "block";
      messagesContainer.appendChild(welcomeHero);
    }
  });

  // EXPLORER MODAL LOGIC
  async function loadAllProperties() {
    if (allPropertiesCache.length > 0) return;
    try {
      const res = await fetch("/api/properties");
      const data = await res.json();
      allPropertiesCache = data.data || [];
    } catch (err) {
      console.error("Failed to load properties:", err);
    }
  }

  function renderModalProperties() {
    let filtered = allPropertiesCache.filter((item) => {
      // Don't show generic corporate articles in directory
      if (item.id && item.id.startsWith("info_")) return false;

      // Source filter
      if (currentFilterSource === "darglobal" && item.source !== "DarGlobal") return false;
      if (currentFilterSource === "wasalt" && item.source !== "Wasalt") return false;

      // Search filter
      const q = modalSearch.value.trim().toLowerCase();
      if (q) {
        const text = (item.title + " " + item.location + " " + (item.brand_partner || "") + " " + (item.description || "")).toLowerCase();
        if (!text.includes(q)) return false;
      }
      return true;
    });

    if (filtered.length === 0) {
      modalPropertiesGrid.innerHTML = `
        <div class="col-span-full text-center py-12 text-slate-500">
          <i class="fa-solid fa-magnifying-glass text-3xl mb-2 text-slate-600"></i>
          <p>No properties match your filter criteria.</p>
        </div>
      `;
      return;
    }

    modalPropertiesGrid.innerHTML = filtered.map(renderPropertyCard).join("");
  }

  btnOpenExplorer.addEventListener("click", async () => {
    explorerModal.classList.remove("hidden");
    explorerModal.classList.add("flex");
    await loadAllProperties();
    renderModalProperties();
  });

  btnCloseExplorer.addEventListener("click", () => {
    explorerModal.classList.add("hidden");
    explorerModal.classList.remove("flex");
  });

  explorerModal.addEventListener("click", (e) => {
    if (e.target === explorerModal) {
      explorerModal.classList.add("hidden");
      explorerModal.classList.remove("flex");
    }
  });

  filterBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      filterBtns.forEach((b) => {
        b.className = "filter-btn px-3 py-1.5 rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700";
      });
      btn.className = "filter-btn px-3 py-1.5 rounded-lg bg-amber-500 text-black font-semibold";
      currentFilterSource = btn.getAttribute("data-source");
      renderModalProperties();
    });
  });

  modalSearch.addEventListener("input", () => {
    renderModalProperties();
  });
});
