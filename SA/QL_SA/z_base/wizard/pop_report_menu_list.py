from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PopupMenuList(models.TransientModel):
    _name = 'popup.menu.list'
    _description = 'Báo cáo danh sách thực đơn'

    begin = fields.Date(string="Từ Ngày", required=True)
    end = fields.Date(string="Đến Ngày", required=True)
    image = fields.Html(default='<img src="\z_base\static\img\ds_thuc_don.png" "style="margin-left: 73px;width: 547px;">',
                        string='Ảnh')

    @api.onchange('begin', 'end')
    def onchange_begin_end(self):
        for r in self:
            if r.begin and r.end:
                if r.end < r.begin:
                    raise ValidationError('Ngày bắt kết thúc phải lớn hơn hoặc bằng ngày bắt đầu')

    def action_print(self):
        return self.env.ref('z_base.report_menu_list').report_action(self)
