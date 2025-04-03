const API_BASE = "https://downlypro.onrender.com"; // ✅ your live backend

document.getElementById("download-btn").addEventListener("click", async () => {
  const url = document.getElementById("url").value.trim();
  const format = document.getElementById("format").value;
  const status = document.getElementById("status");

  if (!url) {
    status.innerHTML = "❌ Please enter a link.";
    return;
  }

  status.innerHTML = "⏳ Processing download...";

  try {
    const endpoint = format === "audio" ? "/download" : "/download-video";
    const formData = new FormData();
    formData.append("url", url);

    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      status.innerHTML = "❌ Download failed.";
      return;
    }

    const blob = await response.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = downloadUrl;
    a.download =
      format === "audio" ? "downlypro_audio.mp3" : "downlypro_video.mp4";
    document.body.appendChild(a);
    a.click();
    a.remove();

    status.innerHTML = "✅ Download complete!";
  } catch (error) {
    console.error("❌ Error:", error);
    status.innerHTML = "❌ Server failed to respond.";
  }
});
