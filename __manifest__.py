{
    'name': 'Puente entre Aportaciones y Préstamos',
    'summary': 'Integración contable entre retiros de aportaciones y pagos de préstamos.',
    'version': '1.0.0',
    'category': 'Technical',
    'description': 'Conecta los retiros de aportaciones con los pagos de préstamos.',
    'author': 'Telemática',
    'website': 'https://telematica.hn',
    'depends': [
        'tel_capp_lm', 'tel_capp_csm',
    ],
    'data': [
        'views/loan_repayment_wizard_view.xml',
        'views/repayment_readonly_view.xml',
        'views/withdrawals_view.xml'
    ],
    'license': 'OPL-1',
    'auto_install': False,
    'application': False,
    'installable': True,
    'maintainer': 'Telemática Development Team',
}