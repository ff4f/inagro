# -*- coding: utf-8 -*-
{
    'name': "Inagro Web Supporting Ticket",

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
    'depends': ['website_support'],

    # always loaded
    'data': [
        'data/res.groups.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/templates.xml', 
        'views/web_support_ticket_views.xml',
        'views/web_support_ticket_compose_views.xml',
        'views/menus.xml',
        'views/support_ticket_view.xml',

    ],
    'installable': True,
    
    'depends' : ['website_support']
    # only loaded in demonstration mode
}