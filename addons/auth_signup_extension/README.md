## Auth Signup Extension

### Overview  
The **Auth Signup Extension** module enhances the default Odoo authentication system by adding additional fields required by **Decoscape**. It modifies the signup process to notify both the user and the admin about the account approval status.

### Features  
- Captures additional fields during user signup as required by **Decoscape**.  
- Sends an email to the user upon registration, informing them that their account is under review and will be approved within **24 hours**.  
- Notifies administrators about new signups via email.  
- Introduces a **User Account Approval** group for admins who should receive signup notifications.  

### Installation  
1. Copy the module into your Odoo add-ons directory.  
2. Restart the Odoo server:  
   ```bash
   odoo-bin -c <your-config-file> -u auth_signup_extension
   ```
3. Ensure the **auth_signup** module is installed for this extension to work.  

### Configuration  
1. Navigate to **Settings > Users & Companies > Groups**.  
2. Find the **User Account Approval** group and add the relevant admin users.  
3. Ensure the email server is properly configured in **Settings > General Settings > Outgoing Mail Servers**.  

### Usage  
1. A new user signs up using the Odoo registration form.  
2. An email is automatically sent to the user confirming that their account is under review.  
3. An admin (who belongs to the **User Account Approval** group) receives an email notification about the new signup.  
4. The admin can approve the user manually via **Settings > Users & Companies > Users**.  
5. Once approved, the user will be able to log in.  

### Dependencies  
- **auth_signup** (Odoo official module)  
- **mail** (Odoo email system)  

### Technical Details  
- Controllers extend `auth_signup` functionality to add validation and approval logic.  
- Emails are triggered via Odoo's `mail.template`.  
- Group-based notification ensures only designated admins receive new signup alerts.  