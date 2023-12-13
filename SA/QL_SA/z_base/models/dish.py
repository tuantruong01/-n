from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class Dish(models.Model):
    _name = 'tigo.dish'
    _description = 'Món Ăn'
    _check_company_auto = True

    name = fields.Char(string=_('Tên món ăn'), required=True)
    ingredient_ids = fields.Many2many('product.template', 'dish_product_ref', 'dish_id', 'ptml_id',
                                      string=_('Nguyên liệu'))
    code_dish = fields.Char(string=_('Mã Món'), readonly=1)
    price_total = fields.Integer(string=_('Giá'), group_operator="avg")
    wage = fields.Integer(string=_('Chi Phí Khác'), group_operator="avg")
    type_service = fields.Selection([('all', 'Tất cả'),
                                     ('service', 'Dịch vụ ngoài'),
                                     ('internal', 'Nội bộ')], string='Kiểu', required=True, default='all')
    type_food = fields.Selection([('eat', 'Đồ ăn'), ('drink', 'Đồ uống')], default='eat', string='Dạng thực phẩm',
                                 required=True)
    type_room = fields.Selection([('sing', 'Phòng Hát'), ('eat', 'Phòng Ăn'), ('all', 'Tất Cả')],
                                 string=_('Món Phòng Hát/Ăn'))
    img = fields.Binary(string='Hình ảnh')
    company_id = fields.Many2one('res.company', string=_('Công ty'), default=lambda x: x.env.company, store=True)

    @api.model
    def create(self, vals_list):
        res = super(Dish, self).create(vals_list)
        res['code_dish'] = self.env['ir.sequence'].next_by_code('tigo.dish')
        return res

    def write(self, vals):
        result = super(Dish, self).write(vals)
        if self.code_dish:
            return result
        else:
            self.code_dish = self.env['ir.sequence'].next_by_code('tigo.dish')
            return result

    @api.onchange('ingredient_ids')
    def onchange_ingredient_ids(self):
        for r in self:
            r.price_total = int(sum(r.ingredient_ids.mapped('list_price'), r.wage))

    @api.onchange('wage')
    def onchange_wage(self):
        for r in self:
            r.price_total = int(sum(r.ingredient_ids.mapped('list_price'), r.wage))

    @api.constrains('name')
    def check_name(self):
        for r in self:
            dish_id = self.env['tigo.dish'].search([('name', '=', r.name), ('company_id', '=', self.env.company.id)])
            if len(dish_id) > 1:
                raise ValidationError(_('Món ăn đã tồn tại!'))
            if len(r.name) > 50:
                raise ValidationError(_('Tên món ăn không được nhỏ hơn 50 ký tự'))
            data = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+', '=', '{', '}', '[', ']', ]
            for i in data:
                if i in r.name:
                    raise ValidationError(_('Tên món ăn không được chứa ký tự đặc biệt'))

    def unlink(self):
        menu_setting_ids = self.env['tigo.menu.setting'].search([('menu_ids', '=', self.id)])
        if len(menu_setting_ids) > 0:
            raise ValidationError(_('Món ăn này đã được sử dụng trong thực đơn!'))
        return super(Dish, self).unlink()
