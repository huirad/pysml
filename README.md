# pysml
Decoder library for SML (Smart Meter Language)

## What and why
Goal of this project is to create a compact python library for decoding SML output from a electric power meter or at least for the one which I am using (the EMH ED300L).

Side goal is to improve my personal skills in python programming.

## References Hardware

* [Volkszaehler::Hardware](http://wiki.volkszaehler.org/hardware/controllers/ir-schreib-lesekopf-usb-ausgang)
* [Weidmann::IR Schreib/Lesekopf USB (Optokopf)](https://shop.weidmann-elektronik.de/index.php?page=product&info=24)
* [German Metering OP-210](http://www.optical-probe.de/Optical%20probes/op200.html)

## References Software
From [Volkszaehler::Software](http://wiki.volkszaehler.org/software/sml#beispiel_1emh_ed300l)

* [libsml](https://github.com/volkszaehler/libsml)
* [SMLlib](https://github.com/tobiasjeske/SMLlib)

## References Protocol

* [Technische Richtlinie BSI TR-03109-1](https://www.bsi.bund.de/SharedDocs/Downloads/DE/BSI/Publikationen/TechnischeRichtlinien/TR03109/TR-03109-1_Anlage_Feinspezifikation_Drahtgebundene_LMN-Schnittstelle_Teilb.pdf?__blob=publicationFile) - the main specification
* [DLMS blue book](https://www.dlms.com/files/Blue-Book-Ed-122-Excerpt.pdf) - contains OBIS codes and measurement units
* [EDI@Energy Codeliste der OBIS-Kennzahlen für den deutschen Energiemarkt](https://www.edi-energy.de/index.php?id=38&tx_bdew_bdew%5Buid%5D=64&tx_bdew_bdew%5Baction%5D=download&tx_bdew_bdew%5Bcontroller%5D=Dokument&cHash=d2cc24364c4712ad83676043d5cc02f5)
* [Beschreibung SML Datenprotokoll für SMART METER](http://itrona.ch/stuff/F2-2_PJM_5_Beschreibung%20SML%20Datenprotokoll%20V1.0_28.02.2011.pdf)

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

## References Protocol Analyis

* [Stefan Weigert](http://www.stefan-weigert.de/php_loader/sml.php) - great approach, Python script
* [msxfaq.de 1](https://www.msxfaq.de/sonst/bastelbude/smartmeter_d0_sml_protokoll.htm)
* [msxfaq.de 2](https://www.msxfaq.de/sonst/bastelbude/smartmeter_d0_sml.htm)
* [volkszaehler.org](https://wiki.volkszaehler.org/hardware/channels/meters/power/edl-ehz/emh-ehz-h1)
* [schatenseite.de](http://www.schatenseite.de/2016/05/30/smart-message-language-stromzahler-auslesen/)
* [kabza.de](http://www.kabza.de/MyHome/SmartMeter.html)

## ED300L specific Links

* [EMH ED300L](https://www.emh-metering.de/produkte/smart-meter/ed300l)
* [Data Sheet](https://www.emh-metering.de/images/Produkt-Dokumentation/Haushaltsz%C3%A4hler/ED300L/ED300L-G-DAB-D-1.00.pdf)
* [User Manual](https://www.emh-metering.de/images/Produkt-Dokumentation/Haushaltsz%C3%A4hler/ED300L/ED300L-G+ED300S-G-BIA-D-1.00.pdf)
* [Produkthandbuch](https://www.ewh.de/fileadmin/user_upload/Stromnetz/Zaehlerstaende/Produktbeschreibung_EMH_ED300L_.pdf) - section 5.3 contains list of data sets
* [Another list of the parameters](http://web1.heissa.de/ED300L.pdf)

## Simple Test: readout data with Linux command line

After plugging, the Weidmann Lesekopf is available as ``` /dev/ttyUSB0 ```

First set the device to 9600 bit/s, raw mode. In particular the raw mode is important!

* ` stty -F /dev/ttyUSB0 9600 `
* ` stty -F /dev/ttyUSB0 raw `

Now read out the data and pipe through hexdump for nice formatting

* ` cat /dev/ttyUSB0 | hexdump -e '16/1 "%02x " "\n"' `

Or store it directly in a binary file for later analysis

* ` cat /dev/ttyUSB0 > edl300_raw.bin `

## Own software - requirements

* Python - portable between Windows/Linux/Raspberry Pi
* Simple - no full SML decoder to reduce complexity
* Robust - even if the ED300L specific format is assumed: implement saninty checks (expected values, crc)
