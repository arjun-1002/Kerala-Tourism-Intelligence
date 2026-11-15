/**
 * Kerala Tourism Intelligence — Client Interaction Engine
 */

let trendsChartInstance = null;

const HERITAGE_TICKERS = [
  "Vagamon's pine hills and rolling meadows host annual international paragliding gatherings in Idukki district.",
  "Munnar's high ranges are home to the Neelakurinji shrub, which blossoms across the shola slopes once every 12 years.",
  "Alappuzha's Punnamada Lake stages the Nehru Trophy Snake Boat Race each monsoon on the Vembanad backwaters.",
  "Kumarakom's Responsible Tourism initiatives model village-linked homestay and agrarian hospitality across Kottayam.",
  "Varkala preserves the only coastal tertiary sedimentary cliff formation rising directly above the Arabian Sea in southern Kerala.",
  "Bekal Fort in Kasaragod remains Kerala's largest 17th-century coastal rampart overlooking the Malabar shoreline."
];

let currentTickerIndex = 0;

document.addEventListener("DOMContentLoaded", function () {
  initHeritageTicker();
  initSearchAutocomplete();
  initAssistant();
});

function toggleMobileNav(forceState) {
  const drawer = document.getElementById("mobileNavDrawer");
  if (!drawer) return;
  const isOpen = typeof forceState === "boolean" ? forceState : !drawer.classList.contains("open");
  drawer.classList.toggle("open", isOpen);
}

function toggleSidebar(forceState) {
  toggleMobileNav(forceState);
}

function toggleDropdown(event) {
  if (event) event.stopPropagation();
  const dropdown = document.getElementById("insightsDropdown");
  if (!dropdown) return;
  dropdown.classList.toggle("open");
}

document.addEventListener("click", function (e) {
  const dropdown = document.getElementById("insightsDropdown");
  if (dropdown && !dropdown.contains(e.target)) {
    dropdown.classList.remove("open");
  }
});

function initHeritageTicker() {
  const tickerEl = document.getElementById("heritage-ticker-text");
  if (!tickerEl) return;

  setInterval(() => {
    currentTickerIndex = (currentTickerIndex + 1) % HERITAGE_TICKERS.length;
    tickerEl.style.opacity = 0;
    setTimeout(() => {
      tickerEl.innerText = HERITAGE_TICKERS[currentTickerIndex];
      tickerEl.style.opacity = 1;
    }, 200);
  }, 7500);
}

function prevTicker() {
  const tickerEl = document.getElementById("heritage-ticker-text");
  if (!tickerEl) return;
  currentTickerIndex = (currentTickerIndex - 1 + HERITAGE_TICKERS.length) % HERITAGE_TICKERS.length;
  tickerEl.innerText = HERITAGE_TICKERS[currentTickerIndex];
}

function nextTicker() {
  const tickerEl = document.getElementById("heritage-ticker-text");
  if (!tickerEl) return;
  currentTickerIndex = (currentTickerIndex + 1) % HERITAGE_TICKERS.length;
  tickerEl.innerText = HERITAGE_TICKERS[currentTickerIndex];
}

function initSearchAutocomplete() {
  const input = document.getElementById("hero-search-input");
  if (!input) return;

  input.addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
      e.preventDefault();
      const val = input.value.trim();
      if (val) {
        window.location.href = `/destinations?search=${encodeURIComponent(val)}`;
      }
    }
  });
}

function filterRoster(category, btnEl) {
  document.querySelectorAll(".landscape-pill").forEach(el => el.classList.remove("active"));
  if (btnEl) btnEl.classList.add("active");

  const items = document.querySelectorAll(".roster-btn");
  items.forEach(item => {
    const itemCat = item.getAttribute("data-category");
    item.style.display = (category === "All Destinations" || category === "All" || itemCat === category) ? "flex" : "none";
  });

  if (typeof window.filterRosterMap === "function") {
    window.filterRosterMap(category);
  }
}

async function selectDestination(destName, btnEl) {
  const targetBtn = btnEl || document.querySelector(`.roster-btn[data-dest-name="${destName}"]`);
  document.querySelectorAll(".roster-btn").forEach(el => el.classList.remove("active"));
  if (targetBtn) {
    targetBtn.classList.add("active");
  }

  if (typeof window.highlightRosterMarker === "function") {
    window.highlightRosterMarker(destName);
  }

  const titleEl = document.getElementById("trend-dest-name");
  if (titleEl) titleEl.innerText = destName;

  const deepLinkEl = document.getElementById("trend-deepdive-link");
  if (deepLinkEl) {
    deepLinkEl.href = `/google-trends?destination=${encodeURIComponent(destName)}`;
  }

  const periodEl = document.getElementById("trend-period-select");
  const period = periodEl ? periodEl.value : "3y";

  try {
    const res = await fetch(`/api/trends/${encodeURIComponent(destName)}?period=${encodeURIComponent(period)}`);
    const data = await res.json();
    renderTrendsChart(destName, data.dates, data.scores);
  } catch (err) {
    console.error("Error loading trends:", err);
  }

  try {
    const dRes = await fetch(`/api/destination/${encodeURIComponent(destName)}`);
    const dData = await dRes.json();
    updateSpotlightCard(dData);
  } catch (err) {
    console.error("Error loading spotlight:", err);
  }
}

