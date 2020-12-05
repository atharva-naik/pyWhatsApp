import json
import colors
from colors import color

class Profile(object):
    '''
    This class is template for storing Profile of WhatsApp user
    '''    
    def __init__(self, username, contact, about=None, common_groups=None):
        self.username = username
        self.contact = contact
        self.about = about
        self.common_groups = common_groups

    def return_dict(self):
        profile = {}
        profile['username'] = self.username
        profile['contact number'] = self.contact
        profile['about'] = self.about
        profile['common groups'] = self.common_groups

        return profile

class MetaData(object):
    '''
    This class is template for storing MetaData for a chat object
    '''
    def __init__(self, timestamp, sender):
        self.time = timestamp.time()
        self.date = timestamp.date()
        self.sender = sender 

    def __str__(self):
        op = (color("sender:", fg="green", bg="black", style="bold")+" "+self.sender+"\n")
        op +=  (color("date:", fg="green", bg="black", style="bold")+" "+self.date.strftime("%d/%m%/Y")+"\n")
        op +=  (color("time:", fg="green", bg="black", style="bold")+" "+self.time.strftime("%I:%M %p")+"\n")
        
        return op

    def __repr__(self):
        return self.__str__()

class Chat(object):
    '''
    This class is template for a chat object, having the chat text, flag telling
    if it is a reply, the quoted text and the metadata like senders name and timestamp 
    '''
    def __init__(self, text, metadata, is_reply=False, reply_to=None):
        assert metadata is not None, "There has to be some MetaData for the text"

        self.text = text 
        self.is_reply = is_reply
        self.reply_to = reply_to
        self.metadata = metadata

        # assert is_reply == True and reply_to is None, "Text is a reply, but the quoted text is missing"

    def __str__(self):
        op = ""
        if self.is_reply:
            op += (color("reply to:", fg="red", bg="white", style="bold")+" "+self.reply_to+"\n")
        op += (color("text:", fg="red", bg="white", style="bold")+" "+self.text+"\n")
        op += (color("metadata:", fg="red", bg="white", style="bold")+"\n"+self.metadata.__str__()+"\n")
        
        return op

    def __repr__(self):
        return self.__str__()