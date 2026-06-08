import { documents, queries, walkthroughSteps } from "./model.js";

function distance(a, b) {
  return Math.hypot(a.x - b.x, a.y - b.y);
}

export class VectorDbViewModel {
  constructor() {
    this.queryKey = "rag";
    this.topK = 3;
    this.currentStep = 0;
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

  similarity(doc) {
    const base = 1 - Math.min(distance(doc, this.query), 1);
    const topicBoost = doc.topics.includes(this.queryKey) ? 0.23 : 0.04;
    return Math.round((base * 0.72 + topicBoost) * 100);
  }
}
