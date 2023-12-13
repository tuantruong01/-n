from odoo import models, fields, _, api


class HrEmployeeInherit(models.Model):
    _inherit = "hr.employee"

    code_employee = fields.Char(string=_('Mã nhân viên'), readonly=1)
    company_id = fields.Many2one('res.company', string=_('Công ty'), default=lambda x: x.env.company)

    @api.model
    def create(self, vals_list):
        res = super(HrEmployeeInherit, self).create(vals_list)
        res['code_employee'] = self.env['ir.sequence'].next_by_code('hr.employee')
        return res

    # def write(self, vals):
    #     result = super(HrEmployeeInherit, self).write(vals)
    #     if self.code_employee:
    #         return result
    #     else:
    #         self.code_employee = self.env['ir.sequence'].next_by_code('hr.employee')
    #         return result
