// DarGlobal & Wasalt Real Estate AI Advisor — Client Script (Luxury Editorial Theme)

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
      const promptText = btn.querySelector(".text-xs, .text-sm").innerText.replace(/[""]/g, "").trim();
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

  // Append user message (Warm Charcoal / Bronze Luxury Style)
  function appendUserMessage(text) {
    if (welcomeHero) welcomeHero.style.display = "none";

    const msgDiv = document.createElement("div");
    msgDiv.className = "flex items-start justify-end space-x-3";
    msgDiv.innerHTML = `
      <div class="max-w-[85%] md:max-w-[75%] rounded-2xl rounded-tr-none px-4 py-3 bg-[#38322b] text-[#ffffff] shadow-md text-sm md:text-base leading-relaxed">
        ${escapeHtml(text)}
      </div>
      <div class="w-8 h-8 rounded-full bg-[#f4f2ee] border border-[#d6cfc5] flex items-center justify-center flex-none text-[#655848] text-xs">
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
      <div class="w-8 h-8 rounded-full bg-[#111111] text-[#d6cfc5] flex items-center justify-center flex-none font-serif font-bold text-xs shadow-sm">
        DG
      </div>
      <div class="rounded-2xl rounded-tl-none px-4 py-3 bg-white border border-[#eae7e1] text-[#6b7280] text-sm flex items-center space-x-2 shadow-sm">
        <span class="w-2 h-2 rounded-full bg-[#8c7355] animate-bounce" style="animation-delay: 0ms;"></span>
        <span class="w-2 h-2 rounded-full bg-[#8c7355] animate-bounce" style="animation-delay: 150ms;"></span>
        <span class="w-2 h-2 rounded-full bg-[#8c7355] animate-bounce" style="animation-delay: 300ms;"></span>
        <span class="text-xs text-[#8c7355] font-medium ml-2">Advisor analyzing portfolio data...</span>
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

  // Render Property Card HTML (Clean Luxury Style)
  function renderPropertyCard(prop) {
    const isDG = prop.source === "DarGlobal";
    const badgeColor = isDG 
      ? "bg-[#faf8f5] text-[#8c7355] border-[#e5dfd5]" 
      : "bg-emerald-50 text-emerald-800 border-emerald-200";
    const sourceLabel = isDG ? "DarGlobal Luxury" : "Wasalt Verified";
    const defaultImg = isDG
      ? "https://cdn.darglobal.co.uk/TTD_exterior_02_bd7d425e3c.webp"
      : "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=600&q=80";
    const imgUrl = prop.image_url || defaultImg;

    return `
      <div class="prop-card-editorial flex flex-col h-full bg-white border border-[#eae7e1] rounded-lg shadow-sm hover:shadow-md transition">
        <div class="relative h-36 w-full bg-[#f4f2ee] overflow-hidden">
          <img 
            src="${imgUrl}" 
            alt="${escapeHtml(prop.title)}" 
            class="w-full h-full object-cover transition-transform duration-500 hover:scale-105"
            onerror="this.src='${defaultImg}'"
          />
          <div class="absolute top-2.5 left-2.5">
            <span class="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded border backdrop-blur-md ${badgeColor}">
              ${sourceLabel}
            </span>
          </div>
        </div>

        <div class="p-3.5 flex-1 flex flex-col justify-between space-y-2.5">
          <div>
            <h4 class="font-serif font-bold text-xs md:text-sm text-[#111111] line-clamp-1" title="${escapeHtml(prop.title)}">
              ${escapeHtml(prop.title)}
            </h4>
            <p class="text-[11px] text-[#6b7280] flex items-center mt-0.5">
              <i class="fa-solid fa-location-dot text-[#8c7355] mr-1 text-[10px]"></i>
              <span class="truncate">${escapeHtml(prop.location || "International")}</span>
            </p>
          </div>

          <div class="flex items-center justify-between text-[11px] text-[#4b5563] pt-2 border-t border-[#f0eee9]">
            <span class="text-[#8c7355] font-semibold truncate">${escapeHtml(prop.price || "Price on Application")}</span>
            ${prop.bedrooms ? `<span class="text-[#6b7280] flex items-center"><i class="fa-solid fa-bed mr-1 text-[10px]"></i>${prop.bedrooms}</span>` : ""}
          </div>

          <a 
            href="${prop.url}" 
            target="_blank" 
            rel="noopener noreferrer" 
            class="block text-center w-full py-2 px-2 rounded bg-[#655848] hover:bg-[#38322b] text-white text-xs font-semibold uppercase tracking-wider transition duration-200"
          >
            View Listing <i class="fa-solid fa-arrow-up-right-from-square ml-1 text-[10px]"></i>
          </a>
        </div>
      </div>
    `;
  }

  // Append assistant message (Editorial White Luxury Card)
  function appendAssistantMessage(data) {
    const msgDiv = document.createElement("div");
    msgDiv.className = "flex items-start space-x-3";

    // Format markdown
    const formattedHtml = marked.parse(data.reply || "");

    // Property cards HTML if available
    let cardsHtml = "";
    if (data.properties && data.properties.length > 0) {
      cardsHtml = `
        <div class="mt-5 pt-3.5 border-t border-[#eae7e1]">
          <div class="text-[11px] font-bold uppercase tracking-widest text-[#8c7355] mb-2.5 flex items-center">
            <i class="fa-solid fa-gem mr-1.5"></i> Featured Portfolio Matches (${data.properties.length})
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
            ${data.properties.map(renderPropertyCard).join("")}
          </div>
        </div>
      `;
    }

    msgDiv.innerHTML = `
      <div class="w-8 h-8 rounded-full bg-[#111111] text-[#d6cfc5] flex items-center justify-center flex-none font-serif font-bold text-xs shadow-sm">
        DG
      </div>
      <div class="max-w-[85%] md:max-w-[80%] rounded-2xl rounded-tl-none px-5 py-4 bg-white border border-[#eae7e1] text-[#24292f] shadow-sm">
        <div class="prose-editorial">
          ${formattedHtml}
        </div>
        ${cardsHtml}
        <div class="mt-3 pt-2.5 border-t border-[#f0eee9] flex items-center justify-between text-[11px] text-[#8e959d]">
          <span class="flex items-center">
            <i class="fa-solid fa-bolt text-[#8c7355] mr-1.5"></i>
            <span class="truncate">Model: ${escapeHtml(data.model_used || "OpenRouter Free")}</span>
          </span>
          <button class="copy-btn text-[#8e959d] hover:text-[#111111] ml-2" title="Copy response">
            <i class="fa-regular fa-copy"></i>
          </button>
        </div>
      </div>
    `;

    // Copy button handler
    msgDiv.querySelector(".copy-btn").addEventListener("click", function() {
      navigator.clipboard.writeText(data.reply || "");
      this.innerHTML = '<i class="fa-solid fa-check text-emerald-600"></i>';
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
          <span class="inline-block w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
          <span>Inference: ${escapeHtml(data.model_used)}</span>
        `;
      }
    } catch (err) {
      removeTypingIndicator();
      console.error(err);
      appendAssistantMessage({
        reply: "I apologize, but I encountered a momentary connection interruption to the inference gateway. Please try sending your inquiry again or selecting an alternate model from the options below.",
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
        <div class="col-span-full text-center py-12 text-[#8e959d]">
          <i class="fa-solid fa-magnifying-glass text-3xl mb-2 text-[#d6cfc5]"></i>
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
        b.className = "filter-btn px-3.5 py-1.5 rounded text-[#4b5563] bg-[#f4f2ee] hover:bg-[#e8e6e1] uppercase tracking-wider text-[11px]";
      });
      btn.className = "filter-btn px-3.5 py-1.5 rounded font-semibold bg-[#655848] text-white uppercase tracking-wider text-[11px]";
      currentFilterSource = btn.getAttribute("data-source");
      renderModalProperties();
    });
  });

  modalSearch.addEventListener("input", () => {
    renderModalProperties();
  });
});
