document.getElementById("shortenForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const resultDiv = document.getElementById("result");
  resultDiv.innerHTML = "<p>Procesando...</p>";

  try {
    const response = await fetch(
      "https://acortador-url-beta.vercel.app/shorten",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({
          original_url: document.getElementById("originalUrl").value,
          custom_alias: document.getElementById("customAlias").value,
        }),
      }
    );

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Error al acortar la URL");
    }

    const data = await response.json();
    resultDiv.innerHTML = `
                    <p>URL acortada: <a href="${data.short_url}" target="_blank">${data.short_url}</a></p>
                `;

    document.getElementById("resultContainer").classList.remove("hidden");
    document.getElementById("resultContainer").classList.add("flex");
    document.getElementById("copyButton").onclick = () => {
      navigator.clipboard
        .writeText(data.short_url)
        .then(() => alert("URL copiada al portapapeles"))
        .catch((err) => console.error("Error al copiar:", err));
    };
  } catch (error) {
    resultDiv.innerHTML = `<p class="error">Error: ${error.message}</p>`;
    console.error("Error:", error);
  }
});
