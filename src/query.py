# -*- coding: utf-8 -*-
# -*- style: PEP8 -*-
import json
import os
from __init__ import api
import requests
from tqdm import tqdm
from colorama import Fore, init
import json_parser
import time
import re
import __main__ as main
import tempfile
import pyperclip
from typing import List, Union
from requests.auth import HTTPDigestAuth
iconOK = (Fore.GREEN + '[ok]')
iconNone = (Fore.YELLOW + '[*]')
iconError = (Fore.RED + '[!]')
init(autoreset=True)
fd_default, path_default = tempfile.mkstemp()

# ===================== ************* ===============================
# ----------- using this for testing purpose -----------------------
# ===================== ************* ===============================
# info = {'attackers': '178.128.78.235\n167.99.81.228',
#           'victims': 'SOCUsers',
#           'context': 'dns bidr.trellian.com'}


def print_banner():
    banner = """
          _______
         /      /, 	;___________________;
        /      //  	; Soc-L1-Automation ;
       /______//	;-------------------;
      (______(/	            danieleperera
      """
    return banner


def get_api():
    # os platform indipendent
    APIpath = os.path.join(api, "api.json")
    with open(APIpath, "r") as f:
        contents = f.read()
        # print(contents)
        data = json.loads(contents)
        # print(data)
        return data


def progressbar_ip(ip_addresses):
    for i in tqdm(ip_addresses, unit="data"):
        time.sleep(0.1)
        pass

# ===================== ************* =================================
# ------- Get IP addresses information form api -----------------------
# ===================== ************* =================================


def virustotal_query(
        query: str,
        query_type: str,
        val: bool,
        sha_sum: list = None) -> dict:
    """
    Documentation for ip_urlhaus.
    It gets one ip addresse at a time as a string,
    uses request to do a get request to ip_urlhaus,
    gets json as text.

    param
        ip: str -- This is a string variable.

    example::

    ```
     ip = '124.164.251.179'
    ```

    return
    dict -- Returns json as a dict.

    """
    # --- Header data ---
    header_whois = (
        '\nWhois Information ' + query + '\n')
    # --- API info ---
    data = get_api()
    api = (data['API info']['virustotal']['api'])
    # --- Color printing ---
    colorQuery = (Fore.RED + query)
    colorString = (Fore.GREEN + 'VirusTotal')
    # --- Status ---
    print(iconNone + ' ' + colorString, end='')
    print(' checking WhoIs Information for ' + colorQuery)
    if query_type == "domain":
        query_domain = data['API info']['virustotal']['query_domain']
        # The data to post
        params = {'apikey': api, 'domain': query}
        response = requests.get(query_domain, params=params)
    elif query_type == "ip":
        query_ip = (data['API info']['virustotal']['query_ip'])
        params = {'apikey': api, 'ip': query}
        response = requests.get(query_ip, params=params)
    elif query_type == 'sha':
        query_sha = (data['API info']['virustotal']['file_url'])
        params = {'apikey': api, 'resource': query}
        response = requests.get(query_sha, params=params)
    else:
        return

    if val:
        return create_tmp_to_clipboard(
            response.json(),
            header_whois,
            val,
            None)
    else:
        status, parsed_Data = json_parser.parse_virustotal(
            response.json(),
            query)
        if status == 'ok':
            return create_tmp_to_clipboard(
                parsed_Data,
                header_whois,
                val,
                'print_table')
        elif status == 'KeyError':
            return create_tmp_to_clipboard(
                parsed_Data,
                header_whois,
                val,
                None)


def iphub_query(
        query: str,
        type: str,
        val: bool,
        sha_sum: list = None) -> dict:
    header_spoofed_IPhub = (
        '\n\nVPN/Proxy/Tor Information IPhub '
        + query + '\n')
    data = get_api()
    api = (data['API info']['iphub']['api'])
    colorQuery = (Fore.RED + query)
    colorString = (Fore.GREEN + 'IPhub')
    print(iconNone + ' ' + colorString, end='')
    print(' checking proxy or spoofed ' + colorQuery)
    if type == "domain":
        print(Fore.RED + '[x] IPhub does not check domains')
    elif type == "ip":
        query_ip = data['API info']['iphub']['query_ip']
        url = query_ip+query
        headers = {
                    'X-Key': api}
        response = requests.get(url, headers=headers)

        if val:
            return create_tmp_to_clipboard(
                response.json(),
                header_spoofed_IPhub,
                val,
                None)
        else:
            return create_tmp_to_clipboard(
                json_parser.parse_iphub(response.json(), query),
                header_spoofed_IPhub,
                val,
                'normal')


