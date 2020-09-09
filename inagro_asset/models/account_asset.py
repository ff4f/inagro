# -*- coding: utf-8 -*-

import qrcode
import base64
import logging
_logger = logging.getLogger(__name__)

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.http import request

import io
try:
    import qrcode

except ImportError:
    _logger.debug('ImportError')

class inherit_accountAsset(models.Model):
    _inherit = 'account.asset.asset'

    location_asset_id = fields.Many2one('asset.location',string="Asset Location",required=True)
    qr_code = fields.Binary("QR Code", attachment=True, store=True, compute="_generate_qr_code", readonly=True)
#     barcode = fields.Char("Barcode")
    
    @api.multi
    def _get_current_url(self):
        url = request.httprequest.host_url
        get_id = self.id
        model = self._name
        menu_id = self.env['ir.ui.menu'].sudo().search([('name','=','Accounting'), ('parent_id','=',False)])
        menu_id = int(menu_id)
        current_url = url+"web?#id=%s"%(get_id)+"&model=%s"%(model)+"&view_type=form&menu_id=%s"%(menu_id)
        
        return current_url
    
    @api.one
    @api.depends('name')
    def _generate_qr_code(self):
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=20, border=4)
        if self._get_current_url() :
            qr.add_data(self._get_current_url())
            qr.make(fit=True)
            img = qr.make_image()
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            qrcode_img = base64.b64encode(buffer.getvalue())
            self.update({'qr_code': qrcode_img,})
    
    
    @api.model
    def create(self, vals):
        res = super(inherit_accountAsset, self).create(vals)
        return res
    
    @api.multi
    def write(self, vals):
        
        res = super(inherit_accountAsset, self).write(vals)
        return res
    
    
    @api.multi
    def validate(self):
        for asset in self:
            if asset.is_equipment:
                equipments = self.env['maintenance.equipment'].search([('id', '=', int(asset.equipment_id))])
                for equipment in equipments:
                    equipment.write({'location_asset_id': asset.location_asset_id.id})
                    
        res = super(inherit_accountAsset, self).validate()
        return res    
    
    @api.multi
    def create_move(self):
        default_asset_id = self.env.context.get('default_asset_id', self.id)
        if default_asset_id:
            ctx = {'default_asset_id':default_asset_id, 'default_from_loc_id': self.location_asset_id.id}
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'asset.move',
                'context': ctx,
            }
#         move_obj = self.env['asset.move']
#         
#         for move in self:
#             move_vals = {
#                 'asset_id' :move.id,
#                 'from_loc_id' : move.location_asset_id.id,
#                 'to_loc_id' : False,
#                 }
#             move_obj.create(move_vals)
#             
#         return True
#     
    @api.multi
    def to_move(self):
        # print('to folio')
        # print('reservation_id ',self.id)
        return {
                'name': ('Asset Move'),
                'view_type':'form',
                'view_mode':'tree,form',
                'view_id': False,
                'res_model':'asset.move',
                'type':'ir.actions.act_window',
#                 'context':{"folio": True},
                'domain': [('asset_id', '=', self.id)],
                'target':'current'
            }
    
    
    
class AssetLocation(models.Model):
    _name = "asset.location"
    _description = "Asset Location" 
    
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    asset_ids = fields.One2many('account.asset.asset','location_asset_id', string='Assets',readonly=True)
    
    
class iinherit_asset_MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'
    
    location_asset_id = fields.Many2one('asset.location',string="Used in Location")