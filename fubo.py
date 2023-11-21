import os
import re
import sys
from threading import Lock
import requests
import json
import secrets
import time, pprint

user = os.environ.get("FUBO_USER")
passwd = os.environ.get("FUBO_PASS")

headers = {
    'authority': 'api.fubo.tv',
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/json',
    'origin': 'https://www.fubo.tv',
    'referer': 'https://www.fubo.tv/',
    'x-client-version': '4.75.0',
    'x-device-app': 'android_tv',
    'x-device-group': 'tenfoot',
    'x-device-model': 'onn. 4K Streaming Box',
    'x-device-platform': 'android_tv',
    'x-device-type': 'puck',
    'x-player-version': 'v1.34.0',
    'x-preferred-language': 'en-US',
    'x-supported-hdrmodes-list': 'hdr10,hlg',
    'x-supported-streaming-protocols': 'hls',
    'x-supported-codecs-list': 'vp9,avc,hevc',
    'user-agent': 'fuboTV/4.75.0 (Linux;Android 12; onn. 4K Streaming Box Build/SGZ1.221127.063.A1.9885170) FuboPlayer/v1.34.0'
}

if user is None or passwd is None:
    sys.stderr.write("FUBO_USER and FUBO_PASS need to be set\n")
    sys.stderr.write(f'FUBO_USER = {user}\n')
    sys.stderr.write(f'FUBO_PASS = {passwd}\n')

    sys.exit(1)

