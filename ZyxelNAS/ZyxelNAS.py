"""Module containing multiple classes to interact with Zyxel NAS"""
# -*- coding:utf-8 -*-
import requests
import urllib3
import json
from wakeonlan import send_magic_packet


class FormatHelper(object):
    """Class containing various formatting functions"""
    @staticmethod
    def bytes_to_readable(num):
        """Converts bytes to a human readable format"""
        if num < 512:
            return "0 Mb"
        elif num < 1024:
            return "1 Mb"

        for unit in [' Kb', ' Mb', ' Gb', ' Tb', ' Pb', ' Eb', ' Zb']:
            if abs(num) < 1024.0:
                return "%3.1f%s" % (num, unit)
            num /= 1024.0
        return "%.1f%s" % (num, 'Yb')

    @staticmethod
    def kilo_bytes_to_megabytes(num):
        """Converts bytes to megabytes"""
        var_mb = num / 1024.0

        return round(var_mb, 1)

    @staticmethod
    def kilo_bytes_to_gigabytes(num):
        """Converts bytes to gigabytes"""
        var_gb = num / 1024.0 / 1024.0

        return round(var_gb, 1)

    @staticmethod
    def kilo_bytes_to_terrabytes(num):
        """Converts bytes to terrabytes"""
        var_tb = num / 1024.0 / 1024.0 / 1024.0

        return round(var_tb, 1)


class ZyxelUtilization(object):
    """Class containing Utilisation data"""

    def __init__(self, raw_input):
        self._data = None
        self.update(raw_input)

    def update(self, raw_input):
        """Allows updating Utilisation data with raw_input data"""
        if raw_input is not None:
            self._data = raw_input['system']

    @property
    def cpu_total_load(self):
        """Total CPU load for Zyxel NAS"""
        if self._data is not None:
            return int(self._data['cpu']['usage'][0:-2])

    @property
    def memory_real_usage(self):
        """Real Memory Usage from Zyxel NAS"""
        if self._data is not None:
            return int(self._data['memory']['usage'][0:-2])

    @property
    def memory_size(self):
        """Total Memory Size of Zyxel NAS"""
        if self._data is not None:
            return int(self._data['memory']['size'][0:-3])

    @property
    def memory_available_real(self):
        """Real available memory"""
        if self._data is not None:
            return int(self._data['memory']['used'][0:-3])

    @property
    def network_up(self):
        """Total upload speed being used"""
        if self._data is not None:
            return float(self._data['connSpeed']['upload'][0:-5])

    @property
    def network_down(self):
        """Total download speed being used"""
        if self._data is not None:
            return float(self._data['connSpeed']['download'][0:-5])

    @property
    def system_status(self):
        """Return system health, ex healthy"""
        if self._data is not None:
            return self._data['status']['sysStatus']

    @property
    def system_status_fan(self):
        """Return system health, ex healthy"""
        if self._data is not None:
            return self._data['status']['speed']

    @property
    def system_status_temp(self):
        """Return system health, ex healthy"""
        if self._data is not None:
            return self._data['status']['temp']


