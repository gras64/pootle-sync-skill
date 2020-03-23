import requests
import re
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
        self.speak_dialog('sync.pootle')
        self.poodle_loader

    def poodle_loader(self):
        self.log.info("start download")
        data = requests.get("https://translate.mycroft.ai/export/?path=/"+self.lang+"/mycroft-skills/")
        data.encoding = 'utf-8'
        #print(data.encoding)
        sentence = "\n".join(re.findall(r'(msgstr ".*")', data.text)).replace("msgstr", "")
        sentence = re.sub(r'["\d]|{\n.*}\n', '', sentence).replace('\n \n','\n').replace('\n \n','\n')
        sentence = sentence.replace('\n \n','\n').replace('\n \n','\n').replace('\n \n','\n')
        #summary = sentence
        #sentence = self.filter_sentence(sentence, args) # filter data
        sentence = sentence.split("\n")
        self.writing_sentence(sentence)
        self.log.info(sentence)
        self.speak_dialog('sync.pootle')

    def writing_sentence(self, sentence, filename="test.txt"):
        sentence = "\n".join(sentence)
        fobj_out = open(self.lang_path+filename, "a")
        fobj_out.write(str(sentence) + "\n")
        fobj_out.close()

    def shutdown(self):
        super(PootleSync, self).shutdown()



def create_skill():
    return PootleSync()

