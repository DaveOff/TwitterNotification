import os
import sqlite3
import http.cookiejar as cookielib
from requests.utils import dict_from_cookiejar
import requests
from configparser import ConfigParser
import json
import winsound
from time import sleep

class twitterNotification:
    def __init__(self):
        firefoxConfig = ConfigParser()
        firefoxConfig.read(os.getenv('APPDATA')+r"\Mozilla\Firefox\profiles.ini")
        if firefoxConfig.has_option('Profile0', 'Path') is False :
            raise Exception("[Init] Firefox Profile Did Not Find!")
        self.cookie_jar = cookielib.CookieJar()
        self.firefox_profile = firefoxConfig.get('Profile0', 'Path')
        ''' Let's Go '''
        self.get_cookies()
        self.run()

    def get_cookies(self):
        path = os.getenv('APPDATA')+r"\Mozilla\Firefox\\"+(self.firefox_profile.replace('/', "\\"))+r"\cookies.sqlite"
        con = sqlite3.connect(path)
        cur = con.cursor()
        cur.execute("SELECT host, path, isSecure, expiry, name, value FROM moz_cookies WHERE host = '.twitter.com'")
        for item in cur.fetchall():
            c = cookielib.Cookie(0, item[4], item[5],
                None, False,
                item[0], item[0].startswith('.'), item[0].startswith('.'),
                item[1], False,
                item[2],
                item[3], item[3]=="",
                None, None, {})
            self.cookie_jar.set_cookie(c)
        cookies = dict_from_cookiejar(self.cookie_jar)
        if 'ct0' not in cookies :
            raise Exception("[Cookies] Token Not Found!")
        self.token = cookies['ct0']

    def run(self):
        while True :
            resp = self.request()
            if resp['total_unread_count'] > 0 :
                winsound.Beep(500, 500)
                winsound.Beep(500, 500)
                sleep(10)
            else :
                flag = 0
                while flag <= 10:
                    print("\r" + ("." * flag), end=" ")
                    flag = flag + 1
                    sleep(1)

    def request(self):
        headers = {
            'x-csrf-token': self.token,
            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'Referer': 'https://twitter.com/notifications',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0'
        }
        response = requests.get('https://api.twitter.com/2/badge_count/badge_count.json?supports_ntab_urt=1', cookies=self.cookie_jar, headers=headers)
        if response.ok is False :
            if response.status_code == 429 : raise Exception("[Request] Refresh Twitter Web Page")
            else : raise Exception("[Request] Something is Wrong!")
        try:
            json_object = json.loads(response.content)
        except ValueError as e:
            raise Exception("[Request] Json is Not Valid!")
        return json_object

if __name__ == "__main__":
    try :
        twitterNotification()
    except Exception as err:
        print("[Error]{}".format(err))
