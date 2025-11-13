document.addEventListener("DOMContentLoaded", () => {
  const chatForm = document.getElementById("chat-form");
  const userInput = document.getElementById("user-input");
  const chatBox = document.getElementById("chat-box");
  const sendBtn = document.getElementById("send-btn");
  const openBtn = document.getElementById("open-chat");
  const closeBtn = document.getElementById("close-btn");
  const chatWindow = document.getElementById("chat-window");

  function appendUser(msg) {
    const wrapper = document.createElement("div");
    wrapper.className = "user-msg text-end mb-2";
    wrapper.innerHTML = `<div class="msg user d-inline-block p-2 rounded" style="background:#0d6efd; color:#fff;">${escapeHtml(msg)}</div>`;
    chatBox.appendChild(wrapper);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  function appendBot(msg) {
    const wrapper = document.createElement("div");
    wrapper.className = "bot-msg text-start mb-2";
    wrapper.innerHTML = `<div class="msg bot d-inline-block p-2 rounded bg-light border">${escapeHtml(msg)}</div>`;
    chatBox.appendChild(wrapper);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  function escapeHtml(text) {
    return text
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;");
  }

  async function sendMessage(message) {
    if (!message) return;
    appendUser(message);
    userInput.value = "";
    try {
      const res = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });
      if (!res.ok) {
        appendBot("⚠️ Server error: " + res.status);
        console.error("Chat fetch returned status", res.status);
        return;
      }
      const data = await res.json();
      appendBot(data.reply || "No reply from server.");
      console.log("chat response:", data);
    } catch (err) {
      appendBot("⚠️ Error: Could not connect to the server.");
      console.error("chat error:", err);
    }
  }

  // Bind submit
  chatForm?.addEventListener("submit", (e) => {
    e.preventDefault();
    const msg = userInput.value.trim();
    if (!msg) return;
    sendMessage(msg);
  });

  // Also handle open/close
  openBtn?.addEventListener("click", () => {
    if (chatWindow) chatWindow.style.display = "block";
  });
  closeBtn?.addEventListener("click", () => {
    if (chatWindow) chatWindow.style.display = "none";
  });

  // Send button (for click)
  sendBtn?.addEventListener("click", (e) => {
    e.preventDefault();
    const msg = userInput.value.trim();
    if (!msg) return;
    sendMessage(msg);
  });
});
