import zipfile
import wget
import os
from os.path import join, basename, exists
from mycroft import MycroftSkill, intent_file_handler
from mycroft.configuration.config import Configuration
import polib


class PootleSync(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    def initialize(self):
        if not self.settings.get('lang_path') is None:
            self.lang_path = self.settings.get('lang_path')
        elif 'translations_dir' in Configuration.get():
            self.lang_path = Configuration.get()['translations_dir']
        else:
            self.lang_path = self.file_system.path+"/mycroft-skills/"
        if not self.settings.get('synctimer') is None:
            sync = self.settings.get('synctimer') * 3600
            self.schedule_repeating_event(self.sync_pootle, None, sync,
                                          name='sync_pootle')

    @intent_file_handler('sync.pootle.intent')
    def handle_sync_pootle(self, message):
        self.speak_dialog('sync.pootle')
        self.sync_pootle()

    def sync_pootle(self):
        self.poodle_downloader()
        folder = self.file_system.path+"/de/de/mycroft-skills"
        self.find_po(folder)
        #self.log.info(translation)

    def find_po(self, folder):
        for root, dirs, files in os.walk(folder):
            for f in files:
                filename = os.path.join(root, f)
                if filename.endswith('.po'):
                    output = self.parse_po_file(filename)
                    filename = filename.replace(folder+"/", '')
                    skillname = filename[:-6]
                    for data in output:
                        filename = self.lang_path+skillname+"/"+self.lang+"/locale/"+data
                        self.writing_sentence(output[data], data, filename)


    def poodle_downloader(self):
        self.log.info("start download")
        if os.path.isfile(self.file_system.path+"/"+self.lang[:-3]+".zip"):
            os.remove(self.file_system.path+"/"+self.lang[:-3]+".zip")
        wget.download("https://translate.mycroft.ai/export/?path=/"+self.lang[:-3], self.file_system.path+"/"+self.lang[:-3]+".zip")
        with zipfile.ZipFile(self.file_system.path+"/"+self.lang[:-3]+".zip",'r') as zfile:
                zfile.extractall(self.file_system.path)
        self.speak_dialog('sync.pootle')

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