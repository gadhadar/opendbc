#!/usr/bin/env python3

from opendbc.car import STD_CARGO_KG, structs, get_safety_config, gen_empty_fingerprint, scale_rot_inertia, scale_tire_stiffness
from opendbc.car.interfaces import CarInterfaceBase
from opendbc.car.byd.values import CAR, HUD_MULTIPLIER

TransmissionType = structs.CarParams.TransmissionType  # GR QZWF


class CarInterface(CarInterfaceBase):

    @staticmethod
    def _get_params(ret: structs.CarParams, candidate, fingerprint, car_fw, experimental_long, docs) -> structs.CarParams:
        ret.carName = "byd"
        ret.safetyConfigs = [get_safety_config(
            structs.CarParams.SafetyModel.byd)]
        ret.safetyConfigs[0].safetyParam = 1
        ret.transmissionType = TransmissionType.automatic
        ret.radarOffCan = True
        ret.enableApgs = False                 # advanced parking guidance system
        ret.enableDsu = False                  # driving support unit

        # Lateral MPC cost on steering rate, higher value = sharper turn
        ret.steerRateCost = 0.1
        ret.steerLimitTimer = 0.1              # time before steerLimitAlert is issued
        ret.steerControlType = structs.CarParams.SteerControlType.angle
        ret.steerActuatorDelay = 0.01          # Steering wheel actuator delay in seconds

        ret.enableGasInterceptor = False
        ret.openpilotLongitudinalControl = True

        if candidate == CAR.BYD_ATTO3:
            ret.wheelbase = 2.72
            ret.steerRatio = 16.0
            ret.centerToFront = ret.wheelbase * 0.44
            tire_stiffness_factor = 0.9871
            ret.mass = 2090. + STD_CARGO_KG
            # the HUD odo is exactly 1 to 1 with gps speed
            ret.wheelSpeedFactor = HUD_MULTIPLIER

            # currently not in use, byd is using stock long
            ret.longitudinalTuning.kpBP = [0., 5., 20.]
            ret.longitudinalTuning.kpV = [1.5, 1.3, 1.0]
            ret.longitudinalActuatorDelayLowerBound = 0.3
            ret.longitudinalActuatorDelayUpperBound = 0.4

        else:
            ret.dashcamOnly = True
            ret.safetyModel = structs.CarParams.SafetyModel.noOutput

        # currently not in use, byd is using stock long
        ret.longitudinalTuning.deadzoneBP = [0., 8.05, 20]
        ret.longitudinalTuning.deadzoneV = [0., 0., 0.]
        ret.longitudinalTuning.kiBP = [0., 5., 20.]
        ret.longitudinalTuning.kiV = [0.32, 0.23, 0.12]
        ret.longitudinalTuning.kiV = [0., 0., 0.]

        ret.minEnableSpeed = -1
        ret.enableBsm = True
        ret.stoppingDecelRate = 0.05  # reach stopping target smoothly

        ret.rotationalInertia = scale_rot_inertia(ret.mass, ret.wheelbase)
        ret.tireStiffnessFront, ret.tireStiffnessRear = scale_tire_stiffness(
            ret.mass, ret.wheelbase, ret.centerToFront, tire_stiffness_factor=tire_stiffness_factor)

        return ret

    @staticmethod
    def init(CP, can_recv, can_send):
        return CarInterface(CP, can_recv, can_send)

    # returns a car.CarState
    def update(self, c, can_strings):
        # to receive CAN Messages
        self.cp.update_strings(can_strings)

        ret = self.CS.update(self.cp)
        ret.canValid = self.cp.can_valid
        ret.steeringRateLimited = self.CC.steer_rate_limited if self.CC is not None else False

        # events
        events = self.create_common_events(ret)

        ret.events = events.to_msg()

        self.CS.out = ret.as_reader()
        return self.CS.out

    # pass in a car.CarControl to be called at 100hz
    def apply(self, c):

        isLdw = c.hudControl.leftLaneDepart or c.hudControl.rightLaneDepart

        can_sends = self.CC.update(c.enabled, self.CS, self.frame, c.actuators, c.hudControl.leadVisible,
                                   c.hudControl.rightLaneVisible, c.hudControl.leftLaneVisible, c.cruiseControl.cancel, isLdw, c.laneActive)
        self.frame += 1
        return can_sends
