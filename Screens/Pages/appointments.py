import datetime
import customtkinter as ctk
from pymongo import MongoClient
from utils import ConfirmDeleteModal, chain_enter_keys

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["PawfectCare"]
appts_col = db["appointments"]
pets_col = db["pets"]
customers_col = db["customers"]
services_col = db["services"]


class BookAppointmentModal(ctk.CTkToplevel):
  #Modal dialog for booking and editing appointments.

  def __init__(self, parent, title="Book Appointment", appt_data=None):
    super().__init__(parent)
    self.title(title)
    self.geometry("460x580")
    self.resizable(False, False)
    self.configure(fg_color="#FAF7F2")

    self.appt_data = appt_data or {}
    self.parent_page = parent

    self.main_container = ctk.CTkFrame(self, fg_color="#FAF7F2")
    self.main_container.pack(fill="both", expand=True, padx=15, pady=10)

    ctk.CTkLabel(
        self.main_container,
        text=title,
        font=("Segoe UI", 18, "bold"),
        text_color="#2D2D2D",
    ).pack(pady=(5, 10))

    # 1. Pet Name
    self.pet_entry = self._create_field(
        "Pet Name:", 
        self.appt_data.get("pet", "")
    )

    # 2. Owner Name
    self.owner_entry = self._create_field(
        "Owner Name:", 
        self.appt_data.get("owner", "")
    )

    # 3. Select Service
    ctk.CTkLabel(
        self.main_container,
        text="Select Service:",
        font=("Segoe UI", 11, "bold"),
        text_color="#8D5A4F",
    ).pack(anchor="w", padx=20, pady=(2, 1))

    service_docs = list(services_col.find({}))
    service_options = [s.get("title") for s in service_docs if s.get("title")]

    if not service_options:
        service_options = ["No services available"]
    default_svc = self.appt_data.get("service") or service_options[0]

    self.service_opt = ctk.CTkOptionMenu(
        self.main_container,
        values=service_options,
        fg_color="white",
        text_color="#2D2D2D",
        button_color="#C96C4B",
        button_hover_color="#B65A3B",
        dropdown_fg_color="white",
        dropdown_text_color="#2D2D2D",
        height=32,
    )
    self.service_opt.set(default_svc)
    self.service_opt.pack(fill="x", padx=20, pady=(0, 4))

    # 4. Date & Time Parsing
    raw_dt = self.appt_data.get("datetime", "")
    date_val = datetime.datetime.now().strftime("%Y-%m-%d")
    time_val = "10:00 AM"

    if " | " in raw_dt:
      parts = raw_dt.split(" | ")
      date_val = parts[0]
      time_val = parts[1]
    elif raw_dt:
      date_val = raw_dt[:10]

    self.date_entry = self._create_field("Appointment Date (YYYY-MM-DD):", date_val)

    # 5. Time Slot
    ctk.CTkLabel(
        self.main_container,
        text="Select Time Slot:",
        font=("Segoe UI", 11, "bold"),
        text_color="#8D5A4F",
    ).pack(anchor="w", padx=20, pady=(2, 1))

    time_slots = [
        "09:00 AM",
        "10:00 AM",
        "11:00 AM",
        "12:00 PM",
        "01:00 PM",
        "02:00 PM",
        "03:00 PM",
        "04:00 PM",
        "05:00 PM",
    ]
    self.time_opt = ctk.CTkOptionMenu(
        self.main_container,
        values=time_slots,
        fg_color="white",
        text_color="#2D2D2D",
        button_color="#C96C4B",
        button_hover_color="#B65A3B",
        dropdown_fg_color="white",
        dropdown_text_color="#2D2D2D",
        height=32,
    )
    self.time_opt.set(time_val if time_val in time_slots else time_slots[1])
    self.time_opt.pack(fill="x", padx=20, pady=(0, 4))

    # 6. Status
    ctk.CTkLabel(
        self.main_container,
        text="Status:",
        font=("Segoe UI", 11, "bold"),
        text_color="#8D5A4F",
    ).pack(anchor="w", padx=20, pady=(2, 1))

    status_options = ["Confirmed", "Completed", "Cancelled"]
    default_status = (
        self.appt_data.get("status", "Confirmed").strip().capitalize()
    )

    self.status_opt = ctk.CTkOptionMenu(
        self.main_container,
        values=status_options,
        fg_color="white",
        text_color="#2D2D2D",
        button_color="#C96C4B",
        button_hover_color="#B65A3B",
        dropdown_fg_color="white",
        dropdown_text_color="#2D2D2D",
        height=32,
    )
    self.status_opt.set(
        default_status if default_status in status_options else "Confirmed"
    )
    self.status_opt.pack(fill="x", padx=20, pady=(0, 6))

    self.err_label = ctk.CTkLabel(
        self.main_container, text="", font=("Segoe UI", 11), text_color="#A94442"
    )
    self.err_label.pack(pady=(0, 2))

    btn_text = "Update Appointment" if self.appt_data else "Save Appointment"
    btn_save = ctk.CTkButton(
        self.main_container,
        text=btn_text,
        fg_color="#C96C4B",
        hover_color="#B65A3B",
        font=("Segoe UI", 13, "bold"),
        height=38,
        corner_radius=10,
        command=self.save_appointment,
    )
    btn_save.pack(fill="x", padx=20, pady=(5, 10))

    chain_enter_keys(
        [self.pet_entry, self.owner_entry, self.date_entry],
        submit_callback=self.save_appointment,
    )

    self.center_on_screen(parent, 460, 580)

  def _create_field(self, label, default=None):
    ctk.CTkLabel(
        self.main_container,
        text=label,
        font=("Segoe UI", 11, "bold"),
        text_color="#8D5A4F",
    ).pack(anchor="w", padx=20, pady=(2, 1))

    entry = ctk.CTkEntry(
        self.main_container,
        fg_color="white",
        text_color="#2D2D2D",
        border_color="#E8D2C8",
        height=32,
    )
    if default is not None:
      entry.insert(0, str(default))
    entry.pack(fill="x", padx=20, pady=(0, 4))
    return entry

  def center_on_screen(self, parent, width, height):
    self.update_idletasks()
    root = parent.winfo_toplevel()
    x = root.winfo_rootx() + (root.winfo_width() // 2) - (width // 2)
    y = root.winfo_rooty() + (root.winfo_height() // 2) - (height // 2)
    self.geometry(f"{width}x{height}+{max(0, x)}+{max(0, y)}")
    self.grab_set()
    self.lift()
    self.focus_force()

  def save_appointment(self):
    pet = self.pet_entry.get().strip()
    owner = self.owner_entry.get().strip()
    service = self.service_opt.get()
    date_str = self.date_entry.get().strip()
    time_str = self.time_opt.get()
    status_str = self.status_opt.get()

    if not pet or not owner or not date_str:
      self.err_label.configure(text="Pet, Owner, and Date are required.")
      return

    full_datetime = f"{date_str} | {time_str}"

    payload = {
        "pet": pet,
        "owner": owner,
        "service": service,
        "datetime": full_datetime,
        "status": status_str,
    }

    if self.appt_data.get("id"):
      appts_col.update_one({"id": self.appt_data["id"]}, {"$set": payload})
      self.parent_page.show_status(
          "Appointment record updated successfully!", "#6D8B74"
      )
    elif self.appt_data.get("_id"):
      appts_col.update_one({"_id": self.appt_data["_id"]}, {"$set": payload})
      self.parent_page.show_status(
          "Appointment record updated successfully!", "#6D8B74"
      )
    else:
      last_appt = appts_col.find_one({}, sort=[("_id", -1)])
      if last_appt and "id" in last_appt:
        try:
          last_num = int(last_appt["id"].split("-")[1])
          appt_id = f"APT-{last_num + 1}"
        except Exception:
          appt_id = "APT-101"
      else:
        appt_id = "APT-101"

      payload["id"] = appt_id
      appts_col.insert_one(payload)
      self.parent_page.show_status(
          "New appointment booked successfully!", "#6D8B74"
      )

    self.parent_page.load_appointments()
    self.destroy()


class AppointmentsPage(ctk.CTkFrame):
  #Appointments Management UI Page.

  def __init__(self, parent):
    super().__init__(parent, fg_color="#FAF7F2")

    self.headers = [
        "ID",
        "Pet Name",
        "Owner",
        "Service",
        "Date & Time",
        "Status",
        "Actions",
    ]
    self.widths = [80, 130, 130, 140, 180, 110, 160]

    controls = ctk.CTkFrame(
      self, 
      fg_color="white", 
      corner_radius=12, 
      height=70
    )
    controls.pack(fill="x", pady=(0, 15))
    controls.pack_propagate(False)

    self.search = ctk.CTkEntry(
        controls,
        placeholder_text="🔍 Search Appointment...",
        width=260,
        height=40,
        fg_color="#FAF7F2",
        border_color="#E8D2C8",
        text_color="#2D2D2D",
        placeholder_text_color="#A68A7A",
    )
    self.search.pack(side="left", padx=(20, 10), pady=15)
    self.search.bind("<KeyRelease>", lambda event: self.load_appointments())

    self.status_filter = ctk.CTkOptionMenu(
        controls,
        values=[
            "All Status",
            "Confirmed",
            "Pending",
            "Completed",
            "Cancelled",
        ],
        width=140,
        height=40,
        fg_color="#FAF7F2",
        text_color="#2D2D2D",
        button_color="#C96C4B",
        button_hover_color="#B65A3B",
        dropdown_text_color="#2D2D2D",
        dropdown_fg_color="white",
        dropdown_hover_color="#F7E8E1",
        command=lambda choice: self.load_appointments(),
    )
    self.status_filter.pack(side="left", padx=5, pady=15)

    btn_add = ctk.CTkButton(
        controls,
        text="+ Book Appointment",
        font=("Segoe UI", 14, "bold"),
        fg_color="#C96C4B",
        hover_color="#B65A3B",
        height=40,
        command=self.open_add_modal,
    )
    btn_add.pack(side="right", padx=20, pady=15)

    table_card = ctk.CTkFrame(
      self, 
      fg_color="white", 
      corner_radius=12
    )
    table_card.pack(fill="both", expand=True)

    ctk.CTkLabel(
        table_card,
        text="📅 Appointments Schedule List",
        font=("Segoe UI", 18, "bold"),
        text_color="#2D2D2D",
    ).pack(anchor="w", padx=20, pady=(15, 10))

    header_frame = ctk.CTkFrame(table_card, fg_color="transparent")
    header_frame.pack(fill="x", padx=20)

    for idx, h in enumerate(self.headers):
      cell = ctk.CTkFrame(
          header_frame,
          width=self.widths[idx],
          height=38,
          fg_color="#F7E8E1",
          border_width=1,
          border_color="#E8D2C8",
      )
      cell.grid(row=0, column=idx, sticky="nsew")
      cell.grid_propagate(False)
      ctk.CTkLabel(
          cell, 
          text=h, 
          font=("Segoe UI", 12, "bold"), 
          text_color="#8D5A4F"
      ).place(relx=0.5, rely=0.5, anchor="center")

    self.scroll_table = ctk.CTkScrollableFrame(
        table_card, 
        fg_color="transparent"
    )
    self.scroll_table.pack(fill="both", expand=True, padx=20, pady=(0, 15))

    self.status_label = ctk.CTkLabel(
        self, 
        text="", 
        font=("Segoe UI", 13, "bold"), 
        text_color="#6D4C41"
    )
    self.status_label.pack(side="bottom", pady=(0, 10))

    self.load_appointments()

  def load_appointments(self):
    for widget in self.scroll_table.winfo_children():
      widget.destroy()

    search_query = self.search.get().strip()
    selected_status = self.status_filter.get()

    query = {}
    if search_query:
      query["$or"] = [
          {"pet": {"$regex": search_query, "$options": "i"}},
          {"owner": {"$regex": search_query, "$options": "i"}},
          {"service": {"$regex": search_query, "$options": "i"}},
          {"datetime": {"$regex": search_query, "$options": "i"}},
          {"id": {"$regex": search_query, "$options": "i"}},
      ]

    if selected_status and selected_status != "All Status":
      query["status"] = {"$regex": f"^{selected_status}$", "$options": "i"}

    appt_records = list(appts_col.find(query))

    for row_idx, appt in enumerate(appt_records):
      row_frame = ctk.CTkFrame(self.scroll_table, fg_color="transparent")
      row_frame.pack(fill="x", pady=1)

      appt_id = appt.get("id") or str(appt.get("_id", ""))
      raw_st = str(appt.get("status", "Confirmed")).strip()
      st = raw_st.capitalize()

      vals = [
          appt_id,
          appt.get("pet", ""),
          appt.get("owner", ""),
          appt.get("service", ""),
          appt.get("datetime", ""),
          st,
      ]

      for col_idx, val in enumerate(vals):
        cell = ctk.CTkFrame(
            row_frame,
            width=self.widths[col_idx],
            height=40,
            fg_color="white",
            border_width=1,
            border_color="#E8E0DC",
        )
        cell.grid(row=0, column=col_idx, sticky="nsew")
        cell.grid_propagate(False)

        if col_idx == 5:
          color = (
              "#5F7F63"
              if st == "Completed"
              else (
                  "#2E6B9E"
                  if st == "Confirmed"
                  else "#C96C4B" if st == "Pending" else "#A94442"
              )
          )
          font = ("Segoe UI", 12, "bold")
          text_color = color
        else:
          font = ("Segoe UI", 12, "bold") if col_idx == 0 else ("Segoe UI", 12)
          text_color = "#8D5A4F" if col_idx == 0 else "#2D2D2D"

        ctk.CTkLabel(
            cell, 
            text=str(val), 
            font=font, 
            text_color=text_color
        ).place(relx=0.5, rely=0.5, anchor="center")

      # Actions Column Frame
      action_cell = ctk.CTkFrame(
          row_frame,
          width=self.widths[6],
          height=40,
          fg_color="white",
          border_width=1,
          border_color="#E8E0DC",
      )
      action_cell.grid(row=0, column=6, sticky="nsew")
      action_cell.grid_propagate(False)

      container = ctk.CTkFrame(action_cell, fg_color="transparent")
      container.place(relx=0.5, rely=0.5, anchor="center")

      # Robust check for Confirmed or Pending (case-insensitive)
      if st in ["Confirmed", "Pending"]:
        # Tick -> Marks status as Completed
        ctk.CTkButton(
            container,
            text="✔",
            width=28,
            height=28,
            fg_color="#D4EFDF",
            hover_color="#A9DFBF",
            text_color="#1E8449",
            font=("Segoe UI", 12, "bold"),
            command=lambda a=appt: self.quick_update_status(a, "Completed"),
        ).pack(side="left", padx=2)

        # Cancel -> Marks status as Cancelled
        ctk.CTkButton(
            container,
            text="✖",
            width=28,
            height=28,
            fg_color="#FADBD8",
            hover_color="#F5B7B1",
            text_color="#A94442",
            font=("Segoe UI", 12, "bold"),
            command=lambda a=appt: self.quick_update_status(a, "Cancelled"),
        ).pack(side="left", padx=2)

      # Edit Button  - Always visible
      ctk.CTkButton(
          container,
          text="✏️",
          width=28,
          height=28,
          fg_color="#F0E0D6",
          hover_color="#E2CEC1",
          text_color="black",
          command=lambda a=appt: self.open_edit_modal(a),
      ).pack(side="left", padx=2)

      # Delete Button - Always visible
      ctk.CTkButton(
          container,
          text="🗑️",
          width=28,
          height=28,
          fg_color="#FADBD8",
          hover_color="#F5B7B1",
          text_color="black",
          command=lambda a=appt: ConfirmDeleteModal(
              self,
              item_name=f"Appointment {a.get('id', '')}",
              confirm_callback=lambda: self.delete_appointment(a),
          ),
      ).pack(side="left", padx=2)

  def quick_update_status(self, appt_item, new_status):
    appt_id = appt_item.get("id")
    mongo_id = appt_item.get("_id")

    if appt_id:
      appts_col.update_one({"id": appt_id}, {"$set": {"status": new_status}})
    elif mongo_id:
      appts_col.update_one({"_id": mongo_id}, {"$set": {"status": new_status}})

    self.show_status(
        f"Appointment status changed to '{new_status}'!", "#6D8B74"
    )
    self.load_appointments()

  def open_add_modal(self):
    BookAppointmentModal(self, title="Book Appointment")

  def open_edit_modal(self, appt_data):
    display_id = appt_data.get("id") or str(appt_data.get("_id", ""))
    BookAppointmentModal(
        self,
        title=f"Edit Appointment ({display_id})",
        appt_data=appt_data,
    )

  def delete_appointment(self, appt_item):
    appt_id = appt_item.get("id")
    mongo_id = appt_item.get("_id")

    if appt_id:
      result = appts_col.delete_one({"id": appt_id})
    elif mongo_id:
      result = appts_col.delete_one({"_id": mongo_id})
    else:
      result = None

    if result and result.deleted_count == 1:
      self.show_status("Appointment record deleted successfully!", "#6D8B74")
      self.load_appointments()
    else:
      self.show_status("Appointment record not found.", "#C96C4B")

  def show_status(self, message, color):
    self.status_label.configure(text=message, text_color=color)
    self.after(5000, lambda: self.status_label.configure(text=""))