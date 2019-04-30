{
    'name': "SMS Framework",
    'version': "1.0",
    'author': "Ryanto The",
    'category': "Tools",
    'summary': """
        Allows you to send and receive smses from multiple gateways
        Original module by Sythil Tech.
        """,
    'description': """
        Allows you to send and receive smses from multiple gateways.
        Original module by Sythil Tech.
        I only modified it to suit our company use, and added inbuilt wassenger gateway for WhatsApp support.
        """,
    'license':'LGPL-3',
    'data': [
        'data/ir.cron.xml',
        'data/sms.gateway.csv',
        'views/sms_views.xml',
        'views/res_partner_views.xml',
        'views/sms_message_views.xml',
        'views/sms_template_views.xml',
        'views/sms_account_views.xml',
        'views/sms_number_views.xml',
        'views/ir_actions_server_views.xml',
        'views/ir_actions_todo.xml',
        'wizard/sms_compose_views.xml',
        'security/ir.model.access.csv',
    ],
    'depends': ['mail'],
    'images':[
        'static/description/3.jpg',
    ],
    'installable': True,
}