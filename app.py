import os, re, requests

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

load_dotenv()

app = App(token=os.getenv("SLACK_BOT_TOKEN"))
pattern_member = r"<@[^|]+\|[^>]+>" # ai assisted regex
pattern_channel = r"<#[^>]+>" # matches <#anything>


@app.command("/count")
def member_count(ack, respond, command):
    ack()
    channel_name = command.get("text", "").strip()
    print(f"someone is trying to look up {channel_name}")

    match_chan = re.fullmatch(pattern_channel, channel_name)
    print(channel_name)
    if not match_chan:
        respond(f"You need to #-mention a channel, you ran `/count {channel_name}`")
        return
    
    trimname = match_chan.group(0)[2:-1]
    try:
        r = requests.get(
            f"https://flaron.halceon.dev/cid/{trimname}",
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
            f"Hey :wavey:, I found your channel <#{trimname}>! \n"
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

@app.command("/promote")
def promote_mcg(ack, respond, command):
    ack()
    selected_user = command.get("text", "").strip()
    print(f"someone is trying to promote {selected_user}")

    match = re.fullmatch(pattern_member, selected_user)
    if not match:
        respond(f"You need to @-mention exactly one user, you ran `/promote {selected_user}`")
        return

    selected_id = match.group(0).split("|")[0][2:]
    respond(f"Got it, attempting to promote {selected_id}")
    try:
        r = requests.get(
            f"https://flaron.halceon.dev/promote/{selected_id}",
            headers={"accept": "application/json"}
        )

        if r.status_code != 200:
            print(f"Flaron API error: {r.status_code}")
            respond(f"Flaron API error ({r.status_code}). idk what happened.")
            return

        respond(f"Promoted <@{selected_id}> :tada:")
        print("another happy customer")
    except requests.exceptions.RequestException:
        print("Network error while connecting to Flaron API.")
        respond("Could not connect to Flaron API. womp womp, go ping @freddie to fix his wifi or check status.freddieyershon.co.uk if i ever make ts")
    except Exception:
        print("An unexpected error occurred.")
        respond("Unexpected error occurred. :sob:")

@app.command("/things")
def bot_details(ack, respond, command):
    ack()
    question = command.get("text", "").strip()
    if question == "help":
        print("user in distress, activated help")
        respond("Heyo :cat-wave: , I'm a bot made by <@freddie> \n Here is what you can run: \n - `/count [#name-of-public-channel]` - find the member count of a public channel \n - `/promote [@user]` - Promote a user from a multi channel guest to full user (use responsably, cc; @shroud) \n - `/things [help|ping]` - this cmd or ping the bot, but why would you need to do that!")
    elif question == "ping":
        print("pong")
        respond("pong :beachball:")
    else:
        print("fuck you")
        respond("If you are typing to ping the bot do `/things ping` you silly cat, otherwise; Sorry, I didn't get that, try either [help|ping]")

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
    handler.start()