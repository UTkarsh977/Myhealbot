document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("contact-form");
  const popup = document.getElementById("success-popup");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = {
      name: form.name.value.trim(),
      email: form.email.value.trim(),
      message: form.message.value.trim(),
    };

    if (!formData.name || !formData.email || !formData.message) {
      alert("Please fill out all fields.");
      return;
    }

    try {
      const res = await fetch("/submit_contact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      const data = await res.json();
      if (data.status === "success") {
        popup.classList.add("show");
        form.reset();

        setTimeout(() => {
          popup.classList.remove("show");
        }, 2500);
      }
    } catch (error) {
      alert("Something went wrong. Please try again.");
    }
  });
});
