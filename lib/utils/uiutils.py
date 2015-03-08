# coding=utf8


# ##################################################### MEMBER PREFIXES ########

PREFIXES = {
    'method': u'○',
    'property': u'●',
    'class':u'♦',
    'interface':u'◊',
    'keyword':u'∆',
    'constructor':u'■',
    'variable': u'V',
    'public':u'[pub]',
    'private':u'[priv]',
    'getter':u'<',
    'setter':u'>'
}


def get_prefix(token):
    if token in PREFIXES:
        return PREFIXES[token]
    else:
        return ''