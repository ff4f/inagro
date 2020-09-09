# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ProductProduct(models.Model):
    _inherit = 'product.product'

    pack_line_ids = fields.One2many(
        'product.pack',
        'parent_product_id',
        'Pack Products',
        help='Products that are part of this pack.'
    )
    used_in_pack_line_ids = fields.One2many(
        'product.pack',
        'product_id',
        'Found in packs',
        help='Packs where product is used.'
    )
