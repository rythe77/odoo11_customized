Biometric Device Integration v11
================================
This module integrates Odoo attendance with biometric device attendance.

Features
========
* Ingrates biometric device(Face+Thumb) with HR attendance.
* Support connection with either Domain name or IP.
* Managing attendance automatically.
* Manual/Automatic download attendance data from all your devices.
* Keeps zk machine history in Odoo.
* Option to configure multiple zk devices.
* Option to clear all zk history from both Device and Odoo.
* Check if Device is reachable or not within odoo.
* Automatically rejects double/mistake attendance records.
  eg: (checkin_1 --> checkin_2 --> checkout_1  will be recorded as checkin_1 --> checkout_1 )

Technical Notes
===============
Used Libraries:

*This module uses the pyzk library which is unofficial library of zksoftware (zkteco family) attendance machine.
you can install pyzk library using "sudo pip install pyzk"

Compatible Devices
==================
(check the library github page for more compatible devices.)

Firmware Version : Ver 6.21 Nov 19 2008
Platform : ZEM500
DeviceName : U580 (Works perfectly)

Firmware Version : Ver 6.60 Apr 9 2010
Platform : ZEM510_TFT
DeviceName : T4-C (Works perfectly)

Firmware Version : Ver 6.60 Dec 1 2010
Platform : ZEM510_TFT
DeviceName : T4-C (Works perfectly)

Firmware Version : Ver 6.60 Mar 18 2011
Platform : ZEM600_TFT
DeviceName : iClock260 (Works perfectly)

Platform         : ZEM560_TFT
Firmware Version : Ver 6.60 Feb  4 2012
DeviceName       : (Works perfectly)

Firmware Version : Ver 6.60 Oct 29 2012
Platform : ZEM800_TFT
DeviceName : iFace402/ID (Works perfectly)

Firmware Version : Ver 6.60 Mar 18 2013
Platform : ZEM560
DeviceName : MA300 (Works perfectly)

Firmware Version : Ver 6.60 Dec 27 2014
Platform : ZEM600_TFT
DeviceName : iFace800/ID (Works perfectly)

Firmware Version : Ver 6.60 Jun 16 2015
Platform : JZ4725_TFT
DeviceName : K14 (tested & verified working as expected.)

Firmware Version : Ver 6.60 Nov 6 2017 (remote tested with correct results)
Platform : ZMM220_TFT
DeviceName : (unknown device) (broken info but at least the important data was read)

Firmware Version : Ver 6.60 Jun 9 2017
Platform : JZ4725_TFT
DeviceName : K20 (latest checked correctly!)

Firmware Version : Ver 6.60 Aug 23 2014 
Platform : ZEM600_TFT
DeviceName : VF680 (face device only, but we read the user and attendance list!)

Firmware Version : Ver 6.70 Feb 16 2017
Platform : ZLM30_TFT
DeviceName : RSP10k1 (latest checked correctly!)

Firmware Version : Ver 6.60 Jun 16 2015
Platform : JZ4725_TFT
DeviceName : iClock260 (Works perfectly)

Firmware Version : Ver 6.60 Jun 5 2015
Platform : ZMM200_TFT
DeviceName : iClock3000/ID (Active testing! latest fix)

Firmware Version : Ver 6.70 Jul 12 2013
Platform : ZEM600_TFT
DeviceName : iClock880-H/ID (Active testing! latest fix)

Author
=======
10Orbits Pvt Ltd <erp.10orbits.com>
Based on original work by: < Cybrosys Techno Solutions, Mostafa Shokiel>

Credits
=======
Developer: Mahesh-wor Dhakal <maheshwor89@gmail.com>
pyzk Library: https://github.com/fananimi/pyzk
