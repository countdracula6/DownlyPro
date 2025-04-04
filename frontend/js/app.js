// frontend/js/app.js

const downloadBtn = document.getElementById("download-btn");
const urlInput = document.getElementById("url");
const formatSelect = document.getElementById("format");
const progressBar = document.getElementById("progress-bar");
const statusMessage = document.getElementById("status");

// Simulate checking if user is premium (later we replace with real check!)
const isPremiumUser = false;

downloadBtn.addEventListener("click", async () => {
  const url = urlInput.value.trim();
  const format = formatSelect.value;

  if (!url) {
    alert("⚠️ Please paste a valid link!");
    return;
  }

  progressBar.style.width = "30%";
  statusMessage.textContent = "⏳ Starting download...";

  // 🚫 Show ad popup for FREE users
  if (!isPremiumUser) {
    await showAdPopup();
  }

  try {
    const baseURL = "https://downlypro.onrender.com"; // your backend URL
    const endpoint =
      format === "audio" ? `${baseURL}/download` : `${baseURL}/download-video`;

    const formData = new FormData();
    formData.append("url", url);

    const response = await fetch(endpoint, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) throw new Error("❌ Server error during download!");

    const blob = await response.blob();
    const downloadLink = document.createElement("a");
    downloadLink.href = URL.createObjectURL(blob);
    downloadLink.download = `downlypro_${
      format === "audio" ? "audio" : "video"
    }.${format === "audio" ? "mp3" : "mp4"}`;
    downloadLink.click();

    statusMessage.textContent = "✅ Download completed!";
    progressBar.style.width = "100%";
  } catch (error) {
    console.error(error);
    statusMessage.textContent = "❌ Download failed.";
    progressBar.style.width = "0%";
  }

  setTimeout(() => {
    progressBar.style.width = "0%";
    statusMessage.textContent = "";
  }, 3000);
});

async function showAdPopup() {
  return new Promise((resolve) => {
    const ad = document.createElement("div");
    ad.style.position = "fixed";
    ad.style.top = "0";
    ad.style.left = "0";
    ad.style.width = "100%";
    ad.style.height = "100%";
    ad.style.background = "rgba(0,0,0,0.8)";
    ad.style.color = "white";
    ad.style.display = "flex";
    ad.style.flexDirection = "column";
    ad.style.alignItems = "center";
    ad.style.justifyContent = "center";
    ad.style.zIndex = "9999";
    ad.innerHTML = `
      <h2>🚀 Support DownlyPro!</h2>
      <p>Watch this quick ad to continue your download.</p>
      <button id="closeAdBtn" style="padding:10px 20px; margin-top:20px;">Close Ad</button>
    `;

    document.body.appendChild(ad);

    document.getElementById("closeAdBtn").addEventListener("click", () => {
      ad.remove();
      resolve();
    });
  });
}
