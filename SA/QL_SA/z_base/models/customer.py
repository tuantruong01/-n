from odoo import models, fields, _, api


class Customer(models.Model):
    _name = 'res.customer'
    _description = 'Khách Hàng'
    _check_company_auto = True

    code_customer = fields.Char(string=_('Mã Khách Hàng'), readonly=1)
    img = fields.Binary(string=_('Image'), attachment=True)
    name = fields.Char(string=_('Tên Khách Hàng'), required=True)
    company = fields.Char(string=_('Công ty'), required=True)
    phone = fields.Char(string=_('Điện thoại'))
    position = fields.Char(string=_('Chức danh'))
    company_id = fields.Many2one('res.company', string=_('Công ty'), default=lambda x: x.env.company, store=True)

    @api.model
    def create(self, vals_list):
        res = super(Customer, self).create(vals_list)
        res['code_customer'] = self.env['ir.sequence'].next_by_code('res.customer')
        return res