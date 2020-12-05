import time
import tqdm
import colors
import selenium
from .objects import *
from colors import color
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options  
from webdriver_manager.chrome import ChromeDriverManager 
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException


class WhatsAppEngine(object):
    '''
    This is the most important class. This class bundles together all basic
    administrative functions like logging in (which is done when an object is initialized)
    logging out (using the close() member function), entering into a particular username
    (switch_to_user) to access chats with the user etc.
    '''
    def __init__(self, patience=5):
        self.patience = int(patience)
        if self.patience <= 0:
            self.patience = 1
        self.driver = webdriver.Chrome(ChromeDriverManager().install()) 
        self.driver.maximize_window()
        self.current_user = None
        self.driver.get('https://web.whatsapp.com/')
        
        print(color("Please scan QR to get into WhatsApp Web!", fg="blue"))
        
    def switch_to_user(self, username):
        while True:
            try:
                search_bar = self.driver.find_elements_by_tag_name('label')[0]
                text_area = search_bar.find_elements_by_class_name('copyable-text')[0]
                break
            except (StaleElementReferenceException, IndexError):
                print(color("Waiting inside switch_to_user ...", fg="red"))
                self.driver.implicitly_wait(self.patience)
        
        text_area.send_keys(username+"\n")
        time.sleep(4)
        while True:
            try:
                side_area = self.driver.find_element_by_id("pane-side")
                if side_area.text == 'No chats, contacts or messages found':
                    print(color(f"{username} not in your contacts"), fg="red", style="bold")
                    print(color(side_area.text, fg="red", style="bold"))
                    text_area.clear()
                else:
                    self.current_user = username
                    print(color(f"{username} was found!", fg="green", style="bold"))
                    break
            except:
                print(color("Waiting inside switch_to_user ...", fg="red"))
                self.driver.implicitly_wait(self.patience)

    def get_received_messages(self):
        start_time = time.time()
        if self.current_user is None:
            print(color("Please select a user first, using switch_to_user!", fg="red"))
            return 

        print(color(f"Getting messages received from {self.current_user} ...", fg="blue"))
        while True:
            try:
                received_messages = self.driver.find_elements_by_class_name('message-in')
                messages = []
                for message in tqdm.tqdm(received_messages):
                    try:
                        text = message.find_elements_by_class_name('selectable-text')[0].text
                        reply_to = None
                        try:
                            reply_to = message.find_elements_by_class_name('quoted-mention')[0].text
                            is_reply = True
                        except IndexError:
                            is_reply = False   

                        metastring = message.find_elements_by_class_name('copyable-text')[0].get_attribute("data-pre-plain-text")      
                        timestamp, sender = metastring.split(']')
                        timestamp = datetime.strptime(timestamp, "[%I:%M %p, %m/%d/%Y")
                        sender = sender.strip()[:-1] 
                        
                        metadata = MetaData(timestamp, sender)                   
                        chat = Chat(text=text, metadata=metadata, is_reply=is_reply, reply_to=reply_to)
                        messages.append(chat)
                    except (AttributeError, StaleElementReferenceException):
                        pass
                print(color(f"retrieval took {time.time()-start_time}s", fg="yellow", style="bold"))
                return messages

            except StaleElementReferenceException:
                print(color("Waiting inside get_received_messages ..."), fg="red")
                self.driver.implicitly_wait(self.patience)
    
    def get_sent_messages(self):
        start_time = time.time()
        if self.current_user is None:
            print(color("Please select a user first, using switch_to_user!", fg="red"))
            return 

        print(color(f"Getting messages sent to {self.current_user} ...", fg="blue"))
        while True:
            try:
                sent_messages = self.driver.find_elements_by_class_name('message-out')
                messages = []
                for message in tqdm.tqdm(sent_messages):
                    try:
                        text = message.find_elements_by_class_name('selectable-text')[0].text
                        # emoji = message.find_elements_by_tag_name("img")[0].get_attribute("alt")
                        reply_to = None
                        try:
                            reply_to = message.find_elements_by_class_name('quoted-mention')[0].text
                            is_reply = True
                        except (AttributeError, IndexError, StaleElementReferenceException):
                            is_reply = False   

                        metastring = message.find_elements_by_class_name('copyable-text')[0].get_attribute("data-pre-plain-text")      
                        timestamp, sender = metastring.split(']')
                        timestamp = datetime.strptime(timestamp, "[%I:%M %p, %m/%d/%Y")
                        sender = sender.strip()[:-1] 
                        
                        metadata = MetaData(timestamp, sender)                   
                        chat = Chat(text=text, metadata=metadata, is_reply=is_reply, reply_to=reply_to)
                        messages.append(chat)
                    except (AttributeError, IndexError, StaleElementReferenceException):
                        pass
                print(color(f"retrieval took {time.time()-start_time}s", fg="yellow", style="bold"))
                return messages

            except StaleElementReferenceException:
                print(color("Waiting inside get_sent_messages ..."), fg="red")
                self.driver.implicitly_wait(self.patience)

    def get_profile(self, username):
        self.switch_to_user(username=username)
        while True:
            try:
                header = self.driver.find_elements_by_tag_name("header")[1]
                header.click()
                break
            except (IndexError, StaleElementReferenceException):
                print(color("Waiting inside get_profile ..."), fg="red")
                self.driver.implicitly_wait(self.patience)
        
        while True:
            try:
                temp = self.driver.find_element_by_xpath("//*[contains(text(), 'About and phone number')]")
                temp = temp.find_element_by_xpath('..')
                temp = temp.find_element_by_xpath("following-sibling::div")
                
                about = temp.text
                temp = temp.find_element_by_xpath("following-sibling::div")
                contact = temp.text

                return Profile(username, contact, about)

            except (IndexError, StaleElementReferenceException):
                print(color("Waiting inside get_profile ..."), fg="red")
                self.driver.implicitly_wait(self.patience) 

    def send_message(self, message, username=None, inform=False):
        if username is None:
            if self.current_user is None:
                print(color("Please select a user first, using switch_to_user!", fg="red"))
                return

            else:
                # send the text message
                if inform:
                    text_box = self.driver.find_element_by_xpath("//div[@spellcheck='true']")
                    text_box.clear()
                    text_box.send_keys("_*beep boop I'm pyBot*_\n")
                text_box = self.driver.find_element_by_xpath("//div[@spellcheck='true']")
                text_box.clear()
                text_box.send_keys('_*pyBot says*_, '+message+'\n')

        else:
            # send the text message
            self.switch_to_user(username=username)
            if inform:
                text_box = self.driver.find_element_by_xpath("//div[@spellcheck='true']")
                text_box.clear()
                text_box.send_keys("_*beep boop I'm pyBot*_\n")
            text_box = self.driver.find_element_by_xpath("//div[@spellcheck='true']")
            text_box.clear()
            text_box.send_keys('_*pyBot says*_, '+message+'\n')
        

    def is_online(self, username):
        self.switch_to_user(username=username)
        self.driver.implicitly_wait(self.patience)
        try:
            self.driver.find_element_by_xpath("//*[contains(text(), 'online')]")
            print(color(f"{username} was online at {time.strftime('%I:%M:%S %p')}!", fg="green", style="bold"))
            return True
        except (StaleElementReferenceException, NoSuchElementException):
            print(color(f"{username} was offline at {time.strftime('%I:%M:%S %p')}!", fg="red", style="bold"))
            return False

    def close(self):
        while True:
            i = input("Please enter q to quit now!\n")
            if i == 'q':
                self.driver.quit()
                break

# get_username(driver, "Jane doe")
# driver = webdriver.Chrome(ChromeDriverManager().install()) 
# driver.maximize_window()
# driver.get('https://web.whatsapp.com/')


