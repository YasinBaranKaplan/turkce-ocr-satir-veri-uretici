#!/usr/bin/env python3
"""Masaüstü arayüzü: Türkçe OCR satır verisi üreticisi."""

from __future__ import annotations

import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

from satir_uret import generate_dataset

BG = "#f3f5f6"
PANEL = "#ffffff"
FG = "#182b3a"
MUTED = "#536574"
ACCENT = "#176b67"


class GeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Türkçe OCR Satır Verisi Üretici")
        self.root.geometry("760x820")
        self.root.minsize(660, 760)
        self.root.configure(bg=BG)
        self.events = queue.Queue()
        self.output_root = tk.StringVar(value=str(Path.home() / "Documents" / "ocr_satir_verisi"))
        self.examples = tk.StringVar(value="200")
        self.min_words = tk.StringVar(value="4")
        self.max_words = tk.StringVar(value="9")
        self.seed = tk.StringVar()
        self.font_path = tk.StringVar()
        self.image_scale = tk.StringVar(value="Standart (1×)")
        self.background = tk.StringVar(value="Beyaz")
        self.distortion = tk.StringVar(value="Orta")
        self.status = tk.StringVar(value="Ayarları seçip satır verisi üretimini başlatın.")
        self._build()

    def _build(self):
        outer = tk.Frame(self.root, bg=BG, padx=32, pady=28)
        outer.pack(fill="both", expand=True)
        tk.Label(outer, text="Türkçe OCR Satır Verisi Üretici", bg=BG, fg=FG, font=("Helvetica", 22, "bold")).pack(anchor="w")
        tk.Label(
            outer,
            text="OCR eğitimi için Türkçe satır görselleri ve metin etiketleri oluşturun.",
            bg=BG,
            fg=MUTED,
            font=("Helvetica", 12),
            wraplength=660,
            justify="left",
        ).pack(anchor="w", pady=(7, 22))

        card = tk.Frame(outer, bg=PANEL, highlightbackground="#d5dde1", highlightthickness=1, padx=20, pady=16)
        card.pack(fill="x")
        card.columnconfigure(1, weight=1)

        self._field_label(card, "Satır görseli sayısı", 0)
        self._spin(card, self.examples, 1, 50000, 100, 0)
        tk.Label(card, text="Her satır ayrı bir PNG örneği olarak kaydedilir.", bg=PANEL, fg=MUTED, font=("Helvetica", 10)).grid(row=1, column=1, sticky="w", pady=(0, 6))

        self._field_label(card, "Satır başına kelime", 2)
        word_frame = tk.Frame(card, bg=PANEL)
        word_frame.grid(row=2, column=1, sticky="w", pady=8)
        tk.Label(word_frame, text="En az", bg=PANEL, fg=FG, font=("Helvetica", 10)).pack(side="left", padx=(0, 6))
        self._spin(word_frame, self.min_words, 1, 30, 1).pack(side="left")
        tk.Label(word_frame, text="En çok", bg=PANEL, fg=FG, font=("Helvetica", 10)).pack(side="left", padx=(14, 6))
        self._spin(word_frame, self.max_words, 1, 30, 1).pack(side="left")

        self._field_label(card, "Rastgelelik tohumu", 3)
        tk.Entry(card, textvariable=self.seed, width=24, bg="white", fg=FG, insertbackground=FG, relief="solid", bd=1).grid(row=3, column=1, sticky="w", pady=8, ipady=5)
        tk.Label(card, text="Aynı ayarlarla benzer veri setini yeniden üretmek için sayı girin.", bg=PANEL, fg=MUTED, font=("Helvetica", 10)).grid(row=4, column=1, sticky="w", pady=(0, 6))

        self._field_label(card, "Yazı tipi (isteğe bağlı)", 5)
        font_row = tk.Frame(card, bg=PANEL)
        font_row.grid(row=5, column=1, sticky="ew", pady=8)
        tk.Entry(font_row, textvariable=self.font_path, bg="white", fg=FG, insertbackground=FG, relief="solid", bd=1).pack(side="left", fill="x", expand=True, ipady=5)
        self._button(font_row, "TTF/OTF seç…", self._choose_font, secondary=True).pack(side="left", padx=(9, 0))

        self._field_label(card, "Görsel ölçeği", 6)
        self._option(card, self.image_scale, ["Standart (1×)", "Yüksek (1.5×)", "Çok yüksek (2×)"], 6)
        self._field_label(card, "Arka plan", 7)
        self._option(card, self.background, ["Beyaz", "Krem", "Gri"], 7)
        self._field_label(card, "Bozulma düzeyi", 8)
        self._option(card, self.distortion, ["Az", "Orta", "Yüksek"], 8)

        tk.Label(outer, text="Çıktı ana klasörü", bg=BG, fg=FG, font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(20, 5))
        output_row = tk.Frame(outer, bg=BG)
        output_row.pack(fill="x", pady=(4, 18))
        tk.Entry(output_row, textvariable=self.output_root, bg="white", fg=FG, insertbackground=FG, relief="solid", bd=1).pack(side="left", fill="x", expand=True, ipady=7)
        self._button(output_row, "Klasör seç…", self._choose_output, secondary=True).pack(side="left", padx=(9, 0))

        tk.Label(
            outer,
            text="Her üretim yeni bir klasör açar. İçinde images/ PNG'leri ve labels.tsv bulunur; dosyada belge, sayfa ve satır sırası yer alır. Sayfalar 25 satırdan oluşur.",
            bg=BG,
            fg=MUTED,
            font=("Helvetica", 10),
            wraplength=660,
            justify="left",
        ).pack(anchor="w", pady=(0, 14))
        tk.Label(outer, textvariable=self.status, bg=BG, fg=MUTED, font=("Helvetica", 11), wraplength=660, justify="left").pack(anchor="w")
        self.button = self._button(outer, "Veri Seti Oluştur", self._start)
        self.button.pack(anchor="e", pady=(16, 0))

    @staticmethod
    def _field_label(parent, text, row):
        tk.Label(parent, text=text, bg=PANEL, fg=FG, font=("Helvetica", 11)).grid(row=row, column=0, sticky="w", padx=(0, 20), pady=8)

    @staticmethod
    def _spin(parent, variable, start, end, increment, row=None):
        control = tk.Spinbox(parent, from_=start, to=end, increment=increment, textvariable=variable, width=10, bg="white", fg=FG, insertbackground=FG, relief="solid", bd=1)
        if row is not None:
            control.grid(row=row, column=1, sticky="w", pady=6, ipady=5)
        else:
            control.pack(side="left", ipady=4)
        return control

    @staticmethod
    def _option(parent, variable, values, row):
        control = tk.OptionMenu(parent, variable, *values)
        control.configure(bg="white", fg=FG, activebackground="#e7eeee", activeforeground=FG, relief="solid", bd=1, highlightthickness=0, anchor="w", width=20)
        control["menu"].configure(bg="white", fg=FG, activebackground="#dcebea", activeforeground=FG)
        control.grid(row=row, column=1, sticky="w", pady=6)

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
        selected = filedialog.askdirectory(title="Veri seti klasörlerini kaydet")
        if selected:
            self.output_root.set(selected)

    def _choose_font(self):
        selected = filedialog.askopenfilename(
            title="Türkçe destekli yazı tipi seç",
            filetypes=[("Yazı tipi dosyası", "*.ttf *.otf"), ("Tüm dosyalar", "*.*")],
        )
        if selected:
            self.font_path.set(selected)

    def _start(self):
        target = self.output_root.get().strip()
        if not target:
            messagebox.showerror("Eksik bilgi", "Veri seti için bir çıktı klasörü seçin.", parent=self.root)
            return
        try:
            examples = int(self.examples.get())
            min_words = int(self.min_words.get())
            max_words = int(self.max_words.get())
            if examples < 1 or min_words < 1 or max_words < min_words or max_words > 30:
                raise ValueError
            seed_text = self.seed.get().strip()
            seed = int(seed_text) if seed_text else None
        except (ValueError, tk.TclError):
            messagebox.showerror("Geçersiz değer", "Örnek sayısı en az 1 olmalı; kelime aralığı 1–30 arasında olmalı ve en az değeri en çok değerini aşmamalı. Tohum tam sayı olmalı.", parent=self.root)
            return

        font_path = self.font_path.get().strip() or None
        image_scale = {"Standart (1×)": 1.0, "Yüksek (1.5×)": 1.5, "Çok yüksek (2×)": 2.0}[self.image_scale.get()]
        background = self.background.get().lower()
        distortion = {"Az": "az", "Orta": "orta", "Yüksek": "yuksek"}[self.distortion.get()]
        self.button.configure(state="disabled")
        self.status.set("Satır görselleri hazırlanıyor… (%d örnek)" % examples)
        threading.Thread(target=self._generate, args=(target, examples, min_words, max_words, seed, font_path, image_scale, background, distortion), daemon=True).start()
        self.root.after(100, self._poll)

    def _generate(self, target, examples, min_words, max_words, seed, font_path, image_scale, background, distortion):
        try:
            result, total = generate_dataset(target, examples, min_words, max_words, seed, font_path, image_scale, background, distortion)
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
            self.status.set("Hazır: %d satır görseli · labels.tsv · %s" % (total, path))
            messagebox.showinfo("Veri seti oluşturuldu", "%d satır görseli kaydedildi:\n%s" % (total, path), parent=self.root)
        else:
            self.status.set("Üretim tamamlanamadı.")
            messagebox.showerror("Veri seti oluşturulamadı", event[1], parent=self.root)


def main():
    root = tk.Tk()
    GeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