class ZyxelStorage(object):
    """Class containing Storage data"""

    def __init__(self, raw_input):
        self._data = None
        self.update(raw_input)

    def update(self, raw_input):
        """Allows updating Utilisation data with raw_input data"""
        if raw_input is not None:
            self._data = raw_input["storage"]

    @property
    def volumes(self):
        """Returns all available volumes"""
        if self._data is not None:
            volumes = []
            storage_types = ['raidVol', 'groupVol', 'diskGroup']
            for storage_type in storage_types:
                try:
                    for volume in self._data[storage_type]:
                        volumes.append(volume["id"])
                except TypeError:
                    pass
            return volumes

    def _get_volume(self, volume_id):
        """Returns a specific volume"""
        if self._data is not None:
            storage_types = ['raidVol', 'groupVol', 'diskGroup']
            for storage_type in storage_types:
                try:
                    for volume in self._data[storage_type]:
                        if volume["id"] == volume_id:
                            return volume
                except TypeError:
                    pass

    def volume_status(self, volume):
        """Status of the volume (normal, degraded, etc)"""
        volume = self._get_volume(volume)
        if volume is not None:
            return volume["status"]

    def volume_device_type(self, volume):
        """Returns the volume type (RAID1, RAID2, etc)"""
        volume = self._get_volume(volume)
        if volume is not None:
            return volume["raidType"]

    def volume_size_total(self, volume, human_readable=True):
        """Total size of volume"""
        volume = self._get_volume(volume)
        if volume is not None:
            return_data = int(volume["volSize"]["total"])
            if human_readable:
                return FormatHelper.bytes_to_readable(
                    return_data)
            else:
                return return_data

    def volume_size_used(self, volume, human_readable=True):
        """Total used size in volume"""
        volume = self._get_volume(volume)
        if volume is not None:
            return_data = int(volume["volSize"]["used"])
            if human_readable:
                return FormatHelper.bytes_to_readable(
                    return_data)
            else:
                return return_data

    def volume_percentage_used(self, volume):
        """Total used size in percentage for volume"""
        volume = self._get_volume(volume)
        if volume is not None:
            total = int(volume["volSize"]["total"])
            used = int(volume["volSize"]["used"])

            if used is not None and used > 0 and \
               total is not None and total > 0:
                return round((float(used) / float(total)) * 100.0, 1)

    def volume_disk_temp_avg(self, volume):
        """Average temperature of all disks making up the volume"""
        volume = self._get_volume(volume)
        if volume is not None:
            vol_disks = volume["disks"]
            if vol_disks is not None:
                total_temp = 0
                total_disks = 0

                for vol_disk in vol_disks:
                    disk_temp = int(self.disk_temp(vol_disk))
                    if disk_temp is not None:
                        total_disks += 1
                        total_temp += disk_temp

                if total_temp > 0 and total_disks > 0:
                    return round(total_temp / total_disks, 0)

    def volume_disk_temp_max(self, volume):
        """Maximum temperature of all disks making up the volume"""
        volume = self._get_volume(volume)
        if volume is not None:
            vol_disks = volume["disks"]
            if vol_disks is not None:
                max_temp = 0

                for vol_disk in vol_disks:
                    disk_temp = int(self.disk_temp(vol_disk))
                    if disk_temp is not None and disk_temp > max_temp:
                        max_temp = disk_temp

                return max_temp

    @property
    def disks(self):
        """Returns all available (internal) disks"""
        if self._data is not None:
            disks = []
            for disk in self._data["diskInfo"]:
                disks.append(disk["id"])
            return disks

    def _get_disk(self, disk_id):
        """Returns a specific disk"""
        if self._data is not None:
            for disk in self._data["diskInfo"]:
                if disk["id"] == disk_id:
                    return disk

    def disk_name(self, disk):
        """The name of this disk"""
        disk = self._get_disk(disk)
        if disk is not None:
            return disk["modelName"]

    def disk_device(self, disk):
        """The mount point of this disk"""
        disk = self._get_disk(disk)
        if disk is not None:
            return disk["usedBy"]

#     def disk_smart_status(self, disk):
#         """Status of disk according to S.M.A.R.T)"""
#         disk = self._get_disk(disk)
#         if disk is not None:
#             return disk["smart_status"]

    def disk_status(self, disk):
        """Status of disk"""
        disk = self._get_disk(disk)
        if disk is not None:
            return disk["status"]

#     def disk_exceed_bad_sector_thr(self, disk):
#         """Checks if disk has exceeded maximum bad sector threshold"""
#         disk = self._get_disk(disk)
#         if disk is not None:
#             return disk["exceed_bad_sector_thr"]

#     def disk_below_remain_life_thr(self, disk):
#         """Checks if disk has fallen below minimum life threshold"""
#         disk = self._get_disk(disk)
#         if disk is not None:
#             return disk["below_remain_life_thr"]

    def disk_temp(self, disk):
        """Returns the temperature of the disk"""
        disk = self._get_disk(disk)
        if disk is not None:
            return int(disk["temp"])


