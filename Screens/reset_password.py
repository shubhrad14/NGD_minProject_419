import customtkinter as ctk
from PIL import Image
from pymongo import MongoClient
from utils import chain_enter_keys, make_maximized

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["PawfectCare"]
admins = db["admins"]


class ResetPassword(ctk.CTk):
    def __init__(self, username="admin"):
        super().__init__()
        self.username = username

        # Window Setup
        self.title("Pawfect Care - Reset Password")
        make_maximized(self, min_width=1000, min_height=600)
        self.minsize(1000, 600)
        self.configure(fg_color="#FAF7F2")

        # 🖥️ Force Maximized Full Screen on Launch
        self.after(10, lambda: self.state("zoomed"))

        self.create_layout()

        chain_enter_keys(
            [self.new_pass_entry, self.confirm_pass_entry],
            submit_callback=self.update_password
        )


    def create_layout(self):
        card = ctk.CTkFrame(
            self,
            width=500,
            height=540,
            corner_radius=24,
            fg_color="white"
        )
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        container = ctk.CTkFrame(card, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            container, 
            text="🔒", 
            font=("Segoe UI Emoji", 32), 
            text_color="#C96C4B"
        ).pack(pady=(0, 5))

        ctk.CTkLabel(
            container, 
            text="Reset Password", 
            font=("Segoe UI", 26, "bold"), 
            text_color="#2D2D2D"
        ).pack(pady=(0, 15))

        # New Password Input
        ctk.CTkLabel(
            container, 
            text="New Password", 
            font=("Segoe UI", 13, "bold"), 
            text_color="#555555"
        ).pack(anchor="w")

        self.new_pass_entry = ctk.CTkEntry(
            container,
            width=340,
            height=46,
            show="*",
            corner_radius=10,
            placeholder_text="Enter new password",
            placeholder_text_color="#A68A7A",
            text_color="#2D2D2D",
            border_color="#C96C4B",
            border_width=2,
            fg_color="#FFF8F5"
        )
        self.new_pass_entry.pack(pady=(5, 15))

        # Confirm New Password Input
        ctk.CTkLabel(
            container, 
            text="Confirm New Password", 
            font=("Segoe UI", 13, "bold"), 
            text_color="#555555"
        ).pack(anchor="w")

        self.confirm_pass_entry = ctk.CTkEntry(
            container,
            width=340,
            height=46,
            show="*",
            corner_radius=10,
            placeholder_text="Re-enter new password",
            placeholder_text_color="#A68A7A",
            text_color="#2D2D2D",
            border_color="#C96C4B",
            border_width=2,
            fg_color="#FFF8F5"
        )
        self.confirm_pass_entry.pack(pady=(5, 15))

        self.msg_label = ctk.CTkLabel(
            container, 
            text="", 
            font=("Segoe UI", 12)
        )
        self.msg_label.pack(pady=(0, 10))

        btn_update = ctk.CTkButton(
            container,
            text="Update Password & Login",
            width=340,
            height=48,
            corner_radius=12,
            fg_color="#C96C4B",
            hover_color="#B45D42",
            font=("Segoe UI", 14, "bold"),
            command=self.update_password
        )
        btn_update.pack(pady=(0, 15))

    def update_password(self):
        new_pass = self.new_pass_entry.get()
        confirm_pass = self.confirm_pass_entry.get()

        if new_pass == "" or confirm_pass == "":
            self.msg_label.configure(
                text="Please fill in both password fields.", 
                text_color="#A94442"
            )
            return

        if new_pass != confirm_pass:
            self.msg_label.configure(
                text="Passwords do not match!", 
                text_color="#A94442"
            )
            return

        # Update in MongoDB
        result = admins.update_one(
            {"username": self.username},
            {"$set": {"password": new_pass}}
        )

        if result.modified_count == 1 or result.matched_count == 1:
            self.msg_label.configure(
                text="Password updated successfully! Redirecting...", 
                text_color="#5F7F63"
            )
            self.after(1500, self.go_to_login)
        else:
            self.msg_label.configure(
                text="Failed to update password.", 
                text_color="#A94442"
            )

    def go_to_login(self):
        self.destroy()
        from Screens.login import LoginPage
        login_win = LoginPage()
        login_win.mainloop()