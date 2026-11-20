
{
    'name': 'Student Management System',
    'version': '15.0.1.0.0',
    'summary': 'Manage Students, Payments and Academic Information',
    'category': 'Education',
    'depends': [
        'base',
        'web',
        'mail',
        'report_xlsx',
    ],

    'data': [
        'security/security.xml',
        'security/record_rules.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/semester_cron.xml',
        'views/student_views.xml',
        'views/payment_views.xml',
        'views/class_views.xml',
        'views/enrollment_views.xml',
        'views/subject_views.xml',
        'views/timetable_views.xml',
        'views/teacher_views.xml',
        'views/semester_views.xml',
        'report/payment_report_xlsx.xml',
        'report/payment_report_pdf.xml',
        'wizard/payment_report_wizard.xml',
        'views/menu_views.xml',
        
       


    ],

    'installable': True,
    'application': True,
}
