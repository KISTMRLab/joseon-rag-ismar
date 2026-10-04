import { createStage } from "/static/avatar.js";
import { Speech } from "/static/speech.js";

const $ = selector => document.querySelector(selector);
const escapeHTML = value => String(value ?? "").replace(/[&<>"']/g, char => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#39;"
}[char]));
let result = null;
let stage = null;
let speech = null;
let playGeneration = 0;
let delayTimer = null;
let delayResolve = null;

function stopPlayback() {
  playGeneration++;
  if (delayTimer !== null) { clearTimeout(delayTimer); delayTimer = null; delayResolve?.(); delayResolve = null; }
  speech?.cancel();
  stage?.gesture("idle");
  stage?.setSpeech(false);
}

function waitDuration(milliseconds) {
  return new Promise(resolve => {
    delayResolve = resolve;
    delayTimer = setTimeout(() => { delayTimer = null; delayResolve = null; resolve(); }, milliseconds);
  });
}

function ensureStage() {
  if (!stage) {
    stage = createStage($("#avatar-canvas"));
    speech = new Speech(stage);
  }
  $("#avatar-stage").classList.add("active");
}

fetch("/api/corpus").then(response => response.json()).then(corpus => {
  $("#corpus").textContent = `${corpus.collection_label || "Article records"} · ${corpus.articles} records · ${corpus.backend}`;
}).catch(error => { $("#corpus").textContent = `Corpus unavailable: ${error.message}`; });

$("#ask").onsubmit = async event => {
  event.preventDefault();
  stopPlayback();
  result = null;
  $("#answer").textContent = "Retrieving…";
  const body = {query: $("#query").value, token_budget: Number($("#budget").value),
    rewrite: $("#rewrite").value, generation: $("#generation").value};
  try {
    const response = await fetch("/api/ask", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(body)});
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || `Request failed (${response.status})`);
    result = data;
    $("#answer").textContent = data.answer;
    $("#citations").innerHTML = data.citations.map(citation => `<p><a target="_blank" rel="noopener noreferrer" href="${escapeHTML(citation.url)}">${escapeHTML(citation.label)}</a></p>`).join("");
    const trace = data.trace;
    $("#trace").innerHTML = `<b>Original:</b> ${escapeHTML(trace.original_query)}<br><b>Rewritten:</b> ${escapeHTML(trace.rewritten_query)}<br><b>Date:</b> ${escapeHTML(JSON.stringify(trace.date_filter))}<br><b>Budget:</b> ${trace.estimated_tokens}/${trace.token_budget} estimated tokens · ${trace.evidence.length} articles`;
    $("#evidence").innerHTML = trace.evidence.map(item => `<div class="evidence"><b>${escapeHTML(item.article.title || item.article.id)}</b><small>${escapeHTML(item.article.id)} · ${escapeHTML([item.article.year, item.article.month, item.article.day].filter(Boolean).join("-"))} · similarity ${item.similarity} · rerank ${item.rerank_score} · ${item.estimated_tokens} tokens</small><pre>${escapeHTML(item.article.text)}</pre><a href="${escapeHTML(item.article.source_url)}" target="_blank" rel="noopener noreferrer">Source record</a></div>`).join("");
    if (data.agent) {
      ensureStage();
      $("#motion").textContent = `${data.agent.events.length} timed utterances`;
    }
  } catch (error) {
    $("#answer").textContent = `Query failed: ${error.message}`;
  }
};

$("#play").onclick = async () => {
  if (!result?.agent) return;
  stopPlayback();
  const generation = playGeneration;
  const backend = $("#speech-backend").value;
  try {
    for (const event of result.agent.events) {
      if (generation !== playGeneration) return;
      stage.gesture(event.motion);
      $("#motion").textContent = `Gesture: ${event.motion}`;
      await speech.speak(event.text, {backend});
      if (generation !== playGeneration) return;
      await waitDuration(event.duration * 1000);
    }
    if (generation === playGeneration) { stage.gesture("idle"); stage.setSpeech(false); $("#motion").textContent = "Playback complete"; }
  } catch (error) {
    if (generation !== playGeneration) return;
    stopPlayback();
    $("#motion").textContent = `Playback unavailable: ${error.message}`;
  }
};

$("#transcribe").onclick = async () => {
  const file = $("#audio-input").files[0];
  if (!file) { $("#transcribe-status").textContent = "Choose an audio file first"; return; }
  try {
    const transcription = await new Speech().transcribe(file);
    $("#query").value = transcription.text;
    $("#transcribe-status").textContent = `Transcribed with ${transcription.backend}`;
  } catch (error) {
    $("#transcribe-status").textContent = error.message;
  }
};

window.addEventListener("pagehide", () => { stopPlayback(); stage?.dispose(); stage = null; });
