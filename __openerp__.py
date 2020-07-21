# -*- coding: utf-8 -*-
##############################################################################
#
#       Pere Ramon Erro Mas <pereerro@tecnoba.com> All Rights Reserved.
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'MercadoLibre Publisher',
    'version': '9.0.0.1',
    'author': 'Moldeo Interactive',
    'website': 'https://www.moldeointeractive.com',
    "category": "Sales",
    # "depends": ['base', 'product', 'sale', 'website_sale', 'stock', 'mrp'],
    "depends": ['base', 'product', 'sale', 'stock', 'mrp'],
    'data': [
        'security/meli_oerp_security.xml',
        'security/ir.model.access.csv',
        'views/company_view.xml',
        'views/posting_view.xml',
        'views/product_post.xml',
        'views/product_view.xml',
        'views/category_view.xml',
        'views/banner_view.xml',
        'views/warning_view.xml',
        'views/questions_view.xml',
        'views/orders_view.xml',
        'data/cron_jobs.xml',
        'data/error_template_data.xml',
        'data/parameters_data.xml',
        'report/report_shipment_view.xml',
        'report/report_invoice_shipment_view.xml',
        'views/shipment_view.xml',
        'views/shipment_view_reports.xml',
        'views/notifications_view.xml'
    ],
    "external_dependencies": {"python": ['pdf2image']},
    'demo_xml': [],
    'active': False,
    'installable': True,
    'application': True,
}
