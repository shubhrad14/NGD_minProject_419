import customtkinter as ctk
from pymongo import MongoClient
from utils import chain_enter_keys

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["PawfectCare"]
products_col = db["products"]


class AddProductModal(ctk.CTkToplevel):
    #Modal dialog for adding and editing inventory products with Enter key navigation.
    def __init__(
            self, 
            parent, 
            title="Add New Product", 
            product_data=None
        ):
        super().__init__(parent)
        self.title(title)
        self.geometry("460x540")
        self.resizable(False, False)
        self.configure(fg_color="#FAF7F2")

        self.product_data = product_data or {}
        self.parent_page = parent

        # Main Container Wrapper
        self.main_container = ctk.CTkFrame(self, fg_color="#FAF7F2")
        self.main_container.pack(fill="both", expand=True)

        ctk.CTkLabel(
            self.main_container, 
            text=title, 
            font=("Segoe UI", 20, "bold"), 
            text_color="#2D2D2D"
        ).pack(pady=(20, 15))

        self.name_entry = self._create_field("Product Name:", self.product_data.get("name"))

        ctk.CTkLabel(
            self.main_container, 
            text="Category:", 
            font=("Segoe UI", 12, "bold"), 
            text_color="#8D5A4F"
        ).pack(anchor="w", padx=40, pady=(4, 2))

        self.category_opt = ctk.CTkOptionMenu(
            self.main_container,
            values=["Food & Treats", "Grooming Supplies", "Toys & Accessories", "Healthcare & Medicines", "Other"],
            fg_color="white", 
            text_color="#2D2D2D", 
            button_color="#C96C4B", 
            button_hover_color="#B65A3B",
            dropdown_text_color="#2D2D2D", 
            dropdown_fg_color="white", 
            dropdown_hover_color="#F7E8E1"
        )
        if self.product_data.get("category"):
            self.category_opt.set(self.product_data.get("category"))
        self.category_opt.pack(fill="x", padx=40, pady=(0, 6))

        self.price_entry = self._create_field("Price (₹):", self.product_data.get("price"))
        self.stock_entry = self._create_field("Stock Quantity:", self.product_data.get("stock"))

        btn_save = ctk.CTkButton(
            self.main_container, 
            text="Save Product Record", 
            fg_color="#C96C4B",
              hover_color="#B65A3B",
            font=("Segoe UI", 14, "bold"), 
            height=40, 
            command=self.save_product
        )
        btn_save.pack(fill="x", padx=40, pady=20)

        # ⌨️ Chain Enter Key Navigation
        chain_enter_keys(
            [
                self.name_entry,
                self.price_entry,
                self.stock_entry
            ],
            submit_callback=self.save_product
        )

        self.center_on_screen(parent, 460, 540)

    def _create_field(self, label, default=None):
        ctk.CTkLabel(
            self.main_container, 
            text=label, font=("Segoe UI", 12, "bold"), 
            text_color="#8D5A4F"
        ).pack(anchor="w", padx=40, pady=(4, 2))

        entry = ctk.CTkEntry(
            self.main_container, 
            fg_color="white", 
            text_color="#2D2D2D", 
            border_color="#E8D2C8", 
            height=35
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
        name = self.name_entry.get().strip()
        category = self.category_opt.get()
        price = self.price_entry.get().strip()
        stock_str = self.stock_entry.get().strip()

        if not name or not price or not stock_str:
            ctk.CTkLabel(
                self.main_container, 
                text="Please fill in all required fields.", 
                text_color="#C96C4B", 
                font=("Segoe UI", 12)
            ).pack(pady=2)
            return

        if not price.startswith("₹"):
            price = f"₹{price}"

        try:
            stock_qty = int(stock_str)
            if stock_qty == 0:
                status = "Out of Stock"
            elif stock_qty <= 5:
                status = "Low Stock"
            else:
                status = "In Stock"
        except ValueError:
            status = "In Stock"

        if self.product_data.get("id"):
            products_col.update_one(
                {"id": self.product_data["id"]},
                {"$set": {"name": name, "category": category, "price": price, "stock": stock_str, "status": status}}
            )
            self.parent_page.show_status("Product updated successfully!", "#6D8B74")
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

            products_col.insert_one({
                "id": prod_id,
                "name": name,
                "category": category,
                "price": price,
                "stock": stock_str,
                "status": status
            })
            self.parent_page.show_status("Product added successfully!", "#6D8B74")

        self.parent_page.load_products()
        self.destroy()


class ProductsPage(ctk.CTkFrame):
    #Inventory Products Management UI Page.
    def __init__(self, parent):
        super().__init__(parent, fg_color="#FAF7F2")

        self.headers = ["ID", "Product Name", "Category", "Price", "Stock", "Status", "Actions"]
        self.widths = [90, 180, 160, 110, 100, 120, 140]

        # Action Bar
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
            placeholder_text="🔍 Search Product...",
            width=280, 
            height=40, 
            fg_color="#FAF7F2", 
            border_color="#E8D2C8",
            text_color="#2D2D2D", 
            placeholder_text_color="#A68A7A"
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
            command=self.open_add_modal
        )
        btn_add.pack(side="right", padx=20, pady=15)

        # Table Card
        table_card = ctk.CTkFrame(self, fg_color="white", corner_radius=12)
        table_card.pack(fill="both", expand=True)

        ctk.CTkLabel(
            table_card, text="📦 Inventory Master List",
            font=("Segoe UI", 18, "bold"), 
            text_color="#2D2D2D"
        ).pack(anchor="w", padx=20, pady=(15, 10))

        # Header Row
        header_frame = ctk.CTkFrame(table_card, fg_color="transparent")
        header_frame.pack(fill="x", padx=20)

        for idx, h in enumerate(self.headers):
            cell = ctk.CTkFrame(
                header_frame, 
                width=self.widths[idx], 
                height=38,
                fg_color="#F7E8E1", 
                border_width=1, 
                border_color="#E8D2C8"
            )
            cell.grid(row=0, column=idx, sticky="nsew")
            cell.grid_propagate(False)
            ctk.CTkLabel(
                cell, 
                text=h, 
                font=("Segoe UI", 12, "bold"), 
                text_color="#8D5A4F"
            ).place(relx=0.5, rely=0.5, anchor="center")

        # Scrollable Data Frame
        self.scroll_table = ctk.CTkScrollableFrame(table_card, fg_color="transparent")
        self.scroll_table.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        self.status_label = ctk.CTkLabel(
            self, text="", 
            font=("Segoe UI", 13, "bold"), 
            text_color="#6D4C41"
        )
        self.status_label.pack(side="bottom", pady=(0, 10))

        self.load_products()

    def load_products(self):
        for widget in self.scroll_table.winfo_children():
            widget.destroy()

        search_query = self.search.get().strip()
        query = {}
        if search_query:
            query["$or"] = [
                {"name": {"$regex": search_query, "$options": "i"}},
                {"category": {"$regex": search_query, "$options": "i"}},
                {"id": {"$regex": search_query, "$options": "i"}}
            ]

        prod_records = list(products_col.find(query))

        for row_idx, prod in enumerate(prod_records):
            row_frame = ctk.CTkFrame(self.scroll_table, fg_color="transparent")
            row_frame.pack(fill="x", pady=1)

            vals = [
                prod.get("id", ""),
                prod.get("name", ""),
                prod.get("category", ""),
                prod.get("price", ""),
                prod.get("stock", ""),
                prod.get("status", "")
            ]

            for col_idx, val in enumerate(vals):
                cell = ctk.CTkFrame(
                    row_frame, 
                    width=self.widths[col_idx], 
                    height=40,
                    fg_color="white", 
                    border_width=1, 
                    border_color="#E8E0DC"
                )
                cell.grid(row=0, column=col_idx, sticky="nsew")
                cell.grid_propagate(False)

                if col_idx == 5:
                    if val == "In Stock":
                        text_color = "#5F7F63"
                    elif val == "Low Stock":
                        text_color = "#C96C4B"
                    else:
                        text_color = "#A94442"
                    font = ("Segoe UI", 12, "bold")
                else:
                    font = ("Segoe UI", 12, "bold") if col_idx == 0 else ("Segoe UI", 12)
                    text_color = "#8D5A4F" if col_idx == 0 else "#2D2D2D"

                ctk.CTkLabel(
                    cell, 
                    text=str(val), 
                    font=font, 
                    text_color=text_color
                ).place(relx=0.5, rely=0.5, anchor="center")

            # Actions Column
            action_cell = ctk.CTkFrame(
                row_frame, 
                width=self.widths[6], 
                height=40,
                fg_color="white", 
                border_width=1, 
                border_color="#E8E0DC"
            )
            action_cell.grid(row=0, column=6, sticky="nsew")
            action_cell.grid_propagate(False)

            container = ctk.CTkFrame(action_cell, fg_color="transparent")
            container.place(relx=0.5, rely=0.5, anchor="center")

            ctk.CTkButton(
                container, 
                text="✏️", 
                width=28, height=28,
                fg_color="#F0E0D6", 
                hover_color="#E2CEC1", 
                text_color="black",
                command=lambda p=prod: self.open_edit_modal(p)
            ).pack(side="left", padx=4)

            ctk.CTkButton(
                container, 
                text="🗑️", 
                width=28, 
                height=28,
                fg_color="#FADBD8", 
                hover_color="#F5B7B1", 
                text_color="black",
                command=lambda pid=prod["id"]: self.delete_product(pid)
            ).pack(side="left", padx=4)

    def open_add_modal(self):
        AddProductModal(self, title="Add New Product")

    def open_edit_modal(self, product_data):
        AddProductModal(
            self, 
            title=f"Edit Product ({product_data['id']})", 
            product_data=product_data
        )

    def delete_product(self, prod_id):
        result = products_col.delete_one({"id": prod_id})
        if result.deleted_count == 1:
            self.show_status("Product deleted successfully!", "#6D8B74")
            self.load_products()
        else:
            self.show_status("Product not found.", "#C96C4B")

    def show_status(self, message, color):
        self.status_label.configure(text=message, text_color=color)
        self.after(5000, lambda: self.status_label.configure(text=""))