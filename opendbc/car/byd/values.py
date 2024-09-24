# flake8: noqa
"""
This module defines constants and mappings for the BYD ATTO 3 car model used in the OpenPilot project.

Classes:
  CAR: A class containing constants for different car models.

Constants:
  HUD_MULTIPLIER (float): A multiplier constant used for the HUD (Head-Up Display).
  FINGERPRINTS (dict): A dictionary containing CAN message fingerprints for the BYD ATTO 3. Each key is a car model, and the value is a list of dictionaries where each dictionary represents a set of CAN message IDs and their corresponding lengths.
  DBC (dict): A dictionary mapping car models to their corresponding DBC (Database Container) files. The DBC files define the structure of CAN messages for the car.

Imports:
  from selfdrive.car import dbc_dict: Imports the dbc_dict function from the selfdrive.car module.
  from cereal import car: Imports the car module from the cereal package.

Usage:
  This module is used to provide car-specific constants and mappings for the BYD ATTO 3 model in the OpenPilot project. The FINGERPRINTS dictionary is used to identify the car model based on CAN message IDs, and the DBC dictionary provides the corresponding DBC file for decoding CAN messages.
"""

#Rewriting the code using Toyota as a reference.
# from selfdrive.car import dbc_dict
# from cereal import car

import re
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, IntFlag

from opendbc.car import CarSpecs, PlatformConfig, Platforms, AngleRateLimit, dbc_dict
from opendbc.car.common.conversions import Conversions as CV
from opendbc.car.structs import CarParams
from opendbc.car.docs_definitions import CarFootnote, CarDocs, Column, CarParts, CarHarness
from opendbc.car.fw_query_definitions import FwQueryConfig, Request, StdQueries


HUD_MULTIPLIER = 0.718

Ecu = CarParams.Ecu
MIN_ACC_SPEED = 19. * CV.MPH_TO_MS
PEDAL_TRANSITION = 10. * CV.MPH_TO_MS
#https://en.wikipedia.org/wiki/BYD_Atto_3
class CarControllerParams:
  STEER_STEP = 1
  STEER_MAX = 1500
  STEER_ERROR_MAX = 350     # max delta between torque cmd and torque motor

  # Lane Tracing Assist (LTA) control limits
  # Assuming a steering ratio of 13.7:
  # Limit to ~2.0 m/s^3 up (7.5 deg/s), ~3.5 m/s^3 down (13 deg/s) at 75 mph
  # Worst case, the low speed limits will allow ~4.0 m/s^3 up (15 deg/s) and ~4.9 m/s^3 down (18 deg/s) at 75 mph,
  # however the EPS has its own internal limits at all speeds which are less than that:
  # Observed internal torque rate limit on TSS 2.5 Camry and RAV4 is ~1500 units/sec up and down when using LTA
  ANGLE_RATE_LIMIT_UP = AngleRateLimit(speed_bp=[5, 25], angle_v=[0.3, 0.15])
  ANGLE_RATE_LIMIT_DOWN = AngleRateLimit(speed_bp=[5, 25], angle_v=[0.36, 0.26])

  def __init__(self, CP):
      if CP.flags:
        self.ACCEL_MAX = 2.0
      else:
        self.ACCEL_MAX = 1.5  # m/s2, lower than allowed 2.0 m/s^2 for tuning reasons
      self.ACCEL_MIN = -3.5  # m/s2

      if CP.lateralTuning.which() == 'torque':
        self.STEER_DELTA_UP = 15       # 1.0s time to peak torque
        self.STEER_DELTA_DOWN = 25     # always lower than 45 otherwise the Rav4 faults (Prius seems ok with 50)
      else:
        self.STEER_DELTA_UP = 10       # 1.5s time to peak torque
        self.STEER_DELTA_DOWN = 25     # always lower than 45 otherwise the Rav4 faults (Prius seems ok with 50)



@dataclass
class BYDCarDocs(CarDocs):
  package: str = "All"
  car_parts: CarParts = field(default_factory=CarParts.common([CarHarness.custom]))

