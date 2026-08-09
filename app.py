import os
import requests
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

load_dotenv()

app = App(token=os.getenv("SLACK_BOT_TOKEN"))

@app.command("/count")
def streak_command(ack, respond, command):
    ack()
    channel_name = command.get("text")
    print(f"someone is trying to look up {channel_name}")
    if channel_name.startswith('#'):
        trimname = channel_name[1:]
    else:
        pass
    try:
        r = requests.get(
            f"https://flaron.halceon.dev/cname/%23{trimname}",
            headers={"accept": "application/json"}
        )

        if r.status_code == 403:
            print("channel private or non-exsistant")
            respond(f"looks like {trimname} is private or doesn't exist")
            return
        if r.status_code != 200:
            print(f"Flaron API error: {r.status_code}")
            respond(f"Flaron API error ({r.status_code}). idk what happened.")
            return
        
        data = r.json()
        counts = data.get("counts", {})
        total_members = int(counts.get("total", 0))
        bot_members = int(counts.get("bots", 0))
        respond(
            f"Hey :wavey:, I found your channel #{trimname}! \n"
            f"Total Members: {total_members} \n"
            f":sweat_smile:  Real Humans: {total_members - bot_members} \n"
            f":robot: Bots: {bot_members}"
        )
        print("another happy customer")
    except requests.exceptions.RequestException:
        print("Network error while connecting to Flaron API.")
        respond("Could not connect to Flaron API. womp womp, go ping @freddie to fix his wifi or check status.freddieyershon.co.uk if i ever make ts")
    except Exception:
        print("An unexpected error occurred.")
        respond("Unexpected error occurred. Makse sure you use the full channel name as a link, like <#freddies-castle>, oh, you should join btw")

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
    handler.start()