def getipintel_query(
        query: str,
        type: str,
        val: bool,
        sha_sum: list = None) -> dict:
    header_spoofed_getipintel = (
        'VPN/Proxy/Tor Information GetIPintel '
        + query + '\n')
    data = get_api()
    email = data['API info']['getipintel']['email']
    colorQuery = (Fore.RED + query)
    colorString = (Fore.GREEN + 'GetIPintel')
    print(iconNone + ' ' + colorString, end='')
    print(' checking Proxy VPN Tor ' + colorQuery)
    if type == "domain":
        print(Fore.RED + '[x] GetIPintel does not check domains')
    elif type == "ip":
        query_ip = data['API info']['getipintel']['query_ip']
        url = query_ip.format(query, email)
        response = requests.get(url)

        if val:
            return create_tmp_to_clipboard(
                response.json(),
                header_spoofed_getipintel,
                val,
                None)
        else:
            return create_tmp_to_clipboard(
                json_parser.parse_getipintel(response.json(), query),
                header_spoofed_getipintel,
                val,
                'normal')


"""
def fofa_query(query: str, type: str, val: bool, sha_sum: list = None) -> dict:
    data = get_api()
    email = data['API info']['fofa']['email']
    api_key = data['API info']['fofa']['api']
    colorQuery = (Fore.RED + query)
    print(iconNone, end='')
    print(' Checking fofa for ' + colorQuery)
    b64query = base64.b64encode(query)
    print(b64query)
    if type == "domain" or type == "ip":
        query_all = data['API info']['fofa']['query_all']
        params = {
            'email': email,
            'key': api_key,
            'qbase64': b64query
        }

        response = requests.get(query_all, params=params)

        if val:
            return response.json()
        else:
            pass

"""


def threatminer_query(
        query: str,
        type: str,
        val: bool,
        sha_sum: list = None) -> dict:
    data = get_api()
    header_info2 = (
        'Report tagging information/IOCs '
        + query + '\n')

    colorQuery = (Fore.RED + query)
    colorString = (Fore.GREEN + 'Threatminer')
    print(iconNone + ' ' + colorString, end='')
    print(' Report tagging information/IOCs information ' + colorQuery)

    if type == "domain":
        pass
    elif type == "ip":
        query_ip = data['API info']['threatminer']['query_ip']
        url = query_ip.format(query)
        response = requests.get(url)
        data_json = response.json()
        if data_json['status_code'] == '200':
            if val:
                return create_tmp_to_clipboard(
                    response.json(),
                    header_info2,
                    val,
                    None)
            else:
                return create_tmp_to_clipboard(
                    json_parser.parse_threatminer(response.json(), query),
                    header_info2,
                    val,
                    'normal')
        else:
            pass

            


def threatcrowd_query(
        query: str,
        type: str,
        val: bool,
        sha_sum: list = None) -> dict:
    data = get_api()
    header_status = (
        'Current status information '
        + query + '\n')
    colorQuery = (Fore.RED + query)
    colorString = (Fore.GREEN + 'Threatcrowd')
    print(iconNone + ' ' + colorString, end='')
    print(' checking current status' + colorQuery)

    if type == "domain":
        pass
    elif type == "ip":
        query_all = data['API info']['threatcrowd']['query_ip']
        params = {
            'ip': query,
        }

        response = requests.get(query_all, params=params)

    if val:
        return create_tmp_to_clipboard(
            response.json(),
            header_status,
            val,
            None)
    else:
        return create_tmp_to_clipboard(
                json_parser.parse_threatcrowd(response.json(), query),
                header_status,
                val,
                'normal')
        


