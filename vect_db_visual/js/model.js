export const documents = [
  { title: "Embeddings", text: "Texte werden als Zahlenvektoren repräsentiert.", x: 0.68, y: 0.3, topics: ["rag", "database"] },
  { title: "Retrieval", text: "Ähnliche Vektoren liefern relevante Quellen.", x: 0.58, y: 0.48, topics: ["rag"] },
  { title: "Vector Index", text: "ANN-Indizes beschleunigen die Suche in großen Sammlungen.", x: 0.38, y: 0.32, topics: ["database"] },
  { title: "Metadatenfilter", text: "Filter grenzen Treffer nach Quelle, Datum oder Rechten ein.", x: 0.3, y: 0.62, topics: ["database", "privacy"] },
  { title: "Datenschutz", text: "Sensible Inhalte brauchen Zugriffskontrolle und klare Retention.", x: 0.72, y: 0.68, topics: ["privacy"] },
  { title: "Prompt Kontext", text: "Gefundene Chunks werden dem Modell als Kontext gegeben.", x: 0.5, y: 0.72, topics: ["rag"] },
  { title: "Monitoring", text: "Qualität wird mit Trefferquote, Latenz und Feedback gemessen.", x: 0.2, y: 0.42, topics: ["database"] },
];

export const queries = {
  rag: { label: "RAG Frage", x: 0.61, y: 0.43 },
  database: { label: "DB Frage", x: 0.35, y: 0.39 },
  privacy: { label: "Security Frage", x: 0.69, y: 0.64 },
};

export const walkthroughSteps = [
  {
    title: "Vektoren festlegen",
    text: "Wir vergleichen eine Query mit einem Dokument über drei vereinfachte Embedding-Dimensionen.",
    formula: "A = [2, 1, 2]\nB = [3, 1, 1]",
  },
  {
    title: "Skalarprodukt berechnen",
    text: "Gleiche Positionen werden multipliziert und anschließend addiert.",
    formula: "A · B = (2 × 3) + (1 × 1) + (2 × 1)\nA · B = 6 + 1 + 2 = 9",
  },
  {
    title: "Vektorlängen bestimmen",
    text: "Jeder Vektor wird über seine Länge normalisiert, damit längere Texte nicht automatisch gewinnen.",
    formula: "||A|| = √(2² + 1² + 2²) = 3\n||B|| = √(3² + 1² + 1²) = √11 ≈ 3.32",
  },
  {
    title: "Ähnlichkeit einsetzen",
    text: "Das Skalarprodukt wird durch beide Längen geteilt. Der Wert liegt nah an 1, also sind die Vektoren ähnlich.",
    formula: "cos(θ) = 9 / (3 × 3.32)\ncos(θ) ≈ 0.90",
  },
];
