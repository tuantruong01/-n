from odoo import api, fields, models


class PopupReportIngredient(models.TransientModel):
    _name = 'popup.report.ingredient'
    _description = 'Báo Cáo Nguyên Liệu'

    categ_ids = fields.Many2many('product.category', 'product_category_ref', 'ingredient_id', 'category_id',
                                 string='Nhóm Thực Phẩm', required=True)
    all = fields.Boolean(string='Tất Cả')
    image = fields.Html(
        default='<img src="/z_base/static/img/nguyen_lieu.png" style="margin-left: 73px;width: 547px;">',
        string='Ảnh')

    def action_print(self):
        self.ensure_one()
        return self.env.ref('z_base.report_ingredient_xlsx').report_action(self)

    @api.onchange('all')
    def onchange_all(self):
        for r in self:
            if r.all == True:
                r.categ_ids = self.env['product.category'].search([])