function renderTrendsChart(destName, labels, values) {
  const ctx = document.getElementById("trendsChart");
  if (!ctx) return;

  if (trendsChartInstance) {
    trendsChartInstance.destroy();
  }

  const gradient = ctx.getContext("2d").createLinearGradient(0, 0, 0, 270);
  gradient.addColorStop(0, "rgba(21, 71, 52, 0.14)");
  gradient.addColorStop(1, "rgba(21, 71, 52, 0.0)");

  trendsChartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Search Interest",
          data: values,
          borderColor: "#154734",
          backgroundColor: gradient,
          borderWidth: 2.25,
          tension: 0.35,
          fill: true,
          pointBackgroundColor: "#154734",
          pointBorderColor: "#ffffff",
          pointBorderWidth: 1.5,
          pointRadius: 3.5,
          pointHoverRadius: 5.5
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: "index",
        intersect: false
      },
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          backgroundColor: "#0d2a1d",
          titleColor: "#e6c973",
          bodyColor: "#ffffff",
          padding: 10,
          cornerRadius: 8,
          displayColors: false,
          callbacks: {
            label: function (context) {
              return `Interest Index: ${context.parsed.y} / 100`;
            }
          }
        }
      },
      scales: {
        x: {
          grid: {
            display: false
          },
          border: {
            display: false
          },
          ticks: {
            color: "#717e77",
            font: { family: "Plus Jakarta Sans", size: 11 },
            maxRotation: 0,
            autoSkip: true,
            maxTicksLimit: 7
          }
        },
        y: {
          min: 0,
          max: 100,
          border: {
            display: false,
            dash: [4, 4]
          },
          grid: {
            color: "#eceae2",
            tickLength: 0
          },
          ticks: {
            stepSize: 25,
            color: "#717e77",
            font: { family: "Plus Jakarta Sans", size: 11 },
            padding: 8
          }
        }
      }
    }
  });
}

function updateSpotlightCard(data) {
  const imgEl = document.getElementById("spotlight-img");
  const titleEl = document.getElementById("spotlight-title");
  const locEl = document.getElementById("spotlight-loc");
  const clusterPill = document.getElementById("spotlight-cluster-pill");
  const scoreEl = document.getElementById("spotlight-score");
  const ringEl = document.getElementById("spotlight-ring");
  const check1 = document.getElementById("spotlight-check1");
  const check2 = document.getElementById("spotlight-check2");
  const check3 = document.getElementById("spotlight-check3");
  const exploreBtn = document.getElementById("spotlight-explore-btn");

  if (imgEl) imgEl.src = data.Photo_URL;
  if (titleEl) titleEl.innerText = data.Destination;
  if (locEl) locEl.innerText = `${data.District} District · ${data.Tagline}`;
  if (clusterPill) clusterPill.innerText = `${data.Cluster_Name}`;

  const oppScore = Math.max(0, Math.min(100, Number(data.Opportunity_Score) || 0));
  if (scoreEl) scoreEl.innerText = `${oppScore}%`;
  if (ringEl) {
    const circumference = 131.95;
    ringEl.style.strokeDashoffset = (circumference * (1 - oppScore / 100)).toFixed(2);
  }

  const growthNum = Number(data.Growth_2022_2024);
  const growthStr = `${growthNum >= 0 ? "+" : ""}${growthNum.toFixed(1)}%`;

  if (check1) check1.innerHTML = `<strong>Footfall (2024):</strong> ${Number(data.Total_Visitors_2024).toLocaleString()} visits`;
  if (check2) check2.innerHTML = `<strong>3-Year Growth:</strong> <span class="${growthNum >= 0 ? 'growth-pos' : 'growth-neg'}">${growthStr}</span>`;
  if (check3) check3.innerHTML = `<strong>Suggested Venture:</strong> ${data.Primary_Concept || data.Recommended_Business}`;

  if (exploreBtn) exploreBtn.href = `/destinations?highlight=${encodeURIComponent(data.Destination)}`;
}

/* ==========================================================================
   AI ASSISTANT CLIENT ENGINE
   ========================================================================== */

let aiChatHistory = [];
let isAssistantSending = false;

