# -*- coding: utf-8 -*-

from openerp import models, api, fields, tools
import openerp.addons.decimal_precision as dp
from openerp import _

class ResPartner(models.Model):

    _inherit = "res.partner"

    meli_buyer_id = fields.Char('Meli Buyer Id')
    meli_buyer = fields.Many2one('mercadolibre.buyers','Meli Buyer')
