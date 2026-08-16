import customtkinter as ctk
from pymongo import MongoClient
from utils import ConfirmDeleteModal, chain_enter_keys

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["PawfectCare"]
products_col = db["products"]


class AddProductModal(ctk.CTkToplevel):
  #Modal dialog for adding and editing inventory products with Enter key navigation.

  def __init__(self, parent, title="Add New Product", product_data=None):
    super().__init__(parent)
    self.title(title)
    self.geometry("460x580")
    self.resizable(False, False)
    self.configure(fg_color="#FAF7F2")

    self.product_data = product_data or {}
    self.parent_page = parent

    self.main_container = ctk.CTkFrame(self, fg_color="#FAF7F2")
    self.main_container.pack(fill="both", expand=True)

    ctk.CTkLabel(
        self.main_container,
        text=title,
        font=("Segoe UI", 20, "bold"),
        text_color="#2D2D2D",
    ).pack(pady=(20, 15))

    self.name_entry = self._create_field(
        "Product Name:", 
        self.product_data.get("name")
    )

    # Category Dropdown Menu
    ctk.CTkLabel(
        self.main_container,
        text="Category:",
        font=("Segoe UI", 12, "bold"),
        text_color="#8D5A4F",
    ).pack(anchor="w", padx=40, pady=(4, 2))

    categories = [
        "Food & Treats",
        "Toys & Entertainment",
        "Healthcare & Supplements",
        "Grooming Supplies",
        "Accessories & Gear",
        "General",
    ]
    default_cat = self.product_data.get("category") or categories[0]
    if default_cat not in categories:
      categories.append(default_cat)

    self.category_opt = ctk.CTkOptionMenu(
        self.main_container,
        values=categories,
        fg_color="white",
        text_color="#2D2D2D",
        button_color="#C96C4B",
        button_hover_color="#B65A3B",
        dropdown_fg_color="white",
        dropdown_text_color="#2D2D2D",
        height=35,
    )
    self.category_opt.set(default_cat)
    self.category_opt.pack(fill="x", padx=40, pady=(0, 4))

    self.price_entry = self._create_field(
        "Price (₹):", 
        self.product_data.get("price")
    )
    self.stock_entry = self._create_field(
        "Stock Quantity:", 
        self.product_data.get("stock")
    )
    self.desc_entry = self._create_field(
        "Description:", 
        self.product_data.get("description")
    )

    btn_save = ctk.CTkButton(
        self.main_container,
        text="Save Product Record",
        fg_color="#C96C4B",
        hover_color="#B65A3B",
        font=("Segoe UI", 14, "bold"),
        height=44,
        corner_radius=12,
        command=self.save_product,
    )
    btn_save.pack(fill="x", padx=40, pady=20)

    chain_enter_keys(
        [
            self.name_entry,
            self.price_entry,
            self.stock_entry,
            self.desc_entry,
        ],
        submit_callback=self.save_product,
    )

    self.center_on_screen(parent, 460, 580)

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

  def save_product(self):
    name_val = self.name_entry.get().strip()
    category_val = self.category_opt.get()
    price_val = self.price_entry.get().strip()
    stock_val = self.stock_entry.get().strip()
    desc_val = self.desc_entry.get().strip()

    if not name_val or not price_val:
      ctk.CTkLabel(
          self.main_container,
          text="Product Name and Price are required.",
          text_color="#C96C4B",
          font=("Segoe UI", 12),
      ).pack(pady=2)
      return

    if not price_val.startswith("₹"):
      price_val = f"₹{price_val}"

    try:
      stock_num = int(stock_val) if stock_val else 0
    except ValueError:
      stock_num = 0

    payload = {
        "name": name_val,
        "category": category_val,
        "price": price_val,
        "stock": stock_num,
        "description": desc_val,
    }

    if self.product_data.get("id"):
      products_col.update_one(
          {"id": self.product_data["id"]}, {"$set": payload}
      )
      self.parent_page.show_status(
          "Product record updated successfully!", "#6D8B74"
      )
    elif self.product_data.get("_id"):
      products_col.update_one(
          {"_id": self.product_data["_id"]}, {"$set": payload}
      )
      self.parent_page.show_status(
          "Product record updated successfully!", "#6D8B74"
      )
    else:
      last_prod = products_col.find_one({}, sort=[("_id", -1)])
      if last_prod and "id" in last_prod:
        try:
          last_num = int(last_prod["id"].split("-")[1])
          prod_id = f"PRD-{last_num + 1}"
        except Exception:
          prod_id = "PRD-101"
      else:
        prod_id = "PRD-101"

      payload["id"] = prod_id
      products_col.insert_one(payload)
      self.parent_page.show_status("New product added successfully!", "#6D8B74")

    self.parent_page.load_products()
    self.destroy()


