from odoo import api, fields, models


class ReportMenu(models.AbstractModel):
    _name = 'report.report_menu_xlsx'
    _inherit = "report.report_xlsx.abstract"
    _description = 'Báo cáo thực đơn theo thời gian'

    def generate_xlsx_report(self, workbook, data, records):
        name = "Sheet"
        ws = workbook.add_worksheet(name)

        sql = f"""
                SELECT 
                        tms.id,
                        tms.name,
                       CASE 
                            WHEN tms.type_menu = 'set' THEN
                            'Suất' ELSE 'Bàn' 
                            END AS TYPE, 
                        tms.day, 
                        tw.name as week,
                         tms.day_start,
                          tms.day_end,
                        CASE 
                            WHEN tms.state = 'unactive' THEN
                            'Chưa Sử Dụng' ELSE 'Đã Đưa Vào Sử Dụng' 
                            END AS state,
                        tm.name thuc_don
                FROM
                    tigo_menu_setting tms
                    LEFT JOIN tigo_week tw on tms.week = tw.id
                    LEFT JOIN setting_menu_ref smr on tms.id = smr.setting_id
                    Left JOIN tigo_menu tm on smr.menu_id = tm.id
                WHERE
                    ((tms.day_start::date between '{records.begin}' and '{records.end}')
                    OR 
                        (tms.day_end::date between '{records.begin}' and '{records.end}')
                    OR
                        ('{records.begin}'::date between tms.day_start and tms.day_end)
                    OR 
                        ('{records.end}'::date between tms.day_start and tms.day_end)
                    OR
                        tms.day::date between '{records.begin}' and '{records.end}')
                    AND tms.company_id = {self.env.company.id}
                ORDER BY tms.type_menu
            """
        self.env.cr.execute(sql)
        print(sql)
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
        ws.set_column(0, 0, 7)
        ws.set_column(1, 1, 10)
        ws.set_column(2, 2, 20)
        ws.set_column(3, 3, 20)
        ws.set_column(4, 4, 20)
        ws.set_column(5, 5, 20)
        ws.set_column(6, 6, 20)

        table_right = workbook.add_format({
            'bold': 0,
            'text_wrap': 1,
            'align': 'right',
            'valign': 'vcenter',
            'border': 1,
            'font_name': 'Times New Roman',
            'font_size': 11
        })
        row = 3
        ws.merge_range(row, 1, row, 5, 'BÁO CÁO DANH SÁCH THỰC ĐƠN CẤU HÌNH THEO NGÀY/TUẦN', header)
        row += 1
        ws.merge_range(row, 1, row, 5,
                       f'Từ ngày: {records.begin.strftime("%d-%m-%Y")} đến {records.end.strftime("%d-%m-%Y")}',
                       header_content)

        row += 1
        ws.write(row, 1, "STT", table_header)
        ws.write(row, 2, "Mã Cấu Hình ", table_header)
        ws.write(row, 3, "Thực Đơn", table_header)
        ws.write(row, 4, "Kiểu", table_header)
        ws.write(row, 5, "Trạng Thái", table_header)
        row += 1
        stt = 1
        dict_data = {}
        for r in datas:
            # if r['id'] in dict_data:
            #     if r['thuc_don']:
            #         dict_data[r['id']]['thuc_don'] += ',' + r['thuc_don']
            # else:
            #     dict_data[r['id']] = r
            if r['id'] in dict_data:
                if r['week']:
                    dict_data[r['id']]['week'] = (r['week'] + '(' + r['day_start'].strftime("%d-%m-%Y") + ' đến ' +
                                                  r['day_end'].strftime("%d-%m-%Y") + ')')
            else:
                dict_data[r['id']] = r
        print(dict_data)
        for data in dict_data.values():
            ws.write(row, 1, stt, table_content)
            ws.write(row, 2, data.get('name', ''), table_left)
            ws.write(row, 3, data.get('thuc_don', ''), table_left)
            ws.write(row, 4, data.get('type', ''), table_left)
            ws.write(row, 5, data.get('state', ''), table_left)
            row += 1
            stt += 1
