import zipfile
import wget
import os
from shutil import rmtree
from os.path import join, basename, exists
from mycroft import MycroftSkill, intent_file_handler
from mycroft.configuration.config import Configuration
import polib


class PootleSync(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    def initialize(self):
        if self.settings.get('lang_path') is not "":
            self.lang_path = self.settings.get('lang_path')
            self.log.info("found user folder")
        elif 'translations_dir' in Configuration.get():
            self.lang_path = Configuration.get()['translations_dir']
            self.log.info("found transaltion folder")
        else:
            self.lang_path = self.file_system.path+"/mycroft-skills/"
            self.log.info("set default language path")
        synctimer = self.settings.get('synctimer') \
            if self.settings.get('synctimer') else 0
        if synctimer >= 1 :
            sync = synctimer * 3600
            self.schedule_repeating_event(self.sync_pootle, None, sync,
                                        name='sync_pootle')
            self.log.info("start pootdle event every "+str(self.settings.get('synctimer'))+" h")

    @intent_file_handler('sync.pootle.intent')
    def handle_sync_pootle(self, message):
        self.speak_dialog('sync.pootle')
        self.sync_pootle()

    def sync_pootle(self):
        self.poodle_downloader()
        if self.lang == "en-us": #full english data in en-GB
            folder = self.file_system.path+"/"+self.lang[:2]+"/"+self.lang[:2]+"_GB/mycroft-skills"
        else:
            folder = self.file_system.path+"/"+self.lang[:2]+"/"+self.lang[:2]+"/mycroft-skills"
        oldfolder = self.file_system.path+"/"+self.lang[:2]+"-old/"+self.lang[:2]+"/mycroft-skills"
        self.find_po(folder, oldfolder)
        #self.log.info(translation)

    def find_po(self, folder, oldfolder):
        # find, match old and new files. write only new files
        for root, dirs, files in os.walk(folder):
            for f in files:
                filename = os.path.join(root, f)
                if filename.endswith('.po'):
                    output = self.parse_po_file(filename) #new
                    filename = filename.replace(folder+"/", '')
                    if os.path.isfile(oldfolder+"/"+filename):
                        oldoutput = self.parse_po_file(oldfolder+"/"+filename) #old
                    else:
                        oldoutput = {}
                    skillname = filename.replace("-"+self.lang[:2]+".po", "").replace("-en_GB.po", "") ####### todo
                    for key in list(output.keys()):
                        if not key in list(oldoutput.keys()):
                            filename = self.lang_path+skillname+"/"+self.lang+"/locale/"+key
                            self.writing_sentence(output[key], key, filename)
                        else:
                            self.log.info("nothing new for "+skillname)


    def poodle_downloader(self):
        #move files to -old and download new files vor match
        self.log.info("start download")
        if os.path.isfile(self.file_system.path+"/"+self.lang[:2]+".zip"):
            os.remove(self.file_system.path+"/"+self.lang[:2]+".zip")
        wget.download("https://translate.mycroft.ai/export/?path=/"+self.lang[:2], self.file_system.path+"/"+self.lang[:2]+".zip")
        if os.path.exists(self.file_system.path+"/"+self.lang[:2]):
            if os.path.exists(self.file_system.path+"/"+self.lang[:2]+"-old"):
                rmtree(self.file_system.path+"/"+self.lang[:2]+"-old")
            os.rename(self.file_system.path+"/"+self.lang[:2], self.file_system.path+"/"+self.lang[:2]+"-old")
        with zipfile.ZipFile(self.file_system.path+"/"+self.lang[:2]+".zip",'r') as zfile:
                zfile.extractall(self.file_system.path)
        self.speak_dialog('sync.pootle')

    def reading_sentence(self, data, filename):
        sentence = []
        fobj_in = open(filename, "r")
        for line in fobj_in:
            sentence = sentence.append(line)
        fobj_in.close()
        return sentence

    def writing_sentence(self, sentence, data, filename):
        sentence = "\n".join(sentence)
        folder =filename.replace(data, '')
        if not os.path.isdir(folder):
            os.makedirs(folder)
        fobj_out = open(filename, "w")
        self.log.info("write file: "+str(filename))
        fobj_out.write(str(sentence) + "\n")
        fobj_out.close()

    def parse_po_file(self, path):
        """ Create dictionary with translated files as key containing
        the file content as a list.

        Arguments:
            path: path to the po-file of the translation

        Returns:
            Dictionary mapping files to translated content
        """
        out_files = {}  # Dict with all the files of the skill
        # Load the .po file
        po = polib.pofile(path)

        for entity in po:
            for out_file, _ in entity.occurrences:
                f = out_file.split('/')[-1] # Get only the filename
                content = out_files.get(f, [])
                content.append(entity.msgstr)
                out_files[f] = content

        return out_files

    def shutdown(self):
        self.cancel_scheduled_event('sync_pootle')
        super(PootleSync, self).shutdown()


def create_skill():
    return PootleSync()