from pyrogram import Client, filters, enums
from pyrogram.types import Message
from ormx import Database, Table, Column
import datetime
from apscheduler.schedulers.background import BackgroundScheduler

app = Client("app")
db = Database('data.db')


class Reminder(Table):
    __tablename__ = 'reminders'
    user = Column(str)
    message = Column(str)
    time = Column(datetime.datetime)

    def __repr__(self) -> str:
        return f'{self.user} - {self.message} after {self.time} seconds'


db.create(Reminder)

# Define the filter using pyrogram.filters.create()
my_message_filter = filters.create(
    lambda _, __, message:
        message.from_user and message.from_user.is_self and message.reply_to_message and message.text.startswith(
            ".")
)


def get_future_time(t):
    current_time = datetime.datetime.now()
    future_time = current_time + datetime.timedelta(seconds=t)
    return future_time

# Use the filter in a handler function


@app.on_message(my_message_filter)
def handle_my_messages(client, message: Message):
    # Handle the messages that meet the filter criteria
    if message.reply_to_message.from_user.first_name:
        if message.reply_to_message.from_user.last_name:
            user = message.reply_to_message.from_user.first_name + \
                message.reply_to_message.from_user.last_name
        else:
            user = message.reply_to_message.from_user.first_name
    else:
        user = message.reply_to_message.from_user.last_name
    messages = message.text.split()
    seconds = int(messages[1]) if len(messages) > 1 else 300
    time = get_future_time(seconds)
    reminder = Reminder(user=str(user), message=str(
        message.reply_to_message.text), time=time)
    db.save(reminder)
    message.delete(True)





def update():
    all = db.all(Reminder)
    if isinstance(all, Reminder):
        all = [all]
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    current_time_a = datetime.datetime.now() + datetime.timedelta(minutes=1)

    if all:
        for a in all:
            if a.time.strftime("%Y-%m-%d %H:%M:%S") == current_time or a.time.strftime("%Y-%m-%d %H:%M:%S") == current_time_a.strftime("%Y-%m-%d %H:%M:%S"):
                text = f"""<b>It is time to text to {a.user}!</b>
<i>The message was '{a.message}'</i>"""
                app.send_message('me', text, parse_mode=enums.ParseMode.HTML)
                db.delete(a)




scheduler = BackgroundScheduler()
scheduler.add_job(update, "interval", seconds=1)

scheduler.start()
app.run()
