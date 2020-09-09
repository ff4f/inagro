#  -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    @api.multi
    def _action_launch_stock_rule(self):
        
        ctx = dict(self._context or {})
        filteredObj = []
        errors = []
        if ctx.get('skip'):
            filterIds = ctx.get('skip')
            filteredObj = self.filtered(lambda obj : obj.id not in filterIds)
        else:
            filteredObj = self
        for line in filteredObj:
            if line.product_id.is_pack:
                qty = 0.0
                for move in line.move_ids:
                    qty += move.product_qty
                if not line.order_id.procurement_group_id:
                    line.order_id.procurement_group_id = self.env['procurement.group'].create({
                        'name': line.order_id.name, 'move_type': line.order_id.picking_policy,
                        'sale_id': line.order_id.id,
                        'partner_id': line.order_id.partner_shipping_id.id,
                    })
                values = line._prepare_procurement_values(group_id=line.order_id.procurement_group_id)

                for pack_obj in line.product_id.product_pack_ids:
                    if pack_obj.product_id.type == 'service':
                        continue
                    product_qty = line.product_uom_qty * pack_obj.qty
                    try:
                        res = self.env['procurement.group'].run(pack_obj.product_id, product_qty, line.product_uom, line.order_id.partner_shipping_id.property_stock_customer, line.name, line.order_id.name, values)
                    except UserError as error:
                        errors.append(error.name)
        return super(SaleOrderLine, self)._action_launch_stock_rule()
    
    @api.onchange('product_uom_qty', 'product_uom', 'route_id')
    def _onchange_product_id_check_availability(self):
        res = super(SaleOrderLine,self)._onchange_product_id_check_availability()
        product_obj = self.product_id
        if self.product_id.type == 'product':
            if product_obj.is_pack:
                warning_mess = {}
                for pack_product in product_obj.product_pack_ids:
                    qty = self.product_uom_qty
                    _logger.info("#################%r", qty)
                    if qty * pack_product.qty > pack_product.product_id.virtual_available:
                        warning_mess = {
                            'title': _('Not enough inventory!'),
                            'message': ('You plan to sell %s quantities of the pack %s but you have only  %s quantities of the product %s available, and the total quantity to sell is  %s !!' % (qty, pack_product.product_id.name, pack_product.product_id.virtual_available, pack_product.product_id.name, qty * pack_product.qty))
                        }
                        return {'warning': warning_mess}
            return res
        
    @api.multi
    def _get_delivered_qty(self):
        res = super(SaleOrderLine, self)._get_delivered_qty()
        if self.product_id.is_pack:
            return self.product_uom_qty
        return res
    
    
class Inherit_StockMove(models.Model):
    _inherit = "stock.move"
    
    @api.constrains('product_uom')
    def _check_uom(self):
#         res = super(Inherit_StockMove,self)._check_uom()
        print("tesss")
        return super(Inherit_StockMove,self)._check_uom()