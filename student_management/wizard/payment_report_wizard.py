
from odoo import models, fields, _
from odoo.exceptions import UserError

class PaymentReportWizard(models.TransientModel):
    _name = 'school.payment.report.wizard'
    _description = 'Payment Report Wizard'

    date_from = fields.Date(
        string='Payment Date From'
    )

    date_to = fields.Date(
        string='Payment Date To'
    )

    payment_method = fields.Selection([
        ('all', 'All'),
        ('cash', 'Cash'),
        ('bank', 'Bank Transfer'),
        ('online', 'Online Payment'),
    ],
        string='Payment Method',
        default='all',
        required=True
    )

    state = fields.Selection([
        ('all', 'All'),
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ],
        string='Status',
        default='all',
        required=True
    )

    # Get Search Domain
    def _get_domain(self):
        self.ensure_one()

        domain = []

        if self.date_from:
            domain.append(
                ('payment_date', '>=', self.date_from)
            )

        if self.date_to:
            domain.append(
                ('payment_date', '<=', self.date_to)
            )

        if self.payment_method != 'all':
            domain.append(
                ('payment_method', '=', self.payment_method)
            )

        if self.state != 'all':
            domain.append(
                ('state', '=', self.state)
            )

        return domain

    # Get Payment Records
    def _get_payments(self):
        self.ensure_one()

        if (
            self.date_from
            and self.date_to
            and self.date_from > self.date_to
        ):
            raise UserError(
                _('"Date From" must not be later than "Date To".')
            )

        payments = self.env['school.payment'].search(
            self._get_domain(),
            order='payment_date, id'
        )

        if not payments:
            raise UserError(
                _('No payments found for the selected filters.')
            )

        return payments
    
    def _get_report_data(self, payments):
        self.ensure_one()

        method_label = dict(
            self._fields['payment_method'].selection
        )
        state_label = dict(
            self._fields['state'].selection
        )

        return {
            'payment_ids': payments.ids,
            'date_from': str(self.date_from) if self.date_from else '',
            'date_to': str(self.date_to) if self.date_to else '',
            'payment_method': self.payment_method,
            'payment_method_label': method_label.get(
                self.payment_method, 'All'
            ),
            'state': self.state,
            'state_label': state_label.get(self.state, 'All'),
        }

    # # Excel Report
    # def action_print_xlsx(self):
    #     self.ensure_one()

    #     self._get_payments()

    #     return self.env.ref(
    #         'student_management.action_payment_report_xlsx'
    #     ).report_action(self)

    # # PDF Report
    # def action_print_pdf(self):
    #     self.ensure_one()

    #     self._get_payments()

    #     return self.env.ref(
    #         'student_management.action_payment_report_pdf'
    #     ).report_action(self)
    
    
    def action_print_xlsx(self):
        self.ensure_one()

        payments = self._get_payments()
        data = self._get_report_data(payments)

        return self.env.ref(
            'student_management.action_payment_report_xlsx'
        ).report_action(payments, data=data)
        
    def action_print_pdf(self):
        self.ensure_one()

        payments = self._get_payments()
        data = self._get_report_data(payments)

        return self.env.ref(
            'student_management.action_payment_report_pdf'
        ).report_action(payments, data=data)

    