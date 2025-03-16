# MedShel Car Store Wiki

Welcome to the MedShel Car Store project wiki! This document provides an overview of the project structure, key components, and guides for development and usage.

## Project Overview

MedShel is an online car parts store built with Django. The platform allows traders to list automotive parts and customers to browse and purchase these parts. The system includes inventory management, order processing, and user management features.

## Project Structure

The project is organized into several Django apps:

- **accounts**: Handles user authentication and profile management
- **api**: Provides API utilities and base views
- **store**: Core functionality for parts, inventory, and orders
- **project**: Main Django project settings and configuration

## Key Models

### Store App

#### Category System
- **CategoryParent**: Top-level categories
  - Fields: name, description, slug
  - Relationships: Has many child categories

- **Category**: Sub-categories that belong to a parent category
  - Fields: name, description, slug
  - Relationships: Belongs to a CategoryParent

#### Automotive Components
- **Brand**: Car manufacturers
  - Fields: name, founded year, headquarters

- **CarModel**: Specific car models from brands
  - Fields: name, production_start, production_end
  - Relationships: Belongs to a Brand

#### Inventory Management
- **Part**: The core product model
  - Fields: name, description, price, SKU, quantity, etc.
  - Relationships: Belongs to a Category and CategoryParent, owned by a Trader
  - Features: Stock status tracking, restocking functionality

- **Compatibility**: Links parts to compatible car models
  - Relationships: Many-to-many relationship between Part and CarModel

- **PartImage**: Images for parts
  - Relationships: Belongs to a Part

- **InventoryLog**: Tracks inventory changes
  - Fields: quantity, log_type, notes, timestamps
  - Types: NEW, RESTOCK, ADJUSTMENT

#### Order System
- **Order**: Customer orders
  - Fields: status, total, tracking_number, notes
  - Statuses: PENDING, PROCESSING, SHIPPED, DELIVERED, CANCELLED

- **OrderItem**: Individual items in an order
  - Fields: quantity, price
  - Relationships: Belongs to an Order and a Part

- **StockReservation**: Temporary holds on inventory during checkout
  - Fields: quantity, session_key, expires_at

### Accounts App

The accounts app handles user authentication and profile management. It includes:

- **User**: Django's built-in user model
  - Fields: username, email, password, first_name, last_name
  - Features: Authentication, password reset, email verification

- **TraderProfile**: Extended profile for traders
  - Fields: approved status, commission_rate, business_name, business_address, tax_id, phone_number, website
  - Relationships: One-to-one with User
  - Features: KYC verification status, rating system, review count

- **CustomerProfile**: Extended profile for customers
  - Fields: shipping_addresses, phone_number, preferred_payment_method
  - Relationships: One-to-one with User
  - Features: Order history, wishlist management

- **Address**: Stored addresses for users
  - Fields: street, city, state, postal_code, country, is_default
  - Relationships: Many-to-one with User

## Permissions

The system uses custom permissions to control access:

- **IsOwnerOrReadOnly**: Allows read access to anyone, but only owners can modify objects
- **IsTrader**: Restricts access to authenticated traders only
- **IsApprovedTrader**: Allows access only to traders with approved status
- **IsCustomer**: Restricts access to authenticated customers only
- **IsAdminUser**: Limits access to admin users only
- **IsStaffOrReadOnly**: Allows read access to anyone, but only staff can modify objects
- **HasInventoryPermission**: Controls access to inventory management features
- **CanProcessOrders**: Allows access to order processing functionality
- **CanManageCategories**: Controls access to category management features
## API Documentation

API documentation is available through Postman:
[View API Documentation on Postman](https://documenter.getpostman.com/view/23311056/2sAYkBs1ox)

Most endpoints require authentication using JWT tokens.

## Development Setup

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Run migrations:
```bash
python manage.py migrate
```
4. Create a superuser:
```bash
python manage.py createsuperuser
```
5. Run the development server:
```bash
python manage.py runserver
```

## Admin Interface

The Django admin interface provides comprehensive management capabilities:

- Part management with inventory tracking
- Order processing with status updates
- User and trader approval
- Category and brand management

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

*This wiki is a living document and will be updated as the project evolves.*