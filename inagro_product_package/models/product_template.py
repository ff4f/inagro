# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _compute_discounted_pack_price(self):
        for product in self:
            product.has_discounted_amount = False
            if product.is_pack:
                price = 0
                for prod in product.product_pack_ids:
                    price = price + prod.product_id.lst_price * prod.qty
                rem_price = price - product.lst_price
                product.pack_products_price = price
                if rem_price <= 0:
                    product.has_discounted_amount = True

    is_pack = fields.Boolean(
        string='Is product pack', default=False)
    product_pack_ids = fields.One2many(
        'product.pack', 
        inverse_name='product_template_id', 
        string='Product pack', copy=True)

    has_discounted_amount = fields.Boolean(
        compute="_compute_discounted_pack_price",
        string="Remaining price")
    pack_products_price = fields.Float(
        compute="_compute_discounted_pack_price",
        string="Total Product Price")
    
    ############
    pack_line_ids = fields.One2many(
        related='product_variant_ids.pack_line_ids',
    )
    used_in_pack_line_ids = fields.One2many(
        related='product_variant_ids.used_in_pack_line_ids',
        readonly=True,
    )
    ############
    
    @api.model
    def create(self, vals):
        if vals.get('is_pack'):
            if not vals.get('product_pack_ids'):
                raise ValidationError(
                    'No products in this pack. Select at least one product.')
        return super(ProductTemplate, self).create(vals)
    
    def _compute_quantities_dict(self):
        ACT_VARIANTS = self.mapped('product_variant_ids')
        variants_available = self.mapped('product_variant_ids')._product_available()
        prod_available = {}
        for template in self:
            qty_available = 0
            virtual_available = 0
            incoming_qty = 0
            outgoing_qty = 0
            for p in template.product_variant_ids:
                qty_available += variants_available[p.id]["qty_available"]
                virtual_available += variants_available[p.id]["virtual_available"]
                incoming_qty += variants_available[p.id]["incoming_qty"]
                outgoing_qty += variants_available[p.id]["outgoing_qty"]
                if template.is_pack and template.product_pack_ids:
                    for pp in template.product_pack_ids:
                        template.product_variant_ids += pp.product_id
                    variants_available.update(template.mapped('product_variant_ids')._product_available())
                    qty_avail = []
                    vir_avail = []
                    inco_qty = []
                    outgo_qty = []
                    for pp in template.product_pack_ids:
                        if pp.qty > 0:
                            qty_avail.append(variants_available[pp.product_id.id]["qty_available"]/pp.qty)
                            vir_avail.append(variants_available[pp.product_id.id]["virtual_available"]/pp.qty)
                            inco_qty.append(variants_available[pp.product_id.id]["incoming_qty"]/pp.qty)
                            outgo_qty.append(variants_available[pp.product_id.id]["outgoing_qty"]/pp.qty)
                    qty_available = min(qty_avail)
                    virtual_available = min(vir_avail)
                    incoming_qty = min(inco_qty)
                    outgoing_qty = min(outgo_qty)
                    template.product_variant_ids = ACT_VARIANTS
            prod_available[template.id] = {
                "qty_available": qty_available,
                "virtual_available": virtual_available,
                "incoming_qty": incoming_qty,
                "outgoing_qty": outgoing_qty,
            }

        return prod_available

    @api.onchange('type')
    def onchange_type(self):
        if not self.type:
            pass
        if self.type == 'consu' or self.type == 'product':
            self.is_pack = False
    
#################################################            
    @api.multi
    def write(self, vals):
        """We remove from product.product to avoid error."""
        _vals = vals.copy()
        if vals.get('pack_line_ids', False):
            self.product_variant_ids.write(
                {'pack_line_ids': vals.get('pack_line_ids')})
            _vals.pop('pack_line_ids')
        return super().write(_vals)
#####################################################