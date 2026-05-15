import customtkinter as ctk
import random
import animations

PURPLE       = "#534AB7"
PURPLE_HOVER = "#3C3489"
BG_CARD      = ("gray85", "gray20")


def _primary_btn(parent, text, command, width=100):
    return ctk.CTkButton(parent, text=text, command=command,
                         fg_color=PURPLE, hover_color=PURPLE_HOVER,
                         font=ctk.CTkFont(size=13), width=width)


def _ghost_btn(parent, text, command, width=100):
    return ctk.CTkButton(parent, text=text, command=command,
                         fg_color="transparent",
                         hover_color=("gray80", "gray30"),
                         border_width=1, border_color=("gray60", "gray40"),
                         text_color=("gray10", "gray90"),
                         font=ctk.CTkFont(size=13), width=width)


def _danger_btn(parent, text, command, width=32):
    return ctk.CTkButton(parent, text=text, command=command,
                         fg_color="transparent",
                         hover_color=("gray80", "gray30"),
                         text_color=("#A32D2D", "#F09595"),
                         font=ctk.CTkFont(size=12), width=width)


# ─── Main frame ───────────────────────────────────────────────────────────────

class FlashcardsFrame(ctk.CTkFrame):
    """
    Three sub-views in one frame:
      • Deck list  – shows all decks, lets you create/delete them
      • Deck editor – manage cards inside a chosen deck
      • Study mode  – flip cards, mark known/unknown
    """

    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.decks = {}          # {deck_name: [{"front": str, "back": str}, ...]}
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._show_deck_list()

    # ── View switchers ────────────────────────────────────────────────────────

    def _show_deck_list(self):
        self._clear()
        DeckListView(self, self.decks,
                     on_open=self._show_deck_editor,
                     on_delete=self._delete_deck,
                     on_create=self._create_deck).grid(row=0, column=0, sticky="nsew")

    def _show_deck_editor(self, deck_name):
        self._clear()
        DeckEditorView(self, deck_name, self.decks[deck_name],
                       on_back=self._show_deck_list,
                       on_study=lambda: self._show_study(deck_name)).grid(
            row=0, column=0, sticky="nsew")

    def _show_study(self, deck_name):
        self._clear()
        StudyView(self, deck_name, self.decks[deck_name],
                  on_back=lambda: self._show_deck_editor(deck_name)).grid(
            row=0, column=0, sticky="nsew")

    def _create_deck(self, name):
        name = name.strip()
        if not name or name in self.decks:
            return False
        self.decks[name] = []
        self._show_deck_list()
        return True

    def _delete_deck(self, name):
        self.decks.pop(name, None)
        self._show_deck_list()

    def _clear(self):
        for w in self.winfo_children():
            w.destroy()


# ─── Deck list ────────────────────────────────────────────────────────────────

class DeckListView(ctk.CTkFrame):
    def __init__(self, master, decks, on_open, on_delete, on_create):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.decks = decks
        self.on_open = on_open
        self.on_delete = on_delete
        self.on_create = on_create

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(self, text="Flashcards",
                     font=ctk.CTkFont(size=20, weight="bold")).grid(
            row=0, column=0, padx=20, pady=(20, 4), sticky="w")

        inp = ctk.CTkFrame(self, fg_color="transparent")
        inp.grid(row=1, column=0, padx=20, pady=(0, 8), sticky="ew")
        inp.grid_columnconfigure(0, weight=1)
        self.deck_entry = ctk.CTkEntry(inp, placeholder_text="New deck name…", height=34)
        self.deck_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.deck_entry.bind("<Return>", lambda _: self._do_create())
        create_btn = _primary_btn(inp, "+ Create", self._do_create, width=80)
        create_btn.grid(row=0, column=1)
        animations.click_pulse(create_btn)

        self.list_area = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.list_area.grid(row=2, column=0, padx=20, pady=(0, 16), sticky="nsew")
        self.list_area.grid_columnconfigure(0, weight=1)

        self._render()

    def _do_create(self):
        name = self.deck_entry.get()
        if self.on_create(name):
            self.deck_entry.delete(0, "end")

    def _render(self):
        for w in self.list_area.winfo_children():
            w.destroy()

        if not self.decks:
            ctk.CTkLabel(self.list_area, text="No decks yet — create one above!",
                         text_color=("gray60", "gray50")).grid(
                row=0, column=0, pady=20)
            return

        for i, name in enumerate(self.decks):
            count = len(self.decks[name])
            row = ctk.CTkFrame(self.list_area, fg_color=BG_CARD, corner_radius=8)
            row.grid(row=i, column=0, sticky="ew", pady=3)
            row.grid_columnconfigure(0, weight=1)

            ctk.CTkButton(
                row, text=f"  {name}",
                anchor="w",
                fg_color="transparent", hover_color=("gray78", "gray28"),
                text_color=("gray10", "gray90"),
                font=ctk.CTkFont(size=14, weight="bold"),
                command=lambda n=name: self.on_open(n)
            ).grid(row=0, column=0, sticky="ew", padx=(4, 0))

            ctk.CTkLabel(
                row,
                text=f"{count} card{'s' if count != 1 else ''}",
                text_color=("gray50", "gray55"),
                font=ctk.CTkFont(size=11)
            ).grid(row=0, column=1, padx=8)

            del_btn = _danger_btn(row, "🗑", lambda n=name: self.on_delete(n))
            del_btn.grid(row=0, column=2, padx=(0, 6))
            animations.click_pulse(del_btn)


