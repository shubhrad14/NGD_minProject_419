import customtkinter as ctk
from pymongo import MongoClient
from utils import chain_enter_keys, make_maximized

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["PawfectCare"]
admins = db["admins"]


class SecurityQuestion(ctk.CTk):
    def __init__(self, username="admin"):
        super().__init__()
        self.username = username

        # Window Setup
        self.title("Pawfect Care - Security Verification")
        make_maximized(self, min_width=1000, min_height=600)
        self.minsize(1000, 600)
        self.configure(fg_color="#FAF7F2")

        #  Force Maximized Full Screen on Launch
        self.after(10, lambda: self.state("zoomed"))

        # Fetch admin data from MongoDB
        self.admin_doc = admins.find_one({"username": self.username}) or {}
        self.create_layout()

        chain_enter_keys(
            [self.answer_entry], 
            submit_callback=self.verify_answer
        )

    def create_layout(self):
        card = ctk.CTkFrame(
            self,
            width=520,
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
            text="🛡️", 
            font=("Segoe UI Emoji", 32), 
            text_color="#C96C4B"
        ).pack(pady=(0, 5))

        ctk.CTkLabel(
            container, 
            text="Security Verification", 
            font=("Segoe UI", 24, "bold"), 
            text_color="#2D2D2D"
        ).pack(pady=(0, 15))

        # Security Question Direct Text Label (No Box)
        sec_question = self.admin_doc.get("security_question", "What is your primary pet's name?")
        
        ctk.CTkLabel(
            container, 
            text="Security Question:", 
            font=("Segoe UI", 12, "bold"), 
            text_color="#8D5A4F"
        ).pack(anchor="w")

        ctk.CTkLabel(
            container, 
            text=sec_question, 
            font=("Segoe UI", 15, "bold"), 
            text_color="#C96C4B", 
            wraplength=360, 
            justify="left"
        ).pack(anchor="w", pady=(4, 20))

        # Security Answer Entry
        ctk.CTkLabel(
            container, 
            text="Your Answer", 
            font=("Segoe UI", 13, "bold"), 
            text_color="#555555"
        ).pack(anchor="w")

        self.answer_entry = ctk.CTkEntry(
            container,
            width=360,
            height=46,
            corner_radius=10,
            placeholder_text="Enter your security answer",
            placeholder_text_color="#A68A7A",
            text_color="#2D2D2D",
            border_color="#C96C4B",
            border_width=2,
            fg_color="#FFF8F5"
        )
        self.answer_entry.pack(pady=(5, 15))

        self.msg_label = ctk.CTkLabel(
            container, 
            text="", 
            font=("Segoe UI", 12)
        )
        self.msg_label.pack(pady=(0, 10))

        btn_verify = ctk.CTkButton(
            container,
            text="Verify & Reset Password ➔",
            width=360,
            height=48,
            corner_radius=12,
            fg_color="#C96C4B",
            hover_color="#B45D42",
            font=("Segoe UI", 14, "bold"),
            command=self.verify_answer
        )
        btn_verify.pack(pady=(0, 15))

        btn_back = ctk.CTkButton(
            container,
            text="← Back",
            fg_color="transparent",
            hover=False,
            text_color="#C96C4B",
            font=("Segoe UI", 13, "underline"),
            command=self.back_to_forgot
        )
        btn_back.pack()

    def verify_answer(self):
        user_answer = self.answer_entry.get().strip()
        correct_answer = self.admin_doc.get("security_answer", "")

        if user_answer == "":
            self.msg_label.configure(
                text="Please type your answer.", 
                text_color="#A94442"
            )
            return

        # Case-insensitive answer comparison
        if user_answer.lower() == str(correct_answer).lower():
            self.destroy()
            from Screens.reset_password import ResetPassword
            reset_win = ResetPassword(username=self.username)
            reset_win.mainloop()
        else:
            self.msg_label.configure(
                text="Incorrect answer. Please try again.", 
                text_color="#A94442"
            )

    def back_to_forgot(self):
        self.destroy()
        from Screens.forgot_password import ForgotPassword
        forgot_win = ForgotPassword()
        forgot_win.mainloop()