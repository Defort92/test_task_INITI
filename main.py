import asyncio


class Event:
    def __init__(self, sender_id, cars_waiting=0, pedestrians_waiting=0, light_state="RED"):
        self.sender_id = sender_id
        self.cars_waiting = cars_waiting
        self.pedestrians_waiting = pedestrians_waiting
        self.light_state = light_state


class TrafficLight:
    def __init__(self, light_id, event_loop, paired_light=None):
        self.id = light_id
        self.state = "RED"
        self.queue = asyncio.Queue()
        self.event_loop = event_loop
        self.cars_waiting = 0
        self.pedestrians_waiting = 0
        self.paired_light = paired_light

    async def listen(self):
        while True:
            event = await self.queue.get()
            print(f"Svetofor {self.id} received event from {event.sender_id} - State: {event.light_state}")
            await self.process_event(event)

    async def process_event(self, event):
        if event.light_state == "GREEN" and self.state == "RED":
            print(f"Svetofor {self.id} stays RED because Svetofor {event.sender_id} is GREEN.")
        elif event.light_state == "RED" and self.state == "RED":
            print(f"Svetofor {self.id} can turn GREEN now because Svetofor {event.sender_id} is RED.")
            await self.switch_to_green()

    async def switch_to_green(self):
        print(f"Svetofor {self.id} switching to GREEN.")
        self.state = "GREEN"
        await asyncio.sleep(5)
        self.state = "RED"
        print(f"Svetofor {self.id} switching to RED.")

    async def send_event(self, receiver_light):
        event = Event(sender_id=self.id, cars_waiting=self.cars_waiting, pedestrians_waiting=self.pedestrians_waiting, light_state=self.state)
        await receiver_light.queue.put(event)
        print(f"Svetofor {self.id} sent event to Svetofor {receiver_light.id}")

    async def control_light(self, other_lights):
        while True:
            if self.paired_light:
                # Если светофор парный, считаем общий вес
                paired_weight = self.calculate_weight() + self.paired_light.calculate_weight()
                if self.should_switch(other_lights, paired_weight):
                    await self.switch_to_green()
            else:
                if self.should_switch(other_lights, self.calculate_weight()):
                    await self.switch_to_green()
            await asyncio.sleep(1)

    def calculate_weight(self):
        return self.cars_waiting * 4 + self.pedestrians_waiting

    def should_switch(self, other_lights, current_weight):
        max_weight = current_weight
        for light in other_lights:
            if light.paired_light:
                paired_weight = light.calculate_weight() + light.paired_light.calculate_weight()
                max_weight = max(max_weight, paired_weight)
            else:
                max_weight = max(max_weight, light.calculate_weight())
        return current_weight == max_weight

    def add_car(self):
        self.cars_waiting += 1

    def add_pedestrian(self):
        self.pedestrians_waiting += 1


class Car:
    def __init__(self, car_id, traffic_light):
        self.id = car_id
        self.traffic_light = traffic_light

    def approach_light(self):
        print(f"Car {self.id} is approaching Svetofor {self.traffic_light.id}")
        self.traffic_light.add_car()


class Pedestrian:
    def __init__(self, ped_id, pedestrian_light):
        self.id = ped_id
        self.pedestrian_light = pedestrian_light

    def approach_light(self):
        print(f"Pedestrian {self.id} is approaching Svetofor {self.pedestrian_light.id}")
        self.pedestrian_light.add_pedestrian()


async def main():
    event_loop = asyncio.get_event_loop()

    svetofor_1 = TrafficLight(1, event_loop)
    svetofor_2 = TrafficLight(2, event_loop, paired_light=svetofor_1)
    svetofor_1.paired_light = svetofor_2 

    svetofor_3 = TrafficLight(3, event_loop)

    other_lights = [svetofor_1, svetofor_2, svetofor_3]

    asyncio.create_task(svetofor_1.listen())
    asyncio.create_task(svetofor_2.listen())
    asyncio.create_task(svetofor_3.listen())

    asyncio.create_task(svetofor_1.control_light(other_lights))
    asyncio.create_task(svetofor_2.control_light(other_lights))
    asyncio.create_task(svetofor_3.control_light(other_lights))

    car_1 = Car(1, svetofor_1)
    car_2 = Car(2, svetofor_3)

    pedestrian_1 = Pedestrian(1, svetofor_1)
    pedestrian_2 = Pedestrian(2, svetofor_3)

    car_1.approach_light()
    car_2.approach_light()

    pedestrian_1.approach_light()
    pedestrian_2.approach_light()

    await asyncio.sleep(20)


if __name__ == "__main__":
    asyncio.run(main())