# ─── Deck editor ──────────────────────────────────────────────────────────────

class DeckEditorView(ctk.CTkFrame):
    def __init__(self, master, deck_name, cards, on_back, on_study):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.deck_name = deck_name
        self.cards = cards
        self.on_back = on_back
        self.on_study = on_study

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Header row
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, padx=20, pady=(20, 4), sticky="ew")
        hdr.grid_columnconfigure(1, weight=1)

        back_btn = _ghost_btn(hdr, "← Back", on_back, width=80)
        back_btn.grid(row=0, column=0, padx=(0, 12))
        animations.click_pulse(back_btn)
        ctk.CTkLabel(hdr, text=deck_name,
                     font=ctk.CTkFont(size=20, weight="bold")).grid(
            row=0, column=1, sticky="w")
        self.study_btn = _primary_btn(hdr, "▶  Study", on_study, width=90)
        self.study_btn.grid(row=0, column=2)
        animations.click_pulse(self.study_btn)

        # Add-card row
        add_row = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=10)
        add_row.grid(row=1, column=0, padx=20, pady=(0, 8), sticky="ew")
        add_row.grid_columnconfigure(0, weight=1)
        add_row.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(add_row, text="Front", font=ctk.CTkFont(size=11),
                     text_color="gray50").grid(row=0, column=0, padx=12, sticky="w")
        ctk.CTkLabel(add_row, text="Back", font=ctk.CTkFont(size=11),
                     text_color="gray50").grid(row=0, column=1, padx=12, sticky="w")

        self.front_entry = ctk.CTkEntry(add_row, placeholder_text="Question / term…", height=32)
        self.front_entry.grid(row=1, column=0, padx=(12, 6), pady=(0, 10), sticky="ew")
        self.front_entry.bind("<Return>", lambda _: self.back_entry.focus())

        self.back_entry = ctk.CTkEntry(add_row, placeholder_text="Answer / definition…", height=32)
        self.back_entry.grid(row=1, column=1, padx=(6, 6), pady=(0, 10), sticky="ew")
        self.back_entry.bind("<Return>", lambda _: self._add_card())

        add_card_btn = _primary_btn(add_row, "+ Add Card", self._add_card, width=90)
        add_card_btn.grid(row=1, column=2, padx=(0, 12), pady=(0, 10))
        animations.click_pulse(add_card_btn)

        # Card list
        self.list_area = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.list_area.grid(row=2, column=0, padx=20, pady=(0, 16), sticky="nsew")
        self.list_area.grid_columnconfigure(0, weight=1)
        self.list_area.grid_columnconfigure(1, weight=1)

        self._render()

    def _add_card(self):
        front = self.front_entry.get().strip()
        back  = self.back_entry.get().strip()
        if not front or not back:
            return
        self.cards.append({"front": front, "back": back})
        self.front_entry.delete(0, "end")
        self.back_entry.delete(0, "end")
        self.front_entry.focus()
        self._render()

    def _delete_card(self, idx):
        self.cards.pop(idx)
        self._render()

    def _render(self):
        for w in self.list_area.winfo_children():
            w.destroy()

        self.study_btn.configure(state="normal" if self.cards else "disabled")

        if not self.cards:
            ctk.CTkLabel(self.list_area,
                         text="No cards yet — add one above!",
                         text_color=("gray60", "gray50")).grid(
                row=0, column=0, columnspan=2, pady=20)
            return

        ctk.CTkLabel(self.list_area, text="FRONT", font=ctk.CTkFont(size=10),
                     text_color="gray50").grid(row=0, column=0, sticky="w", padx=4, pady=(4, 2))
        ctk.CTkLabel(self.list_area, text="BACK", font=ctk.CTkFont(size=10),
                     text_color="gray50").grid(row=0, column=1, sticky="w", padx=4, pady=(4, 2))

        for i, card in enumerate(self.cards):
            row = ctk.CTkFrame(self.list_area, fg_color=BG_CARD, corner_radius=8)
            row.grid(row=i + 1, column=0, columnspan=2, sticky="ew", pady=2)
            row.grid_columnconfigure(0, weight=1)
            row.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(row, text=card["front"], anchor="w",
                         font=ctk.CTkFont(size=13),
                         wraplength=200).grid(
                row=0, column=0, padx=10, pady=8, sticky="ew")
            ctk.CTkLabel(row, text=card["back"], anchor="w",
                         font=ctk.CTkFont(size=13),
                         text_color=("gray50", "gray55"),
                         wraplength=200).grid(
                row=0, column=1, padx=10, pady=8, sticky="ew")
            del_btn = _danger_btn(row, "🗑", lambda i=i: self._delete_card(i))
            del_btn.grid(row=0, column=2, padx=(0, 6))
            animations.click_pulse(del_btn)


