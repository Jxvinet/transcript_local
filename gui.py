"""Ventana: arrastra video/audio y guarda la transcripcion segun ajustes.ini."""
from __future__ import annotations

import os
import queue
import sys
import threading
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
import tkinter as tk

from transcribir import (
    AUDIO_EXT,
    apply_ssl_workaround,
    default_out_dir,
    ensure_ffmpeg_on_path,
    fmt_txt,
    load_ajustes,
    save_outputs,
    transcribe_file,
)

BG = "#F4F1EA"
CARD = "#FFFFFF"
ACCENT = "#B6752E"
INK = "#1F2A2E"
MUTED = "#6B7280"
BLUE = "#1F4E79"


def parse_drop_paths(widget, data: str) -> list[Path]:
    parts = widget.tk.splitlist(data)
    paths = []
    for raw in parts:
        p = Path(str(raw).strip().strip("{}"))
        if p.exists():
            paths.append(p)
    return paths


class App(TkinterDnD.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.ajustes = load_ajustes()
        apply_ssl_workaround(self.ajustes.get("ssl_inseguro", "0") in ("1", "true", "True", "yes"))
        self.out_dir = default_out_dir(self.ajustes)
        self.out_dir.mkdir(parents=True, exist_ok=True)

        self.title("Transcribir reunión")
        self.geometry("540x420")
        self.minsize(480, 380)
        self.configure(bg=BG)
        self.resizable(True, True)

        self._queue: queue.Queue = queue.Queue()
        self._busy = False
        self._pending: list[Path] = []
        self._seg_count = 0

        wrap = tk.Frame(self, bg=BG, padx=28, pady=24)
        wrap.pack(fill="both", expand=True)

        tk.Label(
            wrap,
            text="Transcribir reunión",
            font=("Segoe UI Semibold", 18),
            fg=INK,
            bg=BG,
        ).pack(anchor="w")
        modelo = self.ajustes.get("modelo", "small")
        formatos = self.ajustes.get("formatos", "docx")
        tk.Label(
            wrap,
            text=f"Suelta el vídeo o audio. Modelo {modelo} · salida {formatos}.",
            font=("Segoe UI", 10),
            fg=MUTED,
            bg=BG,
            wraplength=470,
            justify="left",
        ).pack(anchor="w", pady=(4, 16))

        self.drop = tk.Label(
            wrap,
            text="Arrastra aquí el archivo\n\nmp4  ·  mkv  ·  wav  ·  mp3",
            font=("Segoe UI", 12),
            fg=ACCENT,
            bg=CARD,
            relief="solid",
            bd=1,
            highlightthickness=2,
            highlightbackground="#E4D9C8",
            padx=20,
            pady=40,
        )
        self.drop.pack(fill="both", expand=True)

        self.progress = ttk.Progressbar(wrap, mode="indeterminate")
        self.progress.pack(fill="x", pady=(12, 0))

        self.status = tk.Label(
            wrap,
            text=f"Carpeta: {self.out_dir}",
            font=("Segoe UI", 9),
            fg=MUTED,
            bg=BG,
            anchor="w",
            wraplength=470,
            justify="left",
        )
        self.status.pack(fill="x", pady=(10, 8))

        btns = tk.Frame(wrap, bg=BG)
        btns.pack(fill="x")
        self._btn(btns, "Elegir archivo", self._pick, BLUE, "#FFFFFF").pack(side="left")
        self._btn(btns, "Abrir carpeta", self._open_out, "#E8E0D4", INK).pack(side="left", padx=(8, 0))
        self._btn(btns, "Ajustes", self._open_ajustes, "#E8E0D4", INK).pack(side="left", padx=(8, 0))

        self.drop.drop_target_register(DND_FILES)
        self.drop.dnd_bind("<<Drop>>", self._on_drop)
        self.drop.bind("<Button-1>", lambda _e: self._pick())

        self.after(200, self._poll)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.after(100, self._check_deps)

    def _btn(self, parent, text, cmd, bg, fg) -> tk.Button:
        return tk.Button(
            parent,
            text=text,
            command=cmd,
            font=("Segoe UI", 10),
            bg=bg,
            fg=fg,
            activebackground=bg,
            activeforeground=fg,
            relief="flat",
            padx=14,
            pady=6,
            cursor="hand2",
        )

    def _check_deps(self) -> None:
        if ensure_ffmpeg_on_path() is None:
            messagebox.showwarning(
                "Falta FFmpeg",
                "No encuentro ffmpeg.\n\n"
                "Instálalo con:\n  winget install Gyan.FFmpeg\n\n"
                "O pon la carpeta bin en el PATH / variable FFMPEG_PATH.",
            )

    def _on_drop(self, event) -> None:
        self._enqueue(parse_drop_paths(self, event.data))

    def _pick(self) -> None:
        files = filedialog.askopenfilenames(
            title="Elegir vídeo o audio",
            filetypes=[
                (
                    "Vídeo y audio",
                    "*.mp4 *.mkv *.mov *.avi *.webm *.mp3 *.wav *.m4a *.wma *.flac *.ogg",
                ),
                ("Todos", "*.*"),
            ],
        )
        self._enqueue([Path(f) for f in files])

    def _enqueue(self, paths: list[Path]) -> None:
        ok = []
        for p in paths:
            if p.is_file() and p.suffix.lower() in AUDIO_EXT:
                ok.append(p)
            elif p.is_file():
                messagebox.showwarning("Formato", f"No reconozco este tipo de archivo:\n{p.name}")
        if not ok:
            return
        self._pending.extend(ok)
        if not self._busy:
            self._start_next()
        else:
            self.status.config(text=f"En cola: {len(self._pending)} archivo(s). Transcribiendo…")

    def _start_next(self) -> None:
        if not self._pending:
            self._busy = False
            try:
                self.progress.stop()
            except tk.TclError:
                pass
            self.drop.config(text="Arrastra aquí el archivo\n\nmp4  ·  mkv  ·  wav  ·  mp3")
            return
        src = self._pending.pop(0)
        self._busy = True
        self._seg_count = 0
        self.drop.config(text=f"Transcribiendo…\n\n{src.name}\n\nNo cierres esta ventana.")
        self.status.config(text="Cargando modelo / procesando…")
        self.progress.start(12)
        threading.Thread(target=self._work, args=(src,), daemon=True).start()

    def _work(self, src: Path) -> None:
        try:
            formatos = [x.strip() for x in self.ajustes.get("formatos", "docx").split(",") if x.strip()]
            if not formatos:
                formatos = ["docx"]

            def on_segment(start, end, text):
                self._seg_count += 1
                self._queue.put(("prog", src.name, f"{fmt_txt(start)}  ·  {self._seg_count} segmentos"))

            rows = transcribe_file(
                src,
                modelo=self.ajustes.get("modelo", "small"),
                idioma=self.ajustes.get("idioma", "es"),
                device=self.ajustes.get("dispositivo", "cpu"),
                compute_type=self.ajustes.get("calculo", "int8"),
                on_segment=on_segment,
            )
            written = save_outputs(self.out_dir, src, rows, formatos)
            names = ", ".join(p.name for p in written)
            self._queue.put(("ok", src.name, names))
        except Exception as exc:
            self._queue.put(("err", src.name, f"{exc}\n\n{traceback.format_exc()}"))

    def _poll(self) -> None:
        try:
            while True:
                kind, name, payload = self._queue.get_nowait()
                if kind == "prog":
                    self.status.config(text=f"{name}: {payload}")
                elif kind == "ok":
                    try:
                        self.progress.stop()
                    except tk.TclError:
                        pass
                    self.status.config(text=f"Listo: {payload}")
                    self.drop.config(text=f"Hecho: {name}\n\nGuardado en la carpeta de salida")
                    self._busy = False
                    self._start_next()
                else:
                    try:
                        self.progress.stop()
                    except tk.TclError:
                        pass
                    self.status.config(text=f"Error con {name}")
                    messagebox.showerror("Error al transcribir", payload)
                    self._busy = False
                    self._start_next()
        except queue.Empty:
            pass
        self.after(250, self._poll)

    def _open_out(self) -> None:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        os.startfile(self.out_dir)  # noqa: S606

    def _open_ajustes(self) -> None:
        from transcribir import AJUSTES

        if not AJUSTES.exists():
            messagebox.showwarning("Ajustes", f"No encuentro {AJUSTES.name}")
            return
        os.startfile(AJUSTES)  # noqa: S606

    def _on_close(self) -> None:
        if self._busy:
            if not messagebox.askyesno(
                "Transcripción en curso",
                "Hay una transcripción en marcha. Si cierras, se cancela. ¿Salir igual?",
            ):
                return
        self.destroy()


def main() -> None:
    App().mainloop()


if __name__ == "__main__":
    main()
