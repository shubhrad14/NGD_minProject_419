import customtkinter as ctk
from pymongo import MongoClient
from utils import ConfirmDeleteModal, chain_enter_keys

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["PawfectCare"]
services_col = db["services"]


class AddServiceModal(ctk.CTkToplevel):
  #Modal dialog for adding and editing services with Enter key navigation.

  def __init__(
      self, parent, 
      title="Add New Service", 
      service_data=None
    ):
    super().__init__(parent)
    self.title(title)
    self.geometry("460x540")
    self.resizable(False, False)
    self.configure(fg_color="#FAF7F2")

    self.service_data = service_data or {}
    self.parent_page = parent

    self.main_container = ctk.CTkFrame(self, fg_color="#FAF7F2")
    self.main_container.pack(fill="both", expand=True)

    ctk.CTkLabel(
        self.main_container,
        text=title,
        font=("Segoe UI", 20, "bold"),
        text_color="#2D2D2D",
    ).pack(pady=(20, 15))

    self.title_entry = self._create_field(
        "Service Title:", self.service_data.get("title")
    )
    self.price_entry = self._create_field(
        "Price (₹):", self.service_data.get("price")
    )
    self.duration_entry = self._create_field(
        "Duration (e.g. 45 mins):", self.service_data.get("duration")
    )
    self.desc_entry = self._create_field(
        "Description:", self.service_data.get("description")
    )

    btn_save = ctk.CTkButton(
        self.main_container,
        text="Save Service Record",
        fg_color="#C96C4B",
        hover_color="#B65A3B",
        font=("Segoe UI", 14, "bold"),
        height=44,
        corner_radius=12,
        command=self.save_service,
    )
    btn_save.pack(fill="x", padx=40, pady=20)

    chain_enter_keys(
        [
            self.title_entry,
            self.price_entry,
            self.duration_entry,
            self.desc_entry,
        ],
        submit_callback=self.save_service,
    )

    self.center_on_screen(parent, 460, 540)

  def _create_field(self, label, default=None):
    ctk.CTkLabel(
        self.main_container,
        text=label,
        font=("Segoe UI", 12, "bold"),
        text_color="#8D5A4F",
    ).pack(anchor="w", padx=40, pady=(4, 2))

    entry = ctk.CTkEntry(
        self.main_container,
        fg_color="white",
        text_color="#2D2D2D",
        border_color="#E8D2C8",
        height=35,
    )
    if default is not None:
      entry.insert(0, str(default))
    entry.pack(fill="x", padx=40, pady=(0, 4))
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

  def save_service(self):
    title_val = self.title_entry.get().strip()
    price_val = self.price_entry.get().strip()
    duration_val = self.duration_entry.get().strip()
    desc_val = self.desc_entry.get().strip()

    if not title_val or not price_val:
      ctk.CTkLabel(
          self.main_container,
          text="Title and Price are required.",
          text_color="#C96C4B",
          font=("Segoe UI", 12),
      ).pack(pady=2)
      return

    if not price_val.startswith("₹"):
      price_val = f"₹{price_val}"

    payload = {
        "title": title_val,
        "price": price_val,
        "duration": duration_val,
        "description": desc_val,
    }

    if self.service_data.get("id"):
      services_col.update_one(
          {"id": self.service_data["id"]}, {"$set": payload}
      )
      self.parent_page.show_status(
          "Service record updated successfully!", "#6D8B74"
      )
    elif self.service_data.get("_id"):
      services_col.update_one(
          {"_id": self.service_data["_id"]}, {"$set": payload}
      )
      self.parent_page.show_status(
          "Service record updated successfully!", "#6D8B74"
      )
    else:
      last_svc = services_col.find_one({}, sort=[("_id", -1)])
      if last_svc and "id" in last_svc:
        try:
          last_num = int(last_svc["id"].split("-")[1])
          svc_id = f"SVC-{last_num + 1}"
        except Exception:
          svc_id = "SVC-101"
      else:
        svc_id = "SVC-101"

      payload["id"] = svc_id
      services_col.insert_one(payload)
      self.parent_page.show_status("New service added successfully!", "#6D8B74")

    self.parent_page.load_services()
    self.destroy()


