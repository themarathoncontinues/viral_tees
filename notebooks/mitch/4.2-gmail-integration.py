import yagmail

yagmail.register('support@gubr.io', 'temporarypass123!')

yag = yagmail.SMTP('support@gubr.io')

yag.send('mitchbregs@gmail.com', 'subject', 'fucking around')