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
    def __init__(self, master=None, note_id=None):
        self.master = master or tk.Tk()
        self.is_main = master is None

        self.note_id = note_id or str(uuid.uuid4())
        self.note_path = get_note_path(self.note_id)

        self.locked = False
        self.bg_color = "lightyellow"
        self.text_content = ""

        self.load_note()

        self.window = self.master if self.is_main else tk.Toplevel(self.master)
        self.window.title(f"Sticky Note - {self.note_id[:4]}")
        self.window.geometry("250x200")
        self.window.attributes("-topmost", True)
        self.window.configure(bg=self.bg_color)
        self.window.protocol("WM_DELETE_WINDOW", self.save_and_close)

        self.text = tk.Text(self.window, wrap="word", bg=self.bg_color,
                            font=("Arial", 10), relief="flat")
        self.text.insert("1.0", self.text_content)
        self.text.pack(expand=True, fill="both", padx=5, pady=5)

        if self.locked:
            self.text.config(state="disabled")

        self.menu = tk.Menu(self.window, tearoff=0)
        self.menu.add_command(label="New Note", command=self.create_new_note)
        self.menu.add_command(label="Lock Editing", command=self.toggle_lock)
        self.menu.add_command(label="Change Color", command=self.change_color)
        self.menu.add_command(label="Delete Note", command=self.delete_note)
        self.menu.add_command(label="Close", command=self.save_and_close)

        self.window.bind("<Button-3>", self.show_menu)
        self.text.bind("<KeyRelease>", lambda e: self.save_note())

        if self.is_main:
            self.master.mainloop()

    def load_note(self):
        if os.path.exists(self.note_path):
            with open(self.note_path, "r") as f:
                data = json.load(f)
                self.text_content = data.get("text", "")
                self.bg_color = data.get("color", "lightyellow")
                self.locked = data.get("locked", False)

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

    def save_and_close(self):
        self.save_note()
        self.window.destroy()

    def show_menu(self, event):
        self.menu.tk_popup(event.x_root, event.y_root)

    def create_new_note(self):
        StickyNote(master=self.master)  # Create a new Toplevel note

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
        choice = simpledialog.askstring("Choose Color", f"Options: {', '.join(colors)}", parent=self.window)
        if choice and choice in colors:
            self.bg_color = colors[choice]
            self.text.config(bg=self.bg_color)
            self.window.config(bg=self.bg_color)
            self.save_note()
        elif choice:
            messagebox.showinfo("Invalid Color", f"'{choice}' is not a valid color.")

    def delete_note(self):
        confirm = messagebox.askyesno("Delete", "Are you sure you want to delete this note?", parent=self.window)
        if confirm:
            if os.path.exists(self.note_path):
                os.remove(self.note_path)
            self.window.destroy()

# 🚀 AUTO-LOAD all notes on startup
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    found = False
    for filename in os.listdir(SAVE_DIR):
        if filename.endswith(".json"):
            note_id = filename.replace(".json", "")
            StickyNote(master=root, note_id=note_id)
            found = True

    if not found:
        StickyNote(master=root)  # Create a blank note if none exist

    root.mainloop()
