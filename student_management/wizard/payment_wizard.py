from odoo import models, fields, _
from odoo.exceptions import ValidationError


class StudentPaymentWizard(models.TransientModel):
    _name = 'student.payment.wizard'
    _description = 'Student Payment Wizard'

    enrollment_id = fields.Many2one(
        'school.enrollment',
        string='Enrollment',
        required=True
    )

    student_id = fields.Many2one(
        'school.student',
        string='Student',
        related='enrollment_id.student_id',
        readonly=True
    )

    total_fee = fields.Monetary(
        string='Total Fee',
        related='enrollment_id.fee',
        readonly=True
    )

    amount = fields.Monetary(
        string='Payment Amount',
        required=True
    )

    currency_id = fields.Many2one(
        'res.currency',
        related='enrollment_id.currency_id',
        readonly=True
    )

    payment_date = fields.Date(
        string='Payment Date',
        default=fields.Date.today,
        required=True
    )

    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('bank', 'Bank Transfer'),
        ('online', 'Online Payment'),
    ], string='Payment Method', required=True, default='cash')

    def action_create_payment(self):
        self.ensure_one()

        if self.amount <= 0:
            raise ValidationError(_('Payment amount must be greater than zero.'))

        if self.amount != self.total_fee:
            raise ValidationError(
                _('Only full payment is allowed. Please enter the full fee.')
            )

        payment = self.env['school.payment'].create({
            'enrollment_id': self.enrollment_id.id,
            'amount': self.amount,
            'payment_date': self.payment_date,
            'payment_method': self.payment_method,
        })

        payment.action_confirm()

        return {
            'type': 'ir.actions.act_window',
            'name': _('Payment'),
            'res_model': 'school.payment',
            'view_mode': 'form',
            'res_id': payment.id,
            'target': 'current',
        }