import paho.mqtt.client as mqtt
import json
import matplotlib.pyplot as plt
import datetime

time_hum = []
hum = []
temp = []
time_temp = []

BROKER = "test.mosquitto.org"
TOP_TEMP = "zpi/temperature"
TOP_HUM = "zpi/humidity"


def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode("utf-8"))

    if (msg.topic == TOP_HUM):
        if (len(hum) >= 10):
            hum.pop(0)
            time_hum.pop(0)

        timeVal = data["time"].replace(" ", "\n")
        time_hum.append(timeVal)
        hum.append(data["humidity"])

    elif (msg.topic == TOP_TEMP):
        if (len(temp) >= 10):
            temp.pop(0)
            time_temp.pop(0)

        timeVal = data["time"].replace(" ", "\n")
        time_temp.append(timeVal)
        temp.append(data["temperature"])
    print("Recieved: ", data)


if __name__ == "__main__":
    client = mqtt.Client()

    client.on_message = on_message
    client.connect(BROKER, 1883)
    client.subscribe(TOP_HUM)
    client.subscribe(TOP_TEMP)

    client.loop_start()
    try:
        while (True):
            for time in time_hum:
                dayOfyear, timeOfday = time.split("\n")
                day, month, year = dayOfyear.split(".")
                hour, minut, sec = timeOfday.split(":")
                now = datetime.datetime.now()
                if (now.minute - int(minut) > 10):
                    time_hum.pop(0)
                    hum.pop(0)
                    temp.pop(0)
                    time_temp.pop(0)

            if (len(time_hum) != 0 and len(hum) != 0
                    and len(time_temp) != 0 and len(temp) != 0):
                plt.clf()

                # Humudity graph
                plt.subplot(1, 2, 1)
                plt.plot(time_hum, hum, marker="o")

                plt.xlabel("Time Value")
                plt.ylabel("Humidity Value(%)")
                plt.title("Humidity Graph")
                plt.xticks(rotation=45)
                plt.grid()

                # Temperature graph
                plt.subplot(1, 2, 2)
                plt.plot(time_temp, temp, marker="o")

                plt.xlabel("Time Value")
                plt.ylabel("Temperature Value(°C)")
                plt.title("Temperature Graph")
                plt.xticks(rotation=45)
                plt.grid()

                # show plot
                plt.tight_layout()
                plt.draw()
                plt.pause(1)

            else:
                plt.clf()
                plt.title("Waiting for data....")
                plt.pause(1)
    finally:
        client.loop_stop()
        client.disconnect()
