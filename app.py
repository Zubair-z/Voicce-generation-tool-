#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VoiceCraft Studio v3.5 — Pro Edition
Desktop app with Ollama AI, Voice Gallery, and Real-time Previews
"""

import sys, io, os, json, threading, asyncio, subprocess
from pathlib import Path
import customtkinter as ctk
from tkinter import filedialog, messagebox
import tkinter as tk
import winsound  # Native Windows audio playback

# ── Fix Windows encoding ──────────────────────────────────────────────────────
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ── App Theme ─────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ── Character Config ──────────────────────────────────────────────────────────
CHARACTERS = {
    # YouTuber / Creator
    "youtuber":          {"color": "#F5A623", "pill_bg": "#2e2010", "desc": "Casual American male YouTuber ⭐"},
    "youtuber_female":   {"color": "#FF9ED2", "pill_bg": "#2e1020", "desc": "Warm American female vlogger ⭐"},
    # Narrator
    "narrator":          {"color": "#5B8DEF", "pill_bg": "#1a2540", "desc": "British male — documentary"},
    "narrator_female":   {"color": "#82AAFF", "pill_bg": "#101a38", "desc": "American female — audiobook"},
    "narrator_deep":     {"color": "#3a6fd8", "pill_bg": "#0d1a35", "desc": "Deep male — movie trailer"},
    # Expert / Educator
    "expert":            {"color": "#1ABC9C", "pill_bg": "#0a2520", "desc": "Podcast & explainer"},
    "professor":         {"color": "#16a085", "pill_bg": "#091a18", "desc": "Academic & lecture"},
    "expert_female":     {"color": "#48cfad", "pill_bg": "#0a201a", "desc": "News & corporate female"},
    # Characters
    "hero":              {"color": "#4CAF50", "pill_bg": "#122514", "desc": "Bold action hero"},
    "villain":           {"color": "#E74C3C", "pill_bg": "#2a1010", "desc": "Deep menacing villain"},
    "queen":             {"color": "#9B59B6", "pill_bg": "#1e1030", "desc": "Regal British queen"},
    "child":             {"color": "#F39C12", "pill_bg": "#2e1e05", "desc": "Bright young child"},
    "old_man":           {"color": "#a0896e", "pill_bg": "#251a0d", "desc": "Wise elder mentor"},
    # Urdu / Hindi
    "urdu_male":         {"color": "#00A651", "pill_bg": "#052010", "desc": "Natural Urdu male (Asad) 🇵🇰"},
    "urdu_female":       {"color": "#00A651", "pill_bg": "#052010", "desc": "Natural Urdu female (Uzma) 🇵🇰"},
    "hindi_male":        {"color": "#FF671F", "pill_bg": "#2a1505", "desc": "Natural Hindi male (Madhur) 🇮🇳"},
    "hindi_female":      {"color": "#FF671F", "pill_bg": "#2a1505", "desc": "Natural Hindi female (Swara) 🇮🇳"},
    # Accents
    "british_male":      {"color": "#c8a96e", "pill_bg": "#251d0d", "desc": "Casual British male"},
    "british_female":    {"color": "#e8c99e", "pill_bg": "#2a1f0a", "desc": "Friendly British female"},
    "australian_male":   {"color": "#70c8a0", "pill_bg": "#0e2518", "desc": "Relaxed Australian male"},
    "australian_female": {"color": "#90e8c0", "pill_bg": "#0d2018", "desc": "Natural Australian female"},
    "indian_male":       {"color": "#f0a060", "pill_bg": "#2a1a08", "desc": "Indian English professional"},
    # Mood
    "cheerful":          {"color": "#FFD700", "pill_bg": "#2a2200", "desc": "Upbeat positive energy"},
    "serious":           {"color": "#a0a8c0", "pill_bg": "#18192a", "desc": "Formal elegant tone"},
    "friendly":          {"color": "#80c8ff", "pill_bg": "#102030", "desc": "Warm conversational"},
    "excited":           {"color": "#FF6B35", "pill_bg": "#2a1208", "desc": "Hype & announcements"},
}

# ══════════════════════════════════════════════════════════════════════════════
class SceneRow(ctk.CTkFrame):
    """One scene row in the editor."""

    def __init__(self, master, scene_id: int, on_delete, **kwargs):
        super().__init__(master, fg_color="#1e2130", corner_radius=10, **kwargs)
        self.scene_id  = scene_id
        self.on_delete = on_delete
        self.output_path = None

        self.grid_columnconfigure(2, weight=1)

        # ── Scene number badge ────────────────────────────────────────────────
        badge = ctk.CTkLabel(
            self, text=f"  {scene_id}  ",
            fg_color="#2d3250", corner_radius=6,
            text_color="#8899cc", font=ctk.CTkFont(size=12, weight="bold")
        )
        badge.grid(row=0, column=0, padx=(10, 6), pady=10, sticky="ns")

        # ── Character dropdown ────────────────────────────────────────────────
        self.char_var = ctk.StringVar(value="narrator")
        char_menu = ctk.CTkOptionMenu(
            self, values=list(CHARACTERS.keys()),
            variable=self.char_var, width=140,
            fg_color="#252840", button_color="#3a3f6e",
            font=ctk.CTkFont(size=12)
        )
        char_menu.grid(row=0, column=1, padx=6, pady=10)

        # ── Text input ────────────────────────────────────────────────────────
        self.text_box = ctk.CTkTextbox(
            self, height=60, corner_radius=8,
            fg_color="#252840", border_color="#3a3f6e", border_width=1,
            font=ctk.CTkFont(size=13), wrap="word"
        )
        self.text_box.grid(row=0, column=2, padx=6, pady=10, sticky="ew")

        # ── Play Button ───────────────────────────────────────────────────────
        self.play_btn = ctk.CTkButton(
            self, text="▶", width=32, height=32,
            fg_color="#2d3a6e", hover_color="#3a4a8e",
            text_color="#ffffff", corner_radius=8,
            state="disabled",
            command=self._play_audio
        )
        self.play_btn.grid(row=0, column=3, padx=4)

        # ── Status label ──────────────────────────────────────────────────────
        self.status_label = ctk.CTkLabel(
            self, text="", width=28,
            font=ctk.CTkFont(size=16)
        )
        self.status_label.grid(row=0, column=4, padx=4)

        # ── Delete button ─────────────────────────────────────────────────────
        del_btn = ctk.CTkButton(
            self, text="✕", width=32, height=32,
            fg_color="#3a1a1a", hover_color="#6b2020",
            text_color="#ff6b6b", corner_radius=8,
            command=lambda: on_delete(self)
        )
        del_btn.grid(row=0, column=5, padx=(4, 10), pady=10)

    def _play_audio(self):
        if self.output_path and os.path.exists(self.output_path):
            try:
                winsound.PlaySound(self.output_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
            except:
                os.startfile(self.output_path)

    def get_data(self):
        return {
            "id": self.scene_id,
            "character": self.char_var.get(),
            "text": self.text_box.get("1.0", "end").strip(),
            "output_file": f"scene_{self.scene_id}.wav"
        }

    def set_status(self, status: str, path: str = None):
        icons = {"generating": "⏳", "done": "✅", "failed": "❌", "": ""}
        self.status_label.configure(text=icons.get(status, ""))
        if status == "done" and path:
            self.output_path = path
            self.play_btn.configure(state="normal", fg_color="#4CAF50")


# ══════════════════════════════════════════════════════════════════════════════
class VoiceCraftApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("VoiceCraft Studio v3.5 - Pro Edition")
        self.geometry("1100x850")
        self.minsize(950, 700)
        self.configure(fg_color="#131625")

        self.scene_rows: list[SceneRow] = []
        self.output_dir = None
        self._build_ui()

    # ── Build UI ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        # ── Header ────────────────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="#1a1e35", corner_radius=0, height=70)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header, text="🎙  VoiceCraft Studio PRO",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color="#7da8ff"
        ).pack(side="left", padx=24, pady=14)

        # ── Ollama Area ───────────────────────────────────────────────────────
        ollama_frame = ctk.CTkFrame(header, fg_color="#252b45", corner_radius=10)
        ollama_frame.pack(side="right", padx=20, pady=10)

        ctk.CTkLabel(ollama_frame, text="AI Script (Ollama):", font=ctk.CTkFont(size=11)).pack(side="left", padx=(10, 5))
        
        self.ollama_topic = ctk.CTkEntry(ollama_frame, placeholder_text="Topic...", width=180, fg_color="#1a1e35")
        self.ollama_topic.pack(side="left", padx=5)

        self.ollama_model = ctk.CTkOptionMenu(ollama_frame, values=["llama3", "qwen3:4b"], width=100, fg_color="#1a1e35")
        self.ollama_model.pack(side="left", padx=5)

        self.ai_btn = ctk.CTkButton(
            ollama_frame, text="✨ Generate", width=80, fg_color="#5b8def",
            command=self._generate_ai_script
        )
        self.ai_btn.pack(side="left", padx=(5, 10))

        # ── Main layout ───────────────────────────────────────────────────────
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=16)
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(2, weight=1)

        # ── Voice Gallery / Tester ───────────────────────────────────────────
        gallery = ctk.CTkScrollableFrame(main, height=100, fg_color="#1a1e35", corner_radius=10, orientation="horizontal")
        gallery.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        
        ctk.CTkLabel(gallery, text="Voice Gallery:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#6070a0").pack(side="left", padx=10)

        for name, cfg in CHARACTERS.items():
            pill = ctk.CTkFrame(gallery, fg_color=cfg["pill_bg"], corner_radius=20)
            pill.pack(side="left", padx=4, pady=10)
            
            ctk.CTkLabel(pill, text=f" {name} ", font=ctk.CTkFont(size=11), text_color=cfg["color"]).pack(side="left", padx=(4, 2))
            
            test_btn = ctk.CTkButton(
                pill, text="🔊", width=24, height=24, corner_radius=12,
                fg_color="transparent", hover_color="#ffffff22",
                command=lambda n=name: self._test_voice(n)
            )
            test_btn.pack(side="left", padx=(0, 4))
            
            # Tooltip-ish help
            pill.bind("<Enter>", lambda e, d=cfg["desc"]: self._set_status(d))

        # ── Scenes section ────────────────────────────────────────────────────
        scenes_header = ctk.CTkFrame(main, fg_color="transparent")
        scenes_header.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        scenes_header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(scenes_header, text="Script Editor", font=ctk.CTkFont(size=16, weight="bold"), text_color="#c8d4ff").grid(row=0, column=0, sticky="w")

        ctk.CTkButton(scenes_header, text="+ Add Scene", width=110, height=30, fg_color="#2d3a6e", command=self._add_scene).grid(row=0, column=1, sticky="e")

        # ── Scrollable scene list ─────────────────────────────────────────────
        self.scene_scroll = ctk.CTkScrollableFrame(main, fg_color="#161928", corner_radius=12, border_color="#2a2f50", border_width=1)
        self.scene_scroll.grid(row=2, column=0, sticky="nsew", pady=(0, 12))
        main.grid_rowconfigure(2, weight=1)
        self.scene_scroll.grid_columnconfigure(0, weight=1)

        # Start with one scene
        self._add_scene()

        # ── Progress bar ──────────────────────────────────────────────────────
        self.progress_var = ctk.DoubleVar(value=0)
        self.progress_bar = ctk.CTkProgressBar(main, variable=self.progress_var, fg_color="#1e2130", progress_color="#5B8DEF", height=8)
        self.progress_bar.grid(row=3, column=0, sticky="ew", pady=(0, 8))

        self.status_label = ctk.CTkLabel(main, text="Ready", font=ctk.CTkFont(size=12), text_color="#6070a0")
        self.status_label.grid(row=4, column=0, sticky="w")

        # ── Bottom controls ───────────────────────────────────────────────────
        bottom = ctk.CTkFrame(main, fg_color="transparent")
        bottom.grid(row=5, column=0, sticky="ew", pady=(8, 0))
        bottom.grid_columnconfigure(1, weight=1)

        self.project_var = ctk.StringVar(value="my_pro_video")
        ctk.CTkEntry(bottom, textvariable=self.project_var, width=150, fg_color="#1e2130", placeholder_text="Project Name").grid(row=0, column=0, padx=(0, 8))

        self.generate_btn = ctk.CTkButton(bottom, text="🎙  Generate All Pro Voices", height=48, fg_color="#2d54d0", hover_color="#3a68f0", font=ctk.CTkFont(size=15, weight="bold"), command=self._generate)
        self.generate_btn.grid(row=0, column=1, sticky="ew", padx=(0, 8))

        self.open_folder_btn = ctk.CTkButton(bottom, text="📁 Open Folder", width=130, height=48, fg_color="#1a3520", hover_color="#1e4528", state="disabled", command=self._open_output)
        self.open_folder_btn.grid(row=0, column=2)

    # ── AI Generation ─────────────────────────────────────────────────────────
    def _generate_ai_script(self):
        topic = self.ollama_topic.get().strip()
        if not topic:
            messagebox.showwarning("Topic Required", "Please enter a topic for the AI to write about.")
            return
        
        self.ai_btn.configure(state="disabled", text="✨ Writing...")
        self._set_status(f"Ollama is writing a script about '{topic}'...")
        
        threading.Thread(target=self._run_ollama, args=(topic,), daemon=True).start()

    def _run_ollama(self, topic):
        try:
            from super_voice_tool import generate_script_with_ollama
            model = self.ollama_model.get()
            script_data = generate_script_with_ollama(topic, model)
            
            self.after(0, self._apply_ai_script, script_data)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("AI Error", f"Ollama failed: {e}"))
            self.after(0, lambda: self.ai_btn.configure(state="normal", text="✨ Generate"))

    def _apply_ai_script(self, data):
        # Clear current rows
        for r in self.scene_rows: r.destroy()
        self.scene_rows.clear()
        
        # Apply data
        meta = data.get("script_metadata", {})
        self.project_var.set(meta.get("project_name", "ai_video"))
        
        scenes = data.get("scenes", [])
        for scene in scenes:
            row = self._add_scene()
            row.char_var.set(scene.get("character", "narrator"))
            row.text_box.insert("1.0", scene.get("text", ""))
        
        self.ai_btn.configure(state="normal", text="✨ Generate")
        self._set_status(f"AI script loaded: {len(scenes)} scenes generated.")
        if len(scenes) < 5:
            messagebox.showinfo("Wait", f"AI generated {len(scenes)} scenes. You can add more manually or try again for a full script.")


    # ── Voice Testing ─────────────────────────────────────────────────────────
    def _test_voice(self, char):
        self._set_status(f"Testing voice: {char}...")
        threading.Thread(target=self._run_voice_test, args=(char,), daemon=True).start()

    def _run_voice_test(self, char):
        try:
            from super_voice_tool import generate_preview
            path = Path("G:/Voice generation tool/temp_previews")
            path.mkdir(exist_ok=True)
            out_file = path / f"preview_{char}.wav"
            
            if generate_preview(char, str(out_file)):
                winsound.PlaySound(str(out_file), winsound.SND_FILENAME | winsound.SND_ASYNC)
        except Exception as e:
            print(f"Test error: {e}")

    # ── Scene management ──────────────────────────────────────────────────────
    def _add_scene(self) -> SceneRow:
        scene_id = len(self.scene_rows) + 1
        row = SceneRow(self.scene_scroll, scene_id=scene_id, on_delete=self._delete_scene)
        row.grid(row=len(self.scene_rows), column=0, sticky="ew", padx=8, pady=4)
        self.scene_rows.append(row)
        return row

    def _delete_scene(self, row: SceneRow):
        if len(self.scene_rows) <= 1: return
        self.scene_rows.remove(row)
        row.destroy()
        for i, r in enumerate(self.scene_rows, 1): r.scene_id = i

    # ── Main Generation ───────────────────────────────────────────────────────
    def _generate(self):
        scenes = [r.get_data() for r in self.scene_rows if r.get_data()["text"]]
        if not scenes: return

        project = self.project_var.get().strip().replace(" ", "_") or "pro_video"
        script_data = {"script_metadata": {"total_scenes": len(scenes), "project_name": project}, "scenes": scenes}

        base = Path("G:/Voice generation tool/scripts")
        base.mkdir(exist_ok=True)
        tmp_json = base / f"{project}.json"
        with open(tmp_json, "w", encoding="utf-8") as f:
            json.dump(script_data, f, indent=2, ensure_ascii=False)

        self.progress_var.set(0)
        self.generate_btn.configure(state="disabled", text="Generating...")
        
        threading.Thread(target=self._run_generation, args=(str(tmp_json),), daemon=True).start()

    def _run_generation(self, json_path: str):
        try:
            from super_voice_tool import process_json_file
            def progress_cb(current, total, scene_id, char, status):
                self.after(0, lambda: self.progress_var.set(current/total))
                idx = scene_id - 1
                if 0 <= idx < len(self.scene_rows):
                    # We need the output path to enable play button
                    project = self.project_var.get().strip()
                    path = f"G:/Voice generation tool/audio_output/{project}/scene_{scene_id}.wav"
                    self.after(0, lambda i=idx, s=status, p=path: self.scene_rows[i].set_status(s, p))

            summary = process_json_file(json_path, progress_callback=progress_cb)
            self.output_dir = summary["output_directory"]
            self.after(0, self._on_done, summary)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", str(e)))
            self.after(0, lambda: self.generate_btn.configure(state="normal", text="🎙  Generate All Pro Voices"))

    def _on_done(self, summary):
        self.generate_btn.configure(state="normal", text="🎙  Generate All Pro Voices")
        self.open_folder_btn.configure(state="normal")
        self._set_status(f"Done! Saved to {summary['output_directory']}")
        messagebox.showinfo("Success", f"Generated {summary['success_count']} scenes!")

    def _set_status(self, msg: str):
        self.status_label.configure(text=msg)

    def _open_output(self):
        if self.output_dir: os.startfile(self.output_dir)

if __name__ == "__main__":
    app = VoiceCraftApp()
    app.mainloop()
