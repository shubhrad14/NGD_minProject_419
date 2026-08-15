import customtkinter as ctk
from PIL import Image
from pymongo import MongoClient
from utils import chain_enter_keys, make_maximized

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["PawfectCare"]
admins = db["admins"]


class ForgotPassword(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("Pawfect Care - Forgot Password")
        make_maximized(self, min_width=1000, min_height=600)
        self.minsize(1000, 600)
        self.configure(fg_color="#FAF7F2")

        # Force Maximized Full Screen on Launch
        self.after(10, lambda: self.state("zoomed"))
        self.create_layout()

        chain_enter_keys([self.username_entry], submit_callback=self.verify_username)

    def create_layout(self):
        # Main Centered Card
        card = ctk.CTkFrame(
            self,
            width=500,
            height=520,
            corner_radius=24,
            fg_color="white"
        )
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        container = ctk.CTkFrame(card, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            container, 
            text="🔑", 
            font=("Segoe UI Emoji", 32), 
            text_color="#C96C4B"
        ).pack(pady=(0, 5))

        ctk.CTkLabel(
            container, 
            text="Forgot Password?", 
            font=("Segoe UI", 26, "bold"), 
            text_color="#2D2D2D"
        ).pack(pady=(0, 10))

        ctk.CTkLabel(
            container, 
            text="Enter your registered username to verify your account.",
            font=("Segoe UI", 12), 
            text_color="#8D5A4F", 
            wraplength=340, 
            justify="center"
        ).pack(pady=(0, 25))

        ctk.CTkLabel(
            container, 
            text="Username", 
            font=("Segoe UI", 13, "bold"), 
            text_color="#555555"
        ).pack(anchor="w")

        self.username_entry = ctk.CTkEntry(
            container,
            width=340,
            height=46,
            corner_radius=10,
            placeholder_text="Enter your username",
            placeholder_text_color="#A68A7A",
            text_color="#2D2D2D",
            border_color="#C96C4B",
            border_width=2,
            fg_color="#FFF8F5"
        )
        self.username_entry.pack(pady=(5, 15))

        self.msg_label = ctk.CTkLabel(container, text="", font=("Segoe UI", 12))
        self.msg_label.pack(pady=(0, 10))

        btn_verify = ctk.CTkButton(
            container,
            text="Continue to Security Question ➔",
            width=340,
            height=48,
            corner_radius=12,
            fg_color="#C96C4B",
            hover_color="#B45D42",
            font=("Segoe UI", 14, "bold"),
            command=self.verify_username
        )
        btn_verify.pack(pady=(0, 15))

        btn_back = ctk.CTkButton(
            container,
            text="← Back to Login",
            fg_color="transparent",
            hover=False,
            text_color="#C96C4B",
            font=("Segoe UI", 13, "underline"),
            command=self.back_to_login
        )
        btn_back.pack()

    def verify_username(self):
        username = self.username_entry.get().strip()

        if username == "":
            self.msg_label.configure(text="Please enter your username.", text_color="#A94442")
            return

        admin = admins.find_one({"username": username})
        if admin:
            self.destroy()
            from Screens.security_question import SecurityQuestion
            sec_win = SecurityQuestion(username=username)
            sec_win.mainloop()
        else:
            self.msg_label.configure(text="Username not found in database.", text_color="#A94442")

    def back_to_login(self):
        self.destroy()
        from Screens.login import LoginPage
        login_win = LoginPage()
        login_win.mainloop()