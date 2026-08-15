import customtkinter as ctk
from pymongo import MongoClient
from utils import chain_enter_keys

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["PawfectCare"]
pets_col = db["pets"]


class AddPetModal(ctk.CTkToplevel):
    #Modal dialog for adding and editing pet records with Enter key navigation.
    def __init__(self, parent, title="Add New Pet", pet_data=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("460x560")
        self.resizable(False, False)
        self.configure(fg_color="#FAF7F2")

        self.pet_data = pet_data or {}
        self.parent_page = parent

        self.main_container = ctk.CTkFrame(self, fg_color="#FAF7F2")
        self.main_container.pack(fill="both", expand=True)

        ctk.CTkLabel(
            self.main_container, 
            text=title, 
            font=("Segoe UI", 20, "bold"), 
            text_color="#2D2D2D"
        ).pack(pady=(20, 15))

        self.name_entry = self._create_field("Pet Name:", self.pet_data.get("name"))
        self.species_entry = self._create_field("Species (e.g. Dog, Cat):", self.pet_data.get("species"))
        self.breed_entry = self._create_field("Breed:", self.pet_data.get("breed"))
        self.age_entry = self._create_field("Age (e.g. 2 yrs):", self.pet_data.get("age"))
        self.owner_entry = self._create_field("Owner Name:", self.pet_data.get("owner"))

        btn_save = ctk.CTkButton(
            self.main_container, 
            text="Save Pet Record", 
            fg_color="#C96C4B", 
            hover_color="#B65A3B",
            font=("Segoe UI", 14, "bold"), 
            height=40, 
            command=self.save_pet
        )
        btn_save.pack(fill="x", padx=40, pady=20)

        chain_enter_keys(
            [
                self.name_entry,
                self.species_entry,
                self.breed_entry,
                self.age_entry,
                self.owner_entry
            ],
            submit_callback=self.save_pet
        )

        self.center_on_screen(parent, 460, 560)

    def _create_field(self, label, default=None):
        ctk.CTkLabel(
            self.main_container, 
            text=label, 
            font=("Segoe UI", 12, "bold"), 
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

    def save_pet(self):
        name = self.name_entry.get().strip()
        species = self.species_entry.get().strip()
        breed = self.breed_entry.get().strip()
        age = self.age_entry.get().strip()
        owner = self.owner_entry.get().strip()

        if not name or not owner:
            ctk.CTkLabel(
                self.main_container, 
                text="Pet Name and Owner Name are required.", 
                text_color="#C96C4B", 
                font=("Segoe UI", 12)
            ).pack(pady=2)
            return

        if self.pet_data.get("id"):
            pets_col.update_one(
                {"id": self.pet_data["id"]},
                {"$set": {"name": name, "species": species, "breed": breed, "age": age, "owner": owner}}
            )
            self.parent_page.show_status("Pet record updated successfully!", "#6D8B74")
        else:
            last_pet = pets_col.find_one({}, sort=[("_id", -1)])
            if last_pet and "id" in last_pet:
                try:
                    last_num = int(last_pet["id"].split("-")[1])
                    pet_id = f"PET-{last_num + 1}"
                except Exception:
                    pet_id = "PET-101"
            else:
                pet_id = "PET-101"

            pets_col.insert_one({
                "id": pet_id,
                "name": name,
                "species": species,
                "breed": breed,
                "age": age,
                "owner": owner
            })
            self.parent_page.show_status("New pet added successfully!", "#6D8B74")

        self.parent_page.load_pets()
        self.destroy()


class PetsPage(ctk.CTkFrame):
    #Pets Management UI Page.
    def __init__(self, parent):
        super().__init__(parent, fg_color="#FAF7F2")

        self.headers = ["ID", "Pet Name", "Species", "Breed", "Age", "Owner", "Actions"]
        self.widths = [90, 150, 130, 140, 90, 150, 140]

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
            placeholder_text="🔍 Search Pet...",
            width=260, 
            height=40, 
            fg_color="#FAF7F2", 
            border_color="#E8D2C8",
            text_color="#2D2D2D", 
            placeholder_text_color="#A68A7A"
        )
        self.search.pack(side="left", padx=(20, 10), pady=15)
        self.search.bind("<KeyRelease>", lambda event: self.load_pets())

        # 🐾 Species Filter Dropdown
        self.species_filter = ctk.CTkOptionMenu(
            controls,
            values=["All Species", "Dog", "Cat", "Bird", "Rabbit", "Other"],
            width=150, 
            height=40,
            fg_color="#FAF7F2", 
            text_color="#2D2D2D",
            button_color="#C96C4B", 
            button_hover_color="#B65A3B",
            dropdown_text_color="#2D2D2D", 
            dropdown_fg_color="white", 
            dropdown_hover_color="#F7E8E1",
            command=lambda choice: self.load_pets()
        )
        self.species_filter.pack(side="left", padx=5, pady=15)

        btn_add = ctk.CTkButton(
            controls, 
            text="+ Add Pet", 
            font=("Segoe UI", 14, "bold"),
            fg_color="#C96C4B", 
            hover_color="#B65A3B", 
            height=40,
            command=self.open_add_modal
        )
        btn_add.pack(side="right", padx=20, pady=15)

        # Table Card
        table_card = ctk.CTkFrame(
            self, 
            fg_color="white", 
            corner_radius=12
        )
        table_card.pack(fill="both", expand=True)

        ctk.CTkLabel(
            table_card, text="🐾 Pet Master List",
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
            self, 
            text="", 
            font=("Segoe UI", 13, "bold"), 
            text_color="#6D4C41"
        )
        self.status_label.pack(side="bottom", pady=(0, 10))

        self.load_pets()

    def load_pets(self):
        for widget in self.scroll_table.winfo_children():
            widget.destroy()

        search_query = self.search.get().strip()
        selected_species = self.species_filter.get()

        query = {}
        if search_query:
            query["$or"] = [
                {"name": {"$regex": search_query, "$options": "i"}},
                {"species": {"$regex": search_query, "$options": "i"}},
                {"breed": {"$regex": search_query, "$options": "i"}},
                {"owner": {"$regex": search_query, "$options": "i"}},
                {"id": {"$regex": search_query, "$options": "i"}}
            ]

        if selected_species and selected_species != "All Species":
            query["species"] = {"$regex": f"^{selected_species}", "$options": "i"}

        pet_records = list(pets_col.find(query))

        for row_idx, pet in enumerate(pet_records):
            row_frame = ctk.CTkFrame(self.scroll_table, fg_color="transparent")
            row_frame.pack(fill="x", pady=1)

            vals = [
                pet.get("id", ""),
                pet.get("name", ""),
                pet.get("species", ""),
                pet.get("breed", ""),
                pet.get("age", ""),
                pet.get("owner", "")
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
                width=28, 
                height=28,
                fg_color="#F0E0D6", 
                hover_color="#E2CEC1", 
                text_color="black",
                command=lambda p=pet: self.open_edit_modal(p)
            ).pack(side="left", padx=4)

            ctk.CTkButton(
                container, 
                text="🗑️", 
                width=28, 
                height=28,
                fg_color="#FADBD8", 
                hover_color="#F5B7B1", 
                text_color="black",
                command=lambda pid=pet["id"]: self.delete_pet(pid)
            ).pack(side="left", padx=4)

    def open_add_modal(self):
        AddPetModal(self, title="Add New Pet")

    def open_edit_modal(self, pet_data):
        AddPetModal(self, title=f"Edit Pet ({pet_data['id']})", pet_data=pet_data)

    def delete_pet(self, pet_id):
        result = pets_col.delete_one({"id": pet_id})
        if result.deleted_count == 1:
            self.show_status("Pet record deleted successfully!", "#6D8B74")
            self.load_pets()
        else:
            self.show_status("Pet record not found.", "#C96C4B")

    def show_status(self, message, color):
        self.status_label.configure(text=message, text_color=color)
        self.after(5000, lambda: self.status_label.configure(text=""))