from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class SchoolTimetable(models.Model):
    _name = 'school.timetable'
    _description = 'Class Timetable'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'day_of_week, start_time'

    name = fields.Char(
        string='Session Name',
        required=True,
        tracking=True
    )

    class_id = fields.Many2one(
        'school.class',
        string='Class',
        required=True,
        tracking=True,
        ondelete='restrict'
    )
    
    semester_id = fields.Many2one(
    'school.semester',
    string='Semester',
    required=True,
    tracking=True,
    ondelete='restrict'
    )

    teacher_id = fields.Many2one(
        'school.teacher',
        string='Teacher',
        required=True,
        tracking=True,
        ondelete='restrict'
    )

    subject_id = fields.Many2one(
        'school.subject',
        string='Subject',
        required=True,
        tracking=True,
        ondelete='restrict'
    )
    
    day_of_week = fields.Selection([
    ('monday', 'Monday'),
    ('tuesday', 'Tuesday'),
    ('wednesday', 'Wednesday'),
    ('thursday', 'Thursday'),
    ('friday', 'Friday'),
    ('saturday', 'Saturday'),
    ('sunday', 'Sunday'),
], string='Day', required=True)

    start_time = fields.Float(
        string='Start Time',
        required=True
    )

    end_time = fields.Float(
        string='End Time',
        required=True
    )

    room = fields.Char(
        string='Room',
        tracking=True
    )

    state = fields.Selection([
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='scheduled',
       required=True, tracking=True)

    @api.constrains(
    'day_of_week',
    'start_time',
    'end_time',
    'teacher_id',
    'class_id',
    'room',
    'state'
)
    def _check_schedule(self):
        for rec in self:
            if rec.start_time >= rec.end_time:
                raise ValidationError(_(
                    'End Time must be later than Start Time.'
                ))

            if rec.state == 'cancelled':
                continue

            domain = [
                ('id', '!=', rec.id),
                ('day_of_week', '=', rec.day_of_week),
                ('state', '!=', 'cancelled'),
                ('start_time', '<', rec.end_time),
                ('end_time', '>', rec.start_time),
            ]

            conflicts = self.search(domain)

            if conflicts.filtered(
                lambda s: s.teacher_id == rec.teacher_id
            ):
                raise ValidationError(_(
                    'This teacher already has another class '
                    'at this time.'
                ))

            if conflicts.filtered(
                lambda s: s.class_id == rec.class_id
            ):
                raise ValidationError(_(
                    'This class already has another session '
                    'at this time.'
                ))

            if rec.room and conflicts.filtered(
                lambda s: s.room == rec.room
            ):
                raise ValidationError(_(
                    'This room is already occupied.'
                ))
                
    def unlink(self):
        raise UserError(_(
        "You cannot delete this timetable record."
    ))