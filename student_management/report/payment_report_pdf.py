from odoo import models

class PaymentReportPdf(models.AbstractModel):
    _name = 'report.student_management.payment_report_pdf'
    _description = 'Payment PDF Report'

    def _get_report_values(self, docids, data=None):
        data = data or {}

        payment_ids = data.get('payment_ids') or docids

        payments = self.env['school.payment'].browse(
            payment_ids
        ).exists()

        return {
            'doc_ids': payments.ids,
            'doc_model': 'school.payment',
            'docs': payments,

            'date_from': data.get('date_from') or 'All',
            'date_to': data.get('date_to') or 'All',
            'payment_method': data.get('payment_method_label') or 'All',
            'payment_state': data.get('state_label') or 'All',

            'total_amount': sum(payments.mapped('amount')),
        }