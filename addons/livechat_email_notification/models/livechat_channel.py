from odoo import models, api, fields
import logging

_logger = logging.getLogger(__name__)

class DiscussChannel(models.Model):
    _inherit = 'discuss.channel'

    x_dscape_email_transcript_sent = fields.Boolean(string="Email Transcript Sent", default=False)

    @api.model
    def write(self, vals):
        res = super(DiscussChannel, self).write(vals)
        
        for record in self:
            if (
                record.channel_type == 'livechat'
                and not record.x_dscape_email_transcript_sent
                and record._is_chatbot_finished()
            ):
                record._send_session_email_with_history()
                record.x_dscape_email_transcript_sent = True 
        return res

    def _is_chatbot_finished(self):
        step = self.chatbot_current_step_id
        final_message = self.env['ir.config_parameter'].sudo().get_param(
            'decoscape.livechat_final_message',
            default="Thank you for contacting DecoScape, a representative will be in touch soon."
        )
        return (
            step and
            step.message == final_message
        )

    def _send_session_email_with_history(self):
        admin_group = self.env.ref('livechat_email_notification.group_livechat_end_notification', raise_if_not_found=False)

        if not admin_group:
            _logger.error("Admin group not found!")
            return

        admin_users = self.env['res.users'].sudo().search([
            ('groups_id', 'in', [admin_group.id]),
            ('email', '!=', False)
        ])

        if not admin_users:
            _logger.warning("No users with email found in the group.")
            return

        for user in admin_users:
            try:
                self._email_livechat_transcript(user.email)
            except Exception as e:
                _logger.exception("Failed to send livechat transcript to %s: %s", user.email, str(e))
                