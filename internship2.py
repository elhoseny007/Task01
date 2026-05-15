# -*- coding: utf-8 -*-
#the second way
#our Gaurdrails
response={
    'hello':'Hi there',
    'how are u':'im fine ',
    'bye':'good_bye',
    'name':'im chatbot',
    'help':'i can answer basic question',
    'are u here': 'yes sir how can i help u'
    }
#our model
while True:
    chatbot=input('How can i help u: ')
    clean_data=chatbot.lower().strip()
    if clean_data=='exist':
        print('good bye!')
        break
    else:
        answer=response.get(clean_data,'idk')
        print('bot:',answer)

