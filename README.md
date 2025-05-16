# E-Commerce Application

This is a Flask-based e-commerce web application that leverages MongoDB for its database. The application supports user registration, login, product search and filtering, rating and review functionality, and an administrative panel for managing products and users.

## Vercel Deployment

The application is deployed on Vercel. You can access the live demo at:  
**https://e-commerce-v1-two.vercel.app/**

## How to Login

### Regular User

- **Registration:** New users can register via the "Register" page.
- **Login:** Once registered, log in using your username and password.

### Admin User

- **Default Admin Login:**
  - **Username:** `admin`
  - **Password:** is kept in the local .env file, not displayed for security

> **Note:** The admin user is created automatically if not found in the database when the application starts.

## Design Decisions

### Programming Language & Frameworks

- **Python & Flask:**  
  Python was chosen for its simplicity and the extensive ecosystem of libraries. Flask is used as the web framework due to its lightweight nature and ease of integration with other tools.

### Frontend Libraries

- **Bootstrap:**  
  Bootstrap is used to ensure a responsive and modern UI with minimal custom styling.

- **Font Awesome:**  
  Font Awesome provides icons that enhance the user interface for actions such as filtering, rating, and navigation.

## User Guide

### Home Page

- **Browse Products:**  
  Browse products by categories.
- **Search & Filter:**  
  Use the search bar and filters (price range, category) to narrow down products.
- **Sort Products:**  
  Sort products by price (ascending/descending) or by popularity (based on ratings).

### Product Detail

- **View Details:**  
  Click on any product to view detailed information.
- **Rate & Review:**  
  Registered users can rate and review the product.
- **Review Information:**  
  Reviews display the username of the reviewer and their star rating.

### Profile

- **Profile Information:**  
  View your profile details, including your average rating based on your reviews.
- **Admin Panel Access:**  
  Access the admin panel if you have admin privileges.

### Admin Panel

- **Add Item/User:**  
  Use forms to add new products or regular users.
- **Remove Item/User:**  
  Select products or users to remove using a simple checkbox interface.
- **Admin-Only Access:**  
  Only users with admin privileges can access the admin panel.

### Security

- User passwords are securely hashed using bcrypt.

### Environment Variables

- Sensitive data (e.g., MongoDB URI, Admin Password) is managed using environment variables, which are loaded via the `.env` package.

![image](https://github.com/user-attachments/assets/403e23ea-545b-4b44-be15-3dd03c36d0b5)

![image](https://github.com/user-attachments/assets/faf798b7-5d73-4e1d-9350-8d6e464d5807)

![image](https://github.com/user-attachments/assets/0df9cc1c-1889-4e35-b7f3-63ce2e721f3a)

![image](https://github.com/user-attachments/assets/2b367848-5960-4d30-b9ca-7f9b6ec0a691)

![image](https://github.com/user-attachments/assets/7f2b216b-d261-40f6-8054-2d4c12d3bc82)





