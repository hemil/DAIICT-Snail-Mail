import sys
from bs4 import BeautifulSoup
import re
import mechanize
from prettytable import PrettyTable
import datetime
import smtplib

class Mail():
    def __init__(self):
        self.name=sys.argv[1]
        self.MAIL_USER = sys.argv[2]
        self.MAIL_PASS = sys.argv[3]
        self.recipient = sys.argv[4]

        browser = mechanize.Browser()
        browser.set_handle_robots(False)
        browser.open('http://hostel.daiict.ac.in/index.php?option=com_eventtableedit&view=default&Itemid=2')
        browser.select_form(name='filterform')
        browser['filternach'] = self.name
        browser.submit()

        soup = BeautifulSoup(browser.response().read())

        # Get table
        try:
            table = soup.find('table',{'class':'whoplaystable'})
        except AttributeError as e:
            raise ValueError("No valid table found")

        # Get rows
        try:
            rows = table.find_all('tr')
        except AttributeError as e:
            print 'No table rows found, exiting'
        #has all your dates. To check against last date and send email
        dates = self.TabularPrint(rows)  
        if self.CheckSend(dates):
            print "done. Exiting"
            sys.exit()
        else:
            print "Something went wrong."

    def parse_rows(self,rows):
        """ Get data from rows """
        results = []
        for row in rows:
            table_headers = row.find_all('th')
            if table_headers:
                results.append([headers.get_text() for headers in table_headers])

            table_data = row.find_all('td')
            if table_data:
                results.append([data.get_text() for data in table_data])
        return results

    def multiple_replacer(self,*key_values):
        replace_dict = dict(key_values)
        replacement_function = lambda match: replace_dict[match.group(0)]
        pattern = re.compile("|".join([re.escape(k) for k, v in key_values]), re.M)
        return lambda string: pattern.sub(replacement_function, string)

    def multiple_replace(self,string, *key_values):
        return self.multiple_replacer(*key_values)(string)

    def TabularPrint(self,rows):
        fmt = "%d.%m.%Y"
        dates = []
        # Get data
        replacements = (u'\t',''),(u'\n',''),(u'\r',''),(u'\xa0','')
        table_data = self.parse_rows(rows)
        x = PrettyTable(["ID","Date","Name","Room No","Parcel No"])
        for each in table_data:
            Id = self.multiple_replace(each[0], *replacements)
            #date = time.strftime(time.strptime(multiple_replace(each[1], *replacements),"%d.%m.%Y")
            date = datetime.datetime.strptime(self.multiple_replace(each[1], *replacements),fmt).date()
            dates.append(date)
            name = self.multiple_replace(each[2], *replacements)
            room = self.multiple_replace(each[3], *replacements)
            parcel = self.multiple_replace(each[4], *replacements)
            x.add_row([Id,str(date),name,room,parcel])
        #print x
        return dates

    def SendEmail(self,recipient):
        self.MAIL_USER      #from
        self.MAIL_PASS      #from_password
        SMTP_SERVER = 'webmail.daiict.ac.in'    #server
        SMTP_PORT = 25                          #port

        subject, text = 'Parcel in Hostel','You Got Mail'

        smtpserver = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        smtpserver.ehlo()
        smtpserver.starttls()
        smtpserver.ehlo
        k = smtpserver.login(self.MAIL_USER, self.MAIL_PASS)
        header = 'To:' + recipient + '\n' + 'From:' + self.MAIL_USER
        header = header + '\n' + 'subject:' + subject + '\n'
        msg = header + '\n' + text + '\n\n'
        k = smtpserver.sendmail(self.MAIL_USER,self.recipient, msg)
        k = smtpserver.close()
        return True

    def CheckSend(self,dates):
        #checking for dates more recent thant the one in the file.
        #send the email, if such exists.
        f = open("sent.txt",'r')
        fmt = "%Y-%m-%d"
        LastDate = datetime.datetime.strptime(f.readline(),fmt)
        f.close()
        largest = LastDate.date()
        for each in dates:
            if each>LastDate.date():
                #dates after last checked.
                if each > largest:
                    largest = each
            else:
                #dates earlier than last checked
                continue
        f = open("sent.txt",'w')
        f.write(str(largest))
        if self.SendEmail(self.recipient):
            return True
        else:
            return False
        

    

if __name__ == '__main__':
    status = Mail()
    sys.exit(status)