const DEFAULT_SUGGESTIONS = [
  { label: "Top 5 Growth Destinations", query: "Which destinations had the fastest visitor growth between 2022 and 2024?" },
  { label: "Homestay Investment & ROI", query: "What is the capital requirement and expected ROI for a boutique homestay in Kerala?" },
  { label: "Wayanad Venture Advisory", query: "What business venture is recommended for Wayanad and why?" },
  { label: "Munnar vs Wayanad", query: "Compare Munnar and Wayanad for tourism footfall and hospitality opportunities." },
  { label: "Quiet Hill Stations", query: "Where should I go for a peaceful hill station trip away from crowds?" },
  { label: "Theyyam & Cultural Season", query: "When and where can I experience Theyyam rituals and snake boat races?" }
];

function initAssistant() {
  renderAssistantSuggestions(DEFAULT_SUGGESTIONS);

  // Fetch dynamic suggestions from backend
  fetch("/api/assistant/suggestions")
    .then(r => r.json())
    .then(data => {
      if (data && data.suggestions && data.suggestions.length) {
        renderAssistantSuggestions(data.suggestions);
      }
    })
    .catch(() => {
      // Gracefully uses defaults
    });
}

function renderAssistantSuggestions(suggestions) {
  const container = document.getElementById("aiChipsScroll");
  if (!container) return;

  container.innerHTML = "";
  suggestions.forEach(item => {
    const chip = document.createElement("button");
    chip.type = "button";
    chip.className = "ai-chip";
    chip.innerText = item.label;
    chip.onclick = () => askAssistant(item.query);
    container.appendChild(chip);
  });
}

function toggleAssistant(forceState) {
  const panel = document.getElementById("aiAssistantPanel");
  if (!panel) return;

  const isOpen = typeof forceState === "boolean" ? forceState : !panel.classList.contains("open");
  panel.classList.toggle("open", isOpen);
  panel.setAttribute("aria-hidden", !isOpen);

  if (isOpen) {
    const input = document.getElementById("aiUserInput");
    if (input) setTimeout(() => input.focus(), 150);
  }
}

function handleAssistantSubmit(e) {
  if (e) e.preventDefault();
  const input = document.getElementById("aiUserInput");
  if (!input) return;
  const msg = input.value.trim();
  if (!msg) return;
  askAssistant(msg);
  input.value = "";
}

function askAssistant(query) {
  if (!query || isAssistantSending) return;

  // Make sure panel is open
  toggleAssistant(true);

  // Append user message
  appendUserMessage(query);

  // Set loading state
  isAssistantSending = true;
  const sendBtn = document.getElementById("aiSendBtn");
  const input = document.getElementById("aiUserInput");
  if (sendBtn) sendBtn.disabled = true;
  if (input) input.disabled = true;

  const typingIndicator = document.getElementById("aiTypingIndicator");
  if (typingIndicator) typingIndicator.style.display = "flex";
  scrollAssistantToBottom();

  // Send request
  fetch("/api/assistant/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message: query,
      history: aiChatHistory.slice(-6)
    })
  })
    .then(r => r.json())
    .then(data => {
      if (typingIndicator) typingIndicator.style.display = "none";
      const reply = data && data.reply ? data.reply : "Sorry, I could not process your query right now.";
      appendBotMessage(reply);

      // Save history
      aiChatHistory.push({ role: "user", content: query });
      aiChatHistory.push({ role: "assistant", content: reply });

      if (data && data.suggestions && data.suggestions.length) {
        renderAssistantSuggestions(data.suggestions);
      }
    })
    .catch(err => {
      if (typingIndicator) typingIndicator.style.display = "none";
      appendBotMessage("⚠️ Network error communicating with the assistant service. Please check your connection.");
    })
    .finally(() => {
      isAssistantSending = false;
      if (sendBtn) sendBtn.disabled = false;
      if (input) {
        input.disabled = false;
        input.focus();
      }
      scrollAssistantToBottom();
    });
}

function appendUserMessage(text) {
  const area = document.getElementById("aiMessagesArea");
  if (!area) return;

  const msgDiv = document.createElement("div");
  msgDiv.className = "ai-msg ai-msg-user";

  const bubble = document.createElement("div");
  bubble.className = "ai-msg-bubble";
  bubble.innerText = text;

  msgDiv.appendChild(bubble);
  area.appendChild(msgDiv);
  scrollAssistantToBottom();
}

function appendBotMessage(markdown) {
  const area = document.getElementById("aiMessagesArea");
  if (!area) return;

  const msgDiv = document.createElement("div");
  msgDiv.className = "ai-msg ai-msg-bot";

  const avatar = document.createElement("div");
  avatar.className = "ai-msg-avatar";
  avatar.innerText = "🌴";

  const bubble = document.createElement("div");
  bubble.className = "ai-msg-bubble";
  bubble.innerHTML = parseMarkdownToHtml(markdown);

  msgDiv.appendChild(avatar);
  msgDiv.appendChild(bubble);
  area.appendChild(msgDiv);
  scrollAssistantToBottom();
}