def abuseipdb_query(
        query: str,
        type: str,
        val: bool,
        sha_sum: list = None) -> dict:
    """
    Documentation for ip_abuseipdb.
    It gets one ip addresse at a time as a string,
    uses request to do a get request to abuseip_db,
    gets json as text.

    param
        ip: str -- This is a string variable.

    example::

    ```
     ip = '124.164.251.179'
    ```

    return
    dict -- Returns json as a dict.

    """
    header_blacklisted = (
        'Blacklisted Data '
        + query + '\n')
    data = get_api()
    colorQuery = (Fore.RED + query)
    colorString = (Fore.GREEN + 'Abuseipdb')
    print(iconNone + ' ' + colorString, end='')
    print(' checking blacklisted ' + colorQuery)
    if type == "domain":
        print(Fore.RED + '[x] AbuseIPdb does not check domains')
    elif type == "ip":
        # --- abuseipdb data ----
        api = (data['API info']['abuseipdb']['api'])
        url = (data['API info']['abuseipdb']['url'])
        request_url = url.replace("API", api)
        final_url = request_url.replace("IP", query)
        # --- Add Timeout for request ---
    else:
        pass
    try:
        response = requests.get(final_url, timeout=10)
        print(response)
        if val:
            return create_tmp_to_clipboard(
                response.json(),
                header_blacklisted,
                val,
                None)
        else:
            status, parsed_Data = json_parser.parse_abuseipdb(
                response.json(),
                query)
        if status == 'ok':
            return create_tmp_to_clipboard(
                parsed_Data,
                header_blacklisted,
                val,
                'normal')
        elif status == 'KeyError':
            return create_tmp_to_clipboard(
                parsed_Data,
                header_blacklisted,
                val,
                None)     
    except requests.exceptions.Timeout:
        print(Fore.RED + 'Timeout error occurred for AbuseIPdb')
        return


def urlscan_query(
        query: str,
        type: str,
        val: bool,
        sha_sum: list = None) -> dict:
    """
    Documentation for ip_urlscan.
    It gets one ip addresse at a time as a string,
    uses request to do a get request to ip_urlscan,
    gets json as text.

    param
        ip: str -- This is a string variable.

    example::

    ```
     ip = '124.164.251.179'
    ```

    return
    dict -- Returns json as a dict.

    """
    header_info = (
        'Suspicious connections '
        + query + '\n')
    data = get_api()
    colorQuery = (Fore.RED + query)
    colorString = (Fore.GREEN + 'URLscan')
    print(iconNone + ' ' + colorString, end='')
    print(' Suspicious connections ' + colorQuery)
    if type == "domain":
        query_domain = data['API info']['urlscan.io']['query_domain']
        requests_url = query_domain+query
        info_json = requests.get(requests_url)
        response = json.loads(info_json.text)
    elif type == "ip":
        # --- urlscan.io ok----
        query_ip = data['API info']['urlscan.io']['query_ip']
        requests_url = query_ip+query
        response = requests.get(requests_url)
    
    jdata = response.json()
    if jdata['total'] == 0:
        print('no info')
    else:
        if val:
            return create_tmp_to_clipboard(
                response.json(),
                header_info,
                val,
                None)
        else:
            status, parsed_Data = json_parser.parse_urlscan(
                response.json(),
                query)
            if status == 'ok':
                return create_tmp_to_clipboard(
                    parsed_Data,
                    header_info,
                    val,
                    'print_row_table')
            elif status == 'KeyError':
                return create_tmp_to_clipboard(
                    parsed_Data,
                    header_info,
                    val,
                    None)


def urlhause_query(
        query: str,
        type: str,
        val: bool,
        sha_sum: list = None) -> dict:
    """
    Documentation for ip_urlhaus.
    It gets one ip addresse at a time as a string,
    uses request to do a get request to ip_urlhaus,
    gets json as text.

    param
        ip: str -- This is a string variable.

    example::

    ```
     ip = '124.164.251.179'
    ```

    return
    dict -- Returns json as a dict.

    """
    header_spread = (
        'IP address/Domain was used to spread malware '
        + query + '\n')
    data = get_api()
    colorQuery = (Fore.RED + query)
    colorString = (Fore.GREEN + 'UrlHause')
    print(iconNone + ' ' + colorString, end='')
    print(
        ' checking IP address/Domain was used to spread malware '
        + colorQuery)
    if type == "domain" or type == "ip":
        # --- urlhaus data ok ----
        querry_host_url = (data['API info']['urlhaus']['querry_host_url'])
        params = {"host": query}
        response = requests.post(querry_host_url, params)
    elif type == "url":
        data = {"host": query}
    else:
        pass
    jdata = response.json()
    if jdata['query_status'] != 'ok':
        print('no info')
    else:   
        if val:
            return create_tmp_to_clipboard(
                response.json(),
                header_spread,
                val,
                None)
        else:
            status, parsed_Data = json_parser.parse_urlhause(
                response.json(),
                query)
            if status == 'ok':
                return create_tmp_to_clipboard(
                    parsed_Data,
                    header_spread,
                    val,
                    'print_row_table')
            elif status == 'KeyError':
                return create_tmp_to_clipboard(
                    parsed_Data,
                    header_spread,
                    val,
                    None)


