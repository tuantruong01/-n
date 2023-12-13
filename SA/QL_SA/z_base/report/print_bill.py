from odoo import api, fields, models


class PrintBillXlsx(models.AbstractModel):
    _name = 'report.print_bill_xlsx'
    _inherit = "report.report_xlsx.abstract"
    _description = 'In hóa đơn'

    def generate_xlsx_report(self, workbook, data, records):
        ws = workbook.add_worksheet()

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
        context = workbook.add_format({
            'text_wrap': 1,
            'align': 'left',
            'valign': 'vcenter',
            'font_name': 'Times New Roman',
            'font_size': 11
        })
        ws.set_column(0, 0, 7)
        ws.set_column(1, 1, 7)
        ws.set_column(2, 2, 20)
        ws.set_column(3, 3, 30)
        ws.set_column(4, 4, 20)
        ws.set_column(5, 5, 20)
        ws.set_column(6, 6, 20)
        ws.set_column(7, 7, 20)

        today = fields.Date.today()
        row = 3
        ws.merge_range(row, 1, row, 7, 'HÓA ĐƠN CHI TIẾT', header)

        row +=1
        ws.merge_range(row, 1, row, 3, f'Ngày in phiếu: {today.strftime("%d-%m-%Y")}', context)
        ws.merge_range(row, 4, row, 7, f'Thời gian bắt đầu: {records.start_day.strftime("%d/%m/%Y %H:%M:%S")}', context)

        row += 1
        ws.merge_range(row, 1, row, 3, f'Mã hóa đơn: {records.name}', context)
        ws.merge_range(row, 4, row, 7, f'Thời gian kết thúc: {records.end_day.strftime("%d/%m/%Y %H:%M:%S")}', context)

        row += 1
        ws.merge_range(row, 1, row, 3, f'Người đặt: {records.name_id.name}', context)
        ws.merge_range(row, 4, row, 7, f'Số giờ sử dụng: {records.time_use}', context)

        row += 1
        ws.merge_range(row, 1, row, 3,
                       f'Kiểu Dịch Vụ: {dict(self.env["tigo.service"]._fields["type"].selection).get(records.type)}', context)
        ws.merge_range(row, 4, row, 7, f'Tiền phòng: {records.price} VNĐ', context)

        row += 1
        ws.merge_range(row, 1, row, 3, f'Phòng: {records.room_id.name}', context)
        ws.merge_range(row, 4, row, 7, f'Tiền cọc: {records.deposit} VNĐ', context)

        row += 1
        ws.write(row, 1, "STT", table_header)
        ws.merge_range(row, 2, row, 3, "Tên món", table_header)
        ws.write(row, 4, "Số lượng", table_header)
        ws.write(row, 5, "Đơn giá", table_header)
        ws.write(row, 6, "Thành tiền", table_header)
        ws.write(row, 7, "Ghi chú", table_header)

        row += 1
        stt = 1
        for r in records.order_dish_ids:
            ws.write(row, 1, stt, table_content)
            ws.merge_range(row, 2, row, 3, r.dish_id.name if r.dish_id else '', table_left)
            ws.write(row, 4, r.number if r.number else 0, table_right)
            ws.write(row, 5, r.price_unit if r.price_unit else 0, table_right)
            ws.write(row, 6, r.price if r.price else 0, table_right)
            ws.write(row, 7, r.note if r.note else 0, table_left)
            stt += 1
            row += 1
        ws.merge_range(row, 1, row, 3, f'Tổng:',table_header)
        ws.write(row, 4, '', table_content)
        ws.write(row, 5, '', table_content)
        ws.write(row, 6, '', table_content)
        ws.write(row, 7, f'{records.total_price}', table_left)