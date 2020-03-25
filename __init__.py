import requests
<<<<<<< HEAD
import zipfile
import wget
import re
import os
=======
import re
>>>>>>> 0d96a259a798287641d82fe8f2f998ed28781bda
from mycroft import MycroftSkill, intent_file_handler


class PootleSync(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    def initialize(self):
        self.lang_path = self.settings.get('lang_path') \
            if self.settings.get('lang_path') else self.file_system.path+"/"+self.lang+"/"
        self.log.info("init")

    @intent_file_handler('sync.pootle.intent')
    def handle_sync_pootle(self, message):
        self.poodle_loader()

    def poodle_loader(self):
        self.log.info("start download")
        if os.path.isfile(self.file_system.path+"/"+self.lang[:-3]+".zip"):
            os.remove(self.file_system.path+"/"+self.lang[:-3]+".zip")
        wget.download("https://translate.mycroft.ai/export/?path=/"+self.lang[:-3], self.file_system.path+"/"+self.lang[:-3]+".zip")
        with zipfile.ZipFile(self.file_system.path+"/"+self.lang[:-3]+".zip",'r') as zfile:
                zfile.extractall(self.file_system.path)
        ##data = requests.get("https://translate.mycroft.ai/export/?path=/"+self.lang[:-3]+"/mycroft-skills/")
        ##data.encoding = 'utf-8'
        ##sentence = "\n".join(re.findall(r'(msgstr ".*")', data.text)).replace("msgstr", "")
        #sentence = re.sub(r'["\d]|{\n.*}\n', '', sentence).replace('\n \n','\n').replace('\n \n','\n')
        #sentence = sentence.replace('\n \n','\n').replace('\n \n','\n').replace('\n \n','\n')
        #summary = sentence
        #sentence = self.filter_sentence(sentence, args) # filter data
        #sentence = sentence.split("\n")
        #self.writing_sentence(sentence)
        #self.log.info(sentence)
        self.speak_dialog('sync.pootle')
        self.poodle_loader

        if not os.path.isdir(self.lang_path):
            os.makedirs(self.lang_path)
        fobj_out = open(self.lang_path+filename, "w")
        fobj_out.write(str(sentence) + "\n")
        fobj_out.close()

    def shutdown(self):
        super(PootleSync, self).shutdown()



def create_skill():
    return PootleSync()

