from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare


class SchoolPayment(models.Model):
    _name = 'school.payment'
    _description = 'Student Payment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'payment_date desc, id desc'

    name = fields.Char(
        string='Payment Reference',
        required=True,
        readonly=True,
        copy=False,
        default='New',
        tracking=True
    )

    enrollment_id = fields.Many2one(
        'school.enrollment',
        string='Enrollment',
        required=True,
        tracking=True,
        ondelete='restrict'
    )

    student_id = fields.Many2one(
        'school.student',
        string='Student',
        related='enrollment_id.student_id',
        store=True,
        readonly=True
    )

    amount = fields.Monetary(
        string='Amount',
        required=True,
        tracking=True
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='enrollment_id.currency_id',
        store=True,
        readonly=True
    )

    payment_date = fields.Date(
        string='Payment Date',
        default=fields.Date.today,
        required=True,
        tracking=True
    )

    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('bank', 'Bank Transfer'),
        ('online', 'Online Payment'),
    ], string='Payment Method', required=True, default='cash')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True, required=True)

    @api.constrains('amount')
    def _check_amount(self):
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError(
                    _('Payment amount must be greater than zero.')
                )

    def action_confirm(self):
        for rec in self:

            if rec.state != 'draft':
                raise UserError(
                    _('Only draft payments can be confirmed.')
                )

            if not rec.enrollment_id:
                raise UserError(_('Please select an enrollment.'))

            if rec.amount <= 0:
                raise UserError(
                    _('Payment amount must be greater than zero.')
                )

            enrollment = rec.enrollment_id
            currency = rec.currency_id

            existing_payments = self.search([
                ('enrollment_id', '=', enrollment.id),
                ('state', '=', 'confirmed'),
                ('id', '!=', rec.id)
            ])

            payment_count = len(existing_payments)

            paid_amount = sum(
                existing_payments.mapped('amount')
            )

            remaining_amount = enrollment.fee - paid_amount

            if payment_count >= 2:
                raise UserError(
                    _('Payment is already completed or the payment limit has been reached.')
                )

            if float_compare(
                remaining_amount,
                0,
                precision_rounding=currency.rounding
            ) <= 0:
                raise UserError(
                    _('This enrollment has already been fully paid.')
                )

            if float_compare(
                rec.amount,
                remaining_amount,
                precision_rounding=currency.rounding
            ) > 0:
                raise UserError(
                    _('Payment amount cannot exceed the remaining amount. '
                    'Remaining amount is %s.') % remaining_amount
                )

            if payment_count == 1 and float_compare(
                rec.amount,
                remaining_amount,
                precision_rounding=currency.rounding
            ) != 0:
                raise UserError(
                    _('The second payment must be the exact remaining amount: %s.')
                    % remaining_amount
                )

            rec.write({'state': 'confirmed'})

        return True

    def action_cancel(self):
        for rec in self:
            if rec.state == 'confirmed':
                raise UserError(
                    _('Confirmed payments cannot be cancelled directly.')
                )

            if rec.state == 'cancelled':
                raise UserError(
                    _('This payment is already cancelled.')
                )

            rec.write({'state': 'cancelled'})

        return True
    
    #reference auto generate
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = (
                self.env['ir.sequence'].next_by_code('school.payment')
                or 'New'
            )
        return super(SchoolPayment, self).create(vals)


    def write(self, vals):
        protected_fields = {
            'enrollment_id',
            'amount',
            'payment_date',
            'payment_method',
        }

        for rec in self:
            if rec.state == 'confirmed' and protected_fields.intersection(vals):
                raise UserError(
                    _('Confirmed payment information cannot be modified.')
                )
            if rec.state != 'draft' and 'state' in vals:
                raise UserError(
                    _('Payment status must be changed using the payment actions.')
                )

        return super(SchoolPayment, self).write(vals)
    
    def unlink(self):
        raise UserError(_(
        "You cannot delete this payment record."
    ))