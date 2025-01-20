import os
from pyrogram import Client

BOT_TOKEN = os.environ.get("BOT_TOKEN", "5097637442:AAHvqiHZwfWRVKIn4pSjln3I8ohXP2WH5XU")
API_HASH = os.environ.get("API_HASH", "c23db4aa92da73ff603666812268597a")
API_ID = os.environ.get("API_ID", 2374174)
OWNER_ID = os.environ.get("OWNER_ID", "ahmet118")
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1001522676896"))
STRING_SESSION = os.environ.get('STRING_SESSION', 'BADNvmIAZzZi_xbRLqb09A_9J6MUuZ-jVkn8rYgnCEUnaF94P013hFQL4i0CBnp_YckAUtEKgcgXxrYqkiiuJGVIFNusUOavqNsRyUYZIjgWDovF3u40UGZLRW7uodooFskh7EPKjKl9_jDWhmAu2fZOUPv-vE-EF1Qbg8qGNKt0sDVLf-vG0zXGIr7SSFl3LNP28X2Wsp88HPYGusvNrSLZWBxB2m3Ci4LPSdNtQuMApRjDOQb2FFsFwWHHBJqAbVtxGwY9qLWROykR931Fqux7Lde3c74bidPU0FuHi_rr37INM70riEpE0yVNEK-uJ3-X-5cHrDT658WFgXZQUXYMJyd_iwAAAABfX2ioAA')
if len(STRING_SESSION) != 0:
    try:
        userbot = Client(
            name='Userbot',
            api_id=API_ID,
            api_hash=API_HASH,
            session_string=STRING_SESSION,
        ) 
        userbot.start()
        me = userbot.get_me()
        userbot.send_message(OWNER_ID, f"Userbot Bașlatıldı..\n\n**Premium Durumu**: {me.is_premium}\n**Ad**: {me.first_name}\n**id**: {me.id}")
        print("Userbot Başlatıldı..")
    except Exception as e:
        print(e)
