#!/usr/bin/env python3
"""Masaüstü arayüzü: sentetik Türkçe OCR PDF üreticisi."""

from __future__ import annotations

import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

from belge_uret import generate_pdf

BG = "#f3f5f6"
PANEL = "#ffffff"
FG = "#182b3a"
MUTED = "#536574"
ACCENT = "#176b67"


class GeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sentetik OCR Belge Üretici")
        self.root.geometry("720x610")
        self.root.minsize(640, 560)
        self.root.configure(bg=BG)
        self.events = queue.Queue()
        self.output_path = tk.StringVar(value=str(Path.home() / "Documents" / "ocr_ornegi.pdf"))
        self.pages = tk.StringVar(value="Rastgele (1–10)")
        self.tables_per_page = tk.IntVar(value=0)
        self.words_per_page = tk.IntVar(value=160)
        self.dpi = tk.IntVar(value=180)
        self.seed = tk.StringVar()
        self.status = tk.StringVar(value="PDF ayarlarını seçip üretimi başlatın.")
        self._build()

    def _build(self):
        outer = tk.Frame(self.root, bg=BG, padx=32, pady=28)
        outer.pack(fill="both", expand=True)
        tk.Label(outer, text="Sentetik OCR Belge Üretici", bg=BG, fg=FG, font=("Helvetica", 22, "bold")).pack(anchor="w")
        tk.Label(
            outer,
            text="Türkçe içerikli, taranmış görüntü biçiminde 1–10 sayfalı PDF oluşturun.",
            bg=BG,
            fg=MUTED,
            font=("Helvetica", 12),
            wraplength=620,
            justify="left",
        ).pack(anchor="w", pady=(7, 22))

        card = tk.Frame(outer, bg=PANEL, highlightbackground="#d5dde1", highlightthickness=1, padx=20, pady=16)
        card.pack(fill="x")
        card.columnconfigure(1, weight=1)
        self._field_label(card, "Sayfa sayısı", 0)
        self._option(card, self.pages, ["Rastgele (1–10)"] + [str(i) for i in range(1, 11)], 0)
        self._field_label(card, "Tablo adedi / sayfa", 1)
        self._spin(card, self.tables_per_page, 0, 2, 1, 1)
        tk.Label(card, text="0 = tablo yok; 1 veya 2 ile ekleyin.", bg=PANEL, fg=MUTED, font=("Helvetica", 10)).grid(row=2, column=1, sticky="w", pady=(0, 6))
        self._field_label(card, "Metin yoğunluğu", 3)
        self._spin(card, self.words_per_page, 40, 400, 20, 3)
        tk.Label(card, text="Kelime / sayfa · 40–400", bg=PANEL, fg=MUTED, font=("Helvetica", 10)).grid(row=4, column=1, sticky="w", pady=(0, 6))
        self._field_label(card, "Çözünürlük", 5)
        dpi_frame = tk.Frame(card, bg=PANEL)
        dpi_frame.grid(row=5, column=1, sticky="w", pady=8)
        tk.Spinbox(dpi_frame, from_=100, to=400, increment=20, textvariable=self.dpi, width=8, bg="white", fg=FG, insertbackground=FG, relief="solid", bd=1).pack(side="left", ipady=5)
        tk.Label(dpi_frame, text="DPI · yüksek değer daha büyük dosya üretir", bg=PANEL, fg=MUTED, font=("Helvetica", 10)).pack(side="left", padx=(10, 0))
        self._field_label(card, "Rastgelelik tohumu", 6)
        tk.Entry(card, textvariable=self.seed, width=23, bg="white", fg=FG, insertbackground=FG, relief="solid", bd=1).grid(row=6, column=1, sticky="w", pady=8, ipady=5)
        tk.Label(card, text="Aynı örneği yeniden üretmek için isteğe bağlı sayı.", bg=PANEL, fg=MUTED, font=("Helvetica", 10)).grid(row=7, column=1, sticky="w", pady=(0, 7))

        tk.Label(outer, text="Çıktı PDF'si", bg=BG, fg=FG, font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(20, 5))
        output_row = tk.Frame(outer, bg=BG)
        output_row.pack(fill="x", pady=(4, 18))
        tk.Entry(output_row, textvariable=self.output_path, bg="white", fg=FG, insertbackground=FG, relief="solid", bd=1).pack(side="left", fill="x", expand=True, ipady=7)
        self._button(output_row, "Gözat…", self._choose_output, secondary=True).pack(side="left", padx=(9, 0))

        tk.Label(
            outer,
            text="Her sayfa tek bir görüntüdür; seçilebilir metin katmanı yoktur. Belgeler sentetiktir.",
            bg=BG,
            fg=MUTED,
            font=("Helvetica", 10),
            wraplength=620,
            justify="left",
        ).pack(anchor="w", pady=(0, 14))
        tk.Label(outer, textvariable=self.status, bg=BG, fg=MUTED, font=("Helvetica", 11), wraplength=620, justify="left").pack(anchor="w")
        self.button = self._button(outer, "PDF Oluştur", self._start)
        self.button.pack(anchor="e", pady=(16, 0))

    @staticmethod
    def _field_label(parent, text, row):
        tk.Label(parent, text=text, bg=PANEL, fg=FG, font=("Helvetica", 11)).grid(row=row, column=0, sticky="w", padx=(0, 20), pady=8)

    @staticmethod
    def _option(parent, variable, values, row):
        control = tk.OptionMenu(parent, variable, *values)
        control.configure(bg="white", fg=FG, activebackground="#e7eeee", activeforeground=FG, relief="solid", bd=1, highlightthickness=0, anchor="w", width=20)
        control["menu"].configure(bg="white", fg=FG, activebackground="#dcebea", activeforeground=FG)
        control.grid(row=row, column=1, sticky="w", pady=6)

    @staticmethod
    def _spin(parent, variable, start, end, increment, row):
        control = tk.Spinbox(parent, from_=start, to=end, increment=increment, textvariable=variable, width=8, bg="white", fg=FG, insertbackground=FG, relief="solid", bd=1)
        control.grid(row=row, column=1, sticky="w", pady=6, ipady=5)

    @staticmethod
    def _button(parent, text, command, secondary=False):
        bg = "#e5ecee" if secondary else ACCENT
        fg = FG if secondary else "white"
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground="#d3e0e0" if secondary else "#125753",
            activeforeground=fg,
            relief="flat",
            padx=16,
            pady=9,
            font=("Helvetica", 11, "bold"),
        )

    def _choose_output(self):
        selected = filedialog.asksaveasfilename(
            title="PDF kaydet",
            defaultextension=".pdf",
            initialfile=Path(self.output_path.get()).name or "ocr_ornegi.pdf",
            filetypes=[("PDF dosyası", "*.pdf")],
        )
        if selected:
            self.output_path.set(selected)

    def _start(self):
        target = self.output_path.get().strip()
        if not target:
            messagebox.showerror("Eksik bilgi", "PDF için bir çıktı konumu seçin.", parent=self.root)
            return
        if Path(target).suffix.lower() != ".pdf":
            target += ".pdf"
            self.output_path.set(target)
        try:
            dpi = int(self.dpi.get())
            if not 100 <= dpi <= 400:
                raise ValueError
            tables_per_page = int(self.tables_per_page.get())
            if not 0 <= tables_per_page <= 2:
                raise ValueError
            words_per_page = int(self.words_per_page.get())
            if not 40 <= words_per_page <= 400:
                raise ValueError
            seed_text = self.seed.get().strip()
            seed = int(seed_text) if seed_text else None
        except (ValueError, tk.TclError):
            messagebox.showerror("Geçersiz değer", "Tablo sayısı 0–2, kelime sayısı 40–400, DPI 100–400 olmalı; tohum tam sayı olmalı.", parent=self.root)
            return
        pages = None if self.pages.get().startswith("Rastgele") else int(self.pages.get())
        self.button.configure(state="disabled")
        self.status.set(f"Sayfa görüntüleri hazırlanıyor… ({words_per_page} kelime, {tables_per_page} tablo/sayfa)")
        threading.Thread(target=self._generate, args=(target, pages, tables_per_page, words_per_page, dpi, seed), daemon=True).start()
        self.root.after(100, self._poll)

    def _generate(self, target, pages, tables_per_page, words_per_page, dpi, seed):
        try:
            result, total = generate_pdf(target, pages, tables_per_page, words_per_page, dpi, seed)
            self.events.put(("ok", result, total))
        except Exception as exc:
            self.events.put(("error", str(exc)))

    def _poll(self):
        try:
            event = self.events.get_nowait()
        except queue.Empty:
            self.root.after(100, self._poll)
            return
        self.button.configure(state="normal")
        if event[0] == "ok":
            _, path, total = event
            self.output_path.set(str(path))
            self.status.set(f"Hazır: {total} sayfa · {self.words_per_page.get()} kelime/sayfa · {self.tables_per_page.get()} tablo/sayfa")
            messagebox.showinfo("PDF oluşturuldu", f"{total} sayfalı taranmış PDF kaydedildi:\n{path}", parent=self.root)
        else:
            self.status.set("Üretim tamamlanamadı.")
            messagebox.showerror("PDF oluşturulamadı", event[1], parent=self.root)


def main():
    root = tk.Tk()
    GeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
