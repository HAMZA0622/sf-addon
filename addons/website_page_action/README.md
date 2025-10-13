# Website Page Action

This Odoo module enhances the Website > Pages interface by adding custom actions for managing individual pages directly from the list view.

## ✅ Features

- Adds an **"Edit Page"** action link in the Website Pages tree view.
- Clicking "Edit Page" takes the user directly to the **Edit** form of the page.
- Bypasses the domain-specific routing logic by dynamically using the current browser's base URL.
- Clean integration using native Odoo XML and computed fields.
- Designed for easy extension with additional actions in the future.

## 🧩 Use Case

By default, clicking on a page in the Website Pages list view opens the frontend website. This module adds an "Edit Page" link that opens the backend edit form directly, allowing faster content updates — especially useful in multi-website environments.

## 📦 Installation

Place the module in your custom addons directory and update the app list:

```bash
$ ./odoo-bin -u website_page_action -d your_db
