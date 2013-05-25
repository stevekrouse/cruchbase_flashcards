import requests

frc = 'http://ec2-107-21-104-179.compute-1.amazonaws.com/v/1/financial-organization/first-round-capital.js'


nets = 'http://api.crunchbase.com/v/1/company/jingle+networks.js?api_key=wfx6yz8nj5ddrm9hanh4dycx'


def get_json(url):
    """GET some JSON, raising an HTTPError if we don't get a 200 status.

    First calls make_url using the arguments, then makes the web requests and
    returns the JSON. If the received JSON is empty, throw a ValueError.

    """
    call = requests.get(url)
    call.raise_for_status()
    return call.json()


def un_HTML_ify(text):
    html_chars = ['<p>', '</p>', '\n', u'&#8220;', u'&#8221;', u'&#8211;']
    for char in html_chars:
        text = text.replace(char, '')
    text = text.replace(u'\u2019', "'")
    text = text.replace(u'&#8217;', "'")
    text = text.replace(u'&amp;', '&')
    return text


def textify(price):
    price = int(price)
    if price >= 1000000:
        return str(price/1000000) + 'M'
    else:
        return str(price/1000) + 'K'


def parse_description(company):
    text = un_HTML_ify(company[u'overview'])
    blurb = text[0:400] + '...'
    name = company[u'name']
    return blurb.replace(name, '[company]')


def parse_round(company):
    round = company[u'round_code']
    if len(round) == 1:
        return ' Series ' + round.upper()
    elif round == u'unattributed':
        return ''
    else:
        return ' ' + round[0].upper() + round[1:].lower()


def parse_company(company):
    company = company[u'funding_round']
    round = parse_round(company)
    permalink = company[u'company'][u'permalink']
    url = ('http://api.crunchbase.com/v/1/company/' + permalink + ''
           '.js?api_key=wfx6yz8nj5ddrm9hanh4dycx')

    funded_date = str(company[u'funded_month']) + '/'
    if company[u'funded_day'] is not None:
        funded_date += '' + str(company[u'funded_day']) + '/'
    funded_date += str(company[u'funded_year'])

    url_page = get_json(url)
    description = parse_description(url_page)
    acquisition = url_page[u'acquisition']

    text = ''
    if company[u'raised_amount'] is not None:
        text += textify(company[u'raised_amount'])
    text += round
    text += ' (' + funded_date + ')'
    if acquisition is not None:
        text += ', Acquired by ' + acquisition[u'acquiring_company'][u'name']
        if acquisition[u'price_amount'] is not None:
            text += ' at ' + textify(acquisition[u'price_amount'])
    text += '\n'
    text += description.strip()
    return text

companies = get_json(frc)[u'investments']
already_seen = []
for company in companies:
    name = company[u'funding_round'][u'company'][u'name']
    if name not in already_seen:
        already_seen.append(name)
        text = parse_company(company)
        print(name + ':' + text + '\n')
