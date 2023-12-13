from odoo import models, fields, _, api
from odoo.exceptions import UserError
from datetime import timedelta


class Room(models.Model):
    _name = 'tigo.room'
    _description = 'Phòng'
    _check_company_auto = True

    code_room = fields.Char(string=_('Mã Phòng'), readonly=1)
    name = fields.Char(string=_('Tên Phòng'), required=True)
    type_room = fields.Selection([('sing', 'Phòng Hát'), ('eat', 'Phòng Ăn')], string=_('Dạng'), readonly=1)
    sate = fields.Selection([('unoccupied', 'Trống'), ('occupied', 'Sử dụng')], string=_('Trạng Thái'),
                            default="unoccupied", readonly=1)
    price = fields.Integer(string=_('Giá Phòng / Giờ'), group_operator="avg")
    level = fields.Selection([('normal', 'Phòng thường'), ('vip', 'Phòng VIP')], string=_('Kiểu Phòng'),
                             default="normal", required=True)
    company_id = fields.Many2one('res.company', string=_('Công ty'), default=lambda x: x.env.company, store=True)

    @api.model
    def create(self, vals_list):
        res = super(Room, self).create(vals_list)
        res['code_room'] = self.env['ir.sequence'].next_by_code('tigo.room')
        return res

    def write(self, vals):
        result = super(Room, self).write(vals)
        if self.code_room:
            return result
        else:
            self.code_room = self.env['ir.sequence'].next_by_code('tigo.room')
            return result

    _sql_constraints = [('name', 'unique(name,company_id)', 'Phòng Đã Tồn Tại')]


class Week(models.Model):
    _name = 'tigo.week'
    _description = 'Tuần Trong Năm'
    _check_company_auto = True

    name = fields.Char(string='Tuần', required=1)
    begin = fields.Date(string='Từ ngày', required=1)
    end = fields.Date(string='Đến ngày', readonly=1)
    company_id = fields.Many2one('res.company', string=_('Công ty'), default=lambda x: x.env.company, store=True)

    @api.onchange('begin')
    def onchange_begin(self):
        for r in self:
            if r.begin:
                if r.begin.weekday() != 0:
                    raise UserError(_('Bạn phải chọn ngày đầu tuần.'))
                else:
                    r.end = r.begin + timedelta(days=6)

    def name_get(self):
        result = []
        for record in self:
            name = record.name + " (" + str(record.begin) + " đến " + str(record.end) + ")"
            result.append((record.id, name))
        return result
