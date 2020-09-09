# -*- coding: utf-8 -*-
{
    'name': "Inagro Asset Accounting",

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
    'depends': ['account','account_asset', 'mail','base', 'inagro_asset_maintenance'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/asset_sequence.xml',
        'views/account_asset_views.xml',
        'views/asset_move_views.xml',
        'views/equipment_views.xml',
        'report/asset_report_views.xml',
        'report/asset_report.xml',
        'report/move_report_views.xml',
        'report/move_report.xml'
        
    ],
    # only loaded in demonstration mode
    'demo': [
        
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}