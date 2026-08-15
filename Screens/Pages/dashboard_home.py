import datetime
import customtkinter as ctk
from pymongo import MongoClient
from Screens.Pages.appointments import BookAppointmentModal
from Screens.Pages.customers import AddCustomerModal
from Screens.Pages.pets import AddPetModal
from Screens.Pages.products import AddProductModal

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["PawfectCare"]
pets_col = db["pets"]
customers_col = db["customers"]
appts_col = db["appointments"]
services_col = db["services"]
products_col = db["products"]


class DashboardHomePage(ctk.CTkFrame):
  #Main Dashboard View featuring live KPI stats, Today's Schedule, Quick Action Shortcuts, and Low Stock Alerts.

  def __init__(self, parent):
    super().__init__(parent, fg_color="#FAF7F2")
    self.parent_page = parent

    # 1. Top KPI Summary Cards (Live MongoDB Counts)
    self.build_kpi_cards()

    # 2. Middle Section (Today's Schedule + Quick Actions / Low Stock Alerts)
    self.build_middle_section()

    # 3. Bottom Table (Recent Appointments)
    self.build_recent_appointments_table()

  
  # 1. LIVE KPI STATS CARDS
  
  def build_kpi_cards(self):
    cards_frame = ctk.CTkFrame(self, fg_color="transparent")
    cards_frame.pack(fill="x", pady=(0, 15))

    total_pets = pets_col.count_documents({})
    total_customers = customers_col.count_documents({})
    total_appts = appts_col.count_documents({})
    total_services = services_col.count_documents({})

    kpis = [
        ("🐾 Total Pets", str(total_pets)),
        ("👥 Customers", str(total_customers)),
        ("📅 Appointments", str(total_appts)),
        ("✂ Services", str(total_services)),
    ]

    for title_text, count_text in kpis:
      card = ctk.CTkFrame(
          cards_frame,
          width=245,
          height=95,
          fg_color="white",
          corner_radius=12,
      )
      card.pack(side="left", expand=True, padx=5)
      card.pack_propagate(False)

      ctk.CTkLabel(
          card,
          text=title_text,
          font=("Segoe UI", 14, "bold"),
          text_color="#8D5A4F",
      ).pack(pady=(12, 2))

      ctk.CTkLabel(
          card,
          text=count_text,
          font=("Segoe UI", 26, "bold"),
          text_color="#2D2D2D",
      ).pack()

  
  # 2. MIDDLE SECTION (TODAY'S SCHEDULE & QUICK SHORTCUTS)
  
  def build_middle_section(self):
    middle_frame = ctk.CTkFrame(self, fg_color="transparent")
    middle_frame.pack(fill="x", pady=(0, 15))

    # --- Left Widget: Today's Schedule (60% width) ---
    sched_card = ctk.CTkFrame(
        middle_frame, 
        fg_color="white", 
        corner_radius=12, 
        height=220
    )
    sched_card.pack(side="left", fill="both", expand=True, padx=(0, 10))

    header = ctk.CTkFrame(
      sched_card, 
      fg_color="transparent"
    )
    header.pack(fill="x", padx=15, pady=(10, 5))

    ctk.CTkLabel(
        header,
        text="📅 Today's Schedule",
        font=("Segoe UI", 16, "bold"),
        text_color="#2D2D2D",
    ).pack(side="left")

    today_str = datetime.datetime.now().strftime("%A, %d %b %Y")
    ctk.CTkLabel(
        header,
        text=today_str,
        font=("Segoe UI", 11, "bold"),
        text_color="#8D5A4F",
        fg_color="#F7E8E1",
        corner_radius=6,
        padx=8,
        pady=2,
    ).pack(side="right")

    # Fetch today's appointments from MongoDB
    today_date_only = datetime.datetime.now().strftime("%Y-%m-%d")
    today_appts = list(
        appts_col.find(
            {"datetime": {"$regex": f"^{today_date_only}"}}
        ).limit(3)
    )

    if not today_appts:
      # Fallback to recent 3 appointments if today is empty
      today_appts = list(appts_col.find().sort("_id", -1).limit(3))

    if today_appts:
      for appt in today_appts:
        dt_val = appt.get("datetime", "")
        time_part = (
            dt_val.split(" | ")[1] if " | " in dt_val else dt_val[:10]
        )

        item = ctk.CTkFrame(
            sched_card, 
            fg_color="#FAF7F2", 
            corner_radius=8, 
            height=38
        )
        item.pack(fill="x", padx=15, pady=3)
        item.pack_propagate(False)

        ctk.CTkLabel(
            item,
            text=f"🕒 {time_part}",
            font=("Segoe UI", 12, "bold"),
            text_color="#C96C4B",
            width=90,
            anchor="w",
        ).pack(side="left", padx=10)
        ctk.CTkLabel(
            item,
            text=f"{appt.get('pet', 'Pet')}",
            font=("Segoe UI", 12, "bold"),
            text_color="#2D2D2D",
            width=110,
            anchor="w",
        ).pack(side="left")
        ctk.CTkLabel(
            item,
            text=f"Owner: {appt.get('owner', 'N/A')}",
            font=("Segoe UI", 12),
            text_color="#555",
            width=120,
            anchor="w",
        ).pack(side="left")
        ctk.CTkLabel(
            item,
            text=f"• {appt.get('service', 'Service')}",
            font=("Segoe UI", 12, "bold"),
            text_color="#8D5A4F",
        ).pack(side="left", padx=5)
    else:
      ctk.CTkLabel(
          sched_card,
          text="No appointments scheduled for today.",
          font=("Segoe UI", 12, "italic"),
          text_color="#A68A7A",
      ).pack(pady=30)

    # --- Right Widget: Quick Shortcuts & Low Stock Alerts (40% width) ---
    right_card = ctk.CTkFrame(
        middle_frame, 
        fg_color="white", 
        corner_radius=12, 
        width=420, 
        height=220
    )
    right_card.pack(side="right", fill="both", padx=(10, 0))
    right_card.pack_propagate(False)

    ctk.CTkLabel(
        right_card,
        text="⚡ Quick Actions & Alerts",
        font=("Segoe UI", 16, "bold"),
        text_color="#2D2D2D",
    ).pack(anchor="w", padx=15, pady=(10, 8))

    btn_grid = ctk.CTkFrame(right_card, fg_color="transparent")
    btn_grid.pack(fill="x", padx=15, pady=(0, 10))

    # Quick Action Buttons
    ctk.CTkButton(
        btn_grid,
        text="+ Book Appt",
        fg_color="#C96C4B",
        hover_color="#B65A3B",
        font=("Segoe UI", 11, "bold"),
        height=32,
        corner_radius=8,
        command=lambda: BookAppointmentModal(self, title="Book Appointment"),
    ).pack(side="left", expand=True, fill="x", padx=2)

    ctk.CTkButton(
        btn_grid,
        text="+ Add Pet",
        fg_color="#8D5A4F",
        hover_color="#73473D",
        font=("Segoe UI", 11, "bold"),
        height=32,
        corner_radius=8,
        command=lambda: AddPetModal(self, title="Add New Pet"),
    ).pack(side="left", expand=True, fill="x", padx=2)

    ctk.CTkButton(
        btn_grid,
        text="+ Customer",
        fg_color="#5F7F63",
        hover_color="#49634C",
        font=("Segoe UI", 11, "bold"),
        height=32,
        corner_radius=8,
        command=lambda: AddCustomerModal(self, title="Add Customer"),
    ).pack(side="left", expand=True, fill="x", padx=2)

    # Low Stock Alerts Box
    alerts_frame = ctk.CTkFrame(
      right_card, 
      fg_color="#FFF8F5", 
      corner_radius=8
    )
    alerts_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))

    low_stock_prods = list(
        products_col.find(
            {"status": {"$in": ["Low Stock", "Out of Stock"]}}
        ).limit(2)
    )

    if low_stock_prods:
      for prod in low_stock_prods:
        row = ctk.CTkFrame(alerts_frame, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=4)
        status_color = (
            "#A94442" if prod.get("status") == "Out of Stock" else "#C96C4B"
        )
        ctk.CTkLabel(
            row,
            text=f"⚠️ {prod.get('name')} ({prod.get('status')})",
            font=("Segoe UI", 11, "bold"),
            text_color=status_color,
        ).pack(side="left")
        ctk.CTkLabel(
            row,
            text=f"Stock: {prod.get('stock')}",
            font=("Segoe UI", 11),
            text_color="#555",
        ).pack(side="right")
    else:
      ctk.CTkLabel(
          alerts_frame,
          text="✓ Inventory is healthy. No low stock warnings.",
          font=("Segoe UI", 11),
          text_color="#5F7F63",
      ).pack(pady=15)

  # 3. RECENT APPOINTMENTS TABLE (MongoDB Connected)

  def build_recent_appointments_table(self):
    appointments_frame = ctk.CTkFrame(
      self, 
      fg_color="white", 
      corner_radius=12
    )
    appointments_frame.pack(fill="both", expand=True)

    ctk.CTkLabel(
        appointments_frame,
        text="📋 Recent Appointments",
        font=("Segoe UI", 18, "bold"),
        text_color="#2D2D2D",
    ).pack(anchor="w", padx=20, pady=(12, 10))

    table_frame = ctk.CTkFrame(appointments_frame, fg_color="transparent")
    table_frame.pack(fill="x", padx=20, pady=(0, 15))

    headers = [
        "Pet Name",
        "Owner",
        "Service",
        "Date & Time",
        "Status",
        "Actions",
    ]
    column_widths = [160, 160, 180, 180, 150, 120]

    # Header Row
    for column, header in enumerate(headers):
      header_cell = ctk.CTkFrame(
          table_frame,
          width=column_widths[column],
          height=38,
          fg_color="#F7E8E1",
          border_width=1,
          border_color="#E8D2C8",
          corner_radius=0,
      )
      header_cell.grid(row=0, column=column, sticky="nsew")
      header_cell.grid_propagate(False)

      ctk.CTkLabel(
          header_cell,
          text=header,
          font=("Segoe UI", 12, "bold"),
          text_color="#8D5A4F",
      ).place(relx=0.5, rely=0.5, anchor="center")

    recent_appts = list(appts_col.find().sort("_id", -1).limit(4))

    # Data Rows
    for row, appt in enumerate(recent_appts, start=1):
      vals = [
          appt.get("pet", ""),
          appt.get("owner", ""),
          appt.get("service", ""),
          appt.get("datetime", ""),
          appt.get("status", ""),
      ]

      for column in range(6):
        cell = ctk.CTkFrame(
            table_frame,
            width=column_widths[column],
            height=42,
            fg_color="white",
            border_width=1,
            border_color="#E8E0DC",
            corner_radius=0,
        )
        cell.grid(row=row, column=column, sticky="nsew")
        cell.grid_propagate(False)

        if column < 5:
          value = vals[column]

          if column == 4:
            if value == "Completed":
              text_color = "#5F7F63"
            elif value == "Pending":
              text_color = "#C96C4B"
            elif value == "Cancelled":
              text_color = "#A94442"
            else:
              text_color = "#2E6B9E"
            font = ("Segoe UI", 12, "bold")
          else:
            text_color = "#2D2D2D"
            font = ("Segoe UI", 12)

          ctk.CTkLabel(
              cell, 
              text=str(value), 
              font=font, 
              text_color=text_color
          ).place(relx=0.5, rely=0.5, anchor="center")

        else:
          # Actions Column
          actions_container = ctk.CTkFrame(cell, fg_color="transparent")
          actions_container.place(relx=0.5, rely=0.5, anchor="center")

          ctk.CTkButton(
              actions_container,
              text="✏️",
              width=28,
              height=28,
              fg_color="#F0E0D6",
              hover_color="#E2CEC1",
              text_color="black",
              corner_radius=6,
              command=lambda a=appt: BookAppointmentModal(
                  self, title=f"Edit Appointment ({a['id']})", appt_data=a
              ),
          ).pack(side="left", padx=2)

          ctk.CTkButton(
              actions_container,
              text="🗑️",
              width=28,
              height=28,
              fg_color="#FADBD8",
              hover_color="#F5B7B1",
              text_color="black",
              corner_radius=6,
              command=lambda aid=appt.get("id"): self.delete_appt(aid),
          ).pack(side="left", padx=2)

  def delete_appt(self, appt_id):
    if appt_id:
      appts_col.delete_one({"id": appt_id})
      self.build_recent_appointments_table()

  def load_pets(self):
    pass

  def load_customers(self):
    pass

  def load_appointments(self):
    self.build_recent_appointments_table()