@dataclass
class BYDPlatformConfig(PlatformConfig):
  dbc_dict: dict = field(default_factory=lambda: dbc_dict('byd_general_pt', None))

  def init(self):
    self.dbc_dict = dbc_dict('byd_general_pt', None)



class CAR(Platforms):
  #BYD ATTO 3
  ATTO3 = BYDPlatformConfig(
    [
      BYDCarDocs("BYD ATTO 3")
    ],
  CarSpecs(mass=1750, wheelbase=2.72, steerRatio=14.8, tireStiffnessFactor=0.7983),
  dbc_dict('byd_general_pt', None),
  )


FINGERPRINTS = {
  CAR.ATTO3: [{
    85: 8, 140: 8, 204: 20, 213: 8, 287: 5, 289: 8, 290: 8, 291: 8, 301: 8, 307: 8, 309: 8, 324: 8, 327: 8, 337: 8, 356: 8, 371: 8, 384: 8, 385: 3, 410: 8, 418: 8, 450: 8, 482: 8, 496: 8, 508: 8, 522: 8, 536: 8, 537: 8, 544: 8, 546: 8, 547: 8, 576: 8, 577: 8, 578: 8, 588: 8, 629: 8, 638: 8, 639: 8, 660: 8, 665: 8, 682: 2, 692: 8, 694: 8, 724: 8, 748: 8, 786: 8, 790: 8, 792: 8, 797: 8, 798: 8, 800: 8, 801: 8, 802: 8, 803: 8, 812: 8, 813: 8, 814: 8, 815: 8, 827: 8, 828: 8, 829: 8, 833: 8, 834: 8, 835: 8, 836: 8, 843: 8, 847: 8, 848: 8, 854: 8, 860: 8, 863: 8, 879: 8, 884: 8, 906: 8, 944: 8, 951: 8, 965: 8, 973: 8, 985: 8, 1004: 8, 1020: 8, 1023: 8, 1028: 8, 1031: 8, 1036: 8, 1037: 8, 1040: 8, 1048: 8, 1052: 8, 1058: 8, 1074: 8, 1076: 8, 1098: 8, 1107: 8, 1141: 8, 1168: 8, 1178: 8, 1184: 8, 1189: 8, 1192: 8, 1193: 8, 1211: 8, 1215: 8, 1217: 8, 1246: 8, 1269: 8, 1274: 8, 1278: 8, 1297: 8, 1298: 8, 1319: 8, 1322: 8, 1542: 2, 1590: 8, 1687: 8, 1792: 8, 1798: 3, 1799: 8, 1810: 8, 1813: 8, 1824: 8, 1832: 8, 1840: 8, 1856: 8, 1858: 8, 1859: 8, 1862: 8, 1872: 8, 1879: 8, 1888: 8, 1892: 8, 1927: 8, 1937: 8, 1953: 8, 1968: 8, 1988: 8, 2000: 8, 2001: 8, 2004: 8, 2012: 8, 2015: 8, 2016: 8, 2017: 8, 2024: 8, 2027: 8
  },
  {
    85: 8, 140: 8, 213: 8, 287: 5, 289: 8, 290: 8, 291: 8, 301: 8, 307: 8, 309: 8, 324: 8, 327: 8, 330: 8, 337: 8, 356: 8, 371: 8, 384: 8, 385: 3, 410: 8, 418: 8, 432: 8, 450: 8, 482: 8, 496: 8, 508: 8, 522: 8, 536: 8, 537:      8, 544: 8, 546: 8, 547: 8, 576: 8, 577: 8, 578: 8, 588: 8, 629: 8, 638: 8, 639: 8, 660: 8, 665: 8, 682: 2, 692: 8, 694: 8, 724: 8, 748: 8, 786: 8, 790: 8, 792: 8, 797: 8, 798: 8, 800: 8, 801: 8, 802: 8, 803: 8, 812: 8, 813: 8, 814:      8, 815: 8, 831: 8, 833: 8, 834: 8, 835: 8, 836: 8, 843: 8, 847: 8, 848: 8, 854: 8, 860: 8, 863: 8, 879: 8, 884: 8, 906: 8, 944: 8, 951: 8, 965: 8, 973: 8, 985: 8, 1004: 8, 1020: 8, 1023: 8, 1028: 8, 1031: 8, 1036: 8, 1037: 8, 1040:      8, 1048: 8, 1052: 8, 1058: 8, 1074: 8, 1076: 8, 1098: 8, 1107: 8, 1141: 8, 1178: 8, 1184: 8, 1189: 8, 1193: 8, 1211: 8, 1215: 8, 1217: 8, 1246: 8, 1274: 8, 1278: 8, 1297: 8, 1319: 8, 1322: 8, 1542: 2, 1798: 3, 1824: 8, 1832: 8
  }],
}

