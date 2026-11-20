from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class SchoolSemester(models.Model):
    _name = 'school.semester'
    _description = 'Academic Semester'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_date desc, id desc'

    name = fields.Char(
        string='Semester Name',
        required=True,
        tracking=True
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )

    start_date = fields.Date(
        string='Start Date',
        required=True,
        tracking=True
    )

    end_date = fields.Date(
        string='End Date',
        required=True,
        tracking=True
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ], string='Status',
       default='draft',
       tracking=True)

    @api.constrains('start_date', 'end_date')
    def _check_semester_dates(self):
        for rec in self:
            if rec.start_date and rec.end_date:
                if rec.end_date < rec.start_date:
                    raise ValidationError(
                        _('End Date must be after Start Date.')
                    )

    @api.model
    def create(self, vals):
        record = super(SchoolSemester, self).create(vals)
        record._update_status_from_dates()
        return record

    def write(self, vals):
        if 'active' in vals and not vals['active']:
            if any(rec.state == 'active' for rec in self):
                raise UserError(_(
                    'An active semester cannot be archived. '
                    'Please wait until it is completed.'
                ))
        result = super(SchoolSemester, self).write(vals)
        self._update_status_from_dates()
        return result

    def _update_status_from_dates(self):
        today = fields.Date.today()

        for rec in self:
            if rec.end_date and rec.end_date <= today:
                new_state = 'completed'

            elif rec.start_date and rec.start_date <= today:
                new_state = 'active'

            else:
                new_state = 'draft'

            if rec.state != new_state:
                super(SchoolSemester, rec).write({
                    'state': new_state
                })

            # Update related Timetable
            if new_state == 'completed':
                timetables = self.env['school.timetable'].search([
                    ('semester_id', '=', rec.id),
                    ('state', '!=', 'cancelled')
                ])

                timetables.write({
                    'state': 'completed'
                })

    @api.model
    def _cron_update_semester_status(self):
        semesters = self.search([])
        semesters._update_status_from_dates()
        
    @api.constrains('semester_id', 'state')
    def _check_semester_not_completed(self):
        for rec in self:
            if rec.state == 'scheduled' and rec.semester_id.state == 'completed':
                raise ValidationError(_(
                    'Cannot schedule a session in a completed semester.'
                ))