import customtkinter as ctk
from pymongo import MongoClient
from utils import chain_enter_keys

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["PawfectCare"]
customers_col = db["customers"]
pets_col = db["pets"]
appointments_col = db["appointments"]


class CustomerDetailsModal(ctk.CTkToplevel):
    #Modal window displaying all customer information with matched button styling.

    def __init__(self, parent, customer_data):
        super().__init__(parent)
        self.title(f"Customer Details - {customer_data.get('name', 'Customer')}")
        self.geometry("480x600")
        self.resizable(False, False)
        self.configure(fg_color="#FAF7F2")

        self.main_container = ctk.CTkFrame(self, fg_color="#FAF7F2")
        self.main_container.pack(fill="both", expand=True)

        # Header
        ctk.CTkLabel(
            self.main_container,
            text="👤 Customer Info",
            font=("Segoe UI", 20, "bold"),
            text_color="#2D2D2D",
        ).pack(anchor="w", padx=40, pady=(20, 15))

        # Details Card
        info_card = ctk.CTkFrame(
            self.main_container, 
            fg_color="white", 
            corner_radius=12
        )
        info_card.pack(fill="x", padx=40, pady=(0, 15), ipadx=10, ipady=10)

        details = [
            ("Customer ID:", customer_data.get("id", "N/A")),
            ("Full Name:", customer_data.get("name", "N/A")),
            ("Phone Number:", customer_data.get("phone", "N/A")),
            ("Email Address:", customer_data.get("email", "N/A")),
            ("Address:", customer_data.get("address", "N/A")),
        ]

        for label, val in details:
            row = ctk.CTkFrame(info_card, fg_color="transparent")
            row.pack(fill="x", pady=4, padx=10)
            ctk.CTkLabel(
                row,
                text=label,
                font=("Segoe UI", 12, "bold"),
                text_color="#8D5A4F",
                width=120,
                anchor="w",
            ).pack(side="left")
            ctk.CTkLabel(
                row,
                text=str(val),
                font=("Segoe UI", 12),
                text_color="#2D2D2D",
                anchor="w",
            ).pack(side="left", fill="x", expand=True)

        #  Registered Pets Section
        ctk.CTkLabel(
            self.main_container,
            text="🐾 Registered Pets",
            font=("Segoe UI", 15, "bold"),
            text_color="#2D2D2D",
        ).pack(anchor="w", padx=40, pady=(5, 5))

        cust_name = customer_data.get("name", "")
        linked_pets = list(
            pets_col.find({"owner": {"$regex": f"^{cust_name}$", "$options": "i"}})
        )

        pets_frame = ctk.CTkScrollableFrame(
            self.main_container, height=140, fg_color="transparent"
        )
        pets_frame.pack(
            fill="both", 
            expand=True, 
            padx=40, 
            pady=(0, 15)
        )

        if linked_pets:
            for p in linked_pets:
                pet_card = ctk.CTkFrame(pets_frame, fg_color="white", corner_radius=10)
                pet_card.pack(fill="x", pady=4, padx=2)

                title_text = f"🐾 {p.get('name', 'Pet')} ({p.get('species', 'Pet')})"
                ctk.CTkLabel(
                    pet_card,
                    text=title_text,
                    font=("Segoe UI", 13, "bold"),
                    text_color="#C96C4B",
                ).pack(anchor="w", padx=12, pady=(8, 2))

                sub_text = (
                    f"Breed: {p.get('breed', 'N/A')}   |   Age: {p.get('age', 'N/A')}"
                )
                ctk.CTkLabel(
                    pet_card,
                    text=sub_text,
                    font=("Segoe UI", 11),
                    text_color="#555555",
                ).pack(anchor="w", padx=12, pady=(0, 8))
        else:
            empty_card = ctk.CTkFrame(
                pets_frame, 
                fg_color="white", 
                corner_radius=10
            )
            
            empty_card.pack(fill="x", pady=4)
            ctk.CTkLabel(
                empty_card,
                text="No pets registered under this customer.",
                font=("Segoe UI", 11, "italic"),
                text_color="#A68A7A",
            ).pack(pady=12)

        # 🔘 Standardized Close Button (Identical to Save Customer Button)
        btn_close = ctk.CTkButton(
            self.main_container,
            text="Close",
            fg_color="#C96C4B",
            hover_color="#B65A3B",
            font=("Segoe UI", 14, "bold"),
            height=44,
            corner_radius=12,
            command=self.destroy,
        )
        btn_close.pack(fill="x", padx=40, pady=(0, 20))

        self.center_on_screen(parent, 480, 600)

    def center_on_screen(self, parent, width, height):
        self.update_idletasks()
        root = parent.winfo_toplevel()
        x = root.winfo_rootx() + (root.winfo_width() // 2) - (width // 2)
        y = root.winfo_rooty() + (root.winfo_height() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{max(0, x)}+{max(0, y)}")
        self.grab_set()
        self.lift()
        self.focus_force()


class AddCustomerModal(ctk.CTkToplevel):
    #Modal dialog for adding/editing customers with automatic +91 phone and @gmail.com email defaults.

    def __init__(self, parent, title="Add Customer", customer_data=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("460x520")
        self.resizable(False, False)
        self.configure(fg_color="#FAF7F2")

        self.customer_data = customer_data or {}
        self.parent_page = parent

        self.main_container = ctk.CTkFrame(self, fg_color="#FAF7F2")
        self.main_container.pack(fill="both", expand=True)

        ctk.CTkLabel(
            self.main_container,
            text=title,
            font=("Segoe UI", 20, "bold"),
            text_color="#2D2D2D",
        ).pack(pady=(20, 15))

        phone_default = self.customer_data.get("phone") or "+91 "
        email_default = self.customer_data.get("email") or "@gmail.com"

        self.name_entry = self._create_field(
            "Customer Name:", self.customer_data.get("name")
        )
        self.phone_entry = self._create_field("Phone Number:", phone_default)
        self.email_entry = self._create_field("Email Address:", email_default)
        self.address_entry = self._create_field(
            "Address / City:", self.customer_data.get("address")
        )

        btn_save = ctk.CTkButton(
            self.main_container,
            text="Save Customer",
            fg_color="#C96C4B",
            hover_color="#B65A3B",
            font=("Segoe UI", 14, "bold"),
            height=44,
            corner_radius=12,
            command=self.save_customer,
        )
        btn_save.pack(fill="x", padx=40, pady=20)

        chain_enter_keys(
            [
                self.name_entry,
                self.phone_entry,
                self.email_entry,
                self.address_entry,
            ],
            submit_callback=self.save_customer,
        )

        self.center_on_screen(parent, 460, 520)

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

    def save_customer(self):
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()
        address = self.address_entry.get().strip()

        if not name or not phone or phone in ("+91", "+91 "):
            ctk.CTkLabel(
                self.main_container,
                text="Name and valid Phone Number are required.",
                text_color="#C96C4B",
                font=("Segoe UI", 12),
            ).pack(pady=2)
            return

        if self.customer_data.get("id"):
            customers_col.update_one(
                {"id": self.customer_data["id"]},
                {
                    "$set": {
                        "name": name,
                        "phone": phone,
                        "email": email,
                        "address": address,
                    }
                },
            )
            self.parent_page.show_status(
                "Customer record updated successfully!", "#6D8B74"
            )
        else:
            last_cust = customers_col.find_one({}, sort=[("_id", -1)])
            if last_cust and "id" in last_cust:
                try:
                    last_num = int(last_cust["id"].split("-")[1])
                    cust_id = f"CUST-{last_num + 1}"
                except Exception:
                    cust_id = "CUST-101"
            else:
                cust_id = "CUST-101"

            customers_col.insert_one({
                "id": cust_id,
                "name": name,
                "phone": phone,
                "email": email,
                "address": address,
            })
            self.parent_page.show_status(
                "New customer added successfully!", "#6D8B74"
            )

        self.parent_page.load_customers()
        self.destroy()


class CustomersPage(ctk.CTkFrame):
   # Customers Management UI Page.

    def __init__(self, parent):
        super().__init__(parent, fg_color="#FAF7F2")

        self.headers = [
            "ID",
            "Customer Name",
            "Phone",
            "Email",
            "Address",
            "Actions",
        ]
        self.widths = [90, 160, 140, 180, 160, 160]

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
            placeholder_text="🔍 Search Customer...",
            width=280,
            height=40,
            fg_color="#FAF7F2",
            border_color="#E8D2C8",
            text_color="#2D2D2D",
            placeholder_text_color="#A68A7A",
        )
        self.search.pack(side="left", padx=20, pady=15)
        self.search.bind("<KeyRelease>", lambda event: self.load_customers())

        btn_add = ctk.CTkButton(
            controls,
            text="+ Add Customer",
            font=("Segoe UI", 14, "bold"),
            fg_color="#C96C4B",
            hover_color="#B65A3B",
            height=40,
            command=self.open_add_modal,
        )
        btn_add.pack(side="right", padx=20, pady=15)

        table_card = ctk.CTkFrame(self, fg_color="white", corner_radius=12)
        table_card.pack(fill="both", expand=True)

        ctk.CTkLabel(
            table_card,
            text="👤 Customer Master List",
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
            table_card, fg_color="transparent"
        )
        self.scroll_table.pack(
            fill="both", 
            expand=True, 
            padx=20, 
            pady=(0, 15)
        )

        self.status_label = ctk.CTkLabel(
            self, 
            text="", 
            font=("Segoe UI", 13, "bold"), 
            text_color="#6D4C41"
        )
        self.status_label.pack(side="bottom", pady=(0, 10))

        self.load_customers()

    def load_customers(self):
        for widget in self.scroll_table.winfo_children():
            widget.destroy()

        search_query = self.search.get().strip()
        query = {}
        if search_query:
            query["$or"] = [
                {"name": {"$regex": search_query, "$options": "i"}},
                {"phone": {"$regex": search_query, "$options": "i"}},
                {"email": {"$regex": search_query, "$options": "i"}},
                {"address": {"$regex": search_query, "$options": "i"}},
                {"id": {"$regex": search_query, "$options": "i"}},
            ]

        cust_records = list(customers_col.find(query))

        for row_idx, cust in enumerate(cust_records):
            row_frame = ctk.CTkFrame(
                self.scroll_table, 
                fg_color="transparent"
            )
            row_frame.pack(fill="x", pady=1)

            vals = [
                cust.get("id", ""),
                cust.get("name", ""),
                cust.get("phone", ""),
                cust.get("email", ""),
                cust.get("address", ""),
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

                font = ("Segoe UI", 12, "bold") if col_idx == 0 else ("Segoe UI", 12)
                text_color = "#8D5A4F" if col_idx == 0 else "#2D2D2D"

                ctk.CTkLabel(
                    cell, text=str(val), font=font, text_color=text_color
                ).place(relx=0.5, rely=0.5, anchor="center")

            action_cell = ctk.CTkFrame(
                row_frame,
                width=self.widths[5],
                height=40,
                fg_color="white",
                border_width=1,
                border_color="#E8E0DC",
            )
            action_cell.grid(row=0, column=5, sticky="nsew")
            action_cell.grid_propagate(False)

            container = ctk.CTkFrame(action_cell, fg_color="transparent")
            container.place(relx=0.5, rely=0.5, anchor="center")

            ctk.CTkButton(
                container,
                text="👁️",
                width=28,
                height=28,
                fg_color="#DAE8FC",
                hover_color="#C6DCFA",
                text_color="black",
                command=lambda c=cust: self.open_details_modal(c),
            ).pack(side="left", padx=3)

            ctk.CTkButton(
                container,
                text="✏️",
                width=28,
                height=28,
                fg_color="#F0E0D6",
                hover_color="#E2CEC1",
                text_color="black",
                command=lambda c=cust: self.open_edit_modal(c),
            ).pack(side="left", padx=3)

            ctk.CTkButton(
                container,
                text="🗑️",
                width=28,
                height=28,
                fg_color="#FADBD8",
                hover_color="#F5B7B1",
                text_color="black",
                command=lambda cid=cust["id"]: self.delete_customer(cid),
            ).pack(side="left", padx=3)

    def open_details_modal(self, customer_data):
        CustomerDetailsModal(self, customer_data)

    def open_add_modal(self):
        AddCustomerModal(self, title="Add Customer")

    def open_edit_modal(self, customer_data):
        AddCustomerModal(
            self,
            title=f"Edit Customer ({customer_data['id']})",
            customer_data=customer_data,
        )

    def delete_customer(self, cust_id):
        result = customers_col.delete_one({"id": cust_id})
        if result.deleted_count == 1:
            self.show_status("Customer record deleted successfully!", "#6D8B74")
            self.load_customers()
        else:
            self.show_status("Customer record not found.", "#C96C4B")

    def show_status(self, message, color):
        self.status_label.configure(text=message, text_color=color)
        self.after(5000, lambda: self.status_label.configure(text=""))