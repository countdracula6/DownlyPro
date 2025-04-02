document.getElementById("download-btn").addEventListener("click", () => {
  const url = document.getElementById("url").value.trim();
  const format = document.getElementById("format").value;
  const status = document.getElementById("status");

  if (!url) {
    status.innerText = "❗ Please paste a valid link.";
    return;
  }

  status.innerText = "⏳ Processing download...";

  const endpoint =
    format === "audio"
      ? "http://127.0.0.1:8000/download"
      : "http://127.0.0.1:8000/download-video";

  fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams({ url }),
  })
    .then((res) => {
      if (!res.ok) throw new Error("Server failed to respond.");
      return res.blob();
    })
    .then((blob) => {
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download =
        format === "audio" ? "downlypro_audio.mp3" : "downlypro_video.mp4";
      document.body.appendChild(a);
      a.click();
      a.remove();
      status.innerText = "✅ Download ready!";
    })
    .catch((err) => {
      status.innerText = "❌ Error: " + err.message;
    });
});
