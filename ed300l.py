#!/usr/bin/python3

#######################################################################
#
# Copyright (C) 2020, Helmut Schmidt
#
# License:
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
#######################################################################

"""Read and decode the SML output of the EMH ED300L electric power meter.
Extract the current power consumption and the total energy consumption.

Usage example: 
    python3 ed300l.py -d /dev/ttyUSB0

## Design goals: 
* Simplicity: no full SML decoder - assume the ED300L specific format
* Robustness: implement at least some sanity checks (expected values, crc)

## SML Protocol References

* [Technische Richtlinie BSI TR-03109-1](https://www.bsi.bund.de/SharedDocs/Downloads/DE/BSI/Publikationen/TechnischeRichtlinien/TR03109/TR-03109-1_Anlage_Feinspezifikation_Drahtgebundene_LMN-Schnittstelle_Teilb.pdf?__blob=publicationFile) - the main specification
* [DLMS blue book](https://www.dlms.com/files/Blue-Book-Ed-122-Excerpt.pdf) - contains OBIS codes and measurement units
* [EDI@Energy Codeliste der OBIS-Kennzahlen fuer den deutschen Energiemarkt](https://www.edi-energy.de/index.php?id=38&tx_bdew_bdew%5Buid%5D=64&tx_bdew_bdew%5Baction%5D=download&tx_bdew_bdew%5Bcontroller%5D=Dokument&cHash=d2cc24364c4712ad83676043d5cc02f5)
* [Beschreibung SML Datenprotokoll fuer SMART METER](http://itrona.ch/stuff/F2-2_PJM_5_Beschreibung%20SML%20Datenprotokoll%20V1.0_28.02.2011.pdf)

On OBIS codes from [DLMS blue book](https://www.dlms.com/files/Blue-Book-Ed-122-Excerpt.pdf)

* An OBIS code consists of 6 octets A B C D E F
* section 6 / 6.3.2 / 7.2.1: general structure
* section 7.5: A = 1: Electricity
  * section 7.5.1: C = 1: Active Power +
  * section 7.5.1: C = 2: Active Power -
  * section 7.5.2.1: D = 8: Time Integral 1
  * section 7.5.3.2: E = 0: Total
  * section 7.5.3.2: E = 1: Rate 1
  * section 7.5.3.2: E = 2: Rate 2

"""

__author__ = "Helmut Schmidt, https://github.com/huirad"
__version__ = "0.1"
__date__ = "2020-01-05"
__credits__ = "Copyright: Helmut Schmidt. License: MPLv2"

#######################################################################
#
# Module-History
#  Date         Author              Reason
#  04-Jan-2020  Helmut Schmidt      v0.1 Initial version - not many sanity checks
#  05-Jan-2020  Helmut Schmidt      v0.2 Improve Robustness
#  05-Jan-2020  Helmut Schmidt      v0.3 Improve Robustness
#
#######################################################################

#The program starts here
import serial, argparse, sys, datetime

#global variables
verbose = 0     #debug level

def dump(buf, prefix, cond):
    """Dump a byte array as hex

    Parameters
    ----------
    buf: bytes
        byte array to be dumped
    prefix: string
        a prefix string to be pre-pended the dump
    cond: boolean
        only if this condition is met, the dump will be printed
    
    """ 
    
    if cond and buf:
        print(prefix, "(", len(buf), "):", buf.hex())
        

def openSerial(device):
    """Open the serial device

    Parameters
    ----------
    device: string
        serial device name
    
    Returns
    -------
    Serial
        On succes: serial device handle
    None
        On failure
    """    
    
    result = None # default result
    
    try:
        #For reading 316 bytes at 9600 baud, less than 1 second should be sufficient
        #But the messages cycle time is 2.x seconds - so take this + some headroom
        result = serial.Serial(device, 9600, timeout=2+1)
    except (serial.SerialException):
        pass
    return result


