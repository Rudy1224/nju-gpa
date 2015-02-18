import requests
from bs4 import BeautifulSoup
import getpass

class NJU_GPA_Spider:

    def __init__(self):
        "choose server and define global variables"
        self.servers = {'1': "http://jwas2.nju.edu.cn:8080/jiaowu", '2': "http://jwas3.nju.edu.cn:8080/jiaowu/",
                   '3': "http://desktop.nju.edu.cn:8080/jiaowu/"}
        self.server_index = raw_input("Choose server [1, 2, 3]: ")
        self.cookies = {}
        self.termlist = {}
        self.creditstat = []
        self.totalpoints = 0
        self.totalcredits = 0
        self.gpa = 5
        
    def login(self):
        "get cookie"
        while True:
            flag = True
            if self.server_index in self.servers.keys():
                while True:
                    try:
                        r = requests.get(self.servers[self.server_index])
                        break
                    except requests.exceptions.ConnectionError:
                        del self.servers[self.server_index]
                        print "Can not connect to server %s\n" % self.server_index
                        self.server_index = raw_input("choose server %s:" % str(self.servers.keys()))
                while flag:
                    stuid = raw_input ("Type in your NJU student ID: ")
                    pwd = getpass.getpass ("Type in the password: ")
                    auth = {'userName': stuid, 'password': pwd}
                    r = requests.get(self.servers[self.server_index]+"login.do", params = auth)
                    soup = BeautifulSoup(r.text)
                    flag = soup.find(href="Javascript:window.history.go(-1)")
                self.cookies['JSESSIONID'] = r.headers['set-cookie'][11: 43]
                break
            else:
                print "Please enter number 1, 2 or 3 !"
                self.server_index = raw_input("Choose server 1/ 2/ 3 : ")            
        
    def showTermList(self):
        "list all courses and calculate gpa"
        termCodes = ['20121', '20122', '20131', '20132', '20141', '20142', '20151', '20152']
        temp = []
        for termcode in termCodes:
            r = requests.get(self.servers[self.server_index]+
                             "student/studentinfo/achievementinfo.do?"+
                             "method=searchTermList&termCode="+termcode, cookies=self.cookies)
            soup = BeautifulSoup(r.text)
            for item in soup.find_all(valign="middle"):
                temp.append(item.get_text(strip = True))
        for i in range(len(temp)/9):
            try:
                self.termlist[temp[9*i+2]] = [int(round(float(temp[9*i+5]))), int(round(float(temp[9*i+6])))]
            except:
                print unicode(temp[9*i+3]), 'does not have a numeric score!'
        for key, value in self.termlist.items():
            print unicode(key), value
        self.gpa_calc()
        
    def showCreditStat(self):
        "retrive credit earned"
        r = requests.get(self.servers[self.server_index]+
                         "student/studentinfo/achievementinfo.do?method=searchCreditStat",
                         cookies=self.cookies)
        soup = BeautifulSoup(r.text)
        for item1 in soup.find_all('th', align="center"):
            self.creditstat.append(item1.get_text(strip = True))
        for item2 in soup.find_all('td', align="center"):
            self.creditstat.append(int(round(float(item2.get_text(strip = True)))))
        print "Here\'s your progress till now:\n"
        for i in range(4):
            print '\t', unicode(self.creditstat[i]), '\t', self.creditstat[i+5]
        print '\t', unicode(self.creditstat[4]), self.creditstat[9], '\n'
        self.totalcredits = 0
        for i in range(5, 10):
            self.totalcredits += self.creditstat[i]
        if self.creditstat[9] == 14:
            print "    GE course requirement met."
        else:
            print "    Still need %i credits of GE courses." % (14-self.creditstat[9])
        print "    Still need %i credits for graduation." % (150-self.totalcredits)

    def gpa_calc(self):
        "calculate gpa"
        self.totalcredits = 0
        self.totalpoints = 0
        for value in self.termlist.values():
            self.totalpoints += value[0]*value[1]
            self.totalcredits += value[0]
        self.gpa = (self.totalpoints/self.totalcredits)/20.0
        print '\nObtained %i courses and their scores.' % len(self.termlist.keys())
        print 'Your current GPA is %f.' % self.gpa

mySpider = NJU_GPA_Spider()
mySpider.login()
while True:
    flag = raw_input('''\nChoose function:
                     \n\t A. Show Term List\t B. Show Credit Status\n>''')
    if flag == 'a' or flag == 'A':
        mySpider.showTermList()
        while True:
            newflag = raw_input("Continue to your credit status? Y/N ")
            if newflag == 'Y' or newflag == 'y':
                print '\n'
                mySpider.showCreditStat()
                break
            elif newflag == 'N' or newflag == 'n':
                break
            else:
                print "Please enter 'Y' or 'N' !"
        break
    elif flag == 'b' or flag == 'B':
        mySpider.showCreditStat()
        while True:
            newflag = raw_input("Continue to your credit status? Y/N ")
            if newflag == 'Y' or newflag == 'y':
                print '\n'
                mySpider.showTermList()
                break
            elif newflag == 'N' or newflag == 'n':
                break
            else:
                print "Please enter 'Y' or 'N' !"
        break
    else:
        print 'Please enter \'a\' or \'b\'!\n'

raw_input("Press any key to exit...")