class ServicesPage(ctk.CTkFrame):
  #Services Management UI Page displaying services in an interactive Card Layout.

  def __init__(self, parent):
    super().__init__(parent, fg_color="#FAF7F2")

    # Top Control Bar
    controls = ctk.CTkFrame(self, fg_color="white", corner_radius=12, height=70)
    controls.pack(fill="x", pady=(0, 15))
    controls.pack_propagate(False)

    self.search = ctk.CTkEntry(
        controls,
        placeholder_text="🔍 Search Service...",
        width=280,
        height=40,
        fg_color="#FAF7F2",
        border_color="#E8D2C8",
        text_color="#2D2D2D",
        placeholder_text_color="#A68A7A",
    )
    self.search.pack(side="left", padx=20, pady=15)
    self.search.bind("<KeyRelease>", lambda event: self.load_services())

    btn_add = ctk.CTkButton(
        controls,
        text="+ Add Service",
        font=("Segoe UI", 14, "bold"),
        fg_color="#C96C4B",
        hover_color="#B65A3B",
        height=40,
        command=self.open_add_modal,
    )
    btn_add.pack(side="right", padx=20, pady=15)

    # Main Card Container Frame
    main_card = ctk.CTkFrame(self, fg_color="white", corner_radius=12)
    main_card.pack(fill="both", expand=True)

    ctk.CTkLabel(
        main_card,
        text="✂️ Service Offerings Catalog",
        font=("Segoe UI", 18, "bold"),
        text_color="#2D2D2D",
    ).pack(anchor="w", padx=20, pady=(15, 10))

    # Scrollable Grid Frame for Cards
    self.cards_scroll = ctk.CTkScrollableFrame(
        main_card, fg_color="transparent"
    )
    self.cards_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    self.status_label = ctk.CTkLabel(
        self, text="", font=("Segoe UI", 13, "bold"), text_color="#6D4C41"
    )
    self.status_label.pack(side="bottom", pady=(0, 10))

    self.load_services()

  def load_services(self):
    for widget in self.cards_scroll.winfo_children():
      widget.destroy()

    search_query = self.search.get().strip()
    query = {}
    if search_query:
      query["$or"] = [
          {"title": {"$regex": search_query, "$options": "i"}},
          {"description": {"$regex": search_query, "$options": "i"}},
          {"id": {"$regex": search_query, "$options": "i"}},
      ]

    svc_records = list(services_col.find(query))

    if not svc_records:
      empty_frame = ctk.CTkFrame(
          self.cards_scroll, fg_color="#FAF7F2", corner_radius=10
      )
      empty_frame.pack(fill="x", pady=20, padx=20)
      ctk.CTkLabel(
          empty_frame,
          text="No services found matching your search.",
          font=("Segoe UI", 12, "italic"),
          text_color="#A68A7A",
      ).pack(pady=20)
      return

    # Render Services as Cards
    for svc in svc_records:
      svc_card = ctk.CTkFrame(
          self.cards_scroll,
          fg_color="#FAF7F2",
          corner_radius=12,
          border_width=1,
          border_color="#E8D2C8",
      )
      svc_card.pack(fill="x", pady=6, padx=5, ipadx=10, ipady=8)

      # Top Row: Title + Price Tag
      top_row = ctk.CTkFrame(svc_card, fg_color="transparent")
      top_row.pack(fill="x", padx=10, pady=(6, 2))

      svc_id = svc.get("id") or str(svc.get("_id", ""))
      title_text = f"✂️ {svc.get('title', 'Service')}  ({svc_id})"
      ctk.CTkLabel(
          top_row,
          text=title_text,
          font=("Segoe UI", 15, "bold"),
          text_color="#2D2D2D",
      ).pack(side="left")

      ctk.CTkLabel(
          top_row,
          text=svc.get("price", "₹0"),
          font=("Segoe UI", 13, "bold"),
          text_color="white",
          fg_color="#C96C4B",
          corner_radius=8,
          padx=10,
          pady=3,
      ).pack(side="right")

      # Middle Row: Duration & Description
      body_row = ctk.CTkFrame(svc_card, fg_color="transparent")
      body_row.pack(fill="x", padx=10, pady=2)

      if svc.get("duration"):
        ctk.CTkLabel(
            body_row,
            text=f"⏱️ {svc.get('duration')}",
            font=("Segoe UI", 11, "bold"),
            text_color="#8D5A4F",
        ).pack(anchor="w", pady=(0, 2))

      if svc.get("description"):
        ctk.CTkLabel(
            body_row,
            text=svc.get("description"),
            font=("Segoe UI", 11),
            text_color="#555555",
            justify="left",
            wraplength=700,
        ).pack(anchor="w")

      # Bottom Row: Action Buttons (Edit & Delete)
      actions_row = ctk.CTkFrame(svc_card, fg_color="transparent")
      actions_row.pack(fill="x", padx=10, pady=(6, 2))

      ctk.CTkButton(
          actions_row,
          text="🗑️ Delete",
          width=80,
          height=30,
          fg_color="#FADBD8",
          hover_color="#F5B7B1",
          text_color="#A94442",
          font=("Segoe UI", 11, "bold"),
          corner_radius=6,
          command=lambda s=svc: ConfirmDeleteModal(
              self,
              item_name=s.get("title", "Service"),
              confirm_callback=lambda: self.delete_service(s),
          ),
      ).pack(side="right", padx=(4, 0))

      ctk.CTkButton(
          actions_row,
          text="✏️ Edit",
          width=75,
          height=30,
          fg_color="#F0E0D6",
          hover_color="#E2CEC1",
          text_color="#2D2D2D",
          font=("Segoe UI", 11, "bold"),
          corner_radius=6,
          command=lambda s=svc: self.open_edit_modal(s),
      ).pack(side="right", padx=4)

  def open_add_modal(self):
    AddServiceModal(self, title="Add New Service")

  def open_edit_modal(self, service_data):
    display_id = service_data.get("id") or str(service_data.get("_id", ""))
    AddServiceModal(
        self,
        title=f"Edit Service ({display_id})",
        service_data=service_data,
    )

  def delete_service(self, svc_item):
    svc_id = svc_item.get("id")
    mongo_id = svc_item.get("_id")

    if svc_id:
      result = services_col.delete_one({"id": svc_id})
    elif mongo_id:
      result = services_col.delete_one({"_id": mongo_id})
    else:
      result = None

    if result and result.deleted_count == 1:
      self.show_status("Service record deleted successfully!", "#6D8B74")
      self.load_services()
    else:
      self.show_status("Service record not found.", "#C96C4B")

  def show_status(self, message, color):
    self.status_label.configure(text=message, text_color=color)
    self.after(5000, lambda: self.status_label.configure(text=""))