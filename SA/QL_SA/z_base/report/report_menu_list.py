from odoo import api, fields, models


class ReportMenuList(models.AbstractModel):
    _name = 'report.report_menu_list'
    _inherit = "report.report_xlsx.abstract"
    _description = 'Báo cáo danh sách thực đơn'

    def generate_xlsx_report(self, workbook, data, records):
        name = "Báo cáo danh sách thực đơn"
        ws = workbook.add_worksheet(name)

        sql = f'''
                SELECT
                    tm1.code_menu,
                CASE 
                        WHEN tm1.type_menu = 'set' THEN
                        'Suất' ELSE'Bàn' 
                    END AS TYPE,
                    tm1.NAME,
                    COUNT ( tdr.menu_id ) sl 
                FROM
                    tigo_detailed_registration tdr
                    LEFT JOIN tigo_mealregister tm ON tm.ID = tdr.registration_id
                    LEFT JOIN tigo_menu tm1 ON tdr.menu_id = tm1.ID 
                WHERE
                    tm.DATE::date between '{records.begin}' and '{records.end}'
                    AND tdr.company_id = {self.env.company.id}

                GROUP BY
                    tdr.menu_id,
                    tm1.NAME,
                    tm1.code_menu,
                    tm1.type_menu
                
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
        ws.set_column(1, 1, 10)
        ws.set_column(2, 2, 20)
        ws.set_column(3, 3, 20)
        ws.set_column(4, 4, 20)
        ws.set_column(5, 5, 20)
        row = 3
        ws.merge_range(row, 1, row, 5, 'BÁO CÁO DANH SÁCH THỰC ĐƠN', header)
        row += 1
        ws.merge_range(row, 1, row, 5,
                       f'Từ ngày: {records.begin.strftime("%d-%m-%Y")} đến {records.end.strftime("%d-%m-%Y")}',
                       header_content)
        row += 1
        ws.write(row, 1, "STT", table_header)
        ws.write(row, 2, "Mã thực đơn", table_header)
        ws.write(row, 3, "Tên thực đơn", table_header)
        ws.write(row, 4, "Kiểu thực đơn", table_header)
        ws.write(row, 5, "Số người đã đặt", table_header)

        row += 1
        stt = 1
        for data in datas:
            ws.write(row, 1, stt, table_content)
            ws.write(row, 2, data.get('code_menu', ''), table_left)
            ws.write(row, 3, data.get('name', ''), table_left)
            ws.write(row, 4, data.get('type', ''), table_left)
            ws.write(row, 5, data.get('sl', ''), table_right)
            row += 1
            stt += 1