class ZyxelNAS():
    """Class containing the main Zyxel NAS functions"""

    def __init__(self, zyxel_ip, zyxel_port, username, password,
                 use_https=False, debugmode=False):
        # Store Variables
        self.username = username
        self.password = password
        self.auth = {
            'username': username,
            'password': password,
        }
        self.whoami = {
            'whoami': username
        }
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US;q=0.8,en;q=0.7',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive'
        }
        self.default_params = (
            ('page', '1'),
            ('start', '0'),
            ('limit', '25'),
        )

        # Class Variables
        self._utilisation = None
        self._storage = None
        self._debugmode = debugmode
        self._use_https = use_https

        # Define Session
        self._session_error = False
        self._session = None

        # Build Variables
        if self._use_https:
            # https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings
            # disable SSL warnings due to the auto-genenerated cert
            urllib3.disable_warnings()

            self.base_url = "https://%s:%s" % (zyxel_ip, zyxel_port)
        else:
            self.base_url = "http://%s:%s" % (zyxel_ip, zyxel_port)

    def _debuglog(self, message):
        """Outputs message if debug mode is enabled"""
        if self._debugmode:
            print("DEBUG: " + message)

    def _login(self):
        """Build and execute login request"""
        url = "%s/r51163,/desktop,/cgi-bin/weblogin.cgi" % (
            self.base_url,
        )

        result = self._execute_get_url(url, data=self.auth)

        # Parse Result if valid
        if result is not None:
            self._debuglog("Authentication Succesfull, token: " +
                           str(result.cookies))
            return True
        else:
            self._debuglog("Authentication Failed")
            return False

    def _get_url(self, url, retry_on_error=True, data=None):
        """Function to handle sessions for a GET request"""
        # Check if we failed to request the url or need to login
        if self._session is None or \
           self._session_error:
            # Clear Access Token en reset session error
            self._session_error = False

            # First Reset the session
            if self._session is not None:
                self._session = None
            self._debuglog("Creating New Session")
            self._session = requests.Session()

            # disable SSL certificate verification
            if self._use_https:
                self._session.verify = False

            # We Created a new Session so login
            if self._login() is False:
                self._session_error = True
                self._debuglog("Login Failed, unable to process request")
                return

        # Now request the data
        response = self._execute_get_url(url, data=data)
        if (self._session_error or response is None) and retry_on_error:
            self._debuglog("Error occured, retrying...")
            self._get_url(url, False)

        return response

    def _execute_get_url(self, request_url, data=None):
        """Function to execute and handle a GET request"""
        # Prepare Request
        self._debuglog(
            "Requesting URL: '" + str(request_url) +
            "', msg: '" + str(data) + "'")

        try:
            if data is not None:
                resp = self._session.post(
                    request_url, headers=self.headers, data=data, verify=False)
            else:
                resp = self._session.get(
                    request_url, headers=self.headers,
                    params=self.default_params, verify=False)
            self._debuglog("Request executed: " + str(resp.status_code))
            self._debuglog("Contentet type: " + str(resp.headers))

            if resp.status_code == 200:
                # check if response is ok, not html page
                if "html" not in resp.headers['Content-Type']:
                    # check if json
                    if "json" in resp.headers['Content-Type']:
                        self._debuglog("Response Text: " + str(resp.text))
                        # check if response is data from sensors
                        if "application" in resp.headers['Content-Type']:
                            self._debuglog("Succesfull returning data")
                            return resp.text
                        # check if response is sessions
                        elif "text" in resp.headers['Content-Type']:
                            if "9" in resp.text:
                                self._debuglog("Succesfull session login")
                                return resp
                            else:
                                self._debuglog("Session login error, wrong" +
                                               "or missing. Username: " +
                                               self.username + ", password: " +
                                               self.password)
                        self._session_error = True
                else:
                    self._debuglog("Session error, \
                                   possible session or timeout")
                    self._session_error = True
            else:
                # We got a 404 or 401
                return None
        except KeyError:
            return None
        return None

    def update(self):
        """Updates the various instanced modules"""
        if self._utilisation is not None:
            api = "system_main"
            function = "show_sysinfo"
            url = "%s/cmd,/ck6fup6/%s/%s" % (
                self.base_url,
                api,
                function)
            response = self._get_url(url)
            if not isinstance(response, str):
                self._utilisation.update(response)
            else:
                self._utilisation.update(json.loads(response))
        if self._storage is not None:
            api = "storage_cgi"
            function = "CGIGetAllStorageInfo"
            url = "%s/cmd,/ck6fup6/%s/%s" % (
                self.base_url,
                api,
                function)
            response = self._get_url(url)
            if not isinstance(response, str):
                self._utilisation.update(response)
            else:
                self._storage.update(json.loads(response))

    @property
    def utilisation(self):
        """Getter for various Utilisation variables"""
        if self._utilisation is None:
            api = "system_main"
            function = "show_sysinfo"
            url = "%s/cmd,/ck6fup6/%s/%s" % (
                self.base_url,
                api,
                function)
            self._utilisation = \
                ZyxelUtilization(json.loads(self._get_url(url)))
        return self._utilisation

    @property
    def storage(self):
        """Getter for various Storage variables"""
        if self._storage is None:
            api = "storage_cgi"
            function = "CGIGetAllStorageInfo"
            url = "%s/cmd,/ck6fup6/%s/%s" % (
                self.base_url,
                api,
                function)
            self._storage = \
                ZyxelStorage(json.loads(self._get_url(url)))
        return self._storage

    @property
    def reboot(self):
        return self._shutdown(True)

    @property
    def shutdown(self):
        return self._shutdown(False)

    def _shutdown(self, reboot=False):
        """Shutdown nas"""
        api = "system_main"
        if reboot:
            function = "reboot"
        else:
            function = "shutdown"
        url = "%s/cmd,/ck6fup6/%s/%s" % (
            self.base_url,
            api,
            function)
        resp = self._get_url(url, data=self.whoami)
        try:
            resp_json = json.loads(resp)
        except TypeError:
            resp_json = json.loads(resp.text)
            pass

        self._debuglog(resp_json["errorMsg"])
        if resp_json["errorMsg"] == "OK":
            # Reset the session
            if self._session is not None:
                self._session = None
            self._debuglog("NAS will now %s" % function)
            return True
        return False


class ZyxelPowerOn():

    def __init__(self, mac):
        send_magic_packet(mac)
