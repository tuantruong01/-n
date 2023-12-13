from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    product_type = fields.Selection([
        ('consu', 'Tiêu dùng'),
        ('service', 'Dịch vụ'),
        ('product', 'Sản phẩm lưu kho'),
        ('food', 'Thực phẩm')], string='Loại sản phẩm', default='consu', required=True)
    company_id = fields.Many2one('res.company', string=_('Công ty'), default=lambda x: x.env.company)

    @api.constrains('name')
    def constrains_name(self):
        for r in self:
            if len(r.name) > 50:
                raise ValidationError(_('Tên nguyên liệu không được nhỏ hơn 50 ký tự'))
            data = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+', '=', '{', '}', '[', ']', ]
            # for i in data:
            #     if i in r.name:
            #         raise ValidationError(_('Tên nguyên liệu không được chứa ký tự đặc biệt'))
            # product_template_id = self.env['product.template'].search(
            #     [('name', '=', r.name), ('company_id', '=', self.env.company.id)])
            # if len(product_template_id) > 1:
            #     raise ValidationError(_('Nguyên liệu đã tồn tại!'))
