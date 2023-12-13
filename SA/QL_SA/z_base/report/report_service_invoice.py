from odoo import api, fields, models


class ReportServiceInvoice(models.AbstractModel):
    _name = 'report.report_service_invoice_xlsx'
    _inherit = "report.report_xlsx.abstract"
    _description = 'Báo cáo hóa đơn'

    def generate_xlsx_report(self, workbook, data, records):
        name = "Sheet"
        ws = workbook.add_worksheet(name)

        sql = f"""
                SELECT ts.name as mhd, he.name as nd, tr.name as tp, ts.start_day, ts.end_day, ts.total_price
                FROM    
                        tigo_service ts
                        LEFT JOIN  hr_employee he on ts.name_id = he.id
                        LEFT JOIN tigo_room tr on ts.room_id = tr.id
                WHERE
                    ((ts.start_day::date between '{records.begin}' and '{records.end}')
                        OR 
                        (ts.end_day::date between '{records.begin}' and '{records.end}'))
                    AND
                        ts.state = 'payed'
                    AND
                        ts.company_id = {self.env.company.id}
                    ORDER BY ts.start_day
        """
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
        table_left = workbook.add_format({
            'bold': 0,
            'text_wrap': 1,
            'align': 'left',
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
        table_right = workbook.add_format({
            'bold': 0,
            'text_wrap': 1,
            'align': 'right',
            'valign': 'vcenter',
            'border': 1,
            'font_name': 'Times New Roman',
            'font_size': 11
        })
        right = workbook.add_format({
            'bold': 0,
            'text_wrap': 1,
            'align': 'right',
            'valign': 'vcenter',
            'border': 1,
            'bg_color': '#DDEBF6',
            'font_name': 'Times New Roman',
            'font_size': 11
        })
        ws.set_column(0, 0, 7)
        ws.set_column(1, 1, 10)
        ws.set_column(2, 2, 20)
        ws.set_column(3, 3, 20)
        ws.set_column(4, 4, 20)
        ws.set_column(5, 5, 20)
        ws.set_column(6, 6, 20)
        ws.set_column(7, 7, 20)
        row = 3
        ws.merge_range(row, 1, row, 6, 'BÁO CÁO DANH SÁCH HÓA ĐƠN', header)
        row += 1
        ws.merge_range(row, 1, row, 6,
                       f'Từ ngày: {records.begin.strftime("%d-%m-%Y")} đến {records.end.strftime("%d-%m-%Y")}',
                       header_content)
        row += 1
        ws.write(row, 1, "STT", table_header)
        ws.write(row, 2, "Mã Hóa Đơn", table_header)
        ws.write(row, 3, "Người Đặt", table_header)
        ws.write(row, 4, "Phòng", table_header)
        ws.write(row, 5, "Từ Ngày", table_header)
        ws.write(row, 6, "Đến Ngày", table_header)
        ws.write(row, 7, "Giá", table_header)
        row += 1

        stt = 1
        total = 0
        for data in datas:
            ws.write(row, 1, stt, table_content)
            ws.write(row, 2, data.get('mhd', ''), table_left)
            ws.write(row, 3, data.get('nd', ''), table_left)
            ws.write(row, 4, data.get('tp', ''), table_left)
            ws.write(row, 5, data.get('start_day', '').strftime("%H:%M %d-%m-%Y"), table_content)
            ws.write(row, 6, data.get('end_day', '').strftime("%H:%M %d-%m-%Y"), table_content)
            ws.write(row, 7, data.get('total_price', 0), table_right)
            if data['total_price']:
                total += data.get("total_price", 0)
            else:
                total += 0
            row += 1
            stt += 1
        ws.merge_range(row, 1, row, 2, 'Tổng', table_header)
        ws.write(row, 3, '', table_right)
        ws.write(row, 4, '', table_right)
        ws.write(row, 5, '', table_right)
        ws.write(row, 6, '', table_right)
        ws.write(row, 7, total, table_right)
