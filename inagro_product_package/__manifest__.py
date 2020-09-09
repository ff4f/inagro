# Copyright 2019 NaN (http://www.nan-tic.com) - Àngel Àlvarez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Inagro Product Package',
    'version': '12.0.1.0.1',
    'category': 'Product',
    'summary': 'This module allows you to set a product as a Pack',
    'website': 'inagro.co.id',
    'author': 'faliqul.fikri@inagro.co.id',
    'license': 'AGPL-3',
    'depends': [
        'product','sale','stock','sale_stock'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
