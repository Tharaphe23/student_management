from odoo import models, fields,_
from odoo.exceptions import ValidationError, UserError


class SchoolSubject(models.Model):
    _name = 'school.subject'
    _description = 'Subject'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    # Basic Information
    name = fields.Char(
        string='Subject Name',
        required=True,
        tracking=True
    )

    subject_code = fields.Char(
        string='Subject Code',
        copy=False
    )

    description = fields.Text(
        string='Description'
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )

    # Relationships
    teacher_ids = fields.Many2many(
        'school.teacher',
        relation='school_teacher_subject_rel',
        column1='subject_id',
        column2='teacher_id',
        string='Teachers'
    )

    class_ids = fields.Many2many(
        'school.class',
        relation='school_class_subject_rel',
        column1='subject_id',
        column2='class_id',
        string='Classes'
    )

    timetable_ids = fields.One2many(
        'school.timetable',
        'subject_id',
        string='Timetable'
    )

    fee = fields.Monetary(
        string='Course Fee',
        required=True,
        default=0.0,
        tracking=True
    )

    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.ref('base.MMK'),
        required=True
    )
    
    def unlink(self):
        for record in self:
            if record.timetable_ids:
                raise UserError(_(
                    "Cannot delete a subject linked to a timetable. Archive instead."
                ))

        return super().unlink()