def domain_virustotal(
        domain: str,
        boolvalue: bool,
        sha_sum: list = None) -> dict:
    """
    Documentation for ip_urlhaus.
    It gets one ip addresse at a time as a string,
    uses request to do a get request to ip_urlhaus,
    gets json as text.

    param
        ip: str -- This is a string variable.

    example::

    ```
     ip = '124.164.251.179'
    ```

    return
    dict -- Returns json as a dict.

    """
    if sha_sum is None:
        # --- virustotal data ---
        data = get_api()
        api = (
            data['API info']['virustotal']['api'])
        domain_address_url = (
            data['API info']['virustotal']['domain_address_url'])

        # https://developers.virustotal.com/v2.0/reference#comments-get

        params = {'apikey': api, 'domain': domain}
        response_domain = requests.get(domain_address_url, params=params)
        if boolvalue:
            return response_domain.json(), response_domain.json()
        else:
            return None
            # querry_status_virustotal_domain(response_domain.json(), domain)
    else:
        print(sha_sum)
        # --- virustotal data ---
        data = get_api()
        api = (data['API info']['virustotal']['api'])
        ip_address_url = (data['API info']['virustotal']['ip_address_url'])
        domain_address_url = (
            data['API info']['virustotal']['domain_address_url'])

        # https://developers.virustotal.com/v2.0/reference#comments-get

        params_domain = {'apikey': api, 'domain': domain}
        params_file = {'apikey': api, 'resource': sha_sum}
        response_domain = requests.get(ip_address_url, params=params_domain)
        response_file = requests.get(domain_address_url, params=params_file)

        if boolvalue:
            return domain_address_url.json(), response_file.json()
        else:
            return None
            # querry_status_virustotal_domain(
            # domain_address_url.json(), domain),
            # querry_status_virustotal_file(response_file.json())
    """
        for x in context:
        params = {'apikey': api, 'resource': x}
        response = requests.get(scan_url, params=params)
        print(response.json())
    """


def shodan_query(
        query: str,
        type: str,
        val: bool,
        sha_sum: list = None) -> dict:
    # --- API info ---
    header_compromised = (
        'Compromised Information '
        + query + '\n')
    data = get_api()
    api_key = data['API info']['shodan']['api']
    # print
    colorQuery = (Fore.RED + query)
    colorString = (Fore.GREEN + 'Shodan')
    print(iconNone + ' ' + colorString, end='')
    print(
        ' Checking information about host and see if it was compromised '
        + colorQuery)
    if type == "domain":
        data = {"domain": query}  # The data to post
    elif type == "ip":
        url = data['API info']['shodan']['query_ip'].format(
            query,
            api_key)
        response = requests.get(url)
    else:
        return

    if val:
        return create_tmp_to_clipboard(
            response.json(),
            header_compromised,
            val,
            None)
    else:
        status, parsed_Data = json_parser.parse_shodan(
            response.json(),
            query)
        if status == 'ok':
            return create_tmp_to_clipboard(
                parsed_Data,
                header_compromised,
                val,
                'print_table')
        elif status == 'KeyError':
            return create_tmp_to_clipboard(
                parsed_Data,
                header_compromised,
                val,
                None)


