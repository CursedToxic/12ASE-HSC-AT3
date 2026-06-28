import customtkinter as ctk

# Claude helped me create this
# Dynamically scaling font
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
