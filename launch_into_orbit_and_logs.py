import krpc
import numpy as np
import matplotlib.pyplot as plt
import time

conn = krpc.connect(name="Launch into orbit")

sc = conn.space_center
mj = conn.mech_jeb
ascent = mj.ascent_autopilot

ascent.desired_orbit_altitude = 180000
ascent.desired_inclination = 0
ascent.force_roll = True
ascent.vertical_roll = 90
ascent.turn_roll = 90
ascent.autostage = True
ascent.enabled = True

print("3")
time.sleep(1)
print("2")
time.sleep(1)
print("1")
time.sleep(1)
print("Пуск!")

sc.active_vessel.control.activate_next_stage()

altitude_stream = conn.add_stream(getattr, sc.active_vessel.flight(), "mean_altitude")
speed_stream = conn.add_stream(getattr, sc.active_vessel.flight(sc.active_vessel.orbit.body.reference_frame), "speed")
time_stream = conn.add_stream(getattr, sc.active_vessel, "met")

start_time = time.time()
next_log_time = 1 

time_logger = []
altitude_logger = []
speed_logger = []
mass_logger = []


with conn.stream(getattr, ascent, "enabled") as enabled:
    with enabled.condition:
        while enabled():
            current_time = time.time() - start_time

            altitude = altitude_stream()
            speed = speed_stream()
            flight_time = time_stream()
            mass = sc.active_vessel.mass

            if current_time >= next_log_time:

                time_logger.append(round(flight_time, 2))
                altitude_logger.append(round(altitude, 2))
                speed_logger.append(round(speed, 2))
                mass_logger.append(round(mass, 2))

                next_log_time += 1

            if flight_time > 120:
                break

altitude_stream.remove()
speed_stream.remove()
time_stream.remove()
conn.close()

with open("launch_logs.txt", "w", encoding="UTF-8") as data_file:
    data_file.write(str(time_logger)[1:-1] + "\n")
    data_file.write(str(altitude_logger)[1:-1] + "\n")
    data_file.write(str(speed_logger)[1:-1] + "\n")
    data_file.write(str(mass_logger)[1:-1] + "\n")
    
x = np.linspace(0, time_logger[-1], len(time_logger))  # Общее значение X для всех графиков
y1 = mass_logger  # Первый график: масса
y2 = speed_logger  # Второй график: скорость
y3 = altitude_logger  # Третий график: высота

# Создание фигуры и осей
fig, axs = plt.subplots(3, 1, figsize=(5, 12))

# Первый график
axs[0].plot(x, y1, color="blue", label="Масса", linewidth=2)
axs[0].set_title("График массы (кг)")
axs[0].set_xlabel("Время (сек)")
axs[0].set_ylabel("Масса (кг)")
axs[0].grid()
axs[0].legend()

# Второй график
axs[1].plot(x, y2, color="red", label="Скорость", linewidth=2)
axs[1].set_title("График скорости (м/c)") 
axs[1].set_xlabel("Время (сек)")
axs[1].set_ylabel("Скорость (м/c)")
axs[1].grid()
axs[1].legend()

# Третий график
axs[2].plot(x, y3, color="green", label="Высота", linewidth=2)
axs[2].set_title("График высоты (м)")
axs[2].set_xlabel("Время (сек)")
axs[2].set_ylabel("Высота (м)")
axs[2].grid()
axs[2].legend()

# Настройка общего расстояния между графиками
plt.tight_layout()


# Показ графиков
plt.show()
