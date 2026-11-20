from odoo import http
from odoo.http import request
from odoo_rest_framework import response_json

class StudentAPI(http.Controller):

    # =====================================
    # GET - Read All Students
    # =====================================
    @http.route(
        '/api/students',
        type='http',
        auth='public',
        methods=['GET'],
        csrf=False
    )
    def get_students(self, **kwargs):

        # Get Student Records
        students = request.env['school.student'].sudo().search([])

        # Prepare Student Data
        data = []

        for student in students:

            data.append({
                'id': student.id,
                'student_code': student.student_code or '',
                'name': student.name or '',
                'phone': student.phone or '',
                'email': student.email or '',
                'gender': student.gender or '',
                'class': student.class_id.name if student.class_id else ''
            })

        return response_json(
            success=True,
            message="Students fetched successfully",
            data=data
        )

    # =====================================
    # POST - Create Student
    # =====================================
    @http.route(
        '/api/students/create',
        type='http',
        auth='public',
        methods=['POST'],
        csrf=False
    )
    def create_student(self, **kwargs):

        # Get Form Data
        name = request.httprequest.form.get('name')
        phone = request.httprequest.form.get('phone')
        email = request.httprequest.form.get('email')
        gender = request.httprequest.form.get('gender')
        class_name = request.httprequest.form.get('class_name')

        # Search Class
        school_class = request.env['school.class'].sudo().search([
            ('name', '=', class_name)
        ], limit=1)

        # Create Student
        student = request.env['school.student'].sudo().create({
            'name': name,
            'phone': phone,
            'email': email,
            'gender': gender,
            'class_id': school_class.id if school_class else False
        })

        # Prepare Student Data
        data = {
            'id': student.id,
            'student_code': student.student_code or '',
            'name': student.name or '',
            'phone': student.phone or '',
            'email': student.email or '',
            'gender': student.gender or '',
            'class': student.class_id.name if student.class_id else ''
        }

        return response_json(
            success=True,
            message="Student created successfully",
            data=data
        )

    # =====================================
    # PUT - Full Update Student
    # =====================================
    @http.route(
        '/api/students/<int:student_id>',
        type='http',
        auth='public',
        methods=['PUT'],
        csrf=False
    )
    def update_student(self, student_id, **kwargs):

        # Get Student by ID
        student = request.env['school.student'].sudo().browse(student_id)

        # Check Student Exists
        if not student.exists():
            return response_json(
                success=False,
                message="Student Not Found!",
                data=None
            )

        # Get Form Data
        name = request.httprequest.form.get('name')
        phone = request.httprequest.form.get('phone')
        email = request.httprequest.form.get('email')
        gender = request.httprequest.form.get('gender')
        class_name = request.httprequest.form.get('class_name')

        # Search Class
        school_class = request.env['school.class'].sudo().search([
            ('name', '=', class_name)
        ], limit=1)

        # Update Student
        student.write({
            'name': name,
            'phone': phone,
            'email': email,
            'gender': gender,
            'class_id': school_class.id if school_class else False
        })

        # Prepare Updated Data
        data = {
            'id': student.id,
            'student_code': student.student_code or '',
            'name': student.name or '',
            'phone': student.phone or '',
            'email': student.email or '',
            'gender': student.gender or '',
            'class': student.class_id.name if student.class_id else ''
        }

        return response_json(
            success=True,
            message="Student updated successfully",
            data=data
        )

    # =====================================
    # PATCH - Partially Update Student
    # =====================================
    @http.route(
        '/api/students/id/<int:student_id>',
        type='http',
        auth='public',
        methods=['PATCH'],
        csrf=False
    )
    def update_student_patch(self, student_id, **kwargs):

        # Get Student by ID
        student = request.env['school.student'].sudo().browse(student_id)

        # Check Student Exists
        if not student.exists():
            return response_json(
                success=False,
                message="Student Not Found!",
                data=None
            )

        # Prepare Update Values
        update_values = {}

        # Get Form Data
        name = request.httprequest.form.get('name')
        phone = request.httprequest.form.get('phone')
        email = request.httprequest.form.get('email')
        gender = request.httprequest.form.get('gender')
        class_name = request.httprequest.form.get('class_name')

        # Update Name
        if name is not None:
            update_values['name'] = name

        # Update Phone
        if phone is not None:
            update_values['phone'] = phone

        # Update Email
        if email is not None:
            update_values['email'] = email

        # Update Gender
        if gender is not None:
            update_values['gender'] = gender

        # Update Class
        if class_name is not None:

            school_class = request.env['school.class'].sudo().search([
                ('name', '=', class_name)
            ], limit=1)

            if not school_class:
                return response_json(
                    success=False,
                    message="Class Not Found!",
                    data=None
                )

            update_values['class_id'] = school_class.id

        # Check Data Provided
        if not update_values:
            return response_json(
                success=False,
                message="No Data Provided!",
                data=None
            )

        # Update Student
        student.write(update_values)

        # Prepare Updated Data
        data = {
            'id': student.id,
            'student_code': student.student_code or '',
            'name': student.name or '',
            'phone': student.phone or '',
            'email': student.email or '',
            'gender': student.gender or '',
            'class': student.class_id.name if student.class_id else ''
        }

        return response_json(
            success=True,
            message="Student partially updated successfully",
            data=data
        )

    # =====================================
    # DELETE - Delete Student
    # =====================================
    @http.route(
        '/api/students/<int:student_id>',
        type='http',
        auth='public',
        methods=['DELETE'],
        csrf=False
    )
    def delete_student(self, student_id, **kwargs):

        # Get Student by ID
        student = request.env['school.student'].sudo().browse(student_id)

        # Check Student Exists
        if not student.exists():
            return response_json(
                success=False,
                message="Student Not Found!",
                data=None
            )

        # Delete Student
        student.unlink()

        # Prepare Response Data
        data = {
            'id': student_id
        }

        return response_json(
            success=True,
            message="Student deleted successfully",
            data=data
        )