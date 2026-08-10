import os, re, requests

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

load_dotenv()

app = App(token=os.getenv("SLACK_BOT_TOKEN"))
pattern = r"<@[^|]+\|[^>]+>" # ai assisted regex


@app.command("/count")
def member_count(ack, respond, command):
    ack()
    channel_name = command.get("text", "").strip()
    if not channel_name:
        respond("You need to give me a channel, e.g. `/count #freddies-castle`")
        return
    print(f"someone is trying to look up {channel_name}")
    trimname = channel_name[1:] if channel_name.startswith('#') else channel_name
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

@app.command("/promote")
def promote_mcg(ack, respond, command):
    ack()
    selected_user = command.get("text", "").strip()
    print(f"someone is trying to promote {selected_user}")

    match = re.fullmatch(pattern, selected_user)
    if not match:
        respond("You need to @-mention exactly one user, e.g. `/promote @someone`")
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


if __name__ == "__main__":
    handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
    handler.start()