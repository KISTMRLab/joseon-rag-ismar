import { createStage } from "/static/avatar.js?v=20261006-paper3";
import { Speech } from "/static/speech.js?v=20261006-paper3";
import {prepareApplicationMotion,gestureSummary} from "/static/application-gesture.js?v=20261006-paper3";
import { setupVoiceInput } from "/static/voice-input.js?v=20261006-paper3";

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
let activeMotion = null;

function stopPlayback() {
  playGeneration++;
  if (delayTimer !== null) { clearTimeout(delayTimer); delayTimer = null; delayResolve?.(); delayResolve = null; }
  speech?.cancel();
  activeMotion?.onEnd();activeMotion=null;stage?.clearMotion();
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
    stage.camera.position.set(0,1.5,3.6);stage.camera.lookAt(0,1,0);
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
    await stage.ready;
    for (const event of result.agent.events) {
      if (generation !== playGeneration) return;
      let selected=null;
      try{selected=await prepareApplicationMotion(stage,event.text,{mode:'wild'});}
      catch(error){$("#motion").textContent=`Recorded co-speech unavailable: ${error.message}`;}
      if(generation!==playGeneration)return;
      activeMotion=selected?.motion||null;
      await speech.speak(event.text,{backend,
        onStart:()=>{activeMotion?.onStart();const sources=event.citations?.length?` · sources ${event.citations.join(", ")}`:"";$("#motion").textContent=(selected?`Speaking · ${gestureSummary(selected.data)}`:'Speaking · no recorded co-speech clip')+sources;},
        onProgress:clock=>activeMotion?.onProgress(clock),
        onEnd:()=>{activeMotion?.onEnd();activeMotion=null;stage.clearMotion();stage.gesture('idle');}
      });
      if (generation !== playGeneration) return;
      // Speech completion already awaited; do not add the estimated duration.
    }
    if (generation === playGeneration) { stage.gesture("idle"); stage.setSpeech(false); $("#motion").textContent = "Playback complete"; }
  } catch (error) {
    if (generation !== playGeneration) return;
    stopPlayback();
    $("#motion").textContent = `Playback unavailable: ${error.message}`;
  }
};

// Microphone recording or an audio file is transcribed by the local /api/asr backend.
const stopVoiceInput = setupVoiceInput(new Speech(), $("#query"), $("#record"), $("#audio-input"), $("#transcribe-status"));

window.addEventListener("pagehide", () => { stopVoiceInput(); stopPlayback(); stage?.dispose(); stage = null; });
