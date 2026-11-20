from odoo import models, fields, api,_
from odoo.exceptions import ValidationError, UserError


class SchoolTeacher(models.Model):
    _name = 'school.teacher'
    _description = 'Teacher'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(
        string='Teacher Name',
        required=True,
        tracking=True
    )

    teacher_code = fields.Char(
        string='Teacher ID',
        readonly=True,
        copy=False,
        default='New'
    )
    image=fields.Image(string="Image")

    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')

    specialization = fields.Char(
        string='Specialization'
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )

    subject_ids = fields.Many2many(
        'school.subject',
        relation='school_teacher_subject_rel',
        column1='teacher_id',
        column2='subject_id',
        string='Subjects'
    )


    timetable_ids = fields.One2many(
        'school.timetable',
        'teacher_id',
        string='Timetable'
    )
    #access rights လုပ်ဖို့
    user_id = fields.Many2one(
    'res.users',
    string='Related User',
    domain=[('share', '=', False)],
    ondelete='restrict'
)
    # teacher gmail auto ဝင်ဖို့
    @api.onchange('user_id')
    def _onchange_user_id(self):
        if self.user_id:
            self.email = (
                self.user_id.email
                or self.user_id.partner_id.email
                or self.user_id.login
            )

    @api.model
    def create(self, vals):
        if vals.get('teacher_code', 'New') == 'New':
            vals['teacher_code'] = (
                self.env['ir.sequence'].next_by_code('school.teacher')
                or 'New'
            )
        return super(SchoolTeacher, self).create(vals)

    
    def unlink(self):
        for record in self:
            if record.timetable_ids:
                raise UserError(_(
                    "Cannot delete a teacher linked to a timetable. Archive instead."
                ))

        return super().unlink()