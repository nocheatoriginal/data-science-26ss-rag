import { documents, queries, walkthroughSteps } from "./model.js";

function distance(a, b) {
  return Math.hypot(a.x - b.x, a.y - b.y);
}

export class VectorDbViewModel {
  constructor() {
    this.queryKey = "rag";
    this.topK = 3;
    this.currentStep = 0;
    this.miniExample = {
      query: [0.82, 0.44, 0.36],
      document: [0.76, 0.51, 0.29],
    };
  }

  setQuery(queryKey) {
    if (queries[queryKey]) {
      this.queryKey = queryKey;
    }
  }

  setTopK(topK) {
    this.topK = Number(topK);
  }

  changeWalkthroughStep(direction) {
    this.currentStep = (this.currentStep + direction + walkthroughSteps.length) % walkthroughSteps.length;
  }

  randomizeMiniExample() {
    const query = this.randomVector();
    const mode = Math.random();
    const document = mode < 0.4
      ? this.randomVector()
      : query.map((value) => {
          const offsetRange = mode < 0.7 ? 0.5 : 1.1;
          const offset = Math.random() * offsetRange - offsetRange / 2;
          return this.clamp(value + offset);
        });

    this.miniExample = { query, document };
  }

  get query() {
    return queries[this.queryKey];
  }

  get documents() {
    return documents;
  }

  get selectedTitles() {
    return this.rankedDocs.slice(0, this.topK).map((doc) => doc.title);
  }

  get rankedDocs() {
    return documents
      .map((doc) => ({ ...doc, score: this.similarity(doc) }))
      .sort((a, b) => b.score - a.score);
  }

  get visibleResults() {
    return this.rankedDocs.slice(0, this.topK);
  }

  get walkthroughStep() {
    return {
      ...walkthroughSteps[this.currentStep],
      index: this.currentStep + 1,
      total: walkthroughSteps.length,
    };
  }

  get miniExampleView() {
    const score = this.cosineSimilarity(this.miniExample.query, this.miniExample.document);
    const values = this.miniExample.query.map((queryValue, index) => {
      const documentValue = this.miniExample.document[index];
      const sameDirection = Math.sign(queryValue) === Math.sign(documentValue);
      const closeValue = Math.abs(queryValue - documentValue) < 0.35;
      const matches = sameDirection && closeValue;

      return {
        query: queryValue.toFixed(2),
        document: documentValue.toFixed(2),
        status: score >= 0.5 && matches ? "match" : score < 0.5 && !matches ? "miss" : "neutral",
      };
    });

    return {
      values,
      score,
      percent: Math.round(score * 100),
    };
  }

  similarity(doc) {
    const base = 1 - Math.min(distance(doc, this.query), 1);
    const topicBoost = doc.topics.includes(this.queryKey) ? 0.23 : 0.04;
    return Math.round((base * 0.72 + topicBoost) * 100);
  }

  randomVector() {
    return Array.from({ length: 3 }, () => this.clamp(Math.random() * 1.8 - 0.9));
  }

  clamp(value) {
    return Math.min(0.98, Math.max(-0.98, Number(value.toFixed(2))));
  }

  cosineSimilarity(a, b) {
    const dot = a.reduce((sum, value, index) => sum + value * b[index], 0);
    const lengthA = Math.hypot(...a);
    const lengthB = Math.hypot(...b);
    return Number(Math.max(0, dot / (lengthA * lengthB)).toFixed(2));
  }
}
