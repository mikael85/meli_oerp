# -*- coding: utf-8 -*-

from openerp import models, api, fields, tools
import openerp.addons.decimal_precision as dp
from openerp import _

class ProductAttribute(models.Model):

    _inherit = 'product.attribute'

    meli_id = fields.Char(u'Id Attribute ML')
    meli_default_id_attribute = fields.Many2one('mercadolibre.category.attribute',string="ML Attribute default")
    meli_id_attributes = fields.Many2many('mercadolibre.category.attribute',string="ML Attributes")
