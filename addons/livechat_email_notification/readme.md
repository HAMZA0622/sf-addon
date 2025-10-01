# Live Chat Success Email for Odoo

This Odoo module automatically sends an email containing the full live chat transcript to a specific internal group when a live chat session ends successfully.

---

## 🔧 Features

- ✅ Automatically emails chat history at the end of a live chat session.
- ✅ Final message is **configurable** via system parameters.
- ✅ Prevents duplicate emails using a flag field: `x_dscape_email_transcript_sent`.
- ✅ Targets users in the **Live Chat End Notifications** group.
- ✅ Seamless integration with Odoo's `im_livechat` and `mail` modules.

---

## ⚙️ Configuration

### 1. System Parameter for Final Message

Set the message that identifies a completed chat session. This message is checked against the chatbot’s last step to determine if the session has ended.

- **Go to**: `Settings > Technical > Parameters > System Parameters`
- **Key**: `decoscape.livechat_final_message`
- **Value**: `Thank you for contacting DecoScape, a representative will be in touch soon.`

> Admins can customize this message to match their chatbot’s final output.

---

### 2. Notification Group

Users who should receive the chat transcript must belong to this group:

**Group Name**: `Live Chat End Notifications`

You can assign users to this group via:

- `Settings > Users & Companies > Groups`
- Search `Live Chat End Notifications`
- Open the group and add the desired users under the Users section

   `These users will now receive chat end notifications.`
---

## 🧠 How It Works

1. The module inherits `discuss.channel`.
2. When a live chat is updated (`write()` method), it:
   - Checks if it's a live chat (`channel_type == 'livechat'`)
   - Ensures the transcript hasn’t been emailed yet
   - Confirms the last chatbot step matches the configured system message
3. If all conditions are met:
   - It sends the chat transcript by email to all users in the **Live Chat End Notifications** group
   - Sets the flag `x_dscape_email_transcript_sent = True` to avoid repeats

---

## 📦 Dependencies

This module depends on the following Odoo core modules:

- `base`
- `im_livechat`
- `mail`

---

## 📁 Included Files

- `data/mail_template.xml`: Email template used for transcript delivery
- `data/groups.xml`: Security group definition
- `models/discuss_channel.py`: Main logic for triggering and sending emails

---

## 👨‍💼 Author

**Meer Zaman Khattak**

---

## 📝 License

This module is provided as-is under the terms of the Odoo App Store guidelines or your project's open source policy.

---

## 🚀 Use Case Example

Imagine a customer ends a live chat session and the chatbot sends:
> "Thank you for contacting DecoScape, a representative will be in touch soon."

This message matches the system parameter. The transcript is then automatically sent to your operations or support team members in the **Live Chat End Notifications** group — no manual steps needed.

---

## ✅ Final Notes

- Ensure outgoing email is correctly configured in your Odoo system.
- Make sure users who need the transcripts are added to the correct group.
- Adjust the final message string to match your live chatbot configuration.