class ProductsPage(ctk.CTkFrame):
  #Products Management UI Page displaying items in an interactive Card Layout.

  def __init__(self, parent):
    super().__init__(parent, fg_color="#FAF7F2")

    # Top Control Bar
    controls = ctk.CTkFrame(self, fg_color="white", corner_radius=12, height=70)
    controls.pack(fill="x", pady=(0, 15))
    controls.pack_propagate(False)

    self.search = ctk.CTkEntry(
        controls,
        placeholder_text="🔍 Search Product...",
        width=280,
        height=40,
        fg_color="#FAF7F2",
        border_color="#E8D2C8",
        text_color="#2D2D2D",
        placeholder_text_color="#A68A7A",
    )
    self.search.pack(side="left", padx=20, pady=15)
    self.search.bind("<KeyRelease>", lambda event: self.load_products())

    btn_add = ctk.CTkButton(
        controls,
        text="+ Add Product",
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
        text="📦 Product & Inventory Catalog",
        font=("Segoe UI", 18, "bold"),
        text_color="#2D2D2D",
    ).pack(anchor="w", padx=20, pady=(15, 10))

    # Scrollable Grid Frame for Cards
    self.cards_scroll = ctk.CTkScrollableFrame(
        main_card, 
        fg_color="transparent"
    )
    self.cards_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    self.status_label = ctk.CTkLabel(
        self, text="", 
        font=("Segoe UI", 13, "bold"), 
        text_color="#6D4C41"
    )
    self.status_label.pack(side="bottom", pady=(0, 10))

    self.load_products()

  def load_products(self):
    for widget in self.cards_scroll.winfo_children():
      widget.destroy()

    search_query = self.search.get().strip()
    query = {}
    if search_query:
      query["$or"] = [
          {"name": {"$regex": search_query, "$options": "i"}},
          {"category": {"$regex": search_query, "$options": "i"}},
          {"description": {"$regex": search_query, "$options": "i"}},
          {"id": {"$regex": search_query, "$options": "i"}},
      ]

    prod_records = list(products_col.find(query))

    if not prod_records:
      empty_frame = ctk.CTkFrame(
          self.cards_scroll, 
          fg_color="#FAF7F2", 
          corner_radius=10
      )
      empty_frame.pack(fill="x", pady=20, padx=20)
      ctk.CTkLabel(
          empty_frame,
          text="No products found matching your search.",
          font=("Segoe UI", 12, "italic"),
          text_color="#A68A7A",
      ).pack(pady=20)
      return

    # Render Products as Cards
    for prod in prod_records:
      prod_card = ctk.CTkFrame(
          self.cards_scroll,
          fg_color="#FAF7F2",
          corner_radius=12,
          border_width=1,
          border_color="#E8D2C8",
      )
      prod_card.pack(fill="x", pady=6, padx=5, ipadx=10, ipady=8)

      # Top Row: Title + Price Tag
      top_row = ctk.CTkFrame(prod_card, fg_color="transparent")
      top_row.pack(fill="x", padx=10, pady=(6, 2))

      prod_id = prod.get("id") or str(prod.get("_id", ""))
      title_text = f"📦 {prod.get('name', 'Product')}  ({prod_id})"
      ctk.CTkLabel(
          top_row,
          text=title_text,
          font=("Segoe UI", 15, "bold"),
          text_color="#2D2D2D",
      ).pack(side="left")

      ctk.CTkLabel(
          top_row,
          text=prod.get("price", "₹0"),
          font=("Segoe UI", 13, "bold"),
          text_color="white",
          fg_color="#C96C4B",
          corner_radius=8,
          padx=10,
          pady=3,
      ).pack(side="right")

      # Middle Row: Category & Stock Level Status
      body_row = ctk.CTkFrame(prod_card, fg_color="transparent")
      body_row.pack(fill="x", padx=10, pady=2)

      stock_val = prod.get("stock", 0)
      try:
        stock_num = int(stock_val)
      except ValueError:
        stock_num = 0

      if stock_num == 0:
        status_text = "Out of Stock"
      elif stock_num <= 5:
        status_text = f"Low Stock ({stock_num} left)"
      else:
        status_text = f"In Stock ({stock_num} available)"

      details_text = f"🏷️ Category: {prod.get('category', 'General')}   |   Status: {status_text}"
      ctk.CTkLabel(
          body_row,
          text=details_text,
          font=("Segoe UI", 11, "bold"),
          text_color="#8D5A4F",
      ).pack(anchor="w", pady=(0, 2))

      if prod.get("description"):
        ctk.CTkLabel(
            body_row,
            text=prod.get("description"),
            font=("Segoe UI", 11),
            text_color="#555555",
            justify="left",
            wraplength=700,
        ).pack(anchor="w")

      # Bottom Row: Action Buttons (Edit & Delete)
      actions_row = ctk.CTkFrame(prod_card, fg_color="transparent")
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
          command=lambda p=prod: ConfirmDeleteModal(
              self,
              item_name=p.get("name", "Product"),
              confirm_callback=lambda: self.delete_product(p),
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
          command=lambda p=prod: self.open_edit_modal(p),
      ).pack(side="right", padx=4)

  def open_add_modal(self):
    AddProductModal(self, title="Add New Product")

  def open_edit_modal(self, product_data):
    display_id = product_data.get("id") or str(product_data.get("_id", ""))
    AddProductModal(
        self,
        title=f"Edit Product ({display_id})",
        product_data=product_data,
    )

  def delete_product(self, prod_item):
    prod_id = prod_item.get("id")
    mongo_id = prod_item.get("_id")

    if prod_id:
      result = products_col.delete_one({"id": prod_id})
    elif mongo_id:
      result = products_col.delete_one({"_id": mongo_id})
    else:
      result = None

    if result and result.deleted_count == 1:
      self.show_status("Product record deleted successfully!", "#6D8B74")
      self.load_products()
    else:
      self.show_status("Product record not found.", "#C96C4B")

  def show_status(self, message, color):
    self.status_label.configure(text=message, text_color=color)
    self.after(5000, lambda: self.status_label.configure(text=""))