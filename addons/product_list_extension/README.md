# Product List Extension

This Odoo module extends the product model to include an **Extended Name** field. This new field is displayed **below** the default product name in the product grid on the e-commerce website.

---

## Features

- Adds a new **Extended Name** field to the product template.
- Displays the extended name **beneath** the main product name in the product listing grid (e.g., shop page).
- Seamlessly integrates with the standard Odoo website/e-commerce module (`website_sale`).

---

## Use Case

This module is helpful when you want to show additional product information (like features, variations, or extra descriptors) directly under the product name on your online store.

**Example Display:**

- **Product Name**: "Stylish T-shirt"
  - **Extended Name**: "3 Sizes Available + Custom Size Available"

This example shows how the **Extended Name** field is used to display additional product options, such as available sizes or customizations, directly under the product name in the online store's product listing grid.

---

## Example Implementation:

For each product in your catalog, you can populate the **Extended Name** field like this:

- **Product Name**: "Cosmo 64" Daybed"
  - **Extended Name**: "( 3 sizes available + custom size available )"
  
- **Product Name**: "Luxury Sofa"
  - **Extended Name**: "2 Colors Available + Custom Dimensions Possible"
