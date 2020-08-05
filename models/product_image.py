# -*- coding: utf-8 -*-

from openerp import models, api, fields, tools
import openerp.addons.decimal_precision as dp
from openerp import _

# Implemento imagen como está en website_sale de la v12


class ProductImage(models.Model):
    _name = 'product.image'
    _description = 'Product Image'

    name = fields.Char('Name')
    # image = fields.Binary('Image', attachment=True, store=True)
    image = fields.Binary('Image', store=True)
    product_tmpl_id = fields.Many2one(
        'product.template', 'Related Product', copy=True)

    meli_imagen_id = fields.Char(string='Imagen Id', index=True)
    meli_imagen_link = fields.Char(string='Imagen Link')
    meli_imagen_size = fields.Char(string='Size')
    meli_imagen_max_size = fields.Char(string='Max Size')
    meli_imagen_bytes = fields.Integer(string='Size bytes')
    meli_pub = fields.Boolean(string='Publicar en ML', index=True)
    meli_id = fields.Char(u'ID MELI')
    product_attribute_id = fields.Many2one(
        'product.attribute.value', u'Atributo asociado')


ProductImage()
