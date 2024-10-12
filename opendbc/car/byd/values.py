# QZWF GR

# Updating the code using iXcess Bukapilot as reference

from dataclasses import dataclass, field
# from enum import Enum, IntFlag

# from panda import uds

# from opendbc.car import AngleRateLimit, DbcDict
from opendbc.car import CarSpecs, PlatformConfig, Platforms,  dbc_dict
from opendbc.car.common.conversions import Conversions as CV
from opendbc.car.structs import CarParams
# from opendbc.car.docs_definitions import CarFootnote, Column,
from opendbc.car.docs_definitions import CarDocs, CarParts, CarHarness
# from opendbc.car.fw_query_definitions import FwQueryConfig, Request, StdQueries,p16
from opendbc.car.fw_query_definitions import FwQueryConfig, Request, StdQueries

HUD_MULTIPLIER = 0.718

Ecu = CarParams.Ecu
MIN_ACC_SPEED = 19. * CV.MPH_TO_MS
PEDAL_TRANSITION = 10. * CV.MPH_TO_MS


class CarControllerParams:
    STEER_STEP = 1
    STEER_MAX = 1500
    STEER_ERROR_MAX = 350     # max delta between torque cmd and torque motor

    def __init__(self, CP):
        self.ACCEL_MAX = 2.0
        self.STEER_DELTA_UP = 15       # 1.0s time to peak torque
        # always lower than 45 otherwise the Rav4 faults (Prius seems ok with 50)
        self.STEER_DELTA_DOWN = 25


@dataclass
class BYDCarDocs(CarDocs):
    package: str = "All"
    car_parts: CarParts = field(
        default_factory=CarParts.common([CarHarness.custom]))


@dataclass
class BYDPlatformConfig(PlatformConfig):
    dbc_dict: dict = field(
        default_factory=lambda: dbc_dict('byd_general_pt', None))

    def init(self):
        self.dbc_dict = dbc_dict('byd_general_pt', None)


class CAR(Platforms):
    # BYD ATTO 3
    BYD_ATTO3 = BYDPlatformConfig(
        [
            BYDCarDocs("BYD ATTO 3")
        ],
        CarSpecs(mass=1750, wheelbase=2.72, steerRatio=14.8,
                 tireStiffnessFactor=0.7983),
        dbc_dict('byd_general_pt', None),
    )


# QZWF GR
FW_QUERY_CONFIG = FwQueryConfig(
    requests=[
        Request(
            [StdQueries.UDS_VERSION_REQUEST],
            [StdQueries.UDS_VERSION_RESPONSE],
            bus=0,
        ),
    ],
)

DBC = CAR.create_dbc_map()
