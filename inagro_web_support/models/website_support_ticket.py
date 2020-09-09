# -*- coding: utf-8 -*-

from odoo import models, fields, api,_, exceptions
from docutils.nodes import field
from datetime import datetime
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
# from builtins import True
import logging

_logger = logging.getLogger(__name__)

class DepartementSupport(models.Model):
    
    _name = 'department.support'
    _description = "Department Support"
    _rec_name = "name"
    
    name = fields.Many2one('hr.department', string = 'Department', store=True)
    
    
class inheritWebsiteSupportTicketCategory(models.Model):

    _inherit = "website.support.ticket.category"
    
    department_id = fields.Many2one('department.support', string ='Category Department')

class inherit_WebsiteSupportTicket(models.Model):
     
    _inherit = 'website.support.ticket'
     
    department_id = fields.Many2one('department.support', string ='Department', related="category_id.department_id", store=True)
    employee_id = fields.Many2one('hr.employee', string='User',store=True)
    dept_rel_id = fields.Many2one('hr.department', string='Department Related', related='department_id.name')
#     closed_rel_id = fields.Many2one('hr.employee', string='Closed by Related')
    time_response = fields.Float('Time Response')       
    
    @api.onchange('employee_id')
    def onchange_user_id(self):
        if self.employee_id:
            self.user_id = self.employee_id.user_id
            
#     @api.onchange('closed_rel_id')
#     def onchange_closedby_id(self):
#         if self.closed_rel_id:
#             self.closed_by_id = self.closed_rel_id.user_id
            
            
class WebsiteSupportTicketCompose(models.Model):

    _inherit = "website.support.ticket.compose"
    
    attachment_ids = fields.Many2many('ir.attachment', 'mail_ticket_attachment_rel', 'compose_id', 'attachment_id', 'Attachment File')
    
    @api.one
    def send_reply(self):

        #Change the approval state before we send the mail
        if self.approval:
            #Change the ticket state to awaiting approval
            awaiting_approval_state = self.env['ir.model.data'].get_object('website_support','website_ticket_state_awaiting_approval')
            self.ticket_id.state_id = awaiting_approval_state.id

            #One support request per ticket...
            self.ticket_id.planned_time = self.planned_time
            self.ticket_id.approval_message = self.body
            self.ticket_id.sla_active = False
            

        
        if not self.ticket_id.sla_id or not self.ticket_id.sla_rule_id:
            self.ticket_id.sla_id = sla = self.env['website.support.sla'].search([('id', '=', 1)], limit=1)
            self.ticket_id.sla_rule_id = sla_rule = self.env['website.support.sla.rule'].search([('id', '=', 1)], limit=1)
            if not sla or not sla_rule:
                raise ValidationError(_('You must first select SLA and SLA Rule.'))

        #Send email
        values = {}

        setting_staff_reply_email_template_id = self.env['ir.default'].get('website.support.settings', 'staff_reply_email_template_id')

        if setting_staff_reply_email_template_id:
            email_wrapper = self.env['mail.template'].browse(setting_staff_reply_email_template_id)

        values = email_wrapper.generate_email([self.id])[self.id]
        values['model'] = "website.support.ticket"
        values['res_id'] = self.ticket_id.id
        send_mail = self.env['mail.mail'].create(values)
        send_mail.send()

        #Add to the message history to keep the data clean from the rest HTML
        self.env['website.support.ticket.message'].create({'ticket_id': self.ticket_id.id, 'by': 'staff', 'content':self.body.replace("<p>","").replace("</p>","")})

        #Post in message history
        #self.ticket_id.message_post(body=self.body, subject=self.subject, message_type='comment', subtype='mt_comment')

        if self.approval:
            #Also change the approval
            awaiting_approval = self.env['ir.model.data'].get_object('website_support','awaiting_approval')
            self.ticket_id.approval_id = awaiting_approval.id
        else:
            #Change the ticket state to staff replied
            staff_replied = self.env['ir.model.data'].get_object('website_support','website_ticket_state_staff_replied')
            if not self.ticket_id.close_time:
                self.ticket_id.state_id = staff_replied.id            
            if self.ticket_id.state_id.id == 2:
                if self.ticket_id.time_response == 0:
                    support_ticket = self.env['website.support.ticket'].search([('id', '=', self.ticket_id.id)], limit=1)
                    self.ticket_id.time_response =  (support_ticket.write_date - support_ticket.create_date).total_seconds()/60
                    self.ticket_id.sla_active = True
                    # self.ticket_id.sla_id = sla.id
                    # self.ticket_id.sla_rule_id = sla_rule.id
                
             
                
                
    
    

    