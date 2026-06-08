const sansFont = '-apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif';

export class VectorDbView {
  constructor(viewModel) {
    this.viewModel = viewModel;
    this.canvas = document.querySelector("#vectorCanvas");
    this.ctx = this.canvas.getContext("2d");
    this.querySelect = document.querySelector("#querySelect");
    this.topK = document.querySelector("#topK");
    this.topKValue = document.querySelector("#topKValue");
    this.resultsList = document.querySelector("#resultsList");
    this.prevStep = document.querySelector("#prevStep");
    this.nextStep = document.querySelector("#nextStep");
    this.stepCounter = document.querySelector("#stepCounter");
    this.stepLabel = document.querySelector("#stepLabel");
    this.stepTitle = document.querySelector("#stepTitle");
    this.stepText = document.querySelector("#stepText");
    this.stepFormula = document.querySelector("#stepFormula");
    this.animationStart = performance.now();
    this.animationFrameId = 0;
    this.lastCanvasWidth = 0;
    this.lastCanvasHeight = 0;
    this.lastCanvasRatio = 0;
  }

  bind() {
    this.querySelect.addEventListener("change", () => {
      this.viewModel.setQuery(this.querySelect.value);
      this.update();
    });

    this.topK.addEventListener("input", () => {
      this.viewModel.setTopK(this.topK.value);
      this.update();
    });

    this.prevStep.addEventListener("click", () => {
      this.viewModel.changeWalkthroughStep(-1);
      this.renderWalkthroughStep();
    });

    this.nextStep.addEventListener("click", () => {
      this.viewModel.changeWalkthroughStep(1);
      this.renderWalkthroughStep();
    });

    window.addEventListener("resize", () => this.drawAfterLayout());

    if ("ResizeObserver" in window) {
      new ResizeObserver(() => this.drawAfterLayout()).observe(this.canvas);
    }
  }

  start() {
    this.bind();
    this.update();
    this.drawAfterLayout();
    window.addEventListener("load", () => this.drawAfterLayout(), { once: true });

    cancelAnimationFrame(this.animationFrameId);
    this.animationFrameId = requestAnimationFrame((time) => this.animate(time));
  }

  update() {
    this.animationStart = performance.now();
    this.topKValue.textContent = this.viewModel.topK;
    this.renderResults();
    this.renderWalkthroughStep();
    this.draw();
  }

  renderResults() {
    this.resultsList.innerHTML = this.viewModel.visibleResults
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

  renderWalkthroughStep() {
    const step = this.viewModel.walkthroughStep;
    this.stepCounter.textContent = `${step.index} / ${step.total}`;
    this.stepLabel.textContent = `Schritt ${step.index}`;
    this.stepTitle.textContent = step.title;
    this.stepText.textContent = step.text;
    this.stepFormula.textContent = step.formula;
  }

  fitCanvas() {
    const rect = this.canvas.getBoundingClientRect();
    const ratio = window.devicePixelRatio || 1;
    const width = rect.width || Number(this.canvas.getAttribute("width")) || 760;
    const height = rect.height || Number(this.canvas.getAttribute("height")) || 420;
    const bitmapWidth = Math.floor(width * ratio);
    const bitmapHeight = Math.floor(height * ratio);

    if (this.canvas.width !== bitmapWidth || this.canvas.height !== bitmapHeight || this.lastCanvasRatio !== ratio) {
      this.canvas.width = bitmapWidth;
      this.canvas.height = bitmapHeight;
      this.lastCanvasWidth = width;
      this.lastCanvasHeight = height;
      this.lastCanvasRatio = ratio;
    }

    this.ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
  }

  draw(time = performance.now()) {
    this.fitCanvas();
    const width = this.canvas.clientWidth || this.lastCanvasWidth || Number(this.canvas.getAttribute("width")) || 760;
    const height = this.canvas.clientHeight || this.lastCanvasHeight || Number(this.canvas.getAttribute("height")) || 420;
    const query = this.viewModel.query;
    const selected = this.viewModel.selectedTitles;
    const progress = ((time - this.animationStart) % 2600) / 2600;
    const scanRadius = 28 + progress * Math.max(width, height) * 0.72;
    const pulse = 0.5 + Math.sin(progress * Math.PI * 2) * 0.5;

    this.ctx.clearRect(0, 0, width, height);
    this.ctx.fillStyle = "#ffffff";
    this.ctx.fillRect(0, 0, width, height);
    this.drawGrid(width, height);
    this.drawDocuments(width, height, query, selected, pulse);
    this.drawQuery(width, height, query, scanRadius, progress, pulse);
  }

  drawGrid(width, height) {
    this.ctx.strokeStyle = "#d0d7de";
    this.ctx.lineWidth = 1;

    for (let i = 1; i < 5; i += 1) {
      const x = (width / 5) * i;
      const y = (height / 5) * i;
      this.ctx.beginPath();
      this.ctx.moveTo(x, 0);
      this.ctx.lineTo(x, height);
      this.ctx.moveTo(0, y);
      this.ctx.lineTo(width, y);
      this.ctx.stroke();
    }
  }

  drawDocuments(width, height, query, selected, pulse) {
    this.viewModel.documents.forEach((doc) => {
      const x = doc.x * width;
      const y = doc.y * height;
      const isSelected = selected.includes(doc.title);

      if (isSelected) {
        this.ctx.strokeStyle = `rgba(9, 105, 218, ${0.35 + pulse * 0.45})`;
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();
        this.ctx.moveTo(query.x * width, query.y * height);
        this.ctx.lineTo(x, y);
        this.ctx.stroke();
        this.ctx.lineWidth = 1;
      }

      this.ctx.fillStyle = isSelected ? "#0969da" : "#8c959f";
      this.ctx.beginPath();
      this.ctx.arc(x, y, isSelected ? 8 + pulse * 2 : 6, 0, Math.PI * 2);
      this.ctx.fill();

      this.ctx.fillStyle = "#24292f";
      this.ctx.font = `600 13px ${sansFont}`;
      this.ctx.fillText(doc.title, x + 12, y + 4);
    });
  }

  drawQuery(width, height, query, scanRadius, progress, pulse) {
    this.ctx.strokeStyle = `rgba(207, 34, 46, ${0.48 - progress * 0.28})`;
    this.ctx.lineWidth = 2;
    this.ctx.beginPath();
    this.ctx.arc(query.x * width, query.y * height, scanRadius, 0, Math.PI * 2);
    this.ctx.stroke();

    this.ctx.fillStyle = "#cf222e";
    this.ctx.beginPath();
    this.ctx.arc(query.x * width, query.y * height, 10 + pulse * 2, 0, Math.PI * 2);
    this.ctx.fill();

    this.ctx.strokeStyle = "rgba(207, 34, 46, 0.25)";
    this.ctx.lineWidth = 8;
    this.ctx.beginPath();
    this.ctx.arc(query.x * width, query.y * height, 16 + pulse * 8, 0, Math.PI * 2);
    this.ctx.stroke();

    this.ctx.fillStyle = "#24292f";
    this.ctx.font = `600 14px ${sansFont}`;
    this.ctx.fillText(query.label, query.x * width + 14, query.y * height - 12);
  }

  drawAfterLayout() {
    requestAnimationFrame((time) => {
      this.draw(time);
      requestAnimationFrame(() => this.draw());
    });
  }

  animate(time) {
    this.draw(time);
    this.animationFrameId = requestAnimationFrame((nextTime) => this.animate(nextTime));
  }
}
