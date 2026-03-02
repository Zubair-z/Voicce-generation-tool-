#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

"""
=============================================================
  SUPER VOICE TOOL v3.0
  Natural YouTuber-Style Voices via Microsoft Edge TTS
  Standalone + n8n + Web UI Ready
=============================================================
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("VoiceTool")

# ─── Character → Edge TTS Neural Voice Map ───────────────────────────────────
# Microsoft Free Neural Voices — Real human-like speech
CHARACTER_VOICES = {

    # ── YouTuber / Content Creator ────────────────────────────────────────────
    "youtuber": {
        "voice": "en-US-AndrewNeural",
        "rate": "+8%", "pitch": "+0Hz",
        "description": "Casual American male — natural YouTuber style ⭐"
    },
    "youtuber_female": {
        "voice": "en-US-JennyNeural",
        "rate": "+5%", "pitch": "+0Hz",
        "description": "Warm American female — vlog & tutorial style ⭐"
    },

    # ── Narrator / Storyteller ────────────────────────────────────────────────
    "narrator": {
        "voice": "en-GB-RyanNeural",
        "rate": "+0%", "pitch": "-5Hz",
        "description": "British male — calm, authoritative documentary"
    },
    "narrator_female": {
        "voice": "en-US-AriaNeural",
        "rate": "-5%", "pitch": "+0Hz",
        "description": "Warm American female — audiobook narrator"
    },
    "narrator_deep": {
        "voice": "en-US-SteffanNeural",
        "rate": "-5%", "pitch": "-8Hz",
        "description": "Deep American male — movie trailer narrator"
    },

    # ── Expert / Educator ─────────────────────────────────────────────────────
    "expert": {
        "voice": "en-US-BrianNeural",
        "rate": "+0%", "pitch": "-3Hz",
        "description": "Confident American male — podcast & explainer"
    },
    "professor": {
        "voice": "en-US-EricNeural",
        "rate": "-8%", "pitch": "-5Hz",
        "description": "Clear measured American male — academic & lecture"
    },
    "expert_female": {
        "voice": "en-US-MonicaNeural",
        "rate": "+0%", "pitch": "+0Hz",
        "description": "Professional American female — news & corporate"
    },

    # ── Characters ────────────────────────────────────────────────────────────
    "hero": {
        "voice": "en-US-GuyNeural",
        "rate": "+10%", "pitch": "+0Hz",
        "description": "Bold energetic American male — action hero"
    },
    "villain": {
        "voice": "en-US-ChristopherNeural",
        "rate": "-18%", "pitch": "-15Hz",
        "description": "Deep slow American male — menacing villain"
    },
    "queen": {
        "voice": "en-GB-SoniaNeural",
        "rate": "-5%", "pitch": "+5Hz",
        "description": "Regal British female — queen & authority"
    },
    "child": {
        "voice": "en-US-AnaNeural",
        "rate": "+20%", "pitch": "+15Hz",
        "description": "Bright young American female — child character"
    },
    "old_man": {
        "voice": "en-US-RogerNeural",
        "rate": "-12%", "pitch": "-10Hz",
        "description": "Wise older American male — mentor & elder"
    },

    # ── Accents & Styles ──────────────────────────────────────────────────────
    "british_male": {
        "voice": "en-GB-ThomasNeural",
        "rate": "+0%", "pitch": "+0Hz",
        "description": "Casual British male — everyday conversation"
    },
    "british_female": {
        "voice": "en-GB-LibbyNeural",
        "rate": "+5%", "pitch": "+0Hz",
        "description": "Friendly British female — casual & warm"
    },
    "australian_male": {
        "voice": "en-AU-WilliamNeural",
        "rate": "+5%", "pitch": "+0Hz",
        "description": "Australian male — relaxed & friendly"
    },
    "australian_female": {
        "voice": "en-AU-NatashaNeural",
        "rate": "+0%", "pitch": "+0Hz",
        "description": "Australian female — natural conversation"
    },
    "indian_male": {
        "voice": "en-IN-PrabhatNeural",
        "rate": "+0%", "pitch": "+0Hz",
        "description": "Indian English male — clear & professional"
    },

    # ── Mood / Tone ───────────────────────────────────────────────────────────
    "cheerful": {
        "voice": "en-US-SaraNeural",
        "rate": "+10%", "pitch": "+8Hz",
        "description": "Upbeat cheerful American female — positive energy"
    },
    "serious": {
        "voice": "en-US-NancyNeural",
        "rate": "-5%", "pitch": "-5Hz",
        "description": "Serious elegant American female — formal tone"
    },
    "friendly": {
        "voice": "en-US-MichelleNeural",
        "rate": "+5%", "pitch": "+3Hz",
        "description": "Friendly warm American female — conversational"
    },
    "excited": {
        "voice": "en-US-GuyNeural",
        "rate": "+20%", "pitch": "+10Hz",
        "description": "Energetic excited male — hype & announcements"
    },

    # ── Urdu (Pakistan) 🇵🇰 ────────────────────────────────────────────────────
    "urdu_male": {
        "voice": "ur-PK-AsadNeural",
        "rate": "+0%", "pitch": "+0Hz",
        "description": "Natural Urdu male voice (Asad)"
    },
    "urdu_female": {
        "voice": "ur-PK-UzmaNeural",
        "rate": "+0%", "pitch": "+0Hz",
        "description": "Natural Urdu female voice (Uzma)"
    },

    # ── Hindi (India) 🇮🇳 ──────────────────────────────────────────────────────
    "hindi_male": {
        "voice": "hi-IN-MadhurNeural",
        "rate": "+0%", "pitch": "+0Hz",
        "description": "Natural Hindi male voice (Madhur)"
    },
    "hindi_female": {
        "voice": "hi-IN-SwaraNeural",
        "rate": "+0%", "pitch": "+0Hz",
        "description": "Natural Hindi female voice (Swara)"
    },
}

FALLBACK_CHARACTER = "narrator"


# ─── Ollama Integration ───────────────────────────────────────────────────────

def generate_script_with_ollama(prompt: str, model: str = "llama3") -> dict:
    """Generate a multi-scene script JSON using local Ollama model."""
    try:
        import ollama
    except ImportError:
        raise ImportError("Ollama library not found. Run: uv add ollama")

    system_prompt = f"""
    You are a professional AI Script Writer. 
    TASK: Write a highly engaging 5-scene viral script about the user's topic.
    
    CONSTRAINTS:
    1. Output MUST be a single, valid JSON object.
    2. Exactly 5 scenes are required. Not 2, not 3, but EXACTLY 5.
    3. Do NOT include any text outside the JSON. No introduction, no summary, no markdown snippets.
    4. Text must be natural and human-like.

    JSON STRUCTURE:
    {{
      "script_metadata": {{
        "total_scenes": 5,
        "project_name": "viral_video",
        "description": "Script about {prompt}"
      }},
      "scenes": [
        {{ "id": 1, "character": "youtuber", "text": "...", "output_file": "scene_1.wav" }},
        {{ "id": 2, "character": "expert", "text": "...", "output_file": "scene_2.wav" }},
        {{ "id": 3, "character": "villain", "text": "...", "output_file": "scene_3.wav" }},
        {{ "id": 4, "character": "narrator", "text": "...", "output_file": "scene_4.wav" }},
        {{ "id": 5, "character": "child", "text": "...", "output_file": "scene_5.wav" }}
      ]
    }}

    AVAILABLE CHARACTERS (Use hamesha lowercase):
    youtuber, youtuber_female, narrator, narrator_female, narrator_deep, expert, professor, expert_female, 
    hero, villain, queen, child, old_man, urdu_male, urdu_female, hindi_male, hindi_female,
    british_male, british_female, australian_male, australian_female, indian_male, cheerful, serious, friendly, excited
    """

    user_message = f"Write a complete 5-scene script about: {prompt}. Ensure the output is strictly valid JSON."

    try:
        log.info(f"Calling Ollama ({model}) for a 5-scene script...")
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            options={"temperature": 0.7}
        )
        
        content = response['message']['content'].strip()
        
        # Enhanced JSON extraction (looking for first { and last })
        first_brace = content.find('{')
        last_brace = content.rfind('}')
        
        if first_brace != -1 and last_brace != -1:
            content = content[first_brace:last_brace+1]
        
        script_data = json.loads(content)
        
        # Final check for scene count
        actual_count = len(script_data.get("scenes", []))
        log.info(f"Ollama generated {actual_count} scenes.")
        
        return script_data
        
    except Exception as e:
        log.error(f"Ollama/JSON error: {e}")
        # Return a basic fallback structure if LLM fails
        return {
            "script_metadata": {"total_scenes": 1, "project_name": "fallback"},
            "scenes": [{"id": 1, "character": "narrator", "text": f"Error generating script: {str(e)}", "output_file": "scene_1.wav"}]
        }





# ─── Core Generation ──────────────────────────────────────────────────────────

async def generate_scene_async(text: str, character: str, output_path: str) -> bool:
    """Generate a single scene using edge-tts (async)."""
    try:
        import edge_tts
    except ImportError:
        log.error("edge-tts not installed. Run: uv add edge-tts")
        return False

    char = character.lower().strip()
    if char not in CHARACTER_VOICES:
        log.warning(f"Unknown character '{char}' → using '{FALLBACK_CHARACTER}'")
        char = FALLBACK_CHARACTER

    profile = CHARACTER_VOICES[char]
    # Use quiet logging for previews
    if "preview" not in output_path:
        log.info(f"  Voice: {profile['voice']} | {profile['description']}")

    try:
        communicate = edge_tts.Communicate(
            text=text,
            voice=profile["voice"],
            rate=profile["rate"],
            pitch=profile["pitch"]
        )
        await communicate.save(output_path)
        return True
    except Exception as e:
        log.error(f"  edge-tts error: {e}")
        return False


def generate_preview(character: str, output_path: str) -> bool:
    """Generate a short preview audio for a voice."""
    if character not in CHARACTER_VOICES:
        character = FALLBACK_CHARACTER
        
    text = f"Hello! This is the {character.replace('_', ' ')} voice. Do I sound natural?"
    if "urdu" in character:
        text = "سلام! میں آپ کی ٹول کی ایک آواز ہوں۔ کیا میں ٹھیک لگ رہا ہوں؟"
    elif "hindi" in character:
        text = "नमस्ते! मैं आपके टूल की एक आवाज़ हूँ। क्या मैं ठीक लग रहा हूँ?"
        
    return generate_scene(text, character, output_path)


def generate_scene(text: str, character: str, output_path: str) -> bool:
    """Sync wrapper for async generation."""
    return asyncio.run(generate_scene_async(text, character, output_path))


def load_json(json_path: str) -> dict:
    path = Path(json_path)
    if not path.exists():
        raise FileNotFoundError(f"Not found: {json_path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if "scenes" not in data:
        raise KeyError("Missing 'scenes' key in JSON")
    return data


def get_output_dir(json_path: str, project_name: str) -> Path:
    base = Path(json_path).parent
    out = base / "audio_output" / project_name
    out.mkdir(parents=True, exist_ok=True)
    return out


def process_json_file(json_file_path: str, progress_callback=None) -> dict:
    """Main processing function — used by CLI and Web UI."""
    data        = load_json(json_file_path)
    metadata    = data.get("script_metadata", {})
    project     = metadata.get("project_name", "project")
    scenes      = data["scenes"]
    output_dir  = get_output_dir(json_file_path, project)
    results     = []

    log.info(f"Project: {project} | Scenes: {len(scenes)}")
    log.info(f"Output: {output_dir}")

    for i, scene in enumerate(scenes, 1):
        scene_id  = scene.get("id", i)
        character = scene.get("character", FALLBACK_CHARACTER).lower().strip()
        text      = scene.get("text", "").strip()
        out_file  = scene.get("output_file", f"scene_{scene_id}.wav")
        out_path  = str(output_dir / out_file)

        log.info(f"\n  Scene {scene_id} [{character.upper()}]")
        log.info(f"  Text: {text[:80]}{'...' if len(text) > 80 else ''}")

        if progress_callback:
            progress_callback(i, len(scenes), scene_id, character, "generating")

        if not text:
            results.append({"scene_id": scene_id, "status": "skipped", "reason": "empty_text"})
            continue

        success = generate_scene(text, character, out_path)

        if success:
            log.info(f"  Saved: {out_path}")
            results.append({
                "scene_id": scene_id,
                "character": character,
                "output_file": out_path,
                "filename": out_file,
                "status": "success"
            })
            if progress_callback:
                progress_callback(i, len(scenes), scene_id, character, "done")
        else:
            log.error(f"  FAILED scene {scene_id}")
            results.append({"scene_id": scene_id, "character": character, "status": "failed"})

    summary = {
        "project_name": project,
        "output_directory": str(output_dir),
        "timestamp": datetime.now().isoformat(),
        "total_scenes": len(results),
        "success_count": len([r for r in results if r["status"] == "success"]),
        "failed_count": len([r for r in results if r["status"] == "failed"]),
        "results": results
    }

    summary_file = output_dir / "generation_summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    return summary


# ─── CLI Entry Point ──────────────────────────────────────────────────────────

def main():
    sep = "=" * 60
    print(f"\n{sep}")
    print("  SUPER VOICE TOOL v3.0 — Natural YouTuber Voices")
    print(f"{sep}")

    if len(sys.argv) < 2:
        print("\n  Usage: python super_voice_tool.py <script.json>")
        print("  Or:    uv run python super_voice_tool.py <script.json>\n")
        sys.exit(1)

    json_path = sys.argv[1].strip().strip('"')
    log.info(f"Loading: {json_path}")

    summary = process_json_file(json_path)

    print(f"\n{sep}")
    print(f"  DONE — {summary['project_name'].upper()}")
    print(f"{sep}")
    print(f"  Success : {summary['success_count']}/{summary['total_scenes']} scenes")
    print(f"  Failed  : {summary['failed_count']} scenes")
    print(f"  Output  : {summary['output_directory']}")
    print(f"{sep}\n")


if __name__ == "__main__":
    main()