class Client:
    def __init__(self):
        self.user = os.environ["FUBO_USER"]
        self.passwd = os.environ["FUBO_PASS"]

        self.device = None
        self.loggedIn = False
        self.sessionID = ""
        self.sessionAt = 0
        self.stations = []

        self.gracenoteID_list = {'10179': '32645',
                                 '1021370001': '89714',
                                 '103351': '90858',
                                 '103625': '91096',
                                 '104147': '91579',
                                 '104213': '91640',
                                 '10422': '21319',
                                 '104468': '102959',
                                 '104589': '120551',
                                 '104830': '92204',
                                 '104879': '22561',
                                 '105100': '92436',
                                 '105101': '92437',
                                 '105102': '92438',
                                 '105103': '92439',
                                 '105107': '92443',
                                 '108539': '89098',
                                 '109524': '96469',
                                 '109621': '96550',
                                 '109622': '96551',
                                 '110114': '96971',
                                 '110217': '97047',
                                 '110223': '97051',
                                 '11066': '82773',
                                 '111886': '98443',
                                 '113594': '99988',
                                 '114796': '107241',
                                 '116116': '102309',
                                 '118793': '104846',
                                 '118905': '104950',
                                 '119429': '102850',
                                 '119725': '105723',
                                 '120010': '96827',
                                 '120123': '106100',
                                 '120762': '112158',
                                 '121191': '107076',
                                 '121623': '107478',
                                 '122695': '109454',
                                 '123265': '109016',
                                 '12444': '45507',
                                 '124684': '110289',
                                 '124843': '110428',
                                 '124902': '110480',
                                 '125430': '110951',
                                 '125634': '111140',
                                 '1263880001': '111871',
                                 '126463': '111945',
                                 '126876': '112349',
                                 '126878': '112351',
                                 '126879': '112352',
                                 '126881': '112354',
                                 '126882': '112355',
                                 '126883': '112356',
                                 '126884': '112357',
                                 '126885': '112358',
                                 '126888': '112361',
                                 '126889': '112362',
                                 '126890': '112363',
                                 '127275': '112732',
                                 '127430': '112881',
                                 '127712': '120375',
                                 '127957': '113380',
                                 '128187': '113603',
                                 '1283550001': '113768',
                                 '128770': '114174',
                                 '128875': '114278',
                                 '128911': '68295',
                                 '129089': '114491',
                                 '130049': '115447',
                                 '130712': '116102',
                                 '130949': '116338',
                                 '131568': '116946',
                                 '131622': '116999',
                                 '132722': '118087',
                                 '133606': '118952',
                                 '133868': '119212',
                                 '133889': '119233',
                                 '133890': '119234',
                                 '134013': '119355',
                                 '134321': '119661',
                                 '134814': '119209',
                                 '135019': '120351',
                                 '135138': '120469',
                                 '135842': '110356',
                                 '135843': '121166',
                                 '135844': '121167',
                                 '135874': '121197',
                                 '135881': '133321',
                                 '135986': '121307',
                                 '137124': '122436',
                                 '137212': '122524',
                                 '137369': '122679',
                                 '137849': '123156',
                                 '138563': '123870',
                                 '138963': '124268',
                                 '139326': '124630',
                                 '139332': '124636',
                                 '139513': '124817',
                                 '139922': '125187',
                                 '139931': '125195',
                                 '139932': '125196',
                                 '139933': '125197',
                                 '139952': '125214',
                                 '141441': '126634',
                                 '141477': '126670',
                                 '141948': '127141',
                                 '141981': '127174',
                                 '143350': '128542',
                                 '143825': '129048',
                                 '143912': '129135',
                                 '143989': '129212',
                                 '144254': '129477',
                                 '144256': '129479',
                                 '16485': '59976',
                                 '18633': '122912',
                                 '21298': '91638',
                                 '30420': '82654',
                                 '44229': '44228',
                                 '44264': '65596',
                                 '45409': '45399',
                                 '45537': '45526',
                                 '46730': '46710',
                                 '49175': '49141',
                                 '54539': '54424',
                                 '66322': '56256',
                                 '67508': '57390',
                                 '68871': '58690',
                                 '68900': '58718',
                                 '68971': '58780',
                                 '69008': '58812',
                                 '69429': '59186',
                                 '69495': '59250',
                                 '69553': '59305',
                                 '69697': '59440',
                                 '70111': '59814',
                                 '70522': '60179',
                                 '70566': '60222',
                                 '70668': '60316',
                                 '70835': '60468',
                                 '71094': '60696',
                                 '71605': '58321',
                                 '72411': '61854',
                                 '72650': '62081',
                                 '73952': '63220',
                                 '74063': '63320',
                                 '74065': '63322',
                                 '74067': '63324',
                                 '74568': '63776',
                                 '75083': '64241',
                                 '75410': '50000',
                                 '75478': '64591',
                                 '75486': '64599',
                                 '75524': '64630',
                                 '75529': '64634',
                                 '75572': '64673',
                                 '75963': '65025',
                                 '76019': '65064',
                                 '76327': '65342',
                                 '76634': '65626',
                                 '76716': '65687',
                                 '77355': '66268',
                                 '78529': '67331',
                                 '78575': '67375',
                                 '78969': '67749',
                                 '79162': '67929',
                                 '792940001': '68049',
                                 '79312': '68065',
                                 '79698': '68367',
                                 '80124': '68785',
                                 '80136': '68796',
                                 '80167': '68827',
                                 '80496': '69091',
                                 '81646': '70225',
                                 '81675': '70253',
                                 '81808': '70388',
                                 '83074': '71601',
                                 '83287': '71799',
                                 '832870001': '53168',
                                 '84686': '73115',
                                 '855130001': '73882',
                                 '85639': '73994',
                                 '85678': '74030',
                                 '85680': '74032',
                                 '85722': '74073',
                                 '85788': '26046',
                                 '86703': '75004',
                                 '86781': '75077',
                                 '86927': '75220',
                                 '87146': '32697',
                                 '881660001': '76376',
                                 '881670001': '76377',
                                 '881680001': '76378',
                                 '881690001': '76379',
                                 '88170': '76380',
                                 '881710001': '76381',
                                 '88172': '76382',
                                 '88749': '76950',
                                 '88754': '76943',
                                 '88839': '77033',
                                 '90696': '18284',
                                 '90742': '78850',
                                 '91887': '79911',
                                 '92410': '80399',
                                 '94206': '82119',
                                 '94653': '82547',
                                 '94674': '82563',
                                 '94682': '82571',
                                 '94683': '82572',
                                 '94684': '82573',
                                 '94823': '82695',
                                 '95030': '82892',
                                 '99285': '87000',
                                 '99621': '87317',
                                 '99645': '87339',
                                 '133875': '119219',
                                 '136673': '121991', # IMPACT! Wrestling
                                 '139008': '124313', # FUEL TV
                                 '138625': '125051', # World Poker Tour
                                 '134964': '105893', # Horse & Country
                                 '76835':  '11063',  # RTALHD
                                 '71543':  '61090',  # RTNWHD
                                 '136101': '121422', # RTAL2HD
                                 '73858': '63138',   # NBCSBAH, NBC Sports Bay Area
                                 '114968': '101261', # NBSBA2H, NBC Sports Bay Area Plus
                                 '125380': '110904', # NBCSCX3, NBC Sports California Plus 3
                                 '45551': '45540',   # NBSCAHD, NBC Sports California
                                 '107332': '92393',  # NBCSCAH, NBC Sports California Plus
                                 '44631': '11534', # WHTM - ABC
                                 '109261': '17596', # NBCSPA - NBC Sports Philadelphia
                                 '101207': '88829', # NBCSPP - NBC Sports Philadelphia Plus
                                 '81130': '69734', # NSWAPHD - Monumental Sports Plus
                                 '49925': '49882', # ATTPTHD - SportsNet Pittsburgh
                                 '68797': '58625', # BVO - Bravo
                                 '72360': '61812', # EE  - E!
                                 '50791': '50747', # FOODHD - Food Network
                                 '68602': '58452', # USAN - USA Network
                                 '81949': '70522', # OXG - Oxygen True Crime
                                 '68795': '58623', # SYFY - SYFY
                                 '69896': '59615', # FREFMHD - Freeform
                                 '77475': '66379', # FXXHD - FXX
                                 '49472': '49438', # NGCHD - National Geographic
                                 '126388': '111871', # ACC - ACC Network
                                 '86580': '74885', # DJCHHD - Disney Junior
                                 '68746': '58574', # FXHD - FX
                                 '10171': '59684', # DISN - Disney Channel
                                 '70322': '60006', # DXDHD - Disney XD
                                 '123917': '109605', # FS14K - FS1 4K
                                 '123918': '109606', # FOX4K - FOX 4K
                                 '123916': '109607', # FNBCS4K - NBC Sports 4K
                                 '69551': '59303', # TRAVHD - Travel Channel
                                 '73973': '63236', # BETHD - BET
                                 '69697': '59440', # CMTVHD - CMT
                                 '73033': '62420', # CCHD - Comedy Central
                                 '71401': '60964', # MTVHD - MTV
                                 '69687': '59432', # NIKHD - Nickelodeon
                                 '94767': '82649', # NICJRHD - Nick Jr.
                                 '85147': '73541', # TVLNDHD - TV Land
                                 '70365': '60046', # VH1HD - VH1
                                 '67013': '56905', # DSCHD - Discovery
                                 '67509': '57391', # TLCHD - TLC
                                 '67512': '57394', # APLHD - Animal Planet
                                 '104156': '91588', # UNIVE - NBC Universo
                                 '68703': '58532', # SMITH_HD - Smithsonian Channel
                                 }
        self.timeShift = {'134964': '-2',}

        self.mutex = Lock()

        self.session = requests.Session()
        self.load_device()

    def checkDRM(self, id):
        # print(f"CheckDRM {id}")
        token, error = self.token()
        if error:
            return None, error
        # print(f"Calling for Stream with {id}: {token}")
        stream, error = self.api(f"v3/kgraph/v3/networks/{id}/stream")
        if error:
            return None, error
        return stream.get('streamUrls')[0].get('drmProtected'), None


    def add_stations(self, call_sign, station_id, displayName, networkLogo, group):
        filter_list = list(filter(lambda d: d.get('id') == station_id, self.stations))
        if len(filter_list):
            # print(f'{displayName} in Channel list')
            for elem in self.stations:
                if elem.get('id') == station_id:
                    elem_group = elem.get('group')
                    elem_group.append(group)
                    # print(elem_group)
                    elem.update({'group' : elem_group})
        else:
            self.stations.append({'call_sign': call_sign,
                                  'id': station_id,
                                  'name': displayName,
                                  'logo': networkLogo,
                                  'group': [group],
                                  })
        return()

    def channels(self):
        with self.mutex:
            resp, error = self.api("v3/plan-manager/plans")
            if error:
                return None, error
            resp_user, error = self.api("user")
            if error:
                return None, error
            self.stations = []

            plan_data = resp.get('data')
            user_data = resp_user.get('data')

            for elem in user_data.get('recurly').get('purchased_packages'):
                # print(elem)
                match_filter_list = list(filter(lambda d: d.get('group') == elem, plan_data))
                if len(match_filter_list):
                    # print(f'{elem} In Group')

                    for item in match_filter_list:
                        default_package = item.get('default_package').get('channels')
                        for ch in default_package:
                            self.add_stations(ch.get('call_sign'),
                                              ch.get('station_id'),
                                              ch.get('meta').get('displayName'),
                                              ch.get('meta').get('networkLogoOnWhiteUrl'),
                                              elem)

                        add_on_packages = item.get('add_on_packages')
                        for add_on in user_data.get('recurly').get('purchased_packages'):
                            fubo_extra = list(filter(lambda d: d.get('slug', None) == add_on, add_on_packages))
                            # print(f"    {add_on} part of {elem} add-on package")
                            for extras in fubo_extra:
                                fubo_extra_channels = extras.get('channels')
                                for ch in fubo_extra_channels:
                                    self.add_stations(ch.get('call_sign'),
                                                      ch.get('station_id'),
                                                      ch.get('meta').get('displayName'),
                                                      ch.get('meta').get('networkLogoOnWhiteUrl'),
                                                      add_on)


            for j in self.stations:
                id = j.get('id', '')
                gracenoteId = self.gracenoteID_list.get(str(id), None)
                timeShift = self.timeShift.get(str(id), None)
                if gracenoteId is not None:
                    # print(f"GracenoteID for {j.get('name')} manually mapped to {gracenoteId}" )
                    j.update({'gracenoteId': gracenoteId})
                if timeShift is not None:
                    # print(f"TimeShift Added for {j.get('name')} by {timeShift}" )
                    j.update({'timeShift': timeShift})

            ch_list = self.stations
            # print(json.dumps(self.stations, indent=2, sort_keys=True))
            # print(len(self.stations))
            return ch_list, None

    def watch(self, id):
        with self.mutex:
            token, error = self.token()
            if error:
                return None, error

            stream, error = self.api(f"v3/kgraph/v3/networks/{id}/stream")
            if error:
                return None, error

            url = stream.get('streamUrls')[0].get('url')
            if stream.get('streamUrls')[0].get('drmProtected') is True:
                DRM_Station = list(filter(lambda d: str(d.get('id')) == id, self.stations))
                if not DRM_Station:
                    print(f"Stream {id} is DRM Protected")
                else:
                    print(f"Stream {id} is DRM Protected ({DRM_Station[0].get('call_sign', '')}: {DRM_Station[0].get('name', '')})")
                    print(f"{url}")

                return None, "Stream is DRM Protected"
            return url, None

    def load_device(self):
        with self.mutex:
            try:
                with open("fubo-device.json", "r") as f:
                    self.device = json.load(f)
            except FileNotFoundError:
                self.device = secrets.token_hex(8)
                with open("fubo-device.json", "w") as f:
                    json.dump(self.device, f)

            headers.update({'x-device-id': self.device})

    def token(self):
        if self.sessionID != "" and (time.time() - self.sessionAt) < 4 * 60 * 60:
            return self.sessionID, None
        data = {"email": self.user, "password" : self.passwd}
        # print('Call for sign-in')
        try:
            response = self.session.put('https://api.fubo.tv/signin', json=data, headers=headers)
        except requests.ConnectionError as e:
            print("Connection Error.")
            print(str(e))
            return None, f"Connection Error. {str(e)}"
        # print('Return for sign-in')
        if response.status_code != 200:
            return None, f"HTTP failure {response.status_code}: {response.text}"
        else:
            resp = response.json()

        token = resp.get('access_token', None)
        # print(token)
        self.sessionID = token
        self.sessionAt = time.time()
        return token, None

    def api(self, cmd, data=None):
        token, error = self.token()
        if error:
            return None, error

        if token is not None:
            headers.update({'authorization': f'Bearer {token}'})
        # print(headers)
        url = f"https://api.fubo.tv/{cmd}"
        if data:
            response = self.session.put(url, data=data, headers=headers)
        else:
            response = self.session.get(url, headers=headers)
        if response.status_code != 200:
            return None, f"HTTP failure {response.status_code}: {response.text}"
        return response.json(), None
