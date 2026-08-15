import json
from tkinter import filedialog
import customtkinter as ctk
from pymongo import MongoClient
from utils import chain_enter_keys

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["PawfectCare"]
admins_col = db["admins"]


class SettingsPage(ctk.CTkFrame):
  # Admin Settings & System Configurations UI.

  def __init__(self, parent, username="admin"):
    super().__init__(parent, fg_color="#FAF7F2")
    self.username = username

    # Container Frame
    card = ctk.CTkFrame(
      self, 
      fg_color="white", 
      corner_radius=12
    )
    card.pack(fill="both", expand=True)

    ctk.CTkLabel(
        card,
        text="⚙️ Admin Settings & Preferences",
        font=("Segoe UI", 20, "bold"),
        text_color="#2D2D2D",
    ).pack(anchor="w", padx=30, pady=(20, 15))

    scroll = ctk.CTkScrollableFrame(card, fg_color="transparent")
    scroll.pack(fill="both", expand=True, padx=30, pady=(0, 10))

    # --- Section 1: Admin Profile ---
    ctk.CTkLabel(
        scroll,
        text="Admin Profile Details",
        font=("Segoe UI", 15, "bold"),
        text_color="#8D5A4F",
    ).pack(anchor="w", pady=(10, 10))

    profile_frame = ctk.CTkFrame(scroll, fg_color="#FAF7F2", corner_radius=10)
    profile_frame.pack(fill="x", pady=(0, 20))

    admin_doc = admins_col.find_one({"username": self.username}) or {}
    email_val = admin_doc.get("email", "admin@pawfectcare.com")

    self.user_entry = self._add_setting_input(
        profile_frame, "Admin Username:", self.username
    )
    self.user_entry.configure(state="disabled")  # Username read-only

    self.email_entry = self._add_setting_input(
        profile_frame, "Contact Email:", email_val
    )

    # --- Section 2: Change Password ---
    ctk.CTkLabel(
        scroll,
        text="Change Password",
        font=("Segoe UI", 15, "bold"),
        text_color="#8D5A4F",
    ).pack(anchor="w", pady=(10, 10))

    pwd_frame = ctk.CTkFrame(scroll, fg_color="#FAF7F2", corner_radius=10)
    pwd_frame.pack(fill="x", pady=(0, 20))

    self.curr_pass_entry = self._add_setting_input(
        pwd_frame, "Current Password:", "", show="*"
    )
    self.new_pass_entry = self._add_setting_input(
        pwd_frame, "New Password:", "", show="*"
    )
    self.confirm_pass_entry = self._add_setting_input(
        pwd_frame, "Confirm New Password:", "", show="*"
    )

    btn_update_pwd = ctk.CTkButton(
        pwd_frame,
        text="Update Password",
        fg_color="#C96C4B",
        hover_color="#B65A3B",
        font=("Segoe UI", 13, "bold"),
        width=160,
        height=38,
        corner_radius=10,
        command=self.update_password,
    )
    btn_update_pwd.pack(anchor="w", padx=20, pady=(10, 15))

    chain_enter_keys(
        [
            self.curr_pass_entry,
            self.new_pass_entry,
            self.confirm_pass_entry,
        ],
        submit_callback=self.update_password,
    )

    # --- Section 3: System Utilities ---
    ctk.CTkLabel(
        scroll,
        text="Database Utilities",
        font=("Segoe UI", 15, "bold"),
        text_color="#8D5A4F",
    ).pack(anchor="w", pady=(10, 10))

    db_frame = ctk.CTkFrame(scroll, fg_color="#FAF7F2", corner_radius=10)
    db_frame.pack(fill="x", pady=(0, 20))

    db_info = ctk.CTkLabel(
        db_frame,
        text="MongoDB Target: mongodb://localhost:27017/PawfectCare",
        font=("Segoe UI", 12),
        text_color="#555",
    )
    db_info.pack(anchor="w", padx=20, pady=(15, 10))

    btn_backup = ctk.CTkButton(
        db_frame,
        text="📥 Backup Database JSON",
        fg_color="#5F7F63",
        hover_color="#49634C",
        font=("Segoe UI", 13, "bold"),
        height=38,
        corner_radius=10,
        command=self.backup_database_json,
    )
    btn_backup.pack(anchor="w", padx=20, pady=(0, 15))

    # Bottom Status Label
    self.status_label = ctk.CTkLabel(
        card, text="", font=("Segoe UI", 13, "bold"), text_color="#6D4C41"
    )
    self.status_label.pack(side="bottom", pady=10)

  def _add_setting_input(
      self, parent, label_text, default_val="", show=None
  ):
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    frame.pack(fill="x", padx=20, pady=8)

    ctk.CTkLabel(
        frame,
        text=label_text,
        font=("Segoe UI", 13, "bold"),
        text_color="#2D2D2D",
        width=180,
        anchor="w",
    ).pack(side="left")

    entry = ctk.CTkEntry(
        frame,
        fg_color="white",
        text_color="#2D2D2D",
        placeholder_text_color="#A68A7A",
        border_color="#E8D2C8",
        width=320,
        height=35,
        show=show,
    )
    if default_val:
      entry.insert(0, str(default_val))
    entry.pack(side="left", padx=10)
    return entry

  def update_password(self):
    curr_pass = self.curr_pass_entry.get().strip()
    new_pass = self.new_pass_entry.get().strip()
    confirm_pass = self.confirm_pass_entry.get().strip()

    if not curr_pass or not new_pass or not confirm_pass:
      self.show_status(
          "Please fill in all password fields.", color="#C96C4B"
      )
      return

    admin = admins_col.find_one({"username": self.username})
    if not admin or admin.get("password") != curr_pass:
      self.show_status("Current password is incorrect!", color="#C96C4B")
      return

    if new_pass != confirm_pass:
      self.show_status("New passwords do not match!", color="#C96C4B")
      return

    admins_col.update_one(
        {"username": self.username}, {"$set": {"password": new_pass}}
    )

    self.curr_pass_entry.delete(0, "end")
    self.new_pass_entry.delete(0, "end")
    self.confirm_pass_entry.delete(0, "end")
    self.show_status("Password updated successfully!", color="#6D8B74")

  def backup_database_json(self):
    file_path = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON files", "*.json")],
        initialfile="PawfectCare_Backup.json",
        title="Save Database Backup",
    )

    if not file_path:
      return

    try:
      backup_data = {}
      collections = ["pets", "customers", "products", "services", "appointments"]

      for col_name in collections:
        records = list(db[col_name].find({}, {"_id": 0}))
        backup_data[col_name] = records

      with open(file_path, "w", encoding="utf-8") as f:
        json.dump(backup_data, f, indent=4)

      self.show_status(
          "Database backup created successfully!", color="#6D8B74"
      )
    except Exception as e:
      self.show_status(f"Backup failed: {str(e)}", color="#C96C4B")

  def show_status(self, message, color):
    self.status_label.configure(text=message, text_color=color)
    self.after(5000, lambda: self.status_label.configure(text=""))