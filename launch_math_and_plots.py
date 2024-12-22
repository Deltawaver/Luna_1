import matplotlib.pyplot as plt
import numpy as np
import math

delta = 1

# Функция плотности атмосферы (по таблице)
def q_f(h):
    if h < 2500:
        return 1.225
    elif h < 5000:
        return 0.898
    elif h < 7500:
        return 0.642
    elif h < 10000:
        return 0.446
    elif h < 15000:
        return 0.288
    elif h < 20000:
        return 0.108
    elif h < 25000:
        return 0.04
    elif h < 30000:
        return 0.015
    elif h < 40000:
        return 0.006
    elif h < 50000:
        return 0.001
    else:
        return 0


# Функция силы гравитации
def F_gr(m, h):
    G = 6.6743 * 10**-11
    M = 5.2915158 * 10**22
    R = 600000
    Fgr = G * ((M * m) / ((R + h) ** 2))
    return Fgr


# Функция силы сопротивления
def F_s(q, v):
    c = 0.47
    r = 2
    S = 3.1415 * r**2
    Fs = c * S * q * v**2 / 2
    return Fs


# Функция ускорения
def ax_f(h, q, vx, power, m, fi):
    Fgr = F_gr(m, h)
    Fs = F_s(q, vx)
    Ft_max = 1428000
    a = (power * Ft_max * math.cos(math.radians(fi)) / 100 + Fgr * math.cos(math.radians(-90)) + Fs*math.cos(math.radians(fi - 180))) / m
    return a

def ay_f(h, q, vy, power, m, fi):
    Fgr = F_gr(m, h)
    Fs = F_s(q, vy)
    Ft_max = 1428000
    a = (power * Ft_max * math.sin(math.radians(fi))/ 100 + Fgr * math.sin(math.radians(-90)) + Fs*math.sin(math.radians(fi - 180))) / m
    return a


# Функция скорости
def v_f(t, power, h, vx, vy, m, fi, delta):
    q = q_f(h)
    v = math.sqrt(vx**2 + vy**2)
    ax = ax_f(h, q, vx, power, m, fi)
    ay = ay_f(h, q, vy, power, m, fi)
    vx = vx + ax * delta
    vy = vy + ay * delta
    v = math.sqrt(vx**2 + vy**2)
    return [vx, vy, v]


# Функция изменения угла
def fi_f(t):
    fi = math.exp((-1) * t / 140) * 90
    return fi

# Начальные данные
h = 250
vx = 0
vy = 0
m = 78400
power = 100
t = 0
fi = 90
fl_st = 0
fl_pw = 0
fl_angle1 = 0
fl_angle2 = 0
prev_h = 0

speed_data = []
altitude_data = []
mass_data = []
time_data = []
fi_data = []

while t <= 140:
    fi = fi_f(t)
    if t < 61: # До отсоединения первой ступени
        n = 565 * power / 100
        vf = v_f(t, power, h, vx, vy, m, fi, delta)
    else: # После отсоединения первой ступени
        n = 130 * power / 100
        vf = v_f(t, power/5, h, vx, vy, m, fi, delta)
    vx = vf[0]
    vy = vf[1]
    h += vy * delta
    m = m - n * delta
    if t == 61:
        m = 30300

    time_data.append(t)
    altitude_data.append(h)
    speed_data.append(vf[2])
    mass_data.append(m)
    fi_data.append(fi)

    t += delta


time_logger = []
altitude_logger = []
speed_logger = []
mass_logger = []

with open('launch_logs.txt', 'r', encoding='UTF-8') as data_file:
    time_logger = [float(i) for i in data_file.readline().split(", ")]
    altitude_logger = [float(i) for i in data_file.readline().split(", ")]
    speed_logger = [float(i) for i in data_file.readline().split(", ")]
    mass_logger = [float(i) for i in data_file.readline().split(", ")]


# Построение графиков
time_math = np.linspace(0, time_data[-1], len(time_data))
time_KSP = np.linspace(0, time_logger[-1], len(time_logger))
fig, axs = plt.subplots(3, 2, figsize=(5, 24))


# Масса от времени (Мат. модель)
axs[0][0].plot(time_math, mass_data, color="blue", label="Мат. модель", linewidth=2)
axs[0][0].set_title("График массы (кг)")
axs[0][0].set_xlabel("Время (с)")
axs[0][0].set_ylabel("Масса (кг)")
axs[0][0].grid()
axs[0][0].legend()


# Скорость от времени (Мат. модель)
axs[1][0].plot(time_math, speed_data, color="red", label="Мат. модель", linewidth=2)
axs[1][0].set_title("График скорости (м/c)") 
axs[1][0].set_xlabel("Время (с)")
axs[1][0].set_ylabel("Скорость (м/c)")
axs[1][0].grid()
axs[1][0].legend()

# Высота от времени (Мат. модель)
axs[2][0].plot(time_math, altitude_data, color="pink", label="Мат. модель", linewidth=2)
axs[2][0].set_title("График высоты (м)")
axs[2][0].set_xlabel("Время (с)")
axs[2][0].set_ylabel("Высота (м)")
axs[2][0].grid()
axs[2][0].legend()


# Масса от времени (KSP + Мат. модель)
axs[0][1].plot(time_math, mass_data, color="blue", label="Мат. модель", linewidth=2)
axs[0][1].plot(time_KSP, mass_logger, "--", color="green", label=f"KSP", linewidth=2)
axs[0][1].set_title("График массы (кг)")
axs[0][1].set_xlabel("Время (с)")
axs[0][1].set_ylabel("Масса (кг)")
axs[0][1].grid()
axs[0][1].legend()

# Скорость от времени (KSP + Мат. модель)
axs[1][1].plot(time_math, speed_data, color="red", label="Мат. модель", linewidth=2)
axs[1][1].plot(time_KSP, speed_logger, "--", color="orange", label="KSP", linewidth=2)
axs[1][1].set_title("График скорости (м/c)") 
axs[1][1].set_xlabel("Время (с)")
axs[1][1].set_ylabel("Скорость (м/c)")
axs[1][1].grid()
axs[1][1].legend()

# Высота от времени (KSP + Мат. модель)
axs[2][1].plot(time_math, altitude_data, color="pink", label="Мат. модель", linewidth=2)
axs[2][1].plot(time_KSP, altitude_logger, "--", color="purple", label="KSP", linewidth=2)
axs[2][1].set_title("График высоты (м)")
axs[2][1].set_xlabel("Время (с)")
axs[2][1].set_ylabel("Высота (м)")
axs[2][1].grid()
axs[2][1].legend()



plt.tight_layout()
plt.show()