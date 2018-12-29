import requests
from lxml import etree
from uuid import uuid4
import datetime


def get(url, username, password):
    try:
        crmres = requests.get(url + "XrmServices/2011/Organization.svc?wsdl=wsdl0")
    except requests.exceptions.RequestException as e:
        raise Exception(e)

    try:
        adfs = etree.fromstring(crmres.text)
    except ImportError:
        raise Exception('Failed to import XML response')

    ns = {'ms-xrm': 'http://schemas.microsoft.com/xrm/2011/Contracts/Services'}
    ident = adfs.findall('.//ms-xrm:Identifier', ns)
    if len(ident) == 0:
        raise Exception('Could not find ADFS URL in XML response')

    adfsurl = ident[0].text.replace('http:', 'https:')
    urnaddress = url + "XRMServices/2011/Organization.svc"
    usernamemixed = adfsurl + "/13/usernamemixed"

    xml = "<s:Envelope xmlns:s=\"http://www.w3.org/2003/05/soap-envelope\" xmlns:a=\"http://www.w3.org/2005/08/addressing\">";
    xml += "<s:Header>";
    xml += "<a:Action s:mustUnderstand=\"1\">http://docs.oasis-open.org/ws-sx/ws-trust/200512/RST/Issue</a:Action>";
    xml += "<a:MessageID>urn:uuid:{" + str(uuid4()) + "}</a:MessageID>";
    xml += "<a:ReplyTo>";
    xml += "<a:Address>http://www.w3.org/2005/08/addressing/anonymous</a:Address>";
    xml += "</a:ReplyTo>";
    xml += "<Security s:mustUnderstand=\"1\" xmlns:u=\"http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd\" xmlns=\"http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd\">";
    xml += "<u:Timestamp  u:Id=\"{" + str(uuid4()) + "}\">";
    xml += "<u:Created>" + datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ') + "</u:Created>";
    xml += "<u:Expires>" + (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime(
        '%Y-%m-%dT%H:%M:%S.%fZ') + "</u:Expires>";
    xml += "</u:Timestamp>";
    xml += "<UsernameToken u:Id=\"{" + str(uuid4()) + "}\">";
    xml += "<Username>" + username + "</Username>";
    xml += "<Password Type=\"http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText\">" + password + "</Password>";
    xml += "</UsernameToken>";
    xml += "</Security>";
    xml += "<a:To s:mustUnderstand=\"1\">" + usernamemixed + "</a:To>";
    xml += "</s:Header>";
    xml += "<s:Body>";
    xml += "<trust:RequestSecurityToken xmlns:trust=\"http://docs.oasis-open.org/ws-sx/ws-trust/200512\">";
    xml += "<wsp:AppliesTo xmlns:wsp=\"http://schemas.xmlsoap.org/ws/2004/09/policy\">";
    xml += "<a:EndpointReference>";
    xml += "<a:Address>" + urnaddress + "</a:Address>";
    xml += "</a:EndpointReference>";
    xml += "</wsp:AppliesTo>";
    xml += "<trust:RequestType>http://docs.oasis-open.org/ws-sx/ws-trust/200512/Issue</trust:RequestType>";
    xml += "</trust:RequestSecurityToken>";
    xml += "</s:Body>";
    xml += "</s:Envelope>";

    try:
        res = requests.post(usernamemixed, data=xml, headers={'Content-type': 'application/soap+xml; charset=UTF-8'})
    except requests.exceptions.RequestException as e:
        raise Exception(e)

    try:
        tokxml = etree.fromstring(res.text)
    except ImportError:
        raise Exception('Failed to import Token XML response')

    tok = tokxml.findall('.//xenc:EncryptedData', {'xenc': 'http://www.w3.org/2001/04/xmlenc#'})
    if len(tok) == 0:
        raise Exception('Failed to fetch token')
    token = etree.tostring(tok[0])

    return token.decode("utf-8")