from pyWhatsApp.interface import WhatsAppEngine

engine = WhatsAppEngine()
engine.switch_to_user("<contact_name>")
engine.is_online(username="<contact_name>")
chatlogs = engine.get_received_messages()
print(chatlogs)
chatlogs = engine.get_sent_messages()
print(chatlogs)
engine.close()
