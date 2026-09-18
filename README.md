Pawfect Care

----- Pet Care Management System -----

Pawfect Care is a desktop-based Pet Care Management System developed using Python and MongoDB. The system helps administrators manage pet records, customer information, appointments, services, and products through a simple and user-friendly graphical interface.

----- Project Overview -----

Managing pet and customer records manually can be time-consuming and may lead to errors or loss of information. Pawfect Care provides a centralized system where important pet-care information can be stored, managed, and retrieved efficiently.

The system includes an admin login with password recovery and a dashboard for accessing different management modules.

----- Objectives -----

- Manage pet records digitally.
- Manage customer information.
- Manage appointments.
- Manage pet-care services.
- Manage products.
- Provide secure admin authentication.
- Store application data using MongoDB.
- Provide an easy-to-use graphical interface.

----- Features -----

----- Admin Authentication -----
- Admin username and password login.
- Password visibility toggle.
- Forgot password functionality.
- Security question verification.
- Password reset.

----- Admin Dashboard -----
- Total Pets
- Total Customers
- Appointments
- Services
- Navigation to different modules.

----- Pet Management -----
- Add new pet records.
- Edit existing pet records.
- Delete pet records.
- View pet information in a table.
- Store pet information in MongoDB.

----- Customer Management -----
- Add customer information.
- View customer records.
- Edit customer records.
- Delete customer records.

----- Appointment Management -----
- Manage pet-care appointments.
- Store appointment information in MongoDB.

----- Services Management -----
- Manage services offered by the pet-care system.

----- Products Management -----
- Manage pet-care products.



------ Technologies Used ======

| Technology     | Purpose                   |
|----------------|---------------------------|                  
| Python         | Main programming language |
| CustomTkinter  | Graphical User Interface  |
| MongoDB        | Database                  |
| PyMongo        | MongoDB connectivity      |
| Pillow (PIL)   | Image and logo handling   |
| VS Code        | Development environment   |


------ Database ------

MongoDB is used as the backend database.

Main collections include:

- `admin`
- `pets`
- `customers`
- `appointments`
- `services`
- `products`


------ Project Structure ------
```text
PawfectCare/
│
├── Assets/
│   ├── Icons/
│   └── Logo/
│
├── Database/
│   ├── admin.py
│   └── setup_database.py
│
├── Screens/
│   ├── login.py
│   ├── forgot_password.py
│   ├── security_question.py
│   ├── reset_password.py
│   ├── dashboard.py
│   ├── pets.py
│   ├── customers.py
│   ├── appointments.py
│   ├── services.py
│   └── products.py
│
├── requirements.txt
├── README.md
└── main.py
Project Video
[Click here to watch the PawfectCare Demo Video](https://drive.google.com/file/d/1AkTE3oIYcrCqXAYYzaKjziOrv3oLOIFn/view?usp=drive_link)



