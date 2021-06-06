import os
import sqlite3
import http.cookiejar as cookielib
from requests.utils import dict_from_cookiejar
import requests
from configparser import ConfigParser
import json
import winsound
import datetime
from time import sleep
from nanoleaf.api import nanoleaf2twitter
from win10toast import ToastNotifier
import playsound
from urllib.request import urlopen, Request
from PIL import Image

class twitterNotification:
    def __init__(self):
        firefoxConfig = ConfigParser()
        firefoxConfig.read(os.getenv('APPDATA')+r"\Mozilla\Firefox\profiles.ini")
        if firefoxConfig.has_option('Profile0', 'Path') is False :
            raise Exception("[Init] Firefox Profile Did Not Find!")
        self.notiUrl = "https://api.twitter.com/2/badge_count/badge_count.json?supports_ntab_urt=1"
        self.notiTextUrl = "https://twitter.com/i/api/2/notifications/all.json?include_profile_interstitial_type=1&include_blocking=1&include_blocked_by=1&include_followed_by=1&include_want_retweets=1&include_mute_edge=1&include_can_dm=1&include_can_media_tag=1&skip_status=1&cards_platform=Web-12&include_cards=1&include_ext_alt_text=true&include_quote_count=true&include_reply_count=1&tweet_mode=extended&include_entities=true&include_user_entities=true&include_ext_media_color=true&include_ext_media_availability=true&send_error_codes=true&simple_quoted_tweet=true&count=20&ext=mediaStats,highlightedLabel"
        self.cookie_jar = cookielib.CookieJar()
        self.firefox_profile = firefoxConfig.get('Profile0', 'Path')
        self.toaster = ToastNotifier()
        self.nanoleaf = nanoleaf2twitter(ip='192.168.1.234', token='TOKEN')
        ''' Let's Go '''
        self.keep_beeping = True
        self.get_cookies()
        self.run()

    def get_cookies(self):
        path = os.getenv('APPDATA')+r"\Mozilla\Firefox\\"+self.firefox_profile.replace('/', "\\")+r"\cookies.sqlite"
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
            resp = self.request(self.notiUrl)
            if resp['total_unread_count'] > 0:
                self.nanoleaf.run()
                textResult = self.parseText(self.request(self.notiTextUrl))
                text = textResult[0] if textResult is not None else "You Have a Notification"
                self.toaster.show_toast("Twitter",textResult[0],icon_path=textResult[1],duration=8,threaded=True)
                #winsound.Beep(500, 500)	
                sleep(10)
            else :
                flag = 0
                while flag <= 10:
                    print("\r" + ("." * flag), end=" ")
                    flag = flag + 1
                    sleep(1)

    def request(self, uri):
        headers = {
            'x-csrf-token': self.token,
            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'Referer': 'https://twitter.com/notifications',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0'
        }
        response = requests.get(uri, cookies=self.cookie_jar, headers=headers)
        if response.ok is False :
            if response.status_code == 429 : raise Exception("[Request] Refresh Twitter Web Page")
            else : raise Exception("[Request] Something is Wrong!")
        try:
            json_object = json.loads(response.content)
        except ValueError as e:
            raise Exception("[Request] Json is Not Valid!")
        return json_object
		
    def sortByTime(self, json_object):
        cloz_dict = { 
            abs(int(datetime.datetime.timestamp(datetime.datetime.now())) * 1000 - int(json_object['globalObjects']['notifications'][key[0]]['timestampMs'])) : key
            for key in json_object['globalObjects']['notifications'].items()}
        return cloz_dict[min(cloz_dict.keys())]

    def parseText(self, json_object):
        try:
            res = self.sortByTime(json_object)
            text = res[1]['message']['text']
            uid = json_object['globalObjects']['notifications'][res[1]['id']]['message']['entities'][0]['ref']['user']['id']
            avatar = json_object['globalObjects']['users'][uid]['profile_image_url']
            avatarPath = self.downloadImg(avatar)
            return [text, avatarPath]
            # for key in json_object['globalObjects']['notifications'].items() :
            #     minago = int(datetime.datetime.timestamp(datetime.datetime.now() - datetime.timedelta(minutes=5))) * 1000
            #     if int(json_object['globalObjects']['notifications'][key[0]]['timestampMs']) > minago :
            #         text = json_object['globalObjects']['notifications'][key[0]]['message']['text']
            #         uid = json_object['globalObjects']['notifications'][key[0]]['message']['entities'][0]['ref']['user']['id']
            #         avatar = json_object['globalObjects']['users'][uid]['profile_image_url']
            #         return text
            
        except:
            return None
        
    def downloadImg(self, url):
        try:
            req = Request(url=url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}) 
            imgfilename = "tmp/" + datetime.datetime.today().strftime('%Y%m%d') + '_' + url.split('/')[-1]
            imagefilenameico = imgfilename.split('.')[0] + '.ico'
            with open(imgfilename, 'wb') as f:
                f.write(urlopen(req).read())
            img = Image.open(imgfilename)
            img.save(imagefilenameico)
            os.remove(imgfilename)
            return imagefilenameico
        except ValueError as e:
            raise Exception("[downloadImg]")

if __name__ == "__main__":
    try :
        twitterNotification()
    except Exception as err:
        print("[Error]{}".format(err))
