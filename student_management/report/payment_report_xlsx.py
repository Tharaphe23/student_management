
from odoo import models

class PaymentReportXlsx(models.AbstractModel):
    _name = 'report.student_management.payment_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Payment Excel Report'

    def generate_xlsx_report(self, workbook, data, payments):

        data = data or {}

        sheet = workbook.add_worksheet('Payments')

        title = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'align': 'center'
        })

        info = workbook.add_format({'italic': True})

        header = workbook.add_format({
            'bold': True,
            'bg_color': '#714B67',
            'font_color': 'white',
            'border': 1,
            'align': 'center'
        })

        cell = workbook.add_format({'border': 1})

        money = workbook.add_format({
            'border': 1,
            'num_format': '#,##0'
        })

        total_fmt = workbook.add_format({
            'bold': True,
            'border': 1,
            'num_format': '#,##0'
        })

        # Report Information
        date_from = data.get('date_from') or 'All'
        date_to = data.get('date_to') or 'All'
        method = data.get('payment_method_label') or 'All'
        state = data.get('state_label') or 'All'

        sheet.merge_range(
            'A1:H1',
            'Payment Report',
            title
        )

        sheet.write(
            'A2',
            'Date: %s ~ %s' % (date_from, date_to),
            info
        )

        sheet.write(
            'D2',
            'Method: %s' % method,
            info
        )

        sheet.write(
            'F2',
            'Status: %s' % state,
            info
        )

        # Table Headers
        headers = [
            'Reference',
            'Student ID',
            'Student',
            'Enrollment',
            'Payment Date',
            'Method',
            'Status',
            'Amount (MMK)'
        ]

        for col, h in enumerate(headers):
            sheet.write(3, col, h, header)

        pay_method = dict(
            payments._fields['payment_method'].selection
        )

        pay_state = dict(
            payments._fields['state'].selection
        )

        # Payment Records
        row = 4
        total = 0

        for p in payments:
            sheet.write(row, 0, p.name or '', cell)
            sheet.write(row, 1, p.student_id.student_code or '', cell)
            sheet.write(row, 2, p.student_id.name or '', cell)
            sheet.write(row, 3, p.enrollment_id.name or '', cell)
            sheet.write(row, 4, str(p.payment_date or ''), cell)

            sheet.write(
                row, 5,
                pay_method.get(p.payment_method, ''),
                cell
            )

            sheet.write(
                row, 6,
                pay_state.get(p.state, ''),
                cell
            )

            sheet.write(row, 7, p.amount, money)

            total += p.amount
            row += 1

        # Total Amount
        sheet.write(row, 6, 'Total', total_fmt)
        sheet.write(row, 7, total, total_fmt)

        # Column Width
        sheet.set_column('A:B', 18)
        sheet.set_column('C:D', 22)
        sheet.set_column('E:G', 15)
        sheet.set_column('H:H', 16)