from odoo import api, fields, models


class ReportQtyDepartment(models.AbstractModel):
    _name = 'report.report_qty_department'
    _inherit = "report.report_xlsx.abstract"
    _description = 'Số lượng suất ăn đã đăng ký theo phòng ban'

    def generate_xlsx_report(self, workbook, data, records):
        name = "Số lượng suất ăn đã đăng ký theo phòng ban"
        ws = workbook.add_worksheet(name)

        sql = f'''
                SELECT
                    hd.name,
                    COUNT(tdr.department_id) as sl
                FROM
                    tigo_detailed_registration tdr
                    LEFT JOIN tigo_mealregister tm ON tm.ID = tdr.registration_id
                    LEFT JOIN hr_department hd ON tdr.department_id = hd.ID 
                WHERE
                     tm.DATE::date between '{records.begin}' and '{records.end}'
                     and tdr.department_id is not null
                     and tdr.company_id = {self.env.company.id}
                GROUP BY
                    hd.ID,
                    hd.NAME
        '''
        self.env.cr.execute(sql)
        datas = self.env.cr.dictfetchall()
        header = workbook.add_format({
            'bold': 1,
            'text_wrap': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_name': 'Times New Roman',
            'font_size': 16
        })
        table_header = workbook.add_format({
            'bold': 1,
            'text_wrap': 1,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#DDEBF6',
            'border': 1,
            'font_name': 'Times New Roman',
            'font_size': 13
        })
        table_content = workbook.add_format({
            'bold': 0,
            'text_wrap': 1,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'font_name': 'Times New Roman',
            'font_size': 11
        })
        header_content = workbook.add_format({
            'bold': 1,
            'text_wrap': 1,
            'align': 'left',
            'valign': 'vcenter',
            'font_name': 'Times New Roman',
            'font_size': 11,
            'italic': 1
        })
        table_left = workbook.add_format({
            'bold': 0,
            'text_wrap': 1,
            'align': 'left',
            'valign': 'vcenter',
            'border': 1,
            'font_name': 'Times New Roman',
            'font_size': 11
        })
        table_right = workbook.add_format({
            'bold': 0,
            'text_wrap': 1,
            'align': 'right',
            'valign': 'vcenter',
            'border': 1,
            'font_name': 'Times New Roman',
            'font_size': 11
        })
        ws.set_column(0, 0, 7)
        ws.set_column(1, 1, 7)
        ws.set_column(2, 2, 20)
        ws.set_column(3, 3, 30)
        ws.set_column(4, 4, 20)
        row = 3
        ws.merge_range(row, 1, row, 3, 'BÁO CÁO SỐ LƯỢNG SUẤT ĂN ĐÃ ĐĂNG KÝ THEO PHÒNG BAN', header)
        row += 1
        ws.merge_range(row, 1, row, 3,
                       f'Từ ngày: {records.begin.strftime("%d-%m-%Y")} đến {records.end.strftime("%d-%m-%Y")}',
                       header_content)
        row += 1
        ws.write(row, 1, "STT", table_header)
        ws.write(row, 2, "Tên phòng ban", table_header)
        ws.write(row, 3, "Số lượng đăng ký", table_header)

        row += 1
        stt = 1
        for data in datas:
            ws.write(row, 1, stt, table_content)
            ws.write(row, 2, data.get('name', ''), table_left)
            ws.write(row, 3, data.get('sl', ''), table_right)
            row += 1
            stt += 1
