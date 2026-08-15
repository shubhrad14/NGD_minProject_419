import customtkinter as ctk
from PIL import Image

# Import all page views from Screens.Pages
from Screens.Pages.dashboard_home import DashboardHomePage
from Screens.Pages.pets import PetsPage
from Screens.Pages.customers import CustomersPage
from Screens.Pages.appointments import AppointmentsPage
from Screens.Pages.services import ServicesPage
from Screens.Pages.products import ProductsPage
from Screens.Pages.settings import SettingsPage


class Dashboard(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Pawfect Care - Admin Dashboard")
        self.minsize(1100, 650)
        self.configure(fg_color="#FAF7F2")

        # Force Maximized Full Screen on Launch
        self.after(10, lambda: self.state("zoomed"))

        self.nav_buttons = {}
        self.create_layout()
        self.show_page("Dashboard")

    def center_window(self):
        width, height = 1400, 820
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

    def create_layout(self):
        # Sidebar
        self.sidebar = ctk.CTkFrame(
            self, 
            width=260, 
            fg_color="#C96C4B", 
            corner_radius=0
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        try:
            self.logo = ctk.CTkImage(
                light_image=Image.open("Assets/Logo/logowotxt.png"),
                dark_image=Image.open("Assets/Logo/logowotxt.png"),
                size=(80, 80)
            )
            ctk.CTkLabel(
                self.sidebar, 
                image=self.logo, 
                text=""
            ).pack(pady=(20, 5))

        except Exception:
            ctk.CTkLabel(
                self.sidebar, 
                text="🐾", 
                font=("Segoe UI", 48)
            ).pack(pady=(20, 5))

        ctk.CTkLabel(
            self.sidebar, 
            text="Pawfect Care", 
            font=("Segoe UI", 22, "bold"), 
            text_color="white"
        ).pack()

        ctk.CTkLabel(
            self.sidebar, 
            text="Admin Dashboard", 
            font=("Segoe UI", 12), 
            text_color="#FBE8DD"
        ).pack(pady=(0, 20))

        # Navigation Items
        pages = ["Dashboard", "Pets", "Customers", "Appointments", "Services", "Products", "Settings"]
        for p in pages:
            btn = ctk.CTkButton(
                self.sidebar, 
                text=p, 
                width=210, 
                height=40,
                fg_color="#C96C4B", 
                hover_color="#B65A3B", 
                anchor="w",
                corner_radius=8, 
                font=("Segoe UI", 14),
                command=lambda name=p: self.show_page(name)
            )
            btn.pack(pady=4)
            self.nav_buttons[p] = btn

        # Logout Button
        logout = ctk.CTkButton(
            self.sidebar, 
            text="Logout", 
            width=210, 
            height=40,
            fg_color="#A94442", 
            hover_color="#8B2E2E", 
            corner_radius=8, 
            font=("Segoe UI", 14),
            command=self.logout
        )
        logout.pack(pady=(25, 0))

        # Main Workspace
        self.main = ctk.CTkFrame(
            self, 
            fg_color="#FAF7F2"
        )
        self.main.pack(
            side="left", 
            fill="both", 
            expand=True
        )

        # Top Bar
        self.topbar = ctk.CTkFrame(
            self.main, 
            height=65, 
            fg_color="white", 
            corner_radius=12
        )
        self.topbar.pack(
            fill="x", 
            padx=20, 
            pady=(15, 10)
        )
        self.topbar.pack_propagate(False)

        self.page_title_label = ctk.CTkLabel(
            self.topbar, 
            text="Dashboard", 
            font=("Segoe UI", 24, "bold"), 
            text_color="#2D2D2D"
        )
        self.page_title_label.pack(side="left", padx=20)

        ctk.CTkLabel(
            self.topbar, 
            text="Welcome, Admin ", 
            font=("Segoe UI", 15, "bold"), 
            text_color="#8D5A4F"
        ).pack(side="right", padx=20)

        # Dynamic Content Container
        self.content_container = ctk.CTkFrame(
            self.main, 
            fg_color="#FAF7F2"
        )
        self.content_container.pack(
            fill="both", 
            expand=True, 
            padx=20, 
            pady=(0, 15)
        )

    def show_page(self, page_name):
        self.page_title_label.configure(text=page_name)

        # Highlight Active Nav Button
        for name, btn in self.nav_buttons.items():
            btn.configure(
                fg_color="#B65A3B" 
                if name == page_name 
                else "#C96C4B"
            )

        # Clear active content view
        for widget in self.content_container.winfo_children():
            widget.destroy()

        # Render corresponding page view
        if page_name == "Dashboard":
            page = DashboardHomePage(self.content_container)
        elif page_name == "Pets":
            page = PetsPage(self.content_container)
        elif page_name == "Customers":
            page = CustomersPage(self.content_container)
        elif page_name == "Appointments":
            page = AppointmentsPage(self.content_container)
        elif page_name == "Services":
            page = ServicesPage(self.content_container)
        elif page_name == "Products":
            page = ProductsPage(self.content_container)
        elif page_name == "Settings":
            page = SettingsPage(self.content_container)
        else:
            page = ctk.CTkLabel(self.content_container, text="Page Not Found")

        page.pack(fill="both", expand=True)

    def logout(self):
        # Destroy current dashboard window and navigate back to LoginPage
        self.destroy()
        from Screens.login import LoginPage
        login_page = LoginPage()
        login_page.mainloop()


if __name__ == "__main__":
    app = Dashboard()
    app.mainloop()