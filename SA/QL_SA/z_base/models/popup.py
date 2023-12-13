from odoo import models, fields


class Popup(models.TransientModel):
    _name = 'popup.cmt'

    comment = fields.Text(string='Lý Do')

    def popup_cmt(self):
        service = self.env.context.get('active_id', False)
        record_values = self.env['tigo.service'].browse(service)
        record_values.comment = self.comment
