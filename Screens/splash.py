import customtkinter as ctk
from PIL import Image
from Screens.login import LoginPage


class SplashScreen(ctk.CTk):

    def open_login(self):
        try:
            self.after_cancel(self.animation_id)
        except Exception:
            pass

        self.destroy()
        login = LoginPage()
        login.mainloop()

    def __init__(self):
        super().__init__()

        # Window Configuration
        self.title("Pawfect Care")
        self.minsize(900, 550)
        self.configure(fg_color="#FAF7F2")

        # Force Maximized Full Screen on Launch
        self.after(10, lambda: self.state("zoomed"))

        # Main Frame
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Logo
        self.logo = ctk.CTkImage(
            light_image=Image.open("Assets/Logo/logo.png"),
            dark_image=Image.open("Assets/Logo/logo.png"),
            size=(400, 400)
        )

        self.logo_label = ctk.CTkLabel(
            self.main_frame,
            image=self.logo,
            text=""
        )
        self.logo_label.pack()

        # Loading Indicator
        self.loading = ctk.CTkLabel(
            self.main_frame,
            text=".",
            font=("Segoe UI", 28, "bold"),
            text_color="#C96C4B"
        )
        self.loading.pack()

        self.dot_count = 1
        self.animate()

        # Transition after 3 seconds
        self.after(3000, self.open_login)

    def animate(self):
        dots = [".", 
                "..", 
                "...", 
                "....", 
                "...", 
                ".."
               ]
        self.loading.configure(text=dots[self.dot_count - 1])
        self.dot_count += 1
        if self.dot_count > len(dots):
            self.dot_count = 1
        self.animation_id = self.after(550, self.animate)