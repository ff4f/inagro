#  -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class ProductPack(models.Model):
    _name = 'product.pack'
    _description = 'Product Pack'

    product_id = fields.Many2one(
        'product.product', string='Product', required=True)
    qty = fields.Float(
        string='Quantity', required=True, default=1)
    product_template_id = fields.Many2one(
        'product.template', string='Product pack')
    price = fields.Float(related='product_id.lst_price',
                         string='Product Price')
    uom_id = fields.Many2one(
        related='product_id.uom_id', string="Unit of Measure", readonly="1")
    name = fields.Char(related='product_id.name',string='Name', readonly="1")
    
    #####################
    parent_product_id = fields.Many2one('product.product','Parent Product', ondelete='cascade',
        index=True, required=True)
    
    _sql_constraints = [
        ('product_uniq', 'unique(parent_product_id, product_id)',
         'Product must be only once on a pack!'),
    ]
    
    
    @api.constrains('product_id')
    def _check_recursion(self):
        """Check recursion on packs."""
        for line in self:
            parent_product = line.parent_product_id
            pack_lines = line
            while pack_lines:
                if parent_product in pack_lines.mapped('product_id'):
                    raise ValidationError(_(
                        'You cannot set recursive packs.\n'
                        'Product id: %s') % parent_product.id)
                pack_lines = pack_lines.mapped('product_id.pack_line_ids')
    #####################
