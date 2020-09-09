# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from datetime import datetime

class inherit_MrpProduction(models.Model):
    """ Manufacturing Orders """
    _inherit = 'mrp.production'
    
#     @api.one
#     @api.onchange('bom_id')
#     def _onchange_move_raw_ids(self):
#         print("Testtt")
#         new_lines =[]
#         for record in self.bom_id.bom_line_ids:
#             vals = record.read(['product_id','product_qty','product_uom_id'])[0]
            
    
#     @api.model
#     def create(self, values):
#         values['sequence_char'] = self.env['ir.sequence'].next_by_code('increament_sequence') or _('New')
#         res = super(inherit_MrpProduction, self).create(values)
#         return res
#     
#     sequence_char = fields.Char('Sequence', readonly=True, track_visibility='onchange', 
#                             copy=False,index=True, store=True,
#                             default=lambda self: _('New'))
#     
    

class inherit_MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'
    
    product_qty = fields.Float(
        'Quantity', default=1.0,
        digits=(16,3), required=True)
    
    
class inherit_MrpBom(models.Model):
    _inherit = 'mrp.bom'
    
    picking_id = fields.Many2one('stock.picking.type','Stock Operation', required=True, domain=[('code', '=', 'mrp_operation')])
    
    @api.onchange('picking_id')
    def onchange_picking_id(self):
        if self.picking_id:
            self.picking_type_id = self.picking_id
    
    
class inherit_StockMove(models.Model):
    _inherit = 'stock.move'
    
    product_uom_qty = fields.Float('Initial Demand',
        digits=(16,3), default=0.0, required=True, states={'done': [('readonly', True)]},
        help="This is the quantity of products from an inventory "
             "point of view. For moves in the state 'done', this is the "
             "quantity of products that were actually moved. For other "
             "moves, this is the quantity of product that is planned to "
             "be moved. Lowering this quantity does not generate a "
             "backorder. Changing this quantity on assigned moves affects "
             "the product reservation, and should be done with care.")
    
    reserved_availability = fields.Float(
        'Quantity Reserved', compute='_compute_reserved_availability',
        digits=(16,3),
        readonly=True, help='Quantity that has already been reserved for this move')
    
    quantity_done = fields.Float('Quantity Done', compute='_quantity_done_compute', digits=(16,3), inverse='_quantity_done_set')
    
    
class inherit_MrpProductProduceLine(models.TransientModel):
    _inherit = "mrp.product.produce.line"
    
    qty_to_consume = fields.Float('To Consume',digits=(16,3))
    qty_reserved = fields.Float('Reserved',digits=(16,3))
    qty_done = fields.Float('Consumed',digits=(16,3))
    
    
class inherit_StockQuant(models.Model):
    _inherit = "stock.quant"
    
    quantity = fields.Float('Quantity', digits=(16,5),
        help='Quantity of products in this quant, in the default unit of measure of the product',
        readonly=True, required=True, oldname='qty')
    reserved_quantity = fields.Float('Reserved Quantity', digits=(16,5),default=0.0,
        help='Quantity of reserved products in this quant, in the default unit of measure of the product',
        readonly=True, required=True)    
    
    
class inherit_StockMoveLine(models.Model):
    _inherit = "stock.move.line"
    
    product_uom_qty = fields.Float('Reserved', default=0.0, digits=(16,5), required=True)
    qty_done = fields.Float('Done', default=0.0, digits=(16,5), copy=False)