import requests
from bs4 import BeautifulSoup

class NJU_GPA_Spider:
    def __init__(self):
        self.servers = ["http://jwas2.nju.edu.cn:8080/jiaowu", "http://jwas3.nju.edu.cn:8080/jiaowu/",
                   "http://desktop.nju.edu.cn:8080/jiaowu/"]
        self.server_index = input("choose server [1/ 2/ 3]: ") 
        self.cookies = {}
        self.termlist = {}
        self.creditstat = []
        self.totalpoints = 0
        self.totalcredits = 0
        self.gpa = 5
        
    def login(self):
        #stuid = raw_input ("Type in Your Student ID: ")
        #pwd = raw_input ("Type in the Password: ")
        auth = {'userName': 121090105, 'password': 121858}
        r = requests.get(self.servers[self.server_index-1]+"login.do", params = auth)
        self.cookies['JSESSIONID'] = r.headers['set-cookie'][11: 43]
        
    def showTermList(self):
        termCodes = ['20121', '20122', '20131', '20132', '20141', '20142', '20151', '20152']
        temp = []
        for termcode in termCodes:
            r = requests.get(self.servers[self.server_index-1]+
                             "student/studentinfo/achievementinfo.do?"+
                             "method=searchTermList&termCode="+termcode, cookies=self.cookies)
            soup = BeautifulSoup(r.text)
            for item in soup.find_all(valign="middle"):
                temp.append(item.get_text(strip = True))
        for i in range(len(temp)/9):
            try:
                self.termlist[temp[9*i+2]] = [int(round(float(temp[9*i+5]))), int(round(float(temp[9*i+6])))]
            except:
                print unicode(temp[9*i+3]), 'does not have a score!'
        print self.termlist
        mySpider.gpa_calc()
        
    def showCreditStat(self):
        r = requests.get(self.servers[self.server_index-1]+
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
        for i in range(5, 10):
             self.totalcredits += self.creditstat[i]
        if self.creditstat[9] == 14:
            print "    GE course requirement met."
        else:
            print "    Still need %i credits of GE courses." % (14-self.creditstat[9])
        print "    Still need %i credits for graduation." % (150-self.totalcredits)

    def gpa_calc(self):
        for value in self.termlist.values():
            self.totalpoints += value[0]*value[1]
            self.totalcredits += value[0]
        self.gpa = (self.totalpoints/self.totalcredits)/20.0
        print '\n\n\nObtained %i courses and their scores' % len(self.termlist.keys())
        print 'Your Current GPA = ', self.gpa

mySpider = NJU_GPA_Spider()
mySpider.login()
while True:
    flag = raw_input('''Choose function:
                     \n\t a. Show Term List\t b. Show Credit Status\n>''')
    if flag == 'a':
        mySpider.showTermList()
        break
    elif flag == 'b':
        mySpider.showCreditStat()
        break
    else:
        print 'Please enter \'a\' or \'b\''