def readSMLTransportMessage(ser):
    """Read the next SML transport message from the serial device

    Parameters
    ----------
    ser: Serial
        serial device handle
    
    Returns
    -------
    bytes
        On succes: The complete SML transport message.
    None
        On failure
    """

    result = None # default result
    max_read = 5 #limit the number of read attemps to avoid endless loop
    
    startMessage = b'\x01\x01\x01\x01'
    escapeSequence = b'\x1b\x1b\x1b\x1b'
    endMessageB1 = b'\x1a'
    #search for the 1st escape sequence - it may be for start or end
    t_esc_found = False
    while not t_esc_found and (max_read > 0):
        t_esc = ser.read_until(escapeSequence)
        max_read -= 1
        t_esc_found = t_esc.endswith(escapeSequence)
        dump(t_esc, "t_esc", verbose >=2)
    #search for the packet starting with startMessage and ending with escapeSequence
    t_msg_found = False
    while t_esc_found and (not t_msg_found) and (max_read > 0):
        t_msg = ser.read_until(escapeSequence)
        max_read -= 1
        t_msg_found = t_msg.startswith(startMessage)
        dump(t_msg, "t_msg", verbose >=2)
    #sverify that the terminating escapeSequence is followed by endMessageB1
    t_end_found = False
    if t_msg_found and (max_read > 0):
        t_end = ser.read(4)
        t_end_found = t_end.startswith(endMessageB1)
        dump(t_end, "t_end", verbose >=2)
    if t_end_found:
        result = escapeSequence + t_msg + t_end

    return result


def getOctetString(buffer, offset):
    """Get the octet string value from the buffer at the given offset.

    Parameters
    ----------
    buffer: bytes
        the buffer
    int: offset
        the offset
    
    Returns
    -------
    bytes
        On succes: The extracted octet string value.
    None
        On failure
    """

    result = None # default result
    
    if (len(buffer)-offset) < 2:
        pass
    elif (buffer[offset] & 0xF0) == 0x00: # octet string up to 15 bytes
        size = (buffer[offset] & 0x0F) # size including the 1-byte tag
        if (len(buffer)-offset) >= size:
            result = buffer[offset+1:offset+size]
    elif (buffer[offset] & 0xF0) == 0x80: # larger octet string
        pass # not yet handled
    return result

def getInt(buffer, offset):
    """Get the integer value from the buffer at the given offset.
    Size and signed-ness are determined automatically

    Parameters
    ----------
    buffer: bytes
        the buffer
    int: offset
        the offset
    
    Returns
    -------
    bytes
        On succes: The extracted integer value.
    None
        On failure
    """

    result = None # default result
    
    if (len(buffer)-offset) < 2:
        pass
    elif (buffer[offset] & 0xF0) == 0x50: # signed integer
        size = (buffer[offset] & 0x0F) # size including the 1-byte tag
        if (len(buffer)-offset) >= size:
            tmp = buffer[offset+1:offset+size]
            result = int.from_bytes(tmp, byteorder='big', signed=True)
    elif (buffer[offset] & 0xF0) == 0x60: # unsigned integer
        size = (buffer[offset] & 0x0F) # size including the 1-byte tag
        if (len(buffer)-offset) >= size:
            tmp = buffer[offset+1:offset+size]
            result = int.from_bytes(tmp, byteorder='big', signed=False)  
    return result

