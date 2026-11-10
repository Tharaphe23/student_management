from odoo import models, fields, api


class SchoolClass(models.Model):
    _name = 'school.class'
    _description = 'Class'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    # Basic Information
    name = fields.Char(
        string='Class Name',
        required=True,
        tracking=True
    )

    class_code = fields.Char(
        string='Class Code',
        readonly=True,
        copy=False,
        default='New'
    )

    capacity = fields.Integer(
        string='Student Capacity'
    )

    description = fields.Text(
        string='Description'
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )

    # Relationships
    subject_ids = fields.Many2many(
        'school.subject',
        relation='school_class_subject_rel',
        column1='class_id',
        column2='subject_id',
        string='Subjects'
    )

    student_ids = fields.One2many(
        'school.enrollment',
        'class_id',
        string='Student Enrollments'
    )

    timetable_ids = fields.One2many(
        'school.timetable',
        'class_id',
        string='Timetable'
    )
    
    teacher_user_ids = fields.Many2many(
        'res.users',
        string='Teacher Users',
        compute='_compute_teacher_user_ids',
        store=True
    )

    @api.depends('timetable_ids.teacher_id.user_id')
    def _compute_teacher_user_ids(self):
        for rec in self:
            rec.teacher_user_ids = rec.timetable_ids.mapped(
                'teacher_id.user_id'
            )

    @api.model
    def create(self, vals):
        if vals.get('class_code', 'New') == 'New':
            vals['class_code'] = (
                self.env['ir.sequence'].next_by_code('school.class')
                or 'New'
            )
        return super(SchoolClass, self).create(vals)