def apility_query(
        query: str,
        type: str,
        val: bool,
        sha_sum: list = None) -> dict:
    # --- API info ---
    header_reputation = (
        'Reputation and activity through time '
        + query + '\n')
    data = get_api()
    api_key = data['API info']['apility']['api']
    # print
    colorQuery = (Fore.RED + query)
    colorString = (Fore.GREEN + 'Apility')
    print(iconNone + ' ' + colorString, end='')
    print(' checking reputation and activity through time ' + colorQuery)
    if type == "domain":
        data = {"domain": query}  # The data to post
    elif type == "ip":
        get_url_ip = data['API info']['apility']['url_ip_request']
        headers = {'Accept': 'application/json', 'X-Auth-Token': api_key}
        #print(headers)
        url = get_url_ip+query
        #print(url)
        response = requests.get(url, headers=headers)
        #print(response.url)
        #print(response.status_code)
        #print(response.content)
        # --- Always giving 400 status code check why
        if response.status_code == 200:
            if val:
                return create_tmp_to_clipboard(
                    response.json(),
                    header_reputation,
                    val,
                    None)
            else:
                return create_tmp_to_clipboard(
                    json_parser.parse_apility(response.json(), query),
                    header_reputation,
                    val,
                    'print_row_table')
        elif response.status_code == 400:
            #print('maybe ip clean')
            return create_tmp_to_clipboard(
                    'not sufficient data is availiable\n',
                    header_reputation,
                    val,
                    'n/a')
        else:
            pass


def hybrid_query(
        query: str,
        type: str,
        val: bool,
        sha_sum: list = None) -> dict:
    # --- API info ---
    header_association = (
        'Association with malware information '
        + query + '\n')
    data = get_api()
    api_key = data['API info']['hybrid']['api']
    # printing name
    colorQuery = (Fore.RED + query)
    colorString = (Fore.GREEN + 'Hybrid')
    print(iconNone + ' ' + colorString, end='')
    print(' checking association with malware ' + colorQuery)

    if type == "domain":
        data = {"domain": query}  # The data to post
    elif type == "ip":
        url = data['API info']['hybrid']['query_ip']
        url_query_ip = url + query
        # The api url
        headers = {
            "user-agent": "VxApi Connector"}
        # The request headers
        response = requests.post(
            url_query_ip,
            headers=headers,
            auth=HTTPDigestAuth(api, 'secret'))
        #print(response.status_code)
        #print(response.content)
        """
    else:qqq
        pass
    if val:
        return create_tmp_to_clipboard(
                response.json(),
                header_association,
                val,
                None)
    else:
        return create_tmp_to_clipboard(
                json_parser.parse_hybrid(response.json(), query),
                header_association,
                val,
                'print_row_table')"""
        

# ===================== ************* ===============================
# -----------Working and testing from here on -----------------------
# ===================== ************* ===============================
# http://check.getipintel.net/check.php?ip=66.228.119.72&contact=mr.px0r@gmail.com&format=json


"""
# print(fofa_query(ip, 'ip', True))


"""
# table_reputation = printTable_row(test5)
# table_reputation = printTable_row(test6)

# ===================== ************* ===============================
# ---------- Various Checks and printing ticket --------------------
# ===================== ************* ===============================


def get_ip(ip: dict) -> str:
    """
    Documentation for get_ip.
    It uses a dictionary and check whether,
    the key attackers is empty or not.
    If it's empty then prints No attacker ip found,
    else returns a ip address as string.

    param
        ip: dict -- This is a dictionary variable.

    example::

    ```
     ip[attackers] = {'124.164.251.179',
                      '179.251.164.124.adsl-pool.sx.cn'},
    ```

    return
    str -- Returns only ip addresses as a string.

    """
    if ip['attackers'] == "":
        print("No attacker ip found...")
    else:
        # print(ip['attackers'])
        return ip['attackers']


def text_header(head):
    test = '''### Attackers ->{}
### Victims   ->{}
### Context   ->{}\n'''.format(
                head.get("attackers", "Not found!"),
                head.get("victims", "Not found!"),
                head.get("context", "Not found!"))
    print(test)
    return test


def text_body(body):
    try:
        for key, val in body.items():
            yield (('\n{} -> {}').format(key, val))
    except AttributeError:
        pass


def text_body_table(body: dict):
    try:
        for key, val in body.items():
            yield [str(key), str(val)]
    except AttributeError:
        print('attribute error')
        pass


def check_ip(ipv4_address):
    test = []
    for i in ipv4_address.split(","):
        # print(i)
        regex_ipv4_public = (r"""^([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(?<!172\.(16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31))(?<!127)(?<!^10)(?<!^0)\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(?<!192\.168)(?<!172\.(16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31))\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(?<!\.255$)$""")
        matches_public = re.finditer(regex_ipv4_public, i, re.MULTILINE)

        for x in matches_public:
            test.append(("{match}".format(match=x.group())))
    return test


