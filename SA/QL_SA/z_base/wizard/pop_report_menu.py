from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PopupReportMenu(models.TransientModel):
    _name = 'popup.report.menu'
    _description = 'Báo Cáo Thực Đơn'

    begin = fields.Date(string="Từ Ngày", required=True)
    end = fields.Date(string="Đến Ngày", required=True)
    image = fields.Html(
        default='<img src="/z_base/static/img/400072437_895459194939025_7348562175171294141_n.png" style="margin-left: 73px;width: 547px;">',
        string='Ảnh')

    @api.onchange('begin', 'end')
    def onchange_begin_end(self):
        for r in self:
            if r.begin and r.end:
                if r.end and r.end < r.begin:
                    raise ValidationError('Ngày bắt kết thúc phải lớn hơn hoặc bằng ngày bắt đầu')
                elif r.begin and r.begin > r.end:
                    raise ValidationError('Ngày bắt đầu phải nhỏ hơn hoặc bằng ngày kết thúc')

    def action_print(self):
        return self.env.ref('z_base.report_menu_xlsx').report_action(self)
