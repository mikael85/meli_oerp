# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import api, fields, models, _
from openerp.addons import decimal_precision as dp
from openerp.exceptions import UserError
from openerp.tools import float_utils
import logging
_logger = logging.getLogger(__name__)


class Inventory(models.Model):
    _inherit = "stock.inventory"

    #
    #def action_done(self):
        #import pdb; pdb.set_trace()
        #_logger.info("Inventory action_done")
        #res = super(Inventory, self).action_done()
        #return True


class InventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    #
    #def action_done(self):
        #import pdb; pdb.set_trace()
        #_logger.info("InventoryLine action_done")
        #res = super(InventoryLine, self).action_done()
        #return True
