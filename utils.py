import re
import customtkinter as ctk


def make_maximized(window: ctk.CTk, min_width: int = 1000, min_height: int = 600):
  #Opens window in maximized state while keeping native window controls.
  window.minsize(min_width, min_height)
  window.configure(fg_color="#FAF7F2")
  window.after(50, lambda: window.state("zoomed"))


def chain_enter_keys(entries: list, submit_callback=None):
  #Binds Enter key to move focus to next entry or submit on last field.
  for i in range(len(entries) - 1):
    curr_entry = entries[i]
    next_entry = entries[i + 1]

    def handle_next(event, n=next_entry):
      n.focus()
      n.focus_set()
      return "break"

    curr_entry.bind("<Return>", handle_next)

  if entries and submit_callback:

    def handle_submit(event):
      submit_callback()
      return "break"

    entries[-1].bind("<Return>", handle_submit)


# ----------------  REGEX VALIDATORS ---------------- #
def validate_phone(phone: str) -> bool:
  #Validates Indian phone number (+91 followed by exactly 10 digits).
  pattern = r"^\+91\s?\d{10}$"
  return bool(re.match(pattern, phone.strip()))


def validate_email(email: str) -> bool:
  #Validates standard email format (name@domain.com).
  pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
  return bool(re.match(pattern, email.strip()))


# ----------------  REUSABLE DELETE MODAL ---------------- #
class ConfirmDeleteModal(ctk.CTkToplevel):
  #Reusable modal dialog for confirming item deletions.

  def __init__(self, parent, item_name: str, confirm_callback):
    super().__init__(parent)
    self.title("Confirm Deletion")
    self.geometry("400x220")
    self.resizable(False, False)
    self.configure(fg_color="#FAF7F2")

    self.confirm_callback = confirm_callback

    container = ctk.CTkFrame(self, fg_color="white", corner_radius=12)
    container.pack(fill="both", expand=True, padx=15, pady=15)

    ctk.CTkLabel(
        container, text="⚠️", font=("Segoe UI Emoji", 28), text_color="#A94442"
    ).pack(pady=(12, 2))

    ctk.CTkLabel(
        container,
        text="Are you sure?",
        font=("Segoe UI", 16, "bold"),
        text_color="#2D2D2D",
    ).pack(pady=(0, 4))

    ctk.CTkLabel(
        container,
        text=f"Do you really want to delete '{item_name}'?\nThis action cannot be undone.",
        font=("Segoe UI", 11),
        text_color="#555",
        justify="center",
    ).pack(pady=(0, 15))

    btn_frame = ctk.CTkFrame(container, fg_color="transparent")
    btn_frame.pack(fill="x", padx=20)

    ctk.CTkButton(
        btn_frame,
        text="Cancel",
        fg_color="#E0E0E0",
        hover_color="#D5D5D5",
        text_color="#2D2D2D",
        font=("Segoe UI", 12, "bold"),
        height=36,
        corner_radius=8,
        command=self.destroy,
    ).pack(side="left", expand=True, fill="x", padx=(0, 5))

    ctk.CTkButton(
        btn_frame,
        text="Yes, Delete",
        fg_color="#A94442",
        hover_color="#8B2E2E",
        text_color="white",
        font=("Segoe UI", 12, "bold"),
        height=36,
        corner_radius=8,
        command=self.on_confirm,
    ).pack(side="right", expand=True, fill="x", padx=(5, 0))

    self.center_on_screen(parent, 400, 220)

  def center_on_screen(self, parent, width, height):
    self.update_idletasks()
    root = parent.winfo_toplevel()
    x = root.winfo_rootx() + (root.winfo_width() // 2) - (width // 2)
    y = root.winfo_rooty() + (root.winfo_height() // 2) - (height // 2)
    self.geometry(f"{width}x{height}+{max(0, x)}+{max(0, y)}")
    self.grab_set()
    self.lift()
    self.focus_force()

  def on_confirm(self):
    self.confirm_callback()
    self.after(50, self.destroy)