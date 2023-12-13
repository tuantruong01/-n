import os
from odoo import api, fields, models
from odoo.exceptions import ValidationError
import base64

from QLSA.QL_SA.z_base import wizard


class PopupReportMenuOder(models.TransientModel):
    _name = 'popup.report.menu.oder'
    _description = 'Báo Cáo Suất Ăn Đã Đặt'

    def default_image_base64(src):
        path = os.path.dirname(os.path.realpath(__file__)) + src
        default_image_path = open(path, "rb").read()
        default_image_base64 = base64.b64encode(default_image_path).decode('utf-8')
        return super(wizard.PopupReportMenuOder, models.TransientModel).default_image_base64(default_image_base64)

    src = '/../static\img\quan_ly_thuc_don_da_dat.png'
    default_img = default_image_base64(src)

    begin = fields.Date(string="Từ Ngày", required=True)
    end = fields.Date(string="Đến Ngày", required=True)
    img = fields.Binary(
        default=default_img,
        string='Ảnh Mẫu')

    @api.onchange('begin', 'end')
    def onchange_begin_end(self):
        for r in self:
            if r.begin and r.end:
                if r.end < r.begin:
                    raise ValidationError('Ngày bắt kết thúc phải lớn hơn hoặc bằng ngày bắt đầu')

    def action_print(self):
        return self.env.ref('z_base.report_menu_order').report_action(self)
