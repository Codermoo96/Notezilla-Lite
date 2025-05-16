import tkinter as tk
from tkinter import messagebox, simpledialog
import os
import uuid
import json

SAVE_DIR = "notes_data"

if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

def get_note_path(note_id):
    return os.path.join(SAVE_DIR, f"{note_id}.json")

class StickyNote:
    def __init__(self, note_id=None):
        self.note_id = note_id or str(uuid.uuid4())
        self.note_path = get_note_path(self.note_id)

        self.root = tk.Tk()
        self.root.title(f"Sticky Note - {self.note_id[:4]}")
        self.root.geometry("250x200")
        self.root.attributes("-topmost", True)

        self.root.protocol("WM_DELETE_WINDOW", self.save_and_close)

        self.locked = False
        self.bg_color = "lightyellow"

        # Load saved note if exists
        self.text_content = ""
        self.load_note()

        self.root.configure(bg=self.bg_color)

        self.text = tk.Text(self.root, wrap="word", bg=self.bg_color,
                            font=("Arial", 12), relief="flat")
        self.text.insert("1.0", self.text_content)
        self.text.pack(expand=True, fill="both", padx=5, pady=5)

        if self.locked:
            self.text.config(state="disabled")

        # Context menu
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="New Note", command=self.create_new_note)
        self.menu.add_command(label="Lock Editing", command=self.toggle_lock)
        self.menu.add_command(label="Change Color", command=self.change_color)
        self.menu.add_command(label="Delete Note", command=self.delete_note)
        self.menu.add_command(label="Close", command=self.save_and_close)

        self.root.bind("<Button-3>", self.show_menu)
        self.root.bind("<KeyRelease>", lambda e: self.save_note())  # Auto-save

        self.root.mainloop()

    def save_note(self):
        if self.locked:
            return
        data = {
            "text": self.text.get("1.0", "end-1c"),
            "color": self.bg_color,
            "locked": self.locked
        }
        with open(self.note_path, "w") as f:
            json.dump(data, f)

    def load_note(self):
        if os.path.exists(self.note_path):
            with open(self.note_path, "r") as f:
                data = json.load(f)
                self.text_content = data.get("text", "")
                self.bg_color = data.get("color", "lightyellow")
                self.locked = data.get("locked", False)

    def save_and_close(self):
        self.save_note()
        self.root.destroy()

    def show_menu(self, event):
        self.menu.tk_popup(event.x_root, event.y_root)

    def create_new_note(self):
        StickyNote()  # Create new window

    def toggle_lock(self):
        self.locked = not self.locked
        state = "disabled" if self.locked else "normal"
        self.text.config(state=state)
        self.save_note()

    def change_color(self):
        colors = {
            "Yellow": "lightyellow",
            "Green": "lightgreen",
            "Pink": "lightpink",
            "Blue": "lightblue",
            "White": "white"
        }
        choice = simpledialog.askstring("Choose Color", f"Options: {', '.join(colors)}")
        if choice and choice in colors:
            self.bg_color = colors[choice]
            self.text.config(bg=self.bg_color)
            self.root.config(bg=self.bg_color)
            self.save_note()
        elif choice:
            messagebox.showinfo("Invalid Color", f"'{choice}' is not a valid color.")

    def delete_note(self):
        confirm = messagebox.askyesno("Delete", "Are you sure you want to delete this note?")
        if confirm:
            if os.path.exists(self.note_path):
                os.remove(self.note_path)
            self.root.destroy()

# Launch the app
if __name__ == "__main__":
    StickyNote()
