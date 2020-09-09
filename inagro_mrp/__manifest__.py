# -*- coding: utf-8 -*-
{
    'name': "Inagro Manufacturing",

    'summary': """
        faliqul.fikri@inagro.co.id""",

    'description': """
        -
    """,

    'author': "INAGRO",
    'website': "https://www.inagro.co.id/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['mrp'],

    # always loaded
    'data': [
#         'views/sequence.xml',
        'security/security.xml',
        'views/mrp_production_views.xml',
        'views/mrp_unbuild_views.xml',
        'views/product_views.xml',

    ],
    'installable': True,
    # only loaded in demonstration mode
}