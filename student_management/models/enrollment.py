from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare

class SchoolEnrollment(models.Model):
    _name = 'school.enrollment'
    _description = 'Student Enrollment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'enrollment_date desc, id desc'

    name = fields.Char(
        string='Enrollment Reference',
        required=True,
        readonly=True,
        copy=False,
        default='New',
        tracking=True
    )

    student_id = fields.Many2one(
    'school.student',
    string='Student',
    required=True,
    tracking=True,
    ondelete='restrict'
)
    
    active=fields.Boolean(string="Active",default=True)

    subject_ids = fields.Many2many(
    'school.subject',
    string='Subjects',
    tracking=True
)

    class_id = fields.Many2one(
        'school.class',
        string='Class',
        required=True,
        tracking=True,
        ondelete='restrict'
    )

    enrollment_date = fields.Date(
        string='Enrollment Date',
        default=fields.Date.today,
        required=True,
        tracking=True
    )

    fee = fields.Monetary(
        string='Course Fee',
        required=True,
        tracking=True
    )

    currency_id = fields.Many2one(
    'res.currency',
    string='Currency',
    default=lambda self: self.env.ref('base.MMK'),
    required=True
)

    payment_ids = fields.One2many(
        'school.payment',
        'enrollment_id',
        string='Payments',
        ondelete='restrict'
    )

    paid_amount = fields.Monetary(
        string='Paid Amount',
        compute='_compute_payment_status',
        store=True
    )
    

    payment_status = fields.Selection([
    ('unpaid', 'Unpaid'),
    ('partial', 'Partial'),
    ('paid', 'Paid'),],
    string='Payment Status',
    compute='_compute_payment_status',
    store=True,
    tracking=True)
    
    enrollment_status = fields.Selection([
    ('pending', 'Pending'),
    ('in_progress', 'In Progress'),
    ('completed', 'Completed'),
], string='Enrollment Status',
   compute='_compute_payment_status',
   store=True,
   tracking=True)

    remaining_amount = fields.Monetary(
    string='Remaining Amount',
    compute='_compute_payment_status',
    store=True,
    currency_field='currency_id'
)
    
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'High'),
        ('3', 'Very High')], string="Priority")
    
    
    @api.depends(
        'fee',
        'currency_id',
        'payment_ids.amount',
        'payment_ids.state'
    )
    
    def _compute_payment_status(self):
        for rec in self:
            confirmed_payments = rec.payment_ids.filtered(
                lambda payment: payment.state == 'confirmed'
            )

            paid = sum(confirmed_payments.mapped('amount'))

            rec.paid_amount = paid
            rec.remaining_amount = max(rec.fee - paid, 0)

            if rec.currency_id and float_compare(
                paid,
                rec.fee,
                precision_rounding=rec.currency_id.rounding
            ) >= 0:
                rec.payment_status = 'paid'
                rec.enrollment_status='completed'
            elif paid > 0:
                rec.payment_status = 'partial'
                rec.enrollment_status='in_progress'
            else:
                rec.payment_status = 'unpaid'
                rec.enrollment_status='pending'
                
    @api.constrains('fee')
    def _check_fee(self):
        for rec in self:
            if rec.fee <= 0:
                raise ValidationError(
                    _('Course fee must be greater than zero.')
                )

    
    @api.onchange('class_id')
    def _onchange_class_id(self):
        self.subject_ids = False 

    @api.onchange('subject_ids')
    def _onchange_subject_ids(self):
        self.fee = sum(self.subject_ids.mapped('fee'))


    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = (
                self.env['ir.sequence'].next_by_code('school.enrollment')
                or 'New'
            )
        return super(SchoolEnrollment, self).create(vals)


    def action_open_timetable(self):
        self.ensure_one()

        if self.payment_status == 'unpaid':
            raise UserError(
                _('Payment is not completed. '
                  'Please complete full payment first.')
            )

        return {
            'type': 'ir.actions.act_window',
            'name': _('Student Timetable'),
            'res_model': 'school.timetable',
            'view_mode': 'tree,form',
            'domain': [
                ('class_id', '=', self.class_id.id)
            ],
            'target': 'current',
        }
        
    def unlink(self):
        raise UserError(_(
        "You cannot delete this enrollments record."
    ))
        
    def write(self, vals):
        if vals.get('active') is False:
            for record in self:
                if record.enrollment_status != 'completed':
                    raise UserError(
                        "Only completed enrollments can be archived."
                    )

        return super().write(vals)