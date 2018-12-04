#!/usr/bin/python3

from getpass import getpass
from lxml import html
import requests
import random
import time

class eassess:

    logged_in = False
    host = 'https://eassess.ku.ac.th'
    header = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    page_url = {
        'home': '/m/index.php',
        'login': '/m/index.php',
        'subject_list': '/m/source/select_subject.php',
        'source': '/m/source/',
    }

    def __init__(self):
        self.req = requests.Session()
        if True:
            self.host = 'https://localhost'
    
    def login(self, username, password):
        post_data = {
            'account': username,
            'password': password
        }
        req = self.req.post(self.host+self.page_url['login'], data = post_data)
        doc = html.fromstring(req.text)
        danger = doc.find_class('alert-danger')
        if len(danger)>0:
            return (False,danger[0].text_content())
        self.logged_in = True
        return (True,None)

    def getSubjectList(self, subject_type = '1'):
        if not self.logged_in:
            return (False, 'Login before call this function')
        if subject_type not in ['1','3']:
            return (False, 'This method only allow for type 1 and type 3.')
        req = self.req.get(self.host+self.page_url['subject_list'], params = {'t':subject_type})
        doc = html.fromstring(req.text)
        subject_tr = doc.findall('.//tr')[1:]
        subject = []
        for tr in subject_tr:
            td = tr.findall('td')
            form_input = tr.findall('.//input')
            subform = {}
            formurl = ''
            if len(form_input)>0:
                formurl = tr.find('.//form').attrib['action']
                subform['cs_code'] = form_input[0].attrib['value']
                subform['type_form'] = form_input[1].attrib['value']
                subform['section'] = form_input[2].attrib['value']
                subform['type_section'] = form_input[3].attrib['value']
                subform['Ttimes'] = form_input[4].attrib['value']
            subject.append({
                'id': td[1].text_content(),
                'type': subject_type,
                'name': td[2].text_content(),
                'section': td[3].text_content(),
                'section_lab': td[4].text_content(),
                'assessed': len(td[5].text_content())!=0,
                'form': subform,
                'formurl': formurl,
            })
        return subject

    def getAdvisorList(self):
        if not self.logged_in:
            return (False, 'Login before call this function')
        subject_type = '4'
        req = self.req.get(self.host+self.page_url['subject_list'], params = {'t':subject_type})
        doc = html.fromstring(req.text)
        subject_tr = doc.findall('.//tr')[1:]
        subject = []
        for tr in subject_tr:
            td = tr.findall('td')
            form_input = tr.findall('.//input')
            subform = {}
            formurl = ''
            if len(form_input)>0:
                formurl = tr.find('.//form').attrib['action']
                subform['advisor'] = form_input[0].attrib['value']
                subform['type_form'] = form_input[1].attrib['value']
                subform['Ttimes'] = form_input[2].attrib['value']
                subform['cs_code'] = ''
                subform['section'] = ''
                subform['type_section'] = ''
            subject.append({
                'name': td[1].text_content(),
                'type': subject_type,
                'assessed': len(td[2].text_content())!=0,
                'form': subform,
                'formurl': formurl,
            })
        return subject

    def assess(self, subject ):
        if subject['assessed']:
            return (False, 'was assessed')
        req = self.req.post(self.host+self.page_url['source']+subject['formurl'], data = {**{'submit': 'ประเมิน'},**subject['form']})
        doc = html.fromstring(req.text)
        choice_all = doc.find('.//input[@name="choice_all"]').attrib['value']
        camp_regis = doc.find('.//input[@name="camp_regis"]').attrib['value']
        astfrm = {
            'OK': 'Submit',
            'choice_all': choice_all
        }
        for i in range(1,int(choice_all)+1):
            score = str(random.randint(3,5))
            astfrm['hidcheck'+str(i)] = score
            astfrm['choice['+str(i)+']'] = score
        astfrm['hidcheck'+str(int(choice_all)+1)] = ''
        astfrm['choice['+str(int(choice_all)+1)+']'] = ''
        req = self.req.post(self.host+self.page_url['source']+subject['formurl'], data = {**astfrm,**subject['form']})
        if req.status_code == 200:
            return (True,None)
        return (False,'Connection error (Server return'+str(req.status_code)+')')


if __name__ == "__main__":
    obj = eassess()
    wantsleep = None
    while wantsleep == None:
        _wantsleep = input('Delay between each request? (y/n) [Y]: ').lower()
        if _wantsleep == 'y' or _wantsleep == '':
            wantsleep = True
        elif _wantsleep == 'n':
            wantsleep = False
    username = input('Username: ')
    password = getpass('Password: ')
    obj.login(username,password)
    for sub_type in ['1','3','4']:
        if sub_type == '4':
            print('Be getting advisor list...',end=' ')
            subjects = obj.getAdvisorList()
            print('Gotcha! There are',len(subjects),'advisors.')
        else:
            print('Be getting subject list (Type:',sub_type,')...',end=' ')
            subjects = obj.getSubjectList(sub_type)
            print('Gotcha! There are',len(subjects),'subjects.')
        if wantsleep:
            sleeptime = random.randint(200,500)/100
            time.sleep(sleeptime)
        for subject in subjects:
            result,error = obj.assess(subject)
            if sub_type == '4':
                print('\t',subject['name'],end=' ')
            else:
                print('\t',subject['id'],subject['name'],'(',subject['section'],'/',subject['section_lab'],')',end=' ')
            if result:
                print('assessed')
                if wantsleep:
                    sleeptime = random.randint(1000,1500)/100
                    time.sleep(sleeptime)
            else:
                print(error)

