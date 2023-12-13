from odoo import models, fields, _, api
from odoo.exceptions import UserError
from datetime import datetime, timedelta


class MealRegister(models.Model):
    _name = 'tigo.service'
    _description = 'Dịch vụ'
    _check_company_auto = True

    name_id = fields.Many2one('hr.employee', string=_('Người Đặt'), required=1, check_company=True)
    name = fields.Char(string=_('Mã Hóa Đơn'), readonly=1)
    type = fields.Selection([('sing', 'Hát'), ('eat', 'Ăn uống')], string=_('Kiểu Dịch Vụ'), default="eat", required=True)
    state = fields.Selection([('quotes', 'Báo Giá'),
                              ('order', 'Đặt Phòng'),
                              ('pay', 'Thanh Toán'),
                              ('payed', 'Đã Thanh Toán'),
                              ('cancel', 'Hủy')], string='Trạng Thái', default='quotes')
    room_id = fields.Many2one('tigo.room', string=_('Phòng'), required=True, check_company=True)
    start_day = fields.Datetime(string=_("Ngày bắt đầu"), required=True)
    end_day = fields.Datetime(string=_('Ngày kết thúc'), required=True)
    deposit = fields.Integer(string="Tiền cọc", group_operator="avg")
    price = fields.Integer(string='Tiền Phòng', readonly=1, group_operator="avg")
    time_use = fields.Integer(string='Giờ Sử Dụng', compute='_compute_time_up')
    order_dish_ids = fields.One2many('tigo.dish.order', 'order_dish_id', string=_('Đặt Món Ăn'))
    total_price = fields.Integer(string=_('Tổng Giá'), readonly=1, compute='_compute_total_price', store=True)
    comment = fields.Text(string=_('Ghi Chú'))
    company_id = fields.Many2one('res.company', string=_('Công ty'), default=lambda x: x.env.company, store=True)

    def write(self, vals):
        result = super(MealRegister, self).write(vals)
        if self.name:
            return result
        else:
            self.name = self.env['ir.sequence'].next_by_code('tigo.service')
            return result

    @api.model
    def create(self, vals_list):
        res = super(MealRegister, self).create(vals_list)
        res['name'] = self.env['ir.sequence'].next_by_code('tigo.service')
        return res

    @api.depends('start_day', 'end_day', 'type', 'room_id', 'price', 'total_price')
    def _compute_time_up(self):
        for r in self:
            if r.start_day and r.end_day and r.room_id:
                if r.type == 'sing' or r.type == 'eat':
                    time_up = r.end_day - r.start_day
                    r.time_use = time_up.total_seconds() / 3600
                    r.price = r.room_id.price * r.time_use
                    r.total_price = r.price - r.deposit
                    if r.order_dish_ids:
                        for line in r.order_dish_ids:
                            r.total_price = r.total_price + line.price
                else:
                    r.time_use = 0
            else:
                r.time_use = 0

    def action_order(self):
        for r in self:
            r.state = 'order'

    def action_pay(self):
        for r in self:
            r.state = 'pay'

    def action_cancel(self):
        for r in self:
            r.state = 'cancel'
            return {
                'type': 'ir.actions.act_window',
                'name': 'Lý Do Từ Chối',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'popup.cmt',
                'views': [(self.env.ref('z_base.popup_cmt_view').id, 'form')],
                'target': 'new',
            }

    def action_payed(self):
        for r in self:
            r.state = 'payed'

    @api.onchange('type', 'room_id')
    def onchange_room_id(self):
        for r in self:
            if r.type == 'eat':
                room = self.env['tigo.room'].search([('type_room', '=', 'eat')]).ids
                return {'domain': {'room_id': [('id', 'in', room)]}}
            else:
                room = self.env['tigo.room'].search([('type_room', '=', 'sing')]).ids
                return {'domain': {'room_id': [('id', 'in', room)]}}

    @api.onchange('start_day')
    def onchange_day_start(self):
        for r in self:
            if r.start_day and r.start_day < datetime.now() - timedelta(days=1):
                raise UserError(_('Ngày bắt đầu phải lớn hơn hoặc bằng ngày hiện tại.'))
            else:
                pass

    @api.onchange('end_day')
    def onchange_day_end(self):
        for r in self:
            if r.start_day and r.end_day:
                if r.end_day and r.end_day < r.start_day:
                    raise UserError(_('Ngày kết thúc phải lớn hơn ngày hiện tại.'))
                else:
                    pass

    @api.onchange('deposit')
    def _onchange_total_price(self):
        for r in self:
            r.total_price = r.price - r.deposit
            if r.order_dish_ids:
                for line in r.order_dish_ids:
                    r.total_price = r.total_price + line.price

    @api.depends('order_dish_ids', 'order_dish_ids.number', 'order_dish_ids.dish_id')
    def _compute_total_price(self):
        for r in self:
            if r.order_dish_ids:
                r.total_price = sum(r.order_dish_ids.mapped('price'))
            else:
                r.total_price = 0

    def print_bill(self):
        self.ensure_one()
        return self.env.ref('z_base.print_bill_xlsx').report_action(self)