import customtkinter as ctk


def _hex_to_rgb(h):
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _rgb_to_hex(r, g, b):
    return f"#{int(r):02x}{int(g):02x}{int(b):02x}"


def _lerp(c1, c2, t):
    r1, g1, b1 = _hex_to_rgb(c1)
    r2, g2, b2 = _hex_to_rgb(c2)
    return _rgb_to_hex(
        r1 + (r2 - r1) * t,
        g1 + (g2 - g1) * t,
        b1 + (b2 - b1) * t,
    )


def _resolve(color):
    """Resolve a CTk color tuple to a plain hex string for the current appearance mode."""
    if isinstance(color, (list, tuple)) and len(color) == 2:
        return color[0] if ctk.get_appearance_mode() == "Light" else color[1]
    return str(color)


def _is_hex(color):
    c = _resolve(color)
    return isinstance(c, str) and c.startswith("#") and len(c) in (4, 7)


# ── Button click pulse ────────────────────────────────────────────────────────

def click_pulse(btn, duration=160, steps=8):
    """
    Wrap a button command with a click animation.
    Solid-color buttons flash toward white/black; transparent buttons get a brief
    purple border glow.
    """
    original_cmd = btn.cget("command")
    fg = _resolve(btn.cget("fg_color"))
    iv = max(1, duration // (steps * 2))

    if _is_hex(fg):
        original_fg = btn.cget("fg_color")
        target = "#ffffff" if ctk.get_appearance_mode() == "Dark" else "#000000"

        def _fade(f, t, i):
            if i > steps:
                return
            try:
                btn.configure(fg_color=_lerp(_resolve(f), _resolve(t), i / steps))
            except Exception:
                return
            btn.after(iv, lambda: _fade(f, t, i + 1))

        def _cmd():
            _fade(original_fg, target, 1)
            btn.after(iv * steps, lambda: _fade(target, original_fg, 1))
            if original_cmd:
                original_cmd()

        btn.configure(command=_cmd)

    else:
        try:
            orig_bw = int(btn.cget("border_width"))
            orig_bc = btn.cget("border_color")
        except Exception:
            orig_bw, orig_bc = 0, "gray30"

        def _flash():
            try:
                btn.configure(border_width=2, border_color="#534AB7")
                btn.after(duration, lambda: btn.configure(
                    border_width=orig_bw, border_color=orig_bc))
            except Exception:
                pass
            if original_cmd:
                original_cmd()

        btn.configure(command=_flash)


# ── Card staggered fade-in ────────────────────────────────────────────────────

def _bg_hex():
    return "#ffffff" if ctk.get_appearance_mode() == "Light" else "#000000"


def _fade_card(widget, target, duration=320, steps=16):
    iv = max(1, duration // steps)
    bg = _bg_hex()
    target_resolved = _resolve(target)

    def _step(i):
        if i > steps:
            try:
                widget.configure(fg_color=target)
            except Exception:
                pass
            return
        try:
            widget.configure(fg_color=_lerp(bg, target_resolved, i / steps))
        except Exception:
            return
        widget.after(iv, lambda: _step(i + 1))

    _step(1)


def stagger_cards(cards, colors, delay_ms=80, duration=320):
    """Fade each card from the window background to its target color with a staggered delay."""
    for i, (card, color) in enumerate(zip(cards, colors)):
        card.after(i * delay_ms, lambda w=card, c=color: _fade_card(w, c, duration=duration))


# ── Responsive font ───────────────────────────────────────────────────────────

def responsive_font(root, family="Helvetica", size=16, weight="normal",
                    divisor=25, min_size=16, max_size=1024):
    """Create a CTkFont that auto-scales with root window width on <Configure>."""
    font = ctk.CTkFont(family=family, size=size, weight=weight)

    def _scale(width):
        font.configure(size=max(min_size, min(int(width / divisor), max_size)))
        root.update_idletasks()

    root.bind("<Configure>",
              lambda e: _scale(e.width) if e.widget is root else None,
              add="+")
    root.after(10, lambda: _scale(root.winfo_width() if root.winfo_width() > 1 else 640))

    return font
