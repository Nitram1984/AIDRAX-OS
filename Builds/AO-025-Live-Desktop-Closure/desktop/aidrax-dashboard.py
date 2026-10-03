#!/usr/bin/python3
"""Visible AIDRAX live desktop surface with no execution controls."""
from pathlib import Path
import tkinter as tk


def main() -> None:
    """Run the non-executing AIDRAX live desktop surface."""
    root = tk.Tk()
    root.title("AIDRAX OS")
    root.configure(bg="#070a18")
    root.attributes("-fullscreen", True)
    canvas = tk.Canvas(root, bg="#070a18", highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    pet_path = Path(__file__).with_name("pets") / "aidrax-draco-standard" / "draco-idle.gif"
    pet_frames: list[tk.PhotoImage] = []
    try:
        pet_frames = [
            tk.PhotoImage(file=pet_path, format=f"gif -index {index}")
            for index in range(6)
        ]
    except tk.TclError:
        pet_frames = []
    frame_index = 0

    def animate() -> None:
        """Advance Draco's local idle loop without invoking any system action."""
        nonlocal frame_index
        if pet_frames:
            canvas.itemconfigure("draco", image=pet_frames[frame_index])
            frame_index = (frame_index + 1) % len(pet_frames)
        root.after(140, animate)

    def draw(_: object = None) -> None:
        """Render the responsive live-status surface."""
        canvas.delete("all")
        width, height = root.winfo_width(), root.winfo_height()
        canvas.create_rectangle(0, 0, width, height, fill="#070a18", outline="")
        canvas.create_oval(width * .55, height * .05, width * 1.15, height * 1.25, fill="#1e1950", outline="")
        canvas.create_text(72, 88, anchor="w", text="AIDRAX OS", fill="#d5dcff", font=("Sans", 38, "bold"))
        canvas.create_text(75, 138, anchor="w", text="LIVE DESKTOP · OWNER-GATED PLATFORM", fill="#8fa6dc", font=("Sans", 14))
        canvas.create_rectangle(72, 220, width - 72, height - 110, fill="#10162c", outline="#5a68bd", width=2)
        canvas.create_text(116, 280, anchor="w", text="SYSTEM READY", fill="#8fe9d3", font=("Sans", 22, "bold"))
        canvas.create_text(116, 334, anchor="w", text="AIDRAX Desktop Shell is active.", fill="#edf0ff", font=("Sans", 18))
        canvas.create_text(116, 376, anchor="w", text="Storage changes, installation, and external dispatch remain owner-gated.", fill="#b9c2e8", font=("Sans", 14))
        if pet_frames:
            canvas.create_image(width - 220, height - 230, image=pet_frames[frame_index], tags="draco")
            canvas.create_text(width - 220, height - 94, text="DRACO · LOCAL IDLE", fill="#8fe9d3", font=("Sans", 11, "bold"))
        else:
            canvas.create_text(width - 220, height - 130, text="DRACO ASSET UNAVAILABLE", fill="#f2c077", font=("Sans", 11, "bold"))
        canvas.create_text(116, height - 158, anchor="w", text="Network configuration is available from the system tray.", fill="#8fa6dc", font=("Sans", 14))
        canvas.create_text(width - 72, height - 68, anchor="e", text="AIDRAX · LIVE", fill="#8fa6dc", font=("Sans", 13, "bold"))

    root.bind("<Configure>", draw)
    root.bind("<Escape>", lambda _: root.destroy())
    draw()
    animate()
    root.mainloop()


if __name__ == "__main__":
    main()
