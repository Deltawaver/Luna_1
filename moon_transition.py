import math
from math import degrees
import time
import krpc


conn = krpc.connect(name="Orbit Ascent")
vessel = conn.space_center.active_vessel
space_center = conn.space_center
vessel.control.sas = True
vessel.control.sas_mode = vessel.control.sas_mode.prograde
time.sleep(10)

angle = 10
angular_diff = 15
print("Ждем подходящего угла")

while abs(angle+angular_diff) >= 0.1:
    obt_frame = vessel.orbit.body.non_rotating_reference_frame
    srf_frame = vessel.orbit.body.reference_frame
    mun_orbit = conn.space_center.bodies["Mun"].position(obt_frame)

    vessel_orbit = vessel.position(obt_frame)
    mun_orb= ((mun_orbit[0]**2 + mun_orbit[2]**2)**0.5)

    # Расчет Delta-V (изменение скорости) для гомановского перелета
    mu = 3531600000000.0
    r = vessel.orbit.apoapsis
    a1 = vessel.orbit.semi_major_axis
    deltav=math.sqrt(mu/a1)*((math.sqrt(2*mun_orb/(mun_orb+a1)))-1)

    angular_diff = math.pi*((1-(1/(2*math.sqrt(2)))*math.sqrt((a1/mun_orb+1)**3))) # Расчет угла опережения для гомановского перелета

    # Расчет угла между вектором положения корабля и вектором положения Муны
    dot = mun_orbit[0] * vessel_orbit[0] + mun_orbit[2] * vessel_orbit[2]
    det = mun_orbit[0]*vessel_orbit[2] - vessel_orbit[0] *mun_orbit[2]
    angle = math.atan2(det, dot)

    # Расчет времени горения двигателя
    F = vessel.available_thrust
    Isp = vessel.specific_impulse * 9.82
    m0 = vessel.mass
    m1 = m0 / math.exp(deltav/Isp)
    flow_rate = F / Isp
    burn_time = (m0 - m1) / flow_rate
    print("Angle", degrees(angle), "Angle Difference in rad: ", abs(angle+angular_diff))
    time.sleep(1)

print("Начинаем Маневр")
vessel.control.sas_mode = vessel.control.sas_mode.prograde
vessel.control.throttle = 1
time.sleep(burn_time)
vessel.control.throttle = 0

