import customtkinter as ctk
from PIL import Image
from pymongo import MongoClient
from utils import chain_enter_keys, make_maximized


client = MongoClient("mongodb://localhost:27017/")
db = client["PawfectCare"]
admins = db["admins"]


class LoginPage(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.password_visible = False

        self.eye_open = ctk.CTkImage(
            light_image=Image.open("Assets/Icons/eye_open.png"),
            dark_image=Image.open("Assets/Icons/eye_open.png"),
            size=(20, 20)
        )

        self.eye_closed = ctk.CTkImage(
            light_image=Image.open("Assets/Icons/eye_closed.png"),
            dark_image=Image.open("Assets/Icons/eye_closed.png"),
            size=(20, 20)
        )

        self.setup_window()
        self.create_main_frames()
        self.create_left_panel()
        self.create_right_panel()
        chain_enter_keys([self.username, self.password], submit_callback=self.login)

    def setup_window(self):
        self.title("Pawfect Care - Admin Login")
        make_maximized(self, min_width=1000, min_height=600)
        self.minsize(1000, 600)
        self.configure(fg_color="#FAF7F2")

        # Force Maximized Full Screen on Launch
        self.after(10, lambda: self.state("zoomed"))

    def create_main_frames(self):
        self.main_frame = ctk.CTkFrame(self, fg_color="#FAF7F2")
        self.main_frame.pack(fill="both", expand=True)

        self.left_frame = ctk.CTkFrame(self.main_frame, fg_color="#FAF7F2")
        self.left_frame.pack(side="left", fill="both", expand=True)

        self.right_frame = ctk.CTkFrame(
            self.main_frame,
            width=500,
            corner_radius=30,
            fg_color="white"
        )
        self.right_frame.pack(side="right", fill="y", padx=25, pady=25)
        self.right_frame.pack_propagate(False)

    def create_left_panel(self):
        self.logo = ctk.CTkImage(
            Image.open("Assets/Logo/logo.png"),
            size=(340, 340)
        )

        ctk.CTkLabel(
            self.left_frame, 
            image=self.logo, 
            text=""
        ).pack(pady=(80, 20))

        ctk.CTkLabel(
            self.left_frame, 
            text="Pet Care Management System", 
            font=("Segoe UI", 24), 
            text_color="#6D4C41"
        ).pack(pady=(10, 15))

        ctk.CTkLabel(
            self.left_frame, 
            text="────────────── 🐾 ──────────────", 
            font=("Segoe UI", 18), 
            text_color="#C96C4B"
        ).pack()

        ctk.CTkLabel(
            self.left_frame, 
            text="Care   •   Love   •   Trust", 
            font=("Segoe UI", 18), 
            text_color="#8D5A4F"
        ).pack(pady=(20, 10))

        ctk.CTkLabel(
            self.left_frame, 
            text="❤", 
            font=("Segoe UI Emoji", 22), 
            text_color="#C96C4B"
        ).pack()

    def create_right_panel(self):
        container = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            container, 
            text="🐾", 
            font=("Segoe UI Emoji", 26), 
            text_color="#C96C4B"
        ).pack(pady=(0, 10))

        ctk.CTkLabel(
            container, 
            text="Admin Login", 
            font=("Segoe UI", 34, "bold"), 
            text_color="#2D2D2D"
        ).pack(pady=(0, 35))

        ctk.CTkLabel(
            container, 
            text="Username", 
            font=("Segoe UI", 14), 
            text_color="#555555"
        ).pack(anchor="w")
        self.username = ctk.CTkEntry(
            container, 
            width=330, 
            height=48, 
            corner_radius=10,
            placeholder_text="Enter your username", 
            placeholder_text_color="#A68A7A",
            text_color="#2D2D2D", 
            border_color="#C96C4B", 
            border_width=2, 
            fg_color="#FFF8F5"
        )
        self.username.pack(pady=(5, 20))

        ctk.CTkLabel(
            container, 
            text="Password", 
            font=("Segoe UI", 14), 
            text_color="#555555"
        ).pack(anchor="w")

        password_frame = ctk.CTkFrame(
            container, 
            width=330, 
            height=48, 
            fg_color="#FFF8F5", 
            border_width=2, 
            border_color="#C96C4B", 
            corner_radius=10
        )
        password_frame.pack(pady=(5, 15))
        password_frame.pack_propagate(False)

        self.password = ctk.CTkEntry(
            password_frame, 
            placeholder_text="Enter your password",
              show="*",
            border_width=0, 
            fg_color="transparent", 
            width=280, 
            text_color="#2D2D2D", 
            placeholder_text_color="#A68A7A"
        )
        self.password.pack(side="left", padx=(12, 0), pady=10)

        self.eye_button = ctk.CTkButton(
            password_frame, 
            image=self.eye_closed, 
            text="", width=30,
            fg_color="transparent", 
            hover_color="#F5F0EC", 
            command=self.toggle_password
        )
        self.eye_button.pack(side="right", padx=(0, 10))

        ctk.CTkButton(
            container, 
            text="Forgot Password?", 
            fg_color="transparent", 
            hover=False,
            text_color="#C96C4B", 
            font=("Segoe UI", 13, "underline"), 
            width=20, 
            command=self.forgot_password
        ).pack(anchor="e", pady=(0, 25))

        self.message = ctk.CTkLabel(
            container, 
            text="", 
            text_color="red", 
            font=("Segoe UI", 13)
        )
        self.message.pack(pady=(0, 10))

        ctk.CTkButton(
            container, 
            text="Login", 
            width=330, 
            height=50, 
            corner_radius=12,
            fg_color="#C96C4B", 
            hover_color="#B45D42", 
            font=("Segoe UI", 16, "bold"), 
            command=self.login
        ).pack()

        ctk.CTkLabel(
            container, 
            text="Happy Pets, Happy Hearts ❤", 
            font=("Segoe UI", 15), 
            text_color="#8D5A4F"
        ).pack(pady=(40, 0))

    def login(self):
        username = self.username.get().strip()
        password = self.password.get()

        if username == "" or password == "":
            self.message.configure(
                text="Please enter username and password", 
                text_color="red"
            )
            return

        admin = admins.find_one({"username": username, "password": password})
        if admin:
            self.destroy()
            from Screens.dashboard import Dashboard
            dashboard = Dashboard()
            dashboard.mainloop()
        else:
            self.message.configure(
                text="Invalid Username or Password", 
                text_color="red"
            )

    def toggle_password(self):
        if self.password_visible:
            self.password.configure(show="*")
            self.eye_button.configure(image=self.eye_closed)
            self.password_visible = False
        else:
            self.password.configure(show="")
            self.eye_button.configure(image=self.eye_open)
            self.password_visible = True

    def forgot_password(self):
        self.destroy()
        from Screens.forgot_password import ForgotPassword
        forgot = ForgotPassword()
        forgot.mainloop()