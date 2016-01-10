# Copyright (c) 2015, SICS Swedish ICT
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the Institute nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE INSTITUTE AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE INSTITUTE OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#
# This file is part of the Contiki operating system.
#
# Author(s): 
#           Janis Judvaitis
#           Atis Elsts <atis.elsts@sics.se>

import os, glob, re
import multiprocessing, subprocess

import codecs
import json

def cp65001(name):
    if name.lower() == 'cp65001':
        return codecs.lookup('utf-8')
codecs.register(cp65001)

FTDI_VENDOR_ID = "0403"
FTDI_PRODUCT_ID = "6001"

doPrintVendorID = False

serial_map = None
def get_serial_map():
    global serial_map
    if serial_map == None:
        wmiout = subprocess.check_output(["powershell",
            "gwmi -query 'SELECT * FROM Win32_PnPEntity WHERE ClassGuid=\"{4d36e978-e325-11ce-bfc1-08002be10318}\"' | ConvertTo-Json"
        ])
        serialjson = json.loads( wmiout.decode("utf-8") )

        serial_map = {}
        map( lambda d: serial_map.update( {comport_name(d): d} ), serialjson)

    return serial_map

def serial_info(key):
    return get_serial_map()[key]

def describe(device):
    """
    Get a human readable description.
    Report driver's Caption property.
    """

    return serial_info(device)["Caption"]

def hwinfo(device):
    ftdipatt = re.compile(r'^FTDIBUS\\VID_(\d{4})\+PID_(\d{4})\+(\w{8}).*')
    matched = re.match(ftdipatt, serial_info(device)["DeviceID"])
    return matched.group(3)

#######################################

def is_nxp_mote(device):
    ftdipatt = re.compile(r'^FTDIBUS\\VID_(\d{4})\+PID_(\d{4})\+(\w{8}).*')
    matched = re.match(ftdipatt, device["DeviceID"])

    if matched == None:
        return False
    if matched.group(1) != FTDI_VENDOR_ID or matched.group(2) != FTDI_PRODUCT_ID:
        return False
    #if device["Manufacturer"] != "NXP":
    #    return False
    return True

def comport_name(device):
    compatt = re.compile(r'.*\((COM\d+)\).*')
    matched = re.match(compatt, device["Caption"])
    if matched == None:
        raise

    return matched.group(1)

def list_motes(flash_programmer):
    return [comport_name(d) for d in get_serial_map().values() if is_nxp_mote(d)]

def extract_information(port, stdout_value):
    mac_str='Unknown' # not supported on Linux
    info='' # not properly supported on Linux

    print(stdout_value)

    macpat = re.compile(r'.*(([0-9A-Fa-f]{2}:){7}([0-9A-Fa-f]){2}).*', re.M)
    matched = re.match(macpat, stdout_value)
    if matched != None:
        mac_str = matched.group(1)

    is_program_success=''

    info = describe(port) + ", SerialID: " + hwinfo(port) + "\n"
    
    for line in stdout_value.split('\n'):
        info = info + re.sub("^\s*%s:\s*" % port, '\t', line) + "\n"

    res = re.compile('(Success)').search(stdout_value)
    if res:
        is_program_success = str(res.group(1))
    else:
        res = re.compile('(Error .*)\n').search(stdout_value)
        if res:
            is_program_success = str(res.group(1))

    return [mac_str, info, is_program_success] 


def program_motes(flash_programmer, motes, firmware_file):
  for m in motes:
      cmd = [flash_programmer, '-V', '10', '-v', '-s', m, '-I', '38400', '-P', '1000000', '-f', firmware_file]
      cmd = " ".join(cmd)
      proc = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,)
      stdout_value, stderr_value = proc.communicate('through stdin to stdout')   
      [mac_str, info, is_program_success] = extract_information(m, stdout_value)
      print m, is_program_success

      errors = (stderr_value)
      if errors != '':
          print 'Errors:', errors  


def print_info(flash_programmer, motes, do_mac_only):
    if do_mac_only:
        print "Listing Mac addresses:"
    else:
        print "Listing mote info:"

    for m in motes:
        cmd=[flash_programmer, '-V', '3', '--deviceconfig', '-s', m]
        proc = subprocess.Popen(cmd, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,)
        stdout_value, stderr_value = proc.communicate('through stdin to stdout')
        [mac_str, info, is_program_success] = extract_information(m, stdout_value)

        if do_mac_only:
            print m, mac_str
        else:
            print m, '\n', info, '\n'

def serialdump(args):
    port_name = args[0]
    serial_dumper = args[1]
    cmd = [serial_dumper, '-b1000000', "/dev/" + port_name.lower()]
    if os.name == "posix" or os.name == "cygwin":
        cmd = " ".join(cmd)
    rv = subprocess.call(cmd, shell=True)

def serialdump_ports(flash_programmer, serial_dumper, ports):
    p = multiprocessing.Pool()
    p.map(serialdump, zip(ports, [serial_dumper] * len(ports)))
    p.close()
