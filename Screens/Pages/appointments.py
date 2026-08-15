import customtkinter as ctk
from pymongo import MongoClient
from utils import chain_enter_keys

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["PawfectCare"]
appointments = db["appointments"]
services_col = db["services"]
pets_col = db["pets"]


class PetSelectModal(ctk.CTkToplevel):
    #Picker modal when multiple pets share a name OR an owner has multiple pets.

    def __init__(
            self, 
            parent, 
            pet_matches, 
            title_text, 
            select_callback
        ):
        super().__init__(parent)
        self.title("Select Pet & Owner")
        self.geometry("420x360")
        self.resizable(False, False)
        self.configure(fg_color="#FAF7F2")

        self.select_callback = select_callback

        self.main_container = ctk.CTkFrame(self, fg_color="#FAF7F2")
        self.main_container.pack(fill="both", expand=True)

        ctk.CTkLabel(
            self.main_container,
            text="Matches Found",
            font=("Segoe UI", 16, "bold"),
            text_color="#2D2D2D",
        ).pack(pady=(15, 2))

        ctk.CTkLabel(
            self.main_container,
            text=title_text,
            font=("Segoe UI", 11),
            text_color="#8D5A4F",
        ).pack(pady=(0, 10))

        scroll = ctk.CTkScrollableFrame(
            self.main_container, fg_color="transparent"
        )
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        for pet in pet_matches:
            btn_text = f"🐾 {pet.get('name')}  |  Owner: {pet.get('owner')} ({pet.get('species', 'Pet')})"
            btn = ctk.CTkButton(
                scroll,
                text=btn_text,
                anchor="w",
                fg_color="white",
                text_color="#2D2D2D",
                hover_color="#F7E8E1",
                height=40,
                font=("Segoe UI", 12),
                command=lambda p=pet: self.choose_pet(p),
            )
            btn.pack(fill="x", pady=4)

        self.center_on_screen(parent, 420, 360)

    def center_on_screen(self, parent, width, height):
        self.update_idletasks()
        root = parent.winfo_toplevel()
        x = root.winfo_rootx() + (root.winfo_width() // 2) - (width // 2)
        y = root.winfo_rooty() + (root.winfo_height() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{max(0, x)}+{max(0, y)}")
        self.grab_set()
        self.lift()
        self.focus_force()

    def choose_pet(self, pet):
        self.select_callback(pet)
        self.destroy()


class BookAppointmentModal(ctk.CTkToplevel):
    #Modal dialog for booking and editing appointments with auto-pop search on typing.

    def __init__(self, parent, title="Book Appointment", appt_data=None):
        super().__init__(parent)
        self.title(title)

        modal_height = 590 if appt_data else 530
        self.geometry(f"460x{modal_height}")
        self.resizable(False, False)
        self.configure(fg_color="#FAF7F2")

        self.appt_data = appt_data or {}
        self.parent_page = parent

        self.main_container = ctk.CTkFrame(self, fg_color="#FAF7F2")
        self.main_container.pack(fill="both", expand=True)

        ctk.CTkLabel(
            self.main_container,
            text=title,
            font=("Segoe UI", 20, "bold"),
            text_color="#2D2D2D",
        ).pack(pady=(20, 15))

        # ----------------  PET NAME FIELD ---------------- #
        ctk.CTkLabel(
            self.main_container,
            text="Pet Name:",
            font=("Segoe UI", 12, "bold"),
            text_color="#8D5A4F",
        ).pack(anchor="w", padx=40, pady=(4, 2))

        pet_frame = ctk.CTkFrame(
            self.main_container, 
            fg_color="transparent"
        )
        pet_frame.pack(fill="x", padx=40, pady=(0, 2))

        self.pet_entry = ctk.CTkEntry(
            pet_frame,
            placeholder_text="Type pet name...",
            fg_color="white",
            text_color="#2D2D2D",
            border_color="#E8D2C8",
            height=35,
        )
        if appt_data and appt_data.get("pet"):
            self.pet_entry.insert(0, appt_data.get("pet"))
        self.pet_entry.pack(side="left", fill="x", expand=True)
        self.pet_entry.bind("<KeyRelease>", self.on_pet_typed)

        btn_search_pet = ctk.CTkButton(
            pet_frame,
            text="🔍",
            width=35,
            height=35,
            fg_color="#C96C4B",
            hover_color="#B65A3B",
            command=self.search_pets_modal,
        )
        btn_search_pet.pack(side="right", padx=(5, 0))

        # ----------------  OWNER NAME FIELD ---------------- #
        ctk.CTkLabel(
            self.main_container,
            text="Owner Name:",
            font=("Segoe UI", 12, "bold"),
            text_color="#8D5A4F",
        ).pack(anchor="w", padx=40, pady=(4, 2))

        owner_frame = ctk.CTkFrame(
            self.main_container, 
            fg_color="transparent"
        )
        owner_frame.pack(fill="x", padx=40, pady=(0, 2))

        self.owner_entry = ctk.CTkEntry(
            owner_frame,
            placeholder_text="Type owner name...",
            fg_color="white",
            text_color="#2D2D2D",
            border_color="#E8D2C8",
            height=35,
        )
        if appt_data and appt_data.get("owner"):
            self.owner_entry.insert(0, appt_data.get("owner"))
        self.owner_entry.pack(side="left", fill="x", expand=True)
        self.owner_entry.bind("<KeyRelease>", self.on_owner_typed)

        btn_search_owner = ctk.CTkButton(
            owner_frame,
            text="🔍",
            width=35,
            height=35,
            fg_color="#C96C4B",
            hover_color="#B65A3B",
            command=self.search_owners_modal,
        )
        btn_search_owner.pack(side="right", padx=(5, 0))

        self.match_status_label = ctk.CTkLabel(
            self.main_container,
            text="💡 Tip: Type pet or owner name for automatic search popup.",
            font=("Segoe UI", 10),
            text_color="#8D5A4F",
        )
        self.match_status_label.pack(anchor="w", padx=40, pady=(2, 6))

        # ----------------  DYNAMIC SERVICE DROPDOWN ---------------- #
        ctk.CTkLabel(
            self.main_container,
            text="Select Service:",
            font=("Segoe UI", 12, "bold"),
            text_color="#8D5A4F",
        ).pack(anchor="w", padx=40, pady=(4, 2))

        service_docs = list(services_col.find())
        service_titles = [s["title"] for s in service_docs if "title" in s]
        if not service_titles:
            service_titles = [
                "Grooming",
                "Bath & Dry",
                "Vaccination",
                "Check-up",
                "Daycare",
            ]

        self.service_opt = ctk.CTkOptionMenu(
            self.main_container,
            values=service_titles,
            fg_color="white",
            text_color="#2D2D2D",
            button_color="#C96C4B",
            button_hover_color="#B65A3B",
            dropdown_text_color="#2D2D2D",
            dropdown_fg_color="white",
            dropdown_hover_color="#F7E8E1",
        )
        if appt_data and appt_data.get("service") in service_titles:
            self.service_opt.set(appt_data.get("service"))
        elif service_titles:
            self.service_opt.set(service_titles[0])

        self.service_opt.pack(fill="x", padx=40, pady=(0, 6))

        # ----------------  AUTO-FORMATTING DATE FIELD ---------------- #
        existing_datetime = appt_data.get("datetime", "") if appt_data else ""
        if " | " in existing_datetime:
            existing_date, 
            existing_time = existing_datetime.split(" | ", 1)
        else:
            existing_date = existing_datetime
            existing_time = "09:00 AM"

        ctk.CTkLabel(
            self.main_container,
            text="Booking Date (YYYY-MM-DD):",
            font=("Segoe UI", 12, "bold"),
            text_color="#8D5A4F",
        ).pack(anchor="w", padx=40, pady=(4, 2))

        self.date_entry = ctk.CTkEntry(
            self.main_container,
            placeholder_text="YYYY-MM-DD",
            fg_color="white",
            text_color="#2D2D2D",
            border_color="#E8D2C8",
            height=35,
        )
        if existing_date:
            self.date_entry.insert(0, existing_date)
        self.date_entry.pack(fill="x", padx=40, pady=(0, 6))
        self.date_entry.bind("<KeyRelease>", self.on_date_typed)

        # ----------------  TIME SLOT DROPDOWN ---------------- #
        ctk.CTkLabel(
            self.main_container,
            text="Select Time Slot:",
            font=("Segoe UI", 12, "bold"),
            text_color="#8D5A4F",
        ).pack(anchor="w", padx=40, pady=(4, 2))

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
            "06:00 PM",
        ]

        self.time_opt = ctk.CTkOptionMenu(
            self.main_container,
            values=time_slots,
            fg_color="white",
            text_color="#2D2D2D",
            button_color="#C96C4B",
            button_hover_color="#B65A3B",
            dropdown_text_color="#2D2D2D",
            dropdown_fg_color="white",
            dropdown_hover_color="#F7E8E1",
        )
        if existing_time in time_slots:
            self.time_opt.set(existing_time)
        else:
            self.time_opt.set(time_slots[0])

        self.time_opt.pack(fill="x", padx=40, pady=(0, 8))

        if appt_data:
            ctk.CTkLabel(
                self.main_container,
                text="Status:",
                font=("Segoe UI", 12, "bold"),
                text_color="#8D5A4F",
            ).pack(anchor="w", padx=40, pady=(4, 2))

            self.status_opt = ctk.CTkOptionMenu(
                self.main_container,
                values=["Confirmed", "Pending", "Completed", "Cancelled"],
                fg_color="white",
                text_color="#2D2D2D",
                button_color="#C96C4B",
                button_hover_color="#B65A3B",
                dropdown_text_color="#2D2D2D",
                dropdown_fg_color="white",
                dropdown_hover_color="#F7E8E1",
            )
            self.status_opt.set(appt_data.get("status", "Confirmed"))
            self.status_opt.pack(fill="x", padx=40, pady=(0, 8))

        btn_save = ctk.CTkButton(
            self.main_container,
            text="Confirm Booking",
            fg_color="#C96C4B",
            hover_color="#B65A3B",
            font=("Segoe UI", 14, "bold"),
            height=40,
            command=self.save_booking,
        )
        btn_save.pack(fill="x", padx=40, pady=18)

        chain_enter_keys(
            [self.pet_entry, self.owner_entry, self.date_entry],
            submit_callback=self.save_booking,
        )

        self.center_on_screen(parent, 460, modal_height)

    def center_on_screen(self, parent, width, height):
        self.update_idletasks()
        root = parent.winfo_toplevel()
        x = root.winfo_rootx() + (root.winfo_width() // 2) - (width // 2)
        y = root.winfo_rooty() + (root.winfo_height() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{max(0, x)}+{max(0, y)}")
        self.grab_set()
        self.lift()
        self.focus_force()

    def on_date_typed(self, event=None):
        if event and event.keysym in ("BackSpace", "Delete"):
            return

        text = self.date_entry.get()
        digits = "".join([c for c in text if c.isdigit()])[:8]

        formatted = ""
        if len(digits) > 0:
            formatted += digits[:4]
        if len(digits) > 4:
            formatted += "-" + digits[4:6]
        if len(digits) > 6:
            formatted += "-" + digits[6:8]

        if text != formatted:
            self.date_entry.delete(0, "end")
            self.date_entry.insert(0, formatted)

    def on_pet_typed(self, event=None):
        #Automatically opens selection popup as user types pet name.
        if event and event.keysym in (
            "BackSpace",
            "Delete",
            "Return",
            "Tab",
            "Escape",
            "Up",
            "Down",
        ):
            return

        typed_pet = self.pet_entry.get().strip()
        if len(typed_pet) < 2:
            return

        matches = list(
            pets_col.find({"name": {"$regex": f"^{typed_pet}", "$options": "i"}})
        )

        if matches:
            PetSelectModal(
                self,
                matches,
                f"Select pet matching '{typed_pet}':",
                self.apply_selected_pet,
            )

    def on_owner_typed(self, event=None):
        # Automatically opens selection popup as user types owner name.
        if event and event.keysym in (
            "BackSpace",
            "Delete",
            "Return",
            "Tab",
            "Escape",
            "Up",
            "Down",
        ):
            return

        typed_owner = self.owner_entry.get().strip()
        if len(typed_owner) < 2:
            return

        matches = list(
            pets_col.find(
                {"owner": {"$regex": f"^{typed_owner}", "$options": "i"}}
            )
        )

        if matches:
            PetSelectModal(
                self,
                matches,
                f"Select pet owned by '{typed_owner}':",
                self.apply_selected_pet,
            )

    def search_pets_modal(self):
        typed_text = self.pet_entry.get().strip()
        query = (
            {"name": {"$regex": typed_text, "$options": "i"}}
            if typed_text
            else {}
        )
        matches = list(pets_col.find(query))
        if matches:
            PetSelectModal(
                self, 
                matches, 
                "Select pet and owner:", 
                self.apply_selected_pet
            )

    def search_owners_modal(self):
        typed_text = self.owner_entry.get().strip()
        query = (
            {"owner": {"$regex": typed_text, "$options": "i"}}
            if typed_text
            else {}
        )
        matches = list(pets_col.find(query))
        if matches:
            PetSelectModal(
                self, 
                matches, 
                "Select pet and owner:", 
                self.apply_selected_pet
            )

    def apply_selected_pet(self, pet_doc):
        self._set_pet_field(pet_doc.get("name", ""))
        self._set_owner_field(pet_doc.get("owner", ""))
        self.match_status_label.configure(
            text=f"✓ Selected {pet_doc.get('name')} (Owner: {pet_doc.get('owner')})",
            text_color="#5F7F63",
        )

    def _set_pet_field(self, text):
        self.pet_entry.delete(0, "end")
        self.pet_entry.insert(0, text)

    def _set_owner_field(self, text):
        self.owner_entry.delete(0, "end")
        self.owner_entry.insert(0, text)

    def save_booking(self):
        pet = self.pet_entry.get().strip()
        owner = self.owner_entry.get().strip()
        service = self.service_opt.get()
        date_val = self.date_entry.get().strip()
        time_val = self.time_opt.get()

        if pet == "" or owner == "" or date_val == "":
            ctk.CTkLabel(
                self.main_container,
                text="Please fill in all required fields.",
                text_color="#C96C4B",
                font=("Segoe UI", 13),
            ).pack(pady=5)
            return

        formatted_datetime = f"{date_val} | {time_val}"

        if self.appt_data and self.appt_data.get("id"):
            status_val = self.status_opt.get()
            appointments.update_one(
                {"id": self.appt_data["id"]},
                {
                    "$set": {
                        "pet": pet,
                        "owner": owner,
                        "service": service,
                        "datetime": formatted_datetime,
                        "status": status_val,
                    }
                },
            )
            self.parent_page.show_status(
                "Appointment updated successfully!", "#6D8B74"
            )

        else:
            last_appt = appointments.find_one({}, sort=[("_id", -1)])
            if last_appt and "id" in last_appt:
                try:
                    last_number = int(last_appt["id"].split("-")[1])
                    appt_id = f"APT-{last_number + 1}"
                except Exception:
                    appt_id = "APT-101"
            else:
                appt_id = "APT-101"

            appt_record = {
                "id": appt_id,
                "pet": pet,
                "owner": owner,
                "service": service,
                "datetime": formatted_datetime,
                "status": "Confirmed",
            }
            appointments.insert_one(appt_record)
            self.parent_page.show_status(
                "Appointment booked successfully!", "#6D8B74"
            )

        self.parent_page.load_appointments()
        self.destroy()


class AppointmentsPage(ctk.CTkFrame):
    #Appointments Management UI Page.

    def __init__(self, parent):
        super().__init__(parent, fg_color="#FAF7F2")

        self.headers = [
            "Appt ID",
            "Pet Name",
            "Owner",
            "Service",
            "Date & Time",
            "Status",
            "Actions",
        ]
        self.widths = [100, 130, 130, 140, 170, 120, 180]

        # Top Action Bar
        controls = ctk.CTkFrame(
            self, fg_color="white", corner_radius=12, height=70
        )
        controls.pack(fill="x", pady=(0, 15))
        controls.pack_propagate(False)

        self.search = ctk.CTkEntry(
            controls,
            placeholder_text="🔍 Search Appointment...",
            width=280,
            height=40,
            fg_color="#FAF7F2",
            border_color="#E8D2C8",
            text_color="#2D2D2D",
            placeholder_text_color="#A68A7A",
        )
        self.search.pack(side="left", padx=20, pady=15)
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
            width=150,
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
            command=self.open_book_modal,
        )
        btn_add.pack(side="right", padx=20, pady=15)

        # Table Card
        table_card = ctk.CTkFrame(self, fg_color="white", corner_radius=12)
        table_card.pack(fill="both", expand=True)

        ctk.CTkLabel(
            table_card,
            text="📅 Appointment Master List",
            font=("Segoe UI", 18, "bold"),
            text_color="#2D2D2D",
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
                border_color="#E8D2C8",
            )
            cell.grid(row=0, column=idx, sticky="nsew")
            cell.grid_propagate(False)

            ctk.CTkLabel(
                cell,
                text=h,
                font=("Segoe UI", 12, "bold"),
                text_color="#8D5A4F",
            ).place(relx=0.5, rely=0.5, anchor="center")

        # Scrollable Data Frame
        self.scroll_table = ctk.CTkScrollableFrame(
            table_card, fg_color="transparent"
        )
        self.scroll_table.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # Status Notification Label
        self.status_label = ctk.CTkLabel(
            self, text="", font=("Segoe UI", 13, "bold"), text_color="#6D4C41"
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
                {"id": {"$regex": search_query, "$options": "i"}},
            ]

        if selected_status and selected_status != "All Status":
            query["status"] = selected_status

        appt_records = list(appointments.find(query))

        for row_idx, appt in enumerate(appt_records):
            row_frame = ctk.CTkFrame(self.scroll_table, fg_color="transparent")
            row_frame.pack(fill="x", pady=1)

            vals = [
                appt.get("id", ""),
                appt.get("pet", ""),
                appt.get("owner", ""),
                appt.get("service", ""),
                appt.get("datetime", ""),
                appt.get("status", ""),
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
                    if val == "Completed":
                        text_color = "#5F7F63"
                    elif val == "Pending":
                        text_color = "#C96C4B"
                    elif val == "Confirmed":
                        text_color = "#2E6B9E"
                    elif val == "Cancelled":
                        text_color = "#A94442"
                    else:
                        text_color = "#2D2D2D"
                    font = ("Segoe UI", 12, "bold")
                else:
                    font = (
                        ("Segoe UI", 12, "bold")
                        if col_idx == 0
                        else ("Segoe UI", 12)
                    )
                    text_color = "#8D5A4F" if col_idx == 0 else "#2D2D2D"

                ctk.CTkLabel(
                    cell, text=str(val), font=font, text_color=text_color
                ).place(relx=0.5, rely=0.5, anchor="center")

            # Actions Column
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

            current_status = appt.get("status", "")

            # 1-CLICK ACTION BUTTONS
            if current_status == "Pending":
                ctk.CTkButton(
                    container,
                    text="✓",
                    width=26,
                    height=28,
                    fg_color="#D5E8D4",
                    hover_color="#C3E1C2",
                    text_color="#274E13",
                    command=lambda aid=appt["id"]: self.quick_update_status(
                        aid, "Confirmed"
                    ),
                ).pack(side="left", padx=2)

                ctk.CTkButton(
                    container,
                    text="❌",
                    width=26,
                    height=28,
                    fg_color="#FADBD8",
                    hover_color="#F5B7B1",
                    text_color="#A94442",
                    command=lambda aid=appt["id"]: self.quick_update_status(
                        aid, "Cancelled"
                    ),
                ).pack(side="left", padx=2)

            elif current_status == "Confirmed":
                ctk.CTkButton(
                    container,
                    text="✔",
                    width=26,
                    height=28,
                    fg_color="#DAE8FC",
                    hover_color="#C6DCFA",
                    text_color="#1C4587",
                    command=lambda aid=appt["id"]: self.quick_update_status(
                        aid, "Completed"
                    ),
                ).pack(side="left", padx=2)

                ctk.CTkButton(
                    container,
                    text="❌",
                    width=26,
                    height=28,
                    fg_color="#FADBD8",
                    hover_color="#F5B7B1",
                    text_color="#A94442",
                    command=lambda aid=appt["id"]: self.quick_update_status(
                        aid, "Cancelled"
                    ),
                ).pack(side="left", padx=2)

            # Edit Button
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

            # Delete Button
            ctk.CTkButton(
                container,
                text="🗑️",
                width=28,
                height=28,
                fg_color="#FADBD8",
                hover_color="#F5B7B1",
                text_color="black",
                command=lambda aid=appt["id"]: self.delete_appointment(aid),
            ).pack(side="left", padx=2)

    def quick_update_status(self, appt_id, new_status):
        appointments.update_one(
            {"id": appt_id}, {"$set": {"status": new_status}}
        )
        self.show_status(f"Appointment marked as {new_status}!", "#6D8B74")
        self.load_appointments()

    def open_book_modal(self):
        BookAppointmentModal(self, title="Book Appointment")

    def open_edit_modal(self, appt_data):
        BookAppointmentModal(
            self,
            title=f"Edit Appointment ({appt_data['id']})",
            appt_data=appt_data,
        )

    def delete_appointment(self, appt_id):
        result = appointments.delete_one({"id": appt_id})
        if result.deleted_count == 1:
            self.show_status("Appointment deleted successfully!", "#6D8B74")
            self.load_appointments()
        else:
            self.show_status("Appointment not found.", "#C96C4B")

    def show_status(self, message, color):
        self.status_label.configure(text=message, text_color=color)
        self.after(5000, lambda: self.status_label.configure(text=""))