# ─── Study mode ───────────────────────────────────────────────────────────────

class StudyView(ctk.CTkFrame):
    def __init__(self, master, deck_name, cards, on_back):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.deck_name = deck_name
        self.on_back = on_back

        self.queue = [dict(c) for c in cards]
        random.shuffle(self.queue)
        self.current = 0
        self.showing_back = False
        self.known = 0
        self.unknown = 0

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, padx=20, pady=(20, 4), sticky="ew")
        hdr.grid_columnconfigure(1, weight=1)
        study_back_btn = _ghost_btn(hdr, "← Back", on_back, width=80)
        study_back_btn.grid(row=0, column=0, padx=(0, 12))
        animations.click_pulse(study_back_btn)
        ctk.CTkLabel(hdr, text=f"Studying: {deck_name}",
                     font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=1, sticky="w")
        self.progress_label = ctk.CTkLabel(hdr, text="",
                                           font=ctk.CTkFont(size=12),
                                           text_color="gray50")
        self.progress_label.grid(row=0, column=2)

        # Card area
        card_area = ctk.CTkFrame(self, fg_color="transparent")
        card_area.grid(row=1, column=0, padx=40, pady=10, sticky="nsew")
        card_area.grid_columnconfigure(0, weight=1)
        card_area.grid_rowconfigure(0, weight=1)

        self.card_frame = ctk.CTkFrame(card_area, fg_color=("gray88", "gray18"),
                                       corner_radius=16, cursor="hand2")
        self.card_frame.grid(row=0, column=0, sticky="nsew")
        self.card_frame.grid_columnconfigure(0, weight=1)
        self.card_frame.grid_rowconfigure(0, weight=1)
        self.card_frame.bind("<Button-1>", lambda _: self._flip())

        self.side_label = ctk.CTkLabel(self.card_frame, text="",
                                       font=ctk.CTkFont(size=11),
                                       text_color="gray50")
        self.side_label.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="n")
        self.side_label.bind("<Button-1>", lambda _: self._flip())

        self.card_text = ctk.CTkLabel(self.card_frame, text="",
                                      font=ctk.CTkFont(size=22, weight="bold"),
                                      wraplength=400, justify="center")
        self.card_text.grid(row=0, column=0, padx=30, pady=30)
        self.card_text.bind("<Button-1>", lambda _: self._flip())

        self.hint_label = ctk.CTkLabel(self.card_frame, text="Click to flip",
                                       font=ctk.CTkFont(size=11),
                                       text_color="gray50")
        self.hint_label.grid(row=1, column=0, pady=(0, 16))
        self.hint_label.bind("<Button-1>", lambda _: self._flip())

        # Action buttons
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.grid(row=2, column=0, pady=(0, 20))

        self.unknown_btn = ctk.CTkButton(
            btn_row, text="✗  Still Learning",
            fg_color=("#8B2020", "#6B1A1A"), hover_color=("#6B1A1A", "#4B1010"),
            font=ctk.CTkFont(size=14), width=150, corner_radius=50,
            command=self._mark_unknown)
        self.unknown_btn.grid(row=0, column=0, padx=10)
        animations.click_pulse(self.unknown_btn)

        self.flip_btn = _ghost_btn(btn_row, "Flip", self._flip, width=80)
        self.flip_btn.grid(row=0, column=1, padx=10)
        animations.click_pulse(self.flip_btn)

        self.known_btn = ctk.CTkButton(
            btn_row, text="✓  Got It",
            fg_color=("#1a5c2a", "#1a4a22"), hover_color=("#134520", "#0f3318"),
            font=ctk.CTkFont(size=14), width=150, corner_radius=50,
            command=self._mark_known)
        self.known_btn.grid(row=0, column=2, padx=10)
        animations.click_pulse(self.known_btn)

        self._load_card()

    def _load_card(self):
        self.showing_back = False
        if self.current >= len(self.queue):
            self._show_results()
            return

        card = self.queue[self.current]
        self.side_label.configure(text="QUESTION")
        self.card_text.configure(text=card["front"])
        self.hint_label.configure(text="Click to flip")
        self.progress_label.configure(
            text=f"{self.current + 1} / {len(self.queue)}")
        self._set_action_state("disabled")

    def _flip(self):
        if self.current >= len(self.queue):
            return
        card = self.queue[self.current]
        if not self.showing_back:
            self.showing_back = True
            self.side_label.configure(text="ANSWER")
            self.card_text.configure(text=card["back"])
            self.hint_label.configure(text="")
            self._set_action_state("normal")
        else:
            self.showing_back = False
            self.side_label.configure(text="QUESTION")
            self.card_text.configure(text=card["front"])
            self.hint_label.configure(text="Click to flip")
            self._set_action_state("disabled")

    def _set_action_state(self, state):
        self.known_btn.configure(state=state)
        self.unknown_btn.configure(state=state)

    def _mark_known(self):
        self.known += 1
        self.current += 1
        self._load_card()

    def _mark_unknown(self):
        self.unknown += 1
        self.current += 1
        self._load_card()

    def _show_results(self):
        for w in self.winfo_children():
            w.destroy()

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        results = ctk.CTkFrame(self, fg_color=("gray88", "gray18"), corner_radius=16)
        results.grid(row=1, column=0, padx=60, pady=20, sticky="nsew")
        results.grid_columnconfigure(0, weight=1)

        total = self.known + self.unknown
        pct = int(self.known / total * 100) if total else 0

        ctk.CTkLabel(results, text="Session Complete!",
                     font=ctk.CTkFont(size=22, weight="bold")).grid(
            row=0, column=0, pady=(30, 10))

        ctk.CTkLabel(results, text=f"{pct}%",
                     font=ctk.CTkFont(size=56, weight="bold"),
                     text_color=PURPLE).grid(row=1, column=0, pady=(0, 4))

        ctk.CTkLabel(results, text=f"{self.known} known  •  {self.unknown} still learning",
                     font=ctk.CTkFont(size=14), text_color="gray50").grid(
            row=2, column=0, pady=(0, 24))

        btns = ctk.CTkFrame(results, fg_color="transparent")
        btns.grid(row=3, column=0, pady=(0, 30))
        again_btn = _primary_btn(btns, "Study Again", lambda: self.on_back(), width=120)
        again_btn.grid(row=0, column=0, padx=8)
        animations.click_pulse(again_btn)
        back_btn = _ghost_btn(btns, "Back to Deck", self.on_back, width=120)
        back_btn.grid(row=0, column=1, padx=8)
        animations.click_pulse(back_btn)