function scrollAssistantToBottom() {
  const area = document.getElementById("aiMessagesArea");
  if (area) {
    area.scrollTop = area.scrollHeight;
  }
}

function resetAssistantChat() {
  aiChatHistory = [];
  const area = document.getElementById("aiMessagesArea");
  if (!area) return;

  area.innerHTML = `
    <div class="ai-msg ai-msg-bot">
      <div class="ai-msg-avatar">🌴</div>
      <div class="ai-msg-bubble">
        <p><strong>Namaskaram!</strong> Welcome back to Kerala Tourism Intelligence.</p>
        <p>I can help you explore <strong>25 benchmark destinations</strong>, discover <strong>hospitality business opportunities</strong>, estimate <strong>venture ROI</strong>, or plan trips around Kerala's cultural festivals.</p>
        <p style="margin-top:8px; font-size:0.8rem; color:var(--ink-3);">Try asking: <em>"Where should I open an eco-resort?"</em> or <em>"Compare Munnar and Wayanad"</em></p>
      </div>
    </div>
  `;
  renderAssistantSuggestions(DEFAULT_SUGGESTIONS);
  const input = document.getElementById("aiUserInput");
  if (input) {
    input.value = "";
    input.focus();
  }
}

function parseMarkdownToHtml(md) {
  if (!md) return "";

  // 1. Safe escape raw HTML
  let out = md
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  // Headers: ### Title
  out = out.replace(/^### (.*?)$/gm, "<h3>$1</h3>");
  out = out.replace(/^## (.*?)$/gm, "<h3>$1</h3>");
  out = out.replace(/^# (.*?)$/gm, "<h3>$1</h3>");

  // Blockquotes: > quote
  out = out.replace(/^&gt;\s*(.*?)$/gm, "<blockquote>$1</blockquote>");

  // Tables
  const tableRegex = /((?:\|.+?\|\r?\n)+)/g;
  out = out.replace(tableRegex, function (match) {
    const lines = match.trim().split("\n");
    if (lines.length < 2) return match;
    let html = "<table>";
    let isHeader = true;
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      if (/^\|[-:\s|]+\|$/.test(line)) {
        isHeader = false;
        continue;
      }
      const cols = line.split("|").slice(1, -1).map(c => c.trim());
      html += "<tr>";
      cols.forEach(col => {
        if (isHeader) {
          html += `<th>${col}</th>`;
        } else {
          html += `<td>${col}</td>`;
        }
      });
      html += "</tr>";
    }
    html += "</table>";
    return html;
  });

  // Unordered list items: - item
  out = out.replace(/(?:^|\n)-\s+(.*?)(?=\n(?!-\s+)|\n*$)/gs, function (block) {
    const items = block.trim().split(/\n-\s+/).filter(Boolean);
    return "\n<ul>" + items.map(it => `<li>${it}</li>`).join("") + "</ul>\n";
  });

  // Ordered list items: 1. item
  out = out.replace(/(?:^|\n)\d+\.\s+(.*?)(?=\n(?!\d+\.\s+)|\n*$)/gs, function (block) {
    const items = block.trim().split(/\n\d+\.\s+/).filter(Boolean);
    return "\n<ol>" + items.map(it => `<li>${it}</li>`).join("") + "</ol>\n";
  });

  // Bold & Italic
  out = out.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  out = out.replace(/\*(.*?)\*/g, "<em>$1</em>");

  // Markdown links: [text](url)
  out = out.replace(/\[(.*?)\]\((.*?)\)/g, function (m, text, url) {
    const cleanUrl = url.replace(/&amp;/g, "&");
    return `<a href="${cleanUrl}" class="chat-nav-link">${text} &#8594;</a>`;
  });

  // Paragraphs & Double line breaks
  out = out.replace(/\n\n+/g, "</p><p>");
  out = "<p>" + out + "</p>";

  // Clean empty paragraphs and bad nestings
  out = out.replace(/<p>\s*<\/p>/g, "");
  out = out.replace(/<p>(<h3[^>]*>.*?<\/h3>)<\/p>/g, "$1");
  out = out.replace(/<p>(<blockquote[^>]*>.*?<\/blockquote>)<\/p>/g, "$1");
  out = out.replace(/<p>(<table[^>]*>.*?<\/table>)<\/p>/g, "$1");
  out = out.replace(/<p>(<ul[^>]*>.*?<\/ul>)<\/p>/g, "$1");
  out = out.replace(/<p>(<ol[^>]*>.*?<\/ol>)<\/p>/g, "$1");

  return out;
}
