
import customtkinter as ctk
class PawfectCareApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Pawfect Care - Admin Dashboard")

        #  Maximize window to full screen with title bar controls intact
        self.state("zoomed")

        # Set minimum window size so it doesn't break if restored down
        self.minsize(1100, 650)

        # Rest of your main setup code...

# ---Splash Screen---
from Screens.splash import SplashScreen

if __name__ == "__main__":
    app = SplashScreen()
    app.mainloop() 



 