# In a Data Module, an identifier is a string used to recognize an object,
# either by itself or together with the identifiers of parent objects.
# Each returns a 4 byte hex representation of the decimal part number. `b"\x02\x8c\xf0'"` -> 42790951
BYD_BOOT_SOFTWARE_PART_NUMER_REQUEST = b'\x1a\xc0'  # likely does not contain anything useful
BYD_SOFTWARE_MODULE_1_REQUEST = b'\x1a\xc1'
BYD_SOFTWARE_MODULE_2_REQUEST = b'\x1a\xc2'
BYD_SOFTWARE_MODULE_3_REQUEST = b'\x1a\xc3'

# Part number of XML data file that is used to configure ECU
BYD_XML_DATA_FILE_PART_NUMBER = b'\x1a\x9c'
BYD_XML_CONFIG_COMPAT_ID = b'\x1a\x9b'  # used to know if XML file is compatible with the ECU software/hardware

# This DID is for identifying the part number that reflects the mix of hardware,
# software, and calibrations in the ECU when it first arrives at the vehicle assembly plant.
# If there's an Alpha Code, it's associated with this part number and stored in the DID $DB.
BYD_END_MODEL_PART_NUMBER_REQUEST = b'\x1a\xcb'
BYD_END_MODEL_PART_NUMBER_ALPHA_CODE_REQUEST = b'\x1a\xdb'
BYD_BASE_MODEL_PART_NUMBER_REQUEST = b'\x1a\xcc'
BYD_BASE_MODEL_PART_NUMBER_ALPHA_CODE_REQUEST = b'\x1a\xdc'
BYD_FW_RESPONSE = b'\x5a'

BYD_FW_REQUESTS = [
  BYD_BOOT_SOFTWARE_PART_NUMER_REQUEST,
  BYD_SOFTWARE_MODULE_1_REQUEST,
  BYD_SOFTWARE_MODULE_2_REQUEST,
  BYD_SOFTWARE_MODULE_3_REQUEST,
  BYD_XML_DATA_FILE_PART_NUMBER,
  BYD_XML_CONFIG_COMPAT_ID,
  BYD_END_MODEL_PART_NUMBER_REQUEST,
  BYD_END_MODEL_PART_NUMBER_ALPHA_CODE_REQUEST,
  BYD_BASE_MODEL_PART_NUMBER_REQUEST,
  BYD_BASE_MODEL_PART_NUMBER_ALPHA_CODE_REQUEST,
]

BYD_RX_OFFSET = 0x400

FW_QUERY_CONFIG = FwQueryConfig(
  requests=[request for req in BYD_FW_REQUESTS for request in [
    Request(
      [StdQueries.SHORT_TESTER_PRESENT_REQUEST, req],
      [StdQueries.SHORT_TESTER_PRESENT_RESPONSE, BYD_FW_RESPONSE + bytes([req[-1]])],
      rx_offset=BYD_RX_OFFSET,
      bus=0,
      logging=True,
    ),
  ]],
  extra_ecus=[(Ecu.fwdCamera, 0x24b, None)],
)


#This file is located in the /opendbc/dbc/ folder
# DBC = {
#   CAR.ATTO3: dbc_dict('byd_general_pt', None),
# }
DBC = CAR.create_dbc_map()
