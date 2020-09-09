# -*- coding: utf-8 -*-

import re 
from odoo import http
from odoo.http import request
# import website_support 
# from website_support.controllers.main import SupportTicketController

# class CustomSupportTicketController(SupportTicketController):
class CustomSupportTicketController(http.Controller):
    
    @http.route('/support/ticket/submit', type='http', auth="user", website=True)
    def support_submit_ticket(self, **kw):
        # res = super(CustomSupportTicketController, self).support_submit_ticket(**kw)
        
        person_name = ""
        if http.request.env.user.name != "Public user":
            person_name = http.request.env.user.name
        
        category_access = []
        for category_permission in http.request.env.user.groups_id:
            category_access.append(category_permission.id)
        
        department_categories = http.request.env['department.support'].sudo().search([])
        
        department_access = []
        
        for department_record in department_categories:
            department_access.append(department_record.id)
            
        ticket_categories = http.request.env['website.support.ticket.category'].sudo().search(['|',('access_group_ids','in', category_access), ('access_group_ids','=',False),('department_id', 'in', department_access)])
        
        setting_google_recaptcha_active = request.env['ir.default'].get('website.support.settings', 'google_recaptcha_active')
        setting_google_captcha_client_key = request.env['ir.default'].get('website.support.settings', 'google_captcha_client_key')
        setting_max_ticket_attachments = request.env['ir.default'].get('website.support.settings', 'max_ticket_attachments')
        setting_max_ticket_attachment_filesize = request.env['ir.default'].get('website.support.settings', 'max_ticket_attachment_filesize')
        setting_allow_website_priority_set = request.env['ir.default'].get('website.support.settings', 'allow_website_priority_set')

        return http.request.render('website_support.support_submit_ticket', {'department_id':department_categories,'categories': ticket_categories, 'priorities': http.request.env['website.support.ticket.priority'].sudo().search([]), 'person_name': person_name, 'email': http.request.env.user.email, 'setting_max_ticket_attachments': setting_max_ticket_attachments, 'setting_max_ticket_attachment_filesize': setting_max_ticket_attachment_filesize, 'setting_google_recaptcha_active': setting_google_recaptcha_active, 'setting_google_captcha_client_key': setting_google_captcha_client_key, 'setting_allow_website_priority_set': setting_allow_website_priority_set})
    
    @http.route('/support/help', type="http", auth="public", website=True)
    def support_help(self, **kw):
        """Displays all help groups and thier child help pages"""

        permission_list = []
        group_support = False
        for perm_group in request.env.user.groups_id:
            permission_list.append(perm_group.id)
            if perm_group.category_id.name == 'Website Support':
                group_support = True
                

        help_groups = http.request.env['website.support.help.group'].sudo().search(['|', ('group_ids', '=', False ), ('group_ids', 'in', permission_list), ('website_published','=',True)])

        setting_allow_user_signup = request.env['ir.default'].get('website.support.settings', 'allow_user_signup')

        manager = False
        if request.env['website.support.department.contact'].sudo().search_count([('user_id','=',request.env.user.id)]) == 1:
            manager = True

        return http.request.render('website_support.support_help_pages', {'help_groups': help_groups, 'setting_allow_user_signup': setting_allow_user_signup, 'manager': manager, 'group_support':group_support})
    
    @http.route('/support/subcategories/fetch_department', type='http', auth="public", website=True)
    def support_categories_fetch(self, **kwargs):
        
        ticket_support = int(re.search(r'\d+', kwargs['department']).group())
        hr_support = request.env['department.support'].sudo().search([('name', '=',ticket_support)])    
        category_fields = request.env['website.support.ticket.category'].sudo().search([('department_id', '=', hr_support.id)])
        
        return_string = ""

        if category_fields:
            return_string += "<div class=\"form-group\">\n"
            return_string += "  <label class=\"control-label\" for=\"category\">Category</label>\n"
            return_string += "  <select class=\"form-control\" id=\"category\" name=\"category\">\n"


            for category_field in request.env['website.support.ticket.category'].sudo().search([('department_id', '=', hr_support.id)]):
                return_string += "<option value=\"" + str(category_field.id) + "\">" + category_field.name + "</option>\n"

            return_string += "  </select>\n"
            return_string += "</div>\n"

        return return_string