def manual_mode_ip(ip_addr: list, verbosity: bool, sha_sum: list = None):
    # check if argpase values are null
    if ip_addr is None:
        ip = ''
        while True:
            print(iconNone, end='')
            ip = input(' Insert a list of potential malicious ip addresses:')
            datalist = ip.split(",")
            if check_ip(ip) == []:
                print(iconError, end='')
                print(" Not valid ip address have been insert, please re-try")
                continue
            else:
                break
        ip_addr = [item.replace(' ', '') for item in datalist]
        simple_dict = {'attackers': ip_addr}
        main.collector(simple_dict, verbosity)
    else:
        # --- Complete manual mode ---
        ip_addr = [item.replace(' ', '') for item in ip_addr]
        simple_dict = {'attackers': ip_addr}
        if sha_sum == []:
            return main.collector(simple_dict, verbosity)
        else:
            return main.collector(simple_dict, verbosity, sha_sum)


def verbose_mode(verbosity: bool) -> bool:
    if verbosity:
        # print("Flag non c'è")   verbosity minima
        return False
    else:
        # print("Flag c'è")   verbosity massima
        return True


def printTable(tbl: Union[str, List[Union[str, List[str]]]], borderHorizontal='-', borderVertical='|', borderCross='+'):
    if isinstance(tbl, str):
        tbl = tbl.split('\n')
    string = ''
    try:
        # get the rows split by the values
        rows = []
        for row in tbl:
            if isinstance(row, str):
                row = row.split(', ')
            rows.append(row)

        # find the longests strings
        lenghts = [[] for _ in range(len(max(rows, key=len)))]
        for row in rows:
            for idx, value in enumerate(row):
                lenghts[idx].append(len(value))
        lengths = [max(lenght) for lenght in lenghts]

        # create formatting string with the length of the longest elements
        f = borderVertical + borderVertical.join(' {:>%d} ' % l for l in lengths) + borderVertical
        s = borderCross + borderCross.join(borderHorizontal * (l+2) for l in lengths) + borderCross
        string += s + '\n'
        print(s)
        for row in rows:
            string += f.format(*row) + '\n'
            print(f.format(*row))
            string += s + '\n'
            print(s)
        return string
    except ValueError:
        print('Value error')
        create_tmp_to_clipboard(tbl, 'test header', False, 'error')
        pass


def printTable_row(
        tbl,
        borderHorizontal='-',
        borderVertical='|',
        borderCross='+'):
    string = ''
    try:
        cols = [list(x) for x in zip(*tbl)]
        lengths = [max(map(len, map(str, col))) for col in cols]
        f = borderVertical + borderVertical.join(
            ' {:>%d} ' % l for l in lengths) + borderVertical
        s = borderCross + borderCross.join(
            borderHorizontal * (l+2) for l in lengths) + borderCross
        string += s + '\n'
        print(s)
        for row in tbl:
            string += f.format(*row) + '\n'
            print(f.format(*row))
            string += s + '\n'
            print(s)
        return string
    except TypeError:
        print('TypeError')
        #create_tmp_to_clipboard(tbl, 'test header', False, 'error1')
        pass


def check_domain_or_ip(data: list) -> str:
    ip = []
    for i in data:
        regex_ipv4_public = (r"""^([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(?<!172\.(16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31))(?<!127)(?<!^10)(?<!^0)\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(?<!192\.168)(?<!172\.(16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31))\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(?<!\.255$)$""")
        matches_public = re.finditer(regex_ipv4_public, i, re.MULTILINE)
        for x in matches_public:
            ip.append(("{match}".format(match=x.group())))

    yield ip, 'ip'
    domain = []
    for z in data:
        # print(z)
        regex_domain = r"^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$"
        matches_domain = re.finditer(regex_domain, z, re.MULTILINE)
        for f in matches_domain:
            domain.append(("{match}".format(match=f.group())))
    # print(domain)
    yield domain, 'domain'


def check_query_type(data: list) -> str:
    for string in data:
        ipv4_pattern = (r"""^([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(?<!172\.(16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31))(?<!127)(?<!^10)(?<!^0)\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(?<!192\.168)(?<!172\.(16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31))\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(?<!\.255$)$""")
        matches_public = re.search(ipv4_pattern, string)
        if matches_public:
            yield matches_public.group(0), 'ip' # or i instead of matches_public.group(0)

        domain_pattern = r"^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$"
        matches_domain = re.search(domain_pattern, string)
        if matches_domain:
            yield matches_domain.group(0), 'domain'

        hash_pattern = (r"[a-f0-9]{32,128}")
        match_hash = re.search(hash_pattern, string, re.IGNORECASE)
        if match_hash:
            yield match_hash.group(0), 'hash'


# ===================== ************* ===============================
# ----------Copy information to tmp file and then to clipboard--------------------
# ===================== ************* ===============================
def create_tmp_to_clipboard(
        data: dict,
        header_data: str,
        val: bool,
        print_type: str,
        path: str = path_default,
        fd: int = fd_default) -> None:
    try:
        with os.fdopen(fd, 'a+', encoding='utf-8', closefd=False) as tmp:
            if val:
                tmp.write('\n')
                tmp.write(header_data)
                tmp.write('\n')
                tmp.write(json.dumps(data))
                tmp.write('\n')
                pass
            else:
                # print with tables and what i think is usefull
                if print_type == 'print_table':
                    #print('print_table')
                    #print(type(data))
                    tableContent = text_body_table(data)
                    #print(type(tableContent))
                    tmp.write('\n')
                    tmp.write(header_data)
                    tmp.write('\n')
                    tmp.write('{}'.format(printTable(tableContent)))
                    pass
                elif print_type == 'print_row_table':
                    tmp.write('\n')
                    tmp.write(header_data)
                    tmp.write('\n')                                   
                    tableContentRow = printTable_row(data)
                    tmp.write('{}'.format(tableContentRow))
                    pass
                elif print_type == 'error':
                    for i in data:
                        tmp.write(i)
                elif print_type == 'error1':
                    tmp.write(data)
                elif print_type == 'normal':
                    tmp.write('\n')
                    tmp.write(header_data)
                    tmp.write('\n')
                    for i in text_body(data):
                        tmp.write(i)
                    tmp.write('\n')
                elif print_type == 'n/a':
                    tmp.write('\n')
                    tmp.write(header_data)
                    tmp.write('\n')
                    tmp.write(data)
                else:
                    tmp.write('\n')
                    tmp.write(header_data)
                    tmp.write('\n')
                    tmp.write(json.dumps(data))
                    tmp.write('\n')
                pass
            #  ===================== ************* ===========================
            # ------ IP addresses are getting worked here --------------------
            # ===================== ************* ============================
            # ip_addresses = info['attackers']
            # tmp.write(text_header(info))
            tmp.seek(0)
            content = tmp.read()
            pyperclip.copy(content)
            tmp.close()
    finally:
        # print(path)
        #time.sleep(20)
        """
        if content == '':
            print('\n' + iconError + ' No ticket was copied to clipboard')
            print("\n\nRemoving tmp files... Please wait")
        else:
            print('\n' + iconOK, end='')
            print(' Ticket was copied to clipboard successfully')
            print("\n\nRemoving tmp files... Please wait")
        #os.remove(path)
        """
        pass

"""
test_dic = {'ciao mondo': 25}
create_tmp_to_clipboard(test_dic, 'test header', False, 'error')
"""
"""

ip = '60.160.182.113'


domain = 'atracktr.info'
virustotal_query(ip, 'ip', False)
#progressbar_ip(ip)

iphub_query(ip, 'ip', False)
#progressbar_ip(ip)


getipintel_query(ip, 'ip', False)
#progressbar_ip(ip)

shodan_query(ip, 'ip', False)
#progressbar_ip(ip)


threatcrowd_query(ip, 'ip', False)
#progressbar_ip(ip)


hybrid_query(ip, 'ip', False)
#progressbar_ip(ip)


apility_query(ip, 'ip', False)
#progressbar_ip(ip)

abuseipdb_query(ip, 'ip', False)
#progressbar_ip(ip)

urlscan_query(ip, 'ip', False)
#progressbar_ip(ip)

urlhause_query(ip, 'ip', False)
#progressbar_ip(ip)


threatminer_query(ip, 'ip', False)
#progressbar_ip(ip)"""