// Wait for the DOM to be fully loaded before running script
document.addEventListener("DOMContentLoaded", () => {
  // Get all the new HTML elements for the floating widget
  const chatWindow = document.getElementById("chatbot-window");
  const chatToggle = document.getElementById("chatbot-toggle");
  const chatClose = document.getElementById("chatbot-close");
  const chatForm = document.getElementById("chatbot-form");
  const chatInput = document.getElementById("chatbot-input");
  const chatMessages = document.getElementById("chatbot-messages");

  // Get mobile nav elements
  const mobileNavToggle = document.getElementById("mobile-nav-toggle");
  const mainNav = document.querySelector(".main-nav");

  // --- Mobile Navigation Logic ---
  if (mobileNavToggle) {
    mobileNavToggle.addEventListener("click", () => {
      mainNav.classList.toggle("active");
      // Optional: Add ARIA attribute for accessibility
      const isExpanded = mainNav.classList.contains("active");
      mobileNavToggle.setAttribute("aria-expanded", isExpanded);
    });
  }

  // --- Chatbot Toggle Logic ---
  if (chatToggle) {
    chatToggle.addEventListener("click", () => {
      chatWindow.classList.toggle("hidden");
    });
  }

  if (chatClose) {
    chatClose.addEventListener("click", () => {
      chatWindow.classList.add("hidden");
    });
  }

  // --- Chatbot Send Message Logic ---
  if (chatForm) {
    chatForm.addEventListener("submit", (e) => {
      e.preventDefault(); // Prevent the form from submitting normally
      const message = chatInput.value.trim();
      if (!message) return; // Don't send empty messages

      // Add user's message to the chat window
      addMessageToChat("user", message);
      chatInput.value = ""; // Clear the input

      // Send the message to the bot (using your original function)
      sendMessageToBot(message);
    });
  }

  /**
   * Adds a message to the chat window with the correct styling
   * @param {string} sender - 'user' or 'bot'
   * @param {string} message - The text content of the message
   */
  function addMessageToChat(sender, message) {
    if (!chatMessages) return;

    const messageElement = document.createElement("div");
    messageElement.className = `chat-message ${sender}`; // e.g., "chat-message user"
    messageElement.textContent = message;
    chatMessages.appendChild(messageElement);

    // Auto-scroll to the bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  /**
   * Sends the user's message to the Flask backend
   * This is your original 'fetch' logic, now inside a dedicated function
   */
  async function sendMessageToBot(message) {
    try {
      // We are fetching from '/chat' relative to the current domain.
      // This is better than 'http://127.0.0.1:5000' because it works in production.
      const response = await fetch("/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: message }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      // Add the bot's reply to the chat
      addMessageToChat("bot", data.reply);
    } catch (error) {
      console.error("Error sending message to bot:", error);
      addMessageToChat(
        "bot",
        "Sorry, something went wrong. Please try again later."
      );
    }
  }
});