{
    'name': 'Live Chat Email Notification',
    'version': '1.0',
    'summary': 'Email chat transcript when live chat session ends successfully',
    'description': """
        This module enhances the live chat functionality in Odoo by automatically emailing the full
        chat transcript to a specified internal group when a live chat session successfully concludes.

        **Key Features:**
        - Sends an email with the entire chat history to users in the "Live Chat End Notifications" group.
        - Triggered only when the last message in the chat matches a predefined final message.
        - Final message is configurable via the system parameter: `decoscape.livechat_final_message`.
        - Ensures the transcript is sent only once per session using a dedicated boolean field (`x_dscape_email_transcript_sent`).
        - Designed for companies that need real-time visibility into completed live chat conversations, such as DecoScape's support operations team.

        
        **Use Case:**
        This module is ideal for operations or customer support managers who want to receive notifications
        and full transcripts for concluded live chat sessions, allowing follow-up or quality checks.
    """,
    'author': 'Meer Zaman Khattak',
    'depends': ['base','im_livechat', 'mail'],
    'data': [
        'data/groups.xml',
    ],
    'installable': True,
    'auto_install': False,
}