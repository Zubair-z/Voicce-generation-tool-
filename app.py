#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZAS Vocalize v5.0 — Ultimate Edition
The Pinnacle of AI Voice Generation.
Features: Glassmorphism, Sidebar Navigation, Mixer Cards.
"""

import sys, io, os, json, threading, asyncio, subprocess
from pathlib import Path
import customtkinter as ctk
from tkinter import filedialog, messagebox
import tkinter as tk
import winsound

# ── Design System: Ultimate Edition ──────────────────────────────────────────
# Palettes
CLR_BG          = "#08090D"  # Pitch Black/Deep Space
CLR_SIDEBAR     = "#0F111A"  # Deep Sidebar
CLR_CARD        = "#141721"  # Card Surface
CLR_CARD_HOVER  = "#1C2030"  # Card Hover
CLR_BORDER      = "#222736"  # Subtle Border
CLR_GLOW        = "#3B82F6"  # Neon Blue
CLR_ACCENT_1    = "#8B5CF6"  # Electric Violet
CLR_ACCENT_2    = "#06B6D4"  # Cyan Glow

TEXT_MAIN       = "#F8FAFC"
TEXT_DIM        = "#64748B"
TEXT_SUB        = "#94A3B8"

# ── Fix Windows encoding ──────────────────────────────────────────────────────
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ctk.set_appearance_mode("dark")

# ── Voice Configuration (Full Set) ────────────────────────────────────────────
CHARACTERS = {
    # Premium AI
    "youtuber":          {"color": CLR_ACCENT_2, "icon": "🎥", "desc": "Casual American Male YouTubing"},
    "youtuber_female":   {"color": "#F472B6", "icon": "🎙️", "desc": "Warm American Female Vlogger"},
    # Narrators
    "narrator":          {"color": CLR_GLOW,     "icon": "📖", "desc": "British Male - Documentary"},
    "narrator_female":   {"color": "#60A5FA", "icon": "📚", "desc": "American Female - Audiobook"},
    "narrator_deep":     {"color": "#2563EB", "icon": "🎬", "desc": "Deep Voice - Movie Trailers"},
    # Experts
    "expert":            {"color": "#10B981", "icon": "🧠", "desc": "Confident Podcast/Tutorial"},
    "professor":         {"color": "#059669", "icon": "🎓", "desc": "Measured Academic Lecture"},
    "expert_female":     {"color": "#34D399", "icon": "📢", "desc": "News & Corporate Female"},
    # Characters
    "hero":              {"color": "#22C55E", "icon": "🛡️", "desc": "Bold Energetic Hero"},
    "villain":           {"color": "#EF4444", "icon": "😈", "desc": "Deep Menacing Villain"},
    "queen":             {"color": CLR_ACCENT_1, "icon": "👑", "desc": "Regal British Authority"},
    "child":             {"color": "#F97316", "icon": "🎈", "desc": "Bright Young Child"},
    "old_man":           {"color": "#D97706", "icon": "👴", "desc": "Wise Elder Mentor"},
    # Urdu / Hindi
    "urdu_male":         {"color": "#10B981", "icon": "🇵🇰", "desc": "Natural Urdu Male (Asad)"},
    "urdu_female":       {"color": "#34D399", "icon": "🇵🇰", "desc": "Natural Urdu Female (Uzma)"},
    "hindi_male":        {"color": "#F97316", "icon": "🇮🇳", "desc": "Natural Hindi Male (Madhur)"},
    "hindi_female":      {"color": "#FB923C", "icon": "🇮🇳", "desc": "Natural Hindi Female (Swara)"},
    # Moods
    "cheerful":          {"color": "#FACC15", "icon": "😊", "desc": "Upbeat Positive Energy"},
    "serious":           {"color": "#64748B", "icon": "😐", "desc": "Formal Elegant Tone"},
    "excited":           {"color": "#F87171", "icon": "🔥", "desc": "Hype & High Energy"},
}

# ══════════════════════════════════════════════════════════════════════════════
class UltimateSceneCard(ctk.CTkFrame):
    """Ultimate Mixer-style Scene Card."""

    def __init__(self, master, scene_id: int, on_delete, **kwargs):
        super().__init__(master, fg_color=CLR_CARD, border_color=CLR_BORDER, border_width=1, corner_radius=15, **kwargs)
        self.scene_id = scene_id
        self.on_delete = on_delete
        self.output_path = None

        self.grid_columnconfigure(1, weight=1)

        # ── Mixer ID Strip ────────────────────────────────────────────────────
        self.id_strip = ctk.CTkFrame(self, width=6, fg_color=CLR_BORDER, corner_radius=0)
        self.id_strip.grid(row=0, column=0, rowspan=2, sticky="ns", padx=(0, 10))

        # ── Header: Scene Info ────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=1, columnspan=2, sticky="ew", padx=10, pady=(10, 0))
        
        self.title_label = ctk.CTkLabel(
            header, text=f"SCENE {scene_id:02d}",
            font=ctk.CTkFont(family="Inter", size=10, weight="bold"),
            text_color=TEXT_DIM
        )
        self.title_label.pack(side="left")

        self.char_var = ctk.StringVar(value="narrator")
        self.char_drop = ctk.CTkOptionMenu(
            header, values=list(CHARACTERS.keys()), variable=self.char_var,
            width=140, height=24, corner_radius=6,
            fg_color=CLR_SIDEBAR, button_color=CLR_BORDER,
            font=ctk.CTkFont(size=11), dropdown_fg_color=CLR_SIDEBAR
        )
        self.char_drop.pack(side="right")

        # ── Body: Text Area ───────────────────────────────────────────────────
        self.text_box = ctk.CTkTextbox(
            self, height=80, corner_radius=12,
            fg_color=CLR_SIDEBAR, border_color=CLR_BORDER, border_width=1,
            text_color=TEXT_MAIN, font=ctk.CTkFont(size=13, family="Inter"),
            wrap="word", padx=10, pady=10
        )
        self.text_box.grid(row=1, column=1, sticky="ew", padx=10, pady=10)

        # ── Right Controls: Audio & Actions ──────────────────────────────────
        controls = ctk.CTkFrame(self, fg_color="transparent")
        controls.grid(row=1, column=2, padx=12, pady=10)

        self.play_btn = ctk.CTkButton(
            controls, text="⏵", width=38, height=38, corner_radius=19,
            fg_color=CLR_BORDER, hover_color=CLR_GLOW, text_color="white",
            state="disabled", font=ctk.CTkFont(size=18),
            command=self._play_audio
        )
        self.play_btn.pack(pady=4)

        self.del_btn = ctk.CTkButton(
            controls, text="✕", width=38, height=38, corner_radius=19,
            fg_color="transparent", hover_color="#EF4444", text_color=TEXT_DIM,
            font=ctk.CTkFont(size=14),
            command=lambda: on_delete(self)
        )
        self.del_btn.pack(pady=4)

    def _play_audio(self):
        if self.output_path and os.path.exists(self.output_path):
            winsound.PlaySound(self.output_path, winsound.SND_FILENAME | winsound.SND_ASYNC)

    def set_status(self, status: str, path: str = None):
        colors = {"generating": CLR_ACCENT_2, "done": "#22C55E", "failed": "#EF4444", "": CLR_BORDER}
        self.id_strip.configure(fg_color=colors.get(status, CLR_BORDER))
        if status == "done" and path:
            self.output_path = str(Path(path).absolute())
            self.play_btn.configure(state="normal", fg_color="#22C55E")

    def get_data(self):
        return {
            "id": self.scene_id,
            "character": self.char_var.get(),
            "text": self.text_box.get("1.0", "end").strip(),
            "output_file": f"scene_{self.scene_id}.wav"
        }

# ══════════════════════════════════════════════════════════════════════════════
class UltimateVocalizeApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("ZAS Vocalize v5.0 — Ultimate Edition")
        self.geometry("1280x850")
        self.minsize(1100, 750)
        self.configure(fg_color=CLR_BG)

        self.scene_rows: list[UltimateSceneCard] = []
        self.current_project = "untitled_project"
        self._build_sidebar()
        self._build_main_area()

    def _build_sidebar(self):
        # ── Sidebar Container ────────────────────────────────────────────────
        self.sidebar = ctk.CTkFrame(self, width=280, fg_color=CLR_SIDEBAR, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Brand Space
        brand = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand.pack(fill="x", pady=40, padx=30)
        
        ctk.CTkLabel(
            brand, text="ZAS", 
            font=ctk.CTkFont(family="Inter", size=28, weight="bold"),
            text_color=CLR_GLOW
        ).pack(side="left")
        ctk.CTkLabel(
            brand, text="Vocalize", 
            font=ctk.CTkFont(family="Inter", size=24),
            text_color=TEXT_MAIN
        ).pack(side="left", padx=5)

        # AI Generator Section
        ctk.CTkLabel(self.sidebar, text="AI MAGIC GENERATOR", font=ctk.CTkFont(size=10, weight="bold"), text_color=TEXT_DIM).pack(anchor="w", padx=30, pady=(20, 10))
        
        self.ai_input = ctk.CTkEntry(
            self.sidebar, placeholder_text="Describe your story...",
            height=40, corner_radius=10, fg_color=CLR_BG, border_color=CLR_BORDER,
            font=ctk.CTkFont(size=12)
        )
        self.ai_input.pack(fill="x", padx=30, pady=5)

        self.ai_model = ctk.CTkOptionMenu(
            self.sidebar, values=["llama3", "qwen3:4b"], height=36, corner_radius=10,
            fg_color=CLR_BG, button_color=CLR_BORDER
        )
        self.ai_model.pack(fill="x", padx=30, pady=5)

        self.ai_btn = ctk.CTkButton(
            self.sidebar, text="✨ Generate Script", height=44, corner_radius=12,
            fg_color=CLR_ACCENT_1, hover_color="#7C3AED", font=ctk.CTkFont(size=13, weight="bold"),
            command=self._generate_ai_script
        )
        self.ai_btn.pack(fill="x", padx=30, pady=(15, 30))

        # Project Stats
        stats = ctk.CTkFrame(self.sidebar, fg_color=CLR_BG, corner_radius=15, border_width=1, border_color=CLR_BORDER)
        stats.pack(fill="x", padx=30, pady=20)
        
        ctk.CTkLabel(stats, text="Project Status", font=ctk.CTkFont(size=11, weight="bold")).pack(pady=(12, 5))
        self.stat_scenes = ctk.CTkLabel(stats, text="0 Scenes", font=ctk.CTkFont(size=14, weight="bold"), text_color=TEXT_SUB)
        self.stat_scenes.pack()
        
        self.progress_bar = ctk.CTkProgressBar(stats, width=180, height=6, fg_color=CLR_SIDEBAR, progress_color=CLR_ACCENT_2)
        self.progress_bar.pack(pady=15)
        self.progress_bar.set(0)

        # Footer version
        ctk.CTkLabel(self.sidebar, text="v5.0 Ultimate Powered by Ollama", font=ctk.CTkFont(size=10), text_color=TEXT_DIM).pack(side="bottom", pady=20)

    def _build_main_area(self):
        # ── Main Container ───────────────────────────────────────────────────
        self.main = ctk.CTkFrame(self, fg_color="transparent")
        self.main.pack(side="right", fill="both", expand=True, padx=40, pady=40)

        # Top Bar: Project Settings & Gallery
        top_bar = ctk.CTkFrame(self.main, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 20))

        # Project Name
        proj_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        proj_frame.pack(side="left")
        ctk.CTkLabel(proj_frame, text="PROJECT NAME", font=ctk.CTkFont(size=10, weight="bold"), text_color=TEXT_DIM).pack(anchor="w")
        self.proj_entry = ctk.CTkEntry(
            proj_frame, width=250, height=44, corner_radius=12,
            fg_color=CLR_SIDEBAR, border_color=CLR_BORDER, border_width=1,
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.proj_entry.pack(anchor="w", pady=5)
        self.proj_entry.insert(0, "viral_project_v5")

        # Voice Marketplace
        self.voice_scroll = ctk.CTkScrollableFrame(
            self.main, height=120, fg_color=CLR_SIDEBAR, corner_radius=20,
            border_color=CLR_BORDER, border_width=1, orientation="horizontal"
        )
        self.voice_scroll.pack(fill="x", pady=(0, 30))
        
        for name, cfg in CHARACTERS.items():
            self._add_gallery_item(name, cfg)

        # Editor Area
        editor_ctrl = ctk.CTkFrame(self.main, fg_color="transparent")
        editor_ctrl.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(editor_ctrl, text="TIMELINE EDITOR", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_DIM).pack(side="left")
        
        ctk.CTkButton(
            editor_ctrl, text="+ Add Scene", width=110, height=32, corner_radius=8,
            fg_color=CLR_SIDEBAR, hover_color=CLR_CARD_HOVER, border_width=1, border_color=CLR_BORDER,
            command=self._add_scene
        ).pack(side="right")

        # Scene List Scroll
        self.scene_scroll = ctk.CTkScrollableFrame(self.main, fg_color="transparent", corner_radius=0)
        self.scene_scroll.pack(fill="both", expand=True)
        self.scene_scroll.grid_columnconfigure(0, weight=1)

        # Bottom Master Action
        footer = ctk.CTkFrame(self.main, fg_color="transparent")
        footer.pack(fill="x", pady=(20, 0))

        self.folder_btn = ctk.CTkButton(
            footer, text="Open Export Folder", width=180, height=52, corner_radius=15,
            fg_color=CLR_SIDEBAR, border_width=1, border_color=CLR_BORDER,
            command=self._open_output
        )
        self.folder_btn.pack(side="left")

        self.render_btn = ctk.CTkButton(
            footer, text="MASTER RENDER AUDIO", width=350, height=60, corner_radius=20,
            fg_color=CLR_GLOW, hover_color="#2563EB", text_color="white",
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self._generate
        )
        self.render_btn.pack(side="right")

        # Initial Scene
        self._add_scene()

    def _add_gallery_item(self, name, cfg):
        item = ctk.CTkFrame(self.voice_scroll, fg_color=CLR_BG, width=160, height=90, corner_radius=15, border_color=CLR_BORDER, border_width=1)
        item.pack(side="left", padx=10, pady=10)
        item.pack_propagate(False)

        badge = ctk.CTkFrame(item, fg_color=cfg["color"], width=30, height=30, corner_radius=8)
        badge.pack(side="left", padx=12)
        ctk.CTkLabel(badge, text=cfg["icon"], font=ctk.CTkFont(size=14)).place(relx=0.5, rely=0.5, anchor="center")

        content = ctk.CTkFrame(item, fg_color="transparent")
        content.pack(side="left", fill="both", expand=True, pady=12)
        
        ctk.CTkLabel(content, text=name.split('_')[0].upper(), font=ctk.CTkFont(size=10, weight="bold"), text_color=TEXT_MAIN).pack(anchor="w")
        
        test_btn = ctk.CTkButton(
            content, text="Test Preview", width=80, height=22, corner_radius=6,
            fg_color=CLR_SIDEBAR, hover_color=cfg["color"], font=ctk.CTkFont(size=9),
            command=lambda n=name: self._test_voice(n)
        )
        test_btn.pack(anchor="w", pady=4)

    # ── Logic: Scripts & Render ──────────────────────────────────────────────
    def _test_voice(self, char):
        threading.Thread(target=self._run_voice_test, args=(char,), daemon=True).start()

    def _run_voice_test(self, char):
        try:
            from super_voice_tool import generate_preview
            path = Path("G:/Voice generation tool/temp_previews")
            path.mkdir(exist_ok=True)
            out_file = path / f"preview_{char}.wav"
            if generate_preview(char, str(out_file)):
                winsound.PlaySound(str(out_file), winsound.SND_FILENAME | winsound.SND_ASYNC)
        except: pass

    def _generate_ai_script(self):
        topic = self.ai_input.get().strip()
        if not topic: return
        self.ai_btn.configure(state="disabled", text="✨ Writing...")
        threading.Thread(target=self._run_ollama, args=(topic,), daemon=True).start()

    def _run_ollama(self, topic):
        try:
            from super_voice_tool import generate_script_with_ollama
            data = generate_script_with_ollama(topic, self.ai_model.get())
            self.after(0, self._apply_ai_script, data)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("AI Error", str(e)))
        self.after(0, lambda: self.ai_btn.configure(state="normal", text="✨ Generate Script"))

    def _apply_ai_script(self, data):
        for r in self.scene_rows: r.destroy()
        self.scene_rows.clear()
        
        scenes = data.get("scenes", [])
        for scene in scenes:
            row = self._add_scene()
            row.char_var.set(scene.get("character", "narrator"))
            row.text_box.insert("1.0", scene.get("text", ""))
        self.stat_scenes.configure(text=f"{len(scenes)} Scenes")

    def _add_scene(self) -> UltimateSceneCard:
        scene_id = len(self.scene_rows) + 1
        card = UltimateSceneCard(self.scene_scroll, scene_id=scene_id, on_delete=self._delete_scene)
        card.grid(row=len(self.scene_rows), column=0, sticky="ew", padx=10, pady=10)
        self.scene_rows.append(card)
        self.stat_scenes.configure(text=f"{len(self.scene_rows)} Scenes")
        return card

    def _delete_scene(self, card: UltimateSceneCard):
        if len(self.scene_rows) <= 1: return
        self.scene_rows.remove(card)
        card.destroy()
        self.stat_scenes.configure(text=f"{len(self.scene_rows)} Scenes")
        for i, c in enumerate(self.scene_rows, 1):
            c.scene_id = i
            c.title_label.configure(text=f"SCENE {i:02d}")

    def _generate(self):
        scenes = [r.get_data() for r in self.scene_rows if r.get_data()["text"]]
        if not scenes: return

        project = self.proj_entry.get().strip().replace(" ", "_") or "untitled_project"
        self.current_project = project
        script_data = {"script_metadata": {"total_scenes": len(scenes), "project_name": project}, "scenes": scenes}

        base = Path("G:/Voice generation tool/scripts")
        base.mkdir(exist_ok=True)
        tmp_json = base / f"{project}.json"
        with open(tmp_json, "w", encoding="utf-8") as f:
            json.dump(script_data, f, indent=2, ensure_ascii=False)

        self.render_btn.configure(state="disabled", text="RENDERING...")
        self.progress_bar.set(0)
        threading.Thread(target=self._run_render, args=(str(tmp_json),), daemon=True).start()

    def _run_render(self, json_path: str):
        try:
            from super_voice_tool import process_json_file
            def cb(curr, total, sid, char, status):
                self.after(0, lambda: self.progress_bar.set(curr/total))
                if 0 <= sid-1 < len(self.scene_rows):
                    p = f"G:/Voice generation tool/audio_output/{self.current_project}/scene_{sid}.wav"
                    self.after(0, lambda: self.scene_rows[sid-1].set_status(status, p))

            summary = process_json_file(json_path, progress_callback=cb)
            self.after(0, self._on_render_done, summary)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Render Error", str(e)))
            self.after(0, lambda: self.render_btn.configure(state="normal", text="MASTER RENDER AUDIO"))

    def _on_render_done(self, summary):
        self.render_btn.configure(state="normal", text="MASTER RENDER AUDIO")
        messagebox.showinfo("ZAS Vocalize Ultimate", f"Project exported successfully!\n({summary['success_count']} scenes)")

    def _open_output(self):
        path = f"G:/Voice generation tool/audio_output/{self.proj_entry.get().strip()}"
        if os.path.exists(path): os.startfile(path)
        else: os.startfile("G:/Voice generation tool/audio_output")

if __name__ == "__main__":
    app = UltimateVocalizeApp()
    app.mainloop()
