# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class inherit_MrpUnbuild(models.Model):

	_inherit = "mrp.unbuild"

	@api.onchange('mo_id')
	def onchange_mo_id(self):
		if self.mo_id:
			self.product_id = self.mo_id.product_id.id
			self.product_qty = self.mo_id.product_qty
			self.location_dest_id = self.mo_id.location_src_id
			self.location_id = self.mo_id.location_dest_id