# -*- coding: utf-8 -*-

import qrcode
import base64
import logging
_logger = logging.getLogger(__name__)
from datetime import datetime
from odoo import api, fields, tools, models, _
from odoo.exceptions import ValidationError
from odoo.http import request

import io
try:
    import qrcode

except ImportError:
    _logger.debug('ImportError')



class AssetMove(models.Model):
    _name = "asset.move"
    _description = "Asset Move" 
    _inherit = ['mail.thread','mail.activity.mixin']
    _order = 'id desc'
    
    name = fields.Char(string='Name', default="_New", copy=False, readonly=True)
    from_loc_id = fields.Many2one('asset.location', string='From Location', required=True)
    asset_id = fields.Many2one('account.asset.asset', string='Asset', required=True)
    to_loc_id = fields.Many2one('asset.location', string='To Location', required=True)
    move_date = fields.Datetime("Move Date",track_visibility='onchange')
    state = fields.Selection([
            ('draft', 'Draft'),
            ('done', 'Done'),
            ('cancel','Cancel')], string='State',track_visibility='onchange', default='draft', copy=False)
    qr_code = fields.Binary("QR Code", attachment=True, store=True, compute="_generate_qr_code", readonly=True)
    
    @api.model
    def create(self, vals):
        if not vals:
            vals = {}
        vals['name'] = self.env['ir.sequence'].\
            next_by_code('asset.move') or '_New'
        result = super(AssetMove, self).create(vals)
        if vals.get('from_loc_id', False) or vals.get('to_loc_id', False):
            if result.from_loc_id == result.to_loc_id:
                raise ValidationError(_("From location and to location must be different."))
        if vals.get('asset_id',False):
            if result.asset_id.location_asset_id != result.from_loc_id:
                raise ValidationError(_("Current location and from location must be same while creating asset."))
            
        asset_obj = self.env['asset.move'].search([('state', '=', 'draft'), ('asset_id', '=', result.asset_id.id),('id', '!=', result.id)])
        if asset_obj:
            raise ValidationError(_("%s is at another operation move. Please cancel or confirm the operation.") %(result.asset_id.name))
        return result
    
    @api.multi
    def _get_current_url(self):
        url = request.httprequest.host_url
        get_id = self.id
        model = self._name
        menu_id = self.env['ir.ui.menu'].sudo().search([('name','=','Accounting'), ('parent_id','=',False)])
        menu_id = int(menu_id)
        current_url = url+"web?#id=%s"%(get_id)+"&model=%s"%(model)+"&view_type=form&menu_id=%s"%(menu_id)
        
        return current_url
        
    @api.multi
    def write(self, vals):
        result = super(AssetMove, self).write(vals)
        if vals.get('from_loc_id', False) or vals.get('to_loc_id', False):
            for move in self:
                if move.from_loc_id == move.to_loc_id:
                    raise ValidationError(_("From location and to location must be different."))
        if vals.get('asset_id',False):
            for asset_obj in self:
                if asset_obj.asset_id.location_asset_id != asset_obj.from_loc_id:
                    raise ValidationError(_("Current location and from location must be same while creating asset."))
        return result
    
    @api.multi
    def action_move(self):
        for move in self:
            while move.state == 'draft':
                move.asset_id.location_asset_id = move.to_loc_id and move.to_loc_id.id or False
                move.state = 'done'
                move.move_date = datetime.now()
            
                if move.asset_id.is_equipment:
                    equipments = self.env['maintenance.equipment'].search([('id', '=', int(move.asset_id.equipment_id))])
                    for equipment in equipments: 
                        equipment.write({'location_asset_id': move.to_loc_id.id})
#         return True
    
    @api.multi
    def action_cancel(self):
        for move in self:
            while move.state == 'draft':
                move.state = 'cancel'
        
    
    @api.one
    @api.depends('name')
    def _generate_qr_code(self):
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=20, border=4)
        if self._get_current_url():
            qr.add_data(self._get_current_url())
            qr.make(fit=True)
            img = qr.make_image()
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            qrcode_img = base64.b64encode(buffer.getvalue())
            self.update({'qr_code': qrcode_img,})
    
    @api.multi
    def unlink(self):
        for record in self:
            if record.state != 'draft':
                raise ValidationError(_('You cannot delete this data !!!'))
            return super(AssetMove, self).unlink()
