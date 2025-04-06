# E-Commerce Application

This is a Flask-based e-commerce web application that leverages MongoDB for its database. The application supports user registration, login, product search and filtering, rating and review functionality, and an administrative panel for managing products and users.

## Vercel Deployment

The application is deployed on Vercel. You can access the live demo at:  
**https://e-commerce-v1-fg9neponn-rabais-projects.vercel.app/**

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

## Additional Notes

### Security
- User passwords are securely hashed using bcrypt.

### Environment Variables
- Sensitive data (e.g., MongoDB URI, Admin Password) is managed using environment variables, which are loaded via the `.env` package.
