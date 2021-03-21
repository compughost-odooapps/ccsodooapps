# -*- coding: utf-8 -*-
{
    'name':"Auto Work Flow",
    'summary':"""Auto confrim sale order, Purchase order, Manufactur Order.""",

    'author':"Compughost Solution",
    'website':"www.compughost.com",

    'category':'sale',
    'version':'14.0.1',

    # any module necessary for this one to work correctly
    'depends':['sale_management', 'sale_stock'],
    
    'data': [
        'views/sale_order_views.xml',
    ],
    'price': 5.26,
    'currency': 'EUR',
}
