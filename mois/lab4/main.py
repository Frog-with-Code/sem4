import asyncio
import spade
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour, PeriodicBehaviour
from spade.message import Message
from spade.template import Template

TEACHER_JID = "teacher@localhost"
STUDENT_JID = "student@localhost"
DEAN_JID = "dean@localhost"
PASSWORD = "password123"


class StudentAgent(Agent):
    def __init__(self, jid, password, request_time: str):
        super().__init__(jid, password)
        self.request_time = request_time

    class RequestConsultation(OneShotBehaviour):
        async def run(self):
            msg = Message(to=TEACHER_JID)
            msg.set_metadata("performative", "request")
            msg.set_metadata("ontology", "scheduling")

            msg.body = self.agent.request_time  # type: ignore

            print(f"[{self.agent.jid.local}] Отправлен запрос на {msg.body}")  # type: ignore
            await self.send(msg)

    class ReceiveResponse(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=5)
            if msg:
                performative = msg.metadata.get("performative")
                if performative == "agree":
                    print(f"[{self.agent.jid.local}] Успешно записан на {msg.body}")  # type: ignore
                elif performative == "refuse":
                    print(f"[{self.agent.jid.local}] Отказано в записи на {msg.body}")  # type: ignore
                else:
                    print(f"Unknown state: {performative}")
                self.kill()

    async def setup(self):
        self.add_behaviour(self.RequestConsultation())

        template = Template()
        template.set_metadata("ontology", "scheduling")
        self.add_behaviour(self.ReceiveResponse(), template)


class TeacherAgent(Agent):
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.booked_slots = []

    class ManageRequests(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=5)
            if msg:
                requested_slot = msg.body
                reply = msg.make_reply()
                reply.set_metadata("ontology", "scheduling")

                if requested_slot not in self.agent.booked_slots:  # type: ignore
                    self.agent.booked_slots.append(requested_slot)  # type: ignore
                    reply.set_metadata("performative", "agree")
                    reply.body = requested_slot
                    print(f"[{self.agent.jid.local}] Одобрена запись на {requested_slot}")  # type: ignore

                    notif = Message(to=DEAN_JID)
                    notif.set_metadata("performative", "inform")
                    notif.set_metadata("ontology", "reporting")
                    notif.body = f"Преподаватель занят на {requested_slot}"
                    await self.send(notif)
                else:
                    reply.set_metadata("performative", "refuse")
                    reply.body = requested_slot
                    print(f"[{self.agent.jid.local}] Отклонен запрос на {requested_slot} (занято)")  # type: ignore

                await self.send(reply)

    async def setup(self):
        template = Template()
        template.set_metadata("performative", "request")
        template.set_metadata("ontology", "scheduling")
        self.add_behaviour(self.ManageRequests(), template)


class DeanAgent(Agent):
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.schedule_log = []

    class ReceiveUpdates(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=5)
            if msg:
                self.agent.schedule_log.append(msg.body)  # type: ignore
                print(f"[{self.agent.jid.local}] Лог обновлен: {msg.body}")  # type: ignore

    class PublishSchedule(PeriodicBehaviour):
        async def run(self):
            print(f"\n--- [{self.agent.jid.local}] Периодический отчет расписания: ---")  # type: ignore
            if self.agent.schedule_log:  # type: ignore
                for record in self.agent.schedule_log:  # type: ignore
                    print(f" - {record}")
            else:
                print(" - Расписание пусто")
            print("---------------------------------------------------\n")

    async def setup(self):
        update_template = Template()
        update_template.set_metadata("performative", "inform")
        update_template.set_metadata("ontology", "reporting")
        self.add_behaviour(self.ReceiveUpdates(), update_template)

        self.add_behaviour(self.PublishSchedule(period=10.0))


async def main():
    dean = DeanAgent(DEAN_JID, PASSWORD)
    teacher = TeacherAgent(TEACHER_JID, PASSWORD)
    student = StudentAgent(STUDENT_JID, PASSWORD, "14:00")

    await dean.start()
    await teacher.start()
    await student.start()

    await asyncio.sleep(15)

    await student.stop()
    await teacher.stop()
    await dean.stop()


if __name__ == "__main__":
    spade.run(main(), embedded_xmpp_server=True)
