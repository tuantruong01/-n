from odoo import models, fields, _, api
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import string, random

from datetime import datetime


class MealRegister(models.Model):
    _name = 'tigo.mealregister'
    _description = 'Đăng ký bữa ăn'
    _check_company_auto = True

    name = fields.Char(string=_('Mã suất ăn'), readonly=True)
    register = fields.Many2one('res.users',
                               string=_('Người đăng ký'),
                               default=lambda self: self.env.user,
                               readonly=1, check_company=True)
    code_employee = fields.Char(string=_('Mã Nhân Viên'), compute='_compute_code_employee')
    number = fields.Selection([('four', '4'), ('six', '6')], string=_('Số người đăng ký'))
    meal_type = fields.Selection([('set', 'Suất'), ('table', 'Bàn')],
                                 string=_('Hình thức ăn'), default='set', required=1)
    date = fields.Date(string=_('Ngày đăng ký'), required=True)
    menu_id = fields.Many2one('tigo.menu', string=_('Thực đơn'))
    employee_meal_register_ids = fields.One2many('tigo.detailed.registration', 'registration_id',
                                                 string="Đăng ký cho nhân viên")
    client_meal_register_ids = fields.One2many('tigo.register.client', 'registration_id',
                                               string="Đăng ký cho khách hàng")
    state = fields.Selection([('draft', 'Chờ'),
                              ('done', 'Đã đăng ký'),
                              ('cancel', 'Hủy')], string='Trạng Thái', default='draft')
    confirm_dish_ids = fields.One2many('confirm.dish', 'mealregister_id', string=_('Suất ăn'))
    detail_dish = fields.Char(string=_('Chi tiết món'), readonly=1)
    company_id = fields.Many2one('res.company', string=_('Công ty'), default=lambda x: x.env.company, store=True)

    @api.model
    def create(self, vals_list):
        res = super(MealRegister, self).create(vals_list)
        res['name'] = self.env['ir.sequence'].next_by_code('tigo.mealregister')
        return res

    @api.onchange('date')
    def onchange_day_start(self):
        for r in self:
            if r.date and r.date < fields.Date.today():
                raise UserError(_('Ngày Đăng Ký Phải Lớn Hơn Hoặc Bằng Ngày Hiện Tại.'))
            else:
                pass

    def action_register(self):
        for r in self:
            check_customer = self.env['confirm.dish'].search([('date_register', '=', r.date)])
            for line in check_customer:
                for p in r.employee_meal_register_ids:
                    if line.employee_id == p.employee_id.name:
                        raise ValidationError(_('Nhân Viên Đã Được Đăng Ký'))
                for p in r.client_meal_register_ids:
                    if line.employee_id == p.partner_id.name:
                        raise ValidationError(_('Khách Hàng Đã Đăng Ký'))

            if r.number == 'four':
                total = len(r.client_meal_register_ids) + len(r.employee_meal_register_ids)
                if total > 4:
                    raise ValidationError(_('Số Người Đăng Ký Phải Bằng Số Nguời/Bàn Đặt'))
                elif total < 4:
                    raise ValidationError(_('Số Người Đăng Ký Phải Bằng Số Nguời/Bàn Đặt'))
            elif r.number == 'six':
                total = len(r.client_meal_register_ids) + len(r.employee_meal_register_ids)
                if total > 6:
                    raise ValidationError(_('Số Người Đăng Ký Phải Bằng Số Nguời/Bàn Đặt'))
                elif total < 6:
                    raise ValidationError(_('Số Người Đăng Ký Phải Bằng Số Nguời/Bàn Đặt'))
            r.state = 'done'
            if r.meal_type == 'set':
                if r.employee_meal_register_ids:
                    for line in r.employee_meal_register_ids:
                        self.env['confirm.dish'].create({
                            'employee_id': line.employee_id.name,
                            'mealregister_id': r.id,
                            'department': line.department_id,
                            'date_register': r.date,
                            'menu_id': line.menu_id.name,
                            'price': line.menu_id.price,

                        })
                if r.client_meal_register_ids:
                    for line in r.client_meal_register_ids:
                        self.env['confirm.dish'].create({
                            'mealregister_id': r.id,
                            'employee_id': line.partner_id.name,
                            'date_register': r.date,
                            'department': line.company,
                            'menu_id': line.menu_id.name,
                            'price': line.menu_id.price,

                        })
            else:
                if r.employee_meal_register_ids:
                    for line in r.employee_meal_register_ids:
                        self.env['confirm.dish'].create({
                            'employee_id': line.employee_id.name,
                            'mealregister_id': r.id,
                            'department': line.department_id,
                            'date_register': r.date,
                            'menu_id': r.detail_dish,
                            'price': r.menu_id.price,

                        })
                if r.client_meal_register_ids:
                    for line in r.client_meal_register_ids:
                        self.env['confirm.dish'].create({
                            'mealregister_id': r.id,
                            'employee_id': line.partner_id.name,
                            'date_register': r.date,
                            'department': line.company,
                            'menu_id': r.detail_dish,
                            'price': r.menu_id.price,
                        })

    def action_cancel(self):
        for r in self:
            check = self.env['confirm.dish'].search([('date_register', '=', r.date)])
            for line in check:
                for p in r.employee_meal_register_ids:
                    if (line.employee_id == p.employee_id.name) and (line.ate == True):
                        raise ValidationError(_('Nhân Viên Đã Ăn Không Thể Hủy'))
                for p in r.client_meal_register_ids:
                    if line.employee_id == p.partner_id.name and (line.ate == True):
                        raise ValidationError(_('Khách Hàng Đã Ăn Không Thể Hủy'))
            for line in r.confirm_dish_ids:
                line.unlink()
            r.state = 'cancel'

    def action_back_draft(self):
        for r in self:
            r.state = 'draft'

    @api.onchange('date', 'number', 'meal_type', 'menu_id')
    def onchange_menu_ids(self):
        for r in self:
            if r.meal_type == 'table' and r.number and r.date:
                if r.number == 'four':
                    menu_week = self.env['tigo.menu.setting'].search(
                        [('day_start', '<=', r.date), ('day_end', '>=', r.date),
                         ('type_menu', '=', r.meal_type), ('state', '=', 'active'),
                         ('number_of_people', '=', r.number)
                         ])
                    menu_day = self.env['tigo.menu.setting'].search(
                        [('day', '=', r.date),
                         ('type_menu', '=', r.meal_type), ('state', '=', 'active'),
                         ('number_of_people', '=', r.number)
                         ])
                    if not menu_week and not menu_day:
                        menu = []
                        return {'domain': {'menu_id': [('id', 'in', menu)]}}
                    else:
                        menu = menu_week + menu_day
                        if menu:
                            return {'domain': {'menu_id': [('id', 'in', menu.menu_ids.ids)]}}
                elif r.number == 'six':
                    menu_week = self.env['tigo.menu.setting'].search(
                        [('day', '=', r.date),
                         ('type_menu', '=', 'table'), ('state', '=', 'active'),
                         ('number_of_people', '=', r.number)])
                    menu_day = self.env['tigo.menu.setting'].search(
                        [('day_start', '<=', r.date), ('day_end', '>=', r.date),
                         ('type_menu', '=', 'table'), ('state', '=', 'active'),
                         ('number_of_people', '=', r.number)])
                    if not menu_week and not menu_day:
                        menu = []
                        return {'domain': {'menu_id': [('id', 'in', menu)]}}
                    else:
                        menu = menu_week + menu_day
                        if menu:
                            return {'domain': {'menu_id': [('id', 'in', menu.menu_ids.ids)]}}
            else:
                menu = []
                return {'domain': {'menu_id': [('id', 'in', menu)]}}

    @api.onchange('menu_id')
    def _onchange_menu_id(self):
        for r in self:
            r.detail_dish = ', '.join([line.name for line in r.menu_id.dish_ids])

    @api.constrains('register')
    def _check_employee_meal_register_ids(self):
        for r in self:
            total = len(r.employee_meal_register_ids) + len(r.client_meal_register_ids)
            if total == 0:
                raise ValidationError(_('Bạn Chưa Đăng Ký Bữa Ăn'))

    @api.depends('register')
    def _compute_code_employee(self):
        for r in self:
            employee_id = self.env['hr.employee'].search([('user_id', '=', r.register.id)], limit=1)
            if employee_id:
                r.code_employee = employee_id.code_employee
            else:
                r.code_employee = False

    def write(self, vals):
        result = super(MealRegister, self).write(vals)
        if self.name:
            return result
        else:
            self.name = self.env['ir.sequence'].next_by_code('tigo.mealregister')
            return result
