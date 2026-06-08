const canvas = document.querySelector("#vectorCanvas");
const ctx = canvas.getContext("2d");
const querySelect = document.querySelector("#querySelect");
const topK = document.querySelector("#topK");
const topKValue = document.querySelector("#topKValue");
const searchButton = document.querySelector("#searchButton");
const resultsList = document.querySelector("#resultsList");
let animationStart = performance.now();
let animationFrameId = 0;

const documents = [
  { title: "Embeddings", text: "Texte werden als Zahlenvektoren repräsentiert.", x: 0.68, y: 0.3, topics: ["rag", "database"] },
  { title: "Retrieval", text: "Ähnliche Vektoren liefern relevante Quellen.", x: 0.58, y: 0.48, topics: ["rag"] },
  { title: "Vector Index", text: "ANN-Indizes beschleunigen die Suche in großen Sammlungen.", x: 0.38, y: 0.32, topics: ["database"] },
  { title: "Metadatenfilter", text: "Filter grenzen Treffer nach Quelle, Datum oder Rechten ein.", x: 0.3, y: 0.62, topics: ["database", "privacy"] },
  { title: "Datenschutz", text: "Sensible Inhalte brauchen Zugriffskontrolle und klare Retention.", x: 0.72, y: 0.68, topics: ["privacy"] },
  { title: "Prompt Kontext", text: "Gefundene Chunks werden dem Modell als Kontext gegeben.", x: 0.5, y: 0.72, topics: ["rag"] },
  { title: "Monitoring", text: "Qualität wird mit Trefferquote, Latenz und Feedback gemessen.", x: 0.2, y: 0.42, topics: ["database"] },
];

const queries = {
  rag: { label: "RAG Frage", x: 0.61, y: 0.43 },
  database: { label: "DB Frage", x: 0.35, y: 0.39 },
  privacy: { label: "Security Frage", x: 0.69, y: 0.64 },
};

function distance(a, b) {
  return Math.hypot(a.x - b.x, a.y - b.y);
}

function similarity(doc, query) {
  const base = 1 - Math.min(distance(doc, query), 1);
  return Math.round((base * 0.72 + (doc.topics.includes(querySelect.value) ? 0.23 : 0.04)) * 100);
}

function getRankedDocs() {
  const query = queries[querySelect.value];
  return documents
    .map((doc) => ({ ...doc, score: similarity(doc, query) }))
    .sort((a, b) => b.score - a.score);
}

function fitCanvas() {
  const rect = canvas.getBoundingClientRect();
  const ratio = window.devicePixelRatio || 1;
  canvas.width = Math.floor(rect.width * ratio);
  canvas.height = Math.floor(rect.height * ratio);
  ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
}

function draw(time = performance.now()) {
  fitCanvas();
  const width = canvas.clientWidth;
  const height = canvas.clientHeight;
  const query = queries[querySelect.value];
  const ranked = getRankedDocs();
  const selected = ranked.slice(0, Number(topK.value)).map((doc) => doc.title);
  const progress = ((time - animationStart) % 2600) / 2600;
  const scanRadius = 28 + progress * Math.max(width, height) * 0.72;
  const pulse = 0.5 + Math.sin(progress * Math.PI * 2) * 0.5;

  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = "#ffffff";
  ctx.fillRect(0, 0, width, height);

  ctx.strokeStyle = "#d0d7de";
  ctx.lineWidth = 1;
  for (let i = 1; i < 5; i += 1) {
    const x = (width / 5) * i;
    const y = (height / 5) * i;
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, height);
    ctx.moveTo(0, y);
    ctx.lineTo(width, y);
    ctx.stroke();
  }

  documents.forEach((doc) => {
    const x = doc.x * width;
    const y = doc.y * height;
    const isSelected = selected.includes(doc.title);

    if (isSelected) {
      ctx.strokeStyle = `rgba(9, 105, 218, ${0.35 + pulse * 0.45})`;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(query.x * width, query.y * height);
      ctx.lineTo(x, y);
      ctx.stroke();
      ctx.lineWidth = 1;
    }

    ctx.fillStyle = isSelected ? "#0969da" : "#8c959f";
    ctx.beginPath();
    ctx.arc(x, y, isSelected ? 8 + pulse * 2 : 6, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = "#24292f";
    ctx.font = "600 13px -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif";
    ctx.fillText(doc.title, x + 12, y + 4);
  });

  ctx.strokeStyle = `rgba(207, 34, 46, ${0.48 - progress * 0.28})`;
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.arc(query.x * width, query.y * height, scanRadius, 0, Math.PI * 2);
  ctx.stroke();

  ctx.fillStyle = "#cf222e";
  ctx.beginPath();
  ctx.arc(query.x * width, query.y * height, 10 + pulse * 2, 0, Math.PI * 2);
  ctx.fill();
  ctx.strokeStyle = "rgba(207, 34, 46, 0.25)";
  ctx.lineWidth = 8;
  ctx.beginPath();
  ctx.arc(query.x * width, query.y * height, 16 + pulse * 8, 0, Math.PI * 2);
  ctx.stroke();
  ctx.fillStyle = "#24292f";
  ctx.font = "700 14px -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif";
  ctx.fillText(query.label, query.x * width + 14, query.y * height - 12);
}

function renderResults() {
  const docs = getRankedDocs().slice(0, Number(topK.value));
  resultsList.innerHTML = docs
    .map(
      (doc) => `
        <article class="result">
          <div class="result-head">
            <span>${doc.title}</span>
            <span class="score">${doc.score}%</span>
          </div>
          <p>${doc.text}</p>
        </article>
      `,
    )
    .join("");
}

function update() {
  topKValue.textContent = topK.value;
  animationStart = performance.now();
  renderResults();
  draw();
}

function animate(time) {
  draw(time);
  animationFrameId = requestAnimationFrame(animate);
}

querySelect.addEventListener("change", update);
topK.addEventListener("input", update);
searchButton.addEventListener("click", update);
window.addEventListener("resize", () => draw());

update();
cancelAnimationFrame(animationFrameId);
animationFrameId = requestAnimationFrame(animate);