def getIntTest():
    """ Module test for getInt 
    """

    # first some values starting at index 0 
    i = getInt(b'\x56\x00\x04\xeb\x09\x6c',0)
    assert (i == 82512236)
    i = getInt(b'\x52\xff',0)
    assert (i == -1)
    i = getInt(b'\x62\x1e',0)
    assert (i == 30)
    i = getInt(b'\x65\x0c\x6a\x50\xb5',0)
    assert (i == 208294069)

    # too short stuff
    i = getInt(b'\x56\x00\x04\xeb\x09',0)
    assert (i == None)
    i = getInt(b'\x65\x0c\x6a',0)
    assert (i == None)
    
    # now with indexes > 0
    i = getInt(b'\xaa\xbb\x56\x00\x04\xeb\x09\x6c',2)
    assert (i == 82512236)
    i = getInt(b'\x00\x52\xff',1)
    assert (i == -1)
    i = getInt(b'\x01\xff\x33\x62\x1e',3)
    assert (i == 30)
    i = getInt(b'\xab\xcd\x87\x44\x65\x0c\x6a\x50\xb5',4)
    assert (i == 208294069)
    
    # now with stuff appended
    i = getInt(b'\x56\x00\x04\xeb\x09\x6c\x12\x34',0)
    assert (i == 82512236)
    i = getInt(b'\xaa\xbb\x52\xff\xcc\xdd',2)
    assert (i == -1)
    i = getInt(b'\x52\x62\x1e\x99',1)
    assert (i == 30)
    i = getInt(b'\x65\x0c\x6a\x50\xb5\x77\x88',0)
    assert (i == 208294069)

def assert_python3():
    """ Assert that at least Python 3.5 is used
    """        
    assert(sys.version_info.major == 3)
    assert(sys.version_info.minor >= 5)
    
#some hard-coded offsets
OF_reqFileId = 27
OF_secIndex = 84
OF_OID_energyTotal = 132
OF_unit_energyTotal = 143
OF_scaler_energyTotal = 145
OF_energyTotal = 147
OF_OID_powerCurrent = 197
OF_unit_powerCurrent = 206
OF_scaler_powerCurrent = 208
OF_powerCurrent = 210

#some hard-coded OIDs
OID_energyTotal = b'\x01\x00\x01\x08\x00\xff'
OID_powerCurrent = b'\x01\x00\x0f\x07\x00\xff'

################################ MAIN #################################
def main():
    """ Main function
    """
    parser = argparse.ArgumentParser(description='Read out the EMH ED300L electric power meter')
    parser.add_argument('-d', '--device', '--port', required=True, help='name of serial port device, e.g. /dev/ttyUSB0 for Linux or COM3 for Windows')
    parser.add_argument('-v', '--verbose', action='count', help='verbosity level')
    args = parser.parse_args()

    if args.verbose:
        global verbose
        verbose = args.verbose
    
    #output variables
    error = None
    reqFileId = None
    secIndex = None
    energyTotal = None
    powerCurrent = None


    if args.device:	
        ser = openSerial(args.device)
        if ser:
            t_msg = readSMLTransportMessage(ser)        
            if t_msg:      
                dump(t_msg, "SMLTransportMessage", verbose >=1)
                #dump(t_msg[27:34], "reqFileId", True) 
                reqFileId = getOctetString(t_msg, OF_reqFileId) # looks like this is always incremented by 2 
                secIndex = getInt(t_msg, OF_secIndex) # looks like this is always incremented by 2 or 3 or 4
                if ((getOctetString(t_msg, OF_OID_energyTotal) == OID_energyTotal) 
                    and (getInt(t_msg, OF_unit_energyTotal) == 30)
                    and (getInt(t_msg, OF_scaler_energyTotal) == -1)):
                    energyTotal = getInt(t_msg, OF_energyTotal)
                if ((getOctetString(t_msg, OF_OID_powerCurrent) == OID_powerCurrent) 
                    and (getInt(t_msg, OF_unit_powerCurrent) == 27)
                    and (getInt(t_msg, OF_scaler_powerCurrent) == -1)):                    
                    powerCurrent = getInt(t_msg, OF_powerCurrent)
            else:
                error = "ERR_MESG"
        else:
            error = "ERR_DEVICE"
    else:
        error = "ERR_OPEN"

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

    if error is None:
        print(now, "OK", reqFileId.hex(), secIndex, powerCurrent, energyTotal)
    else:
        print(now, error)

if __name__ == "__main__":
    # ensure that we are really running python 3, not python 2
    assert_python3()  
    main()