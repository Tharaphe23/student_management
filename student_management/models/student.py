from odoo import models, fields, api, _


class SchoolStudent(models.Model):
    _name = 'school.student'
    _description = 'Student'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(
        string='Student Name',
        required=True,
        tracking=True
    )

    student_code = fields.Char(
        string='Student ID',
        readonly=True,
        copy=False,
        default='New',
        tracking=True
    )

    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    address = fields.Text(string='Address')

    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], string='Gender', tracking=True,required=True)

    date_of_birth = fields.Date(
        string='Date of Birth'
    )

    registration_date = fields.Date(
        string='Registration Date',
        default=fields.Date.today
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )

    enrollment_ids = fields.One2many(
        'school.enrollment',
        'student_id',
        string='Enrollments'
    )
    
    teacher_user_ids = fields.Many2many(
        'res.users',
        string='Teacher Users',
        compute='_compute_teacher_user_ids',
        store=True
    )

    @api.depends('enrollment_ids.class_id.teacher_user_ids')
    def _compute_teacher_user_ids(self):
        for rec in self:
            rec.teacher_user_ids = rec.enrollment_ids.mapped(
                'class_id.teacher_user_ids'
            )

    @api.model
    def create(self, vals):
        if vals.get('student_code', 'New') == 'New' :
            vals['student_code'] = (
                self.env['ir.sequence'].next_by_code(
                    'school.student'
                ) or 'New'
            )

        return super(SchoolStudent, self).create(vals)