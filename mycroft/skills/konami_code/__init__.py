
from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

from os.path import dirname, exists

from mycroft.skills.skill_intents import SkillIntents

__author__ = 'jarbas'

LOGGER = getLogger(__name__)


class KonamiCodeSkill(MycroftSkill):
    def __init__(self):
        super(KonamiCodeSkill, self).__init__(name="KonamiCode")
        # UP UP DOWN DOWN LEFT RIGHT LEFT RIGHT B A
        self.cheat_code_script = dirname(__file__)+"/cheat_code.py"
        # TODO use this path instead of importing default script and read from config file
        self.counter = 0
        self.reload_skill = False


    def initialize(self):
        self.intents = SkillIntents(self.emitter)

        up_intent = IntentBuilder('KonamiUpIntent'). \
            require("KonamiUpKeyword").build()

        down_intent = IntentBuilder('KonamiDownIntent'). \
            require("KonamiDownKeyword").build()

        left_intent = IntentBuilder('KonamiLeftIntent'). \
            require("KonamiLeftKeyword").build()

        right_intent = IntentBuilder('KonamiRightIntent'). \
            require("KonamiRightKeyword").build()

        b_intent = IntentBuilder('KonamiBIntent'). \
            require("KonamiBKeyword").build()

        a_intent = IntentBuilder('KonamiAIntent'). \
            require("KonamiAKeyword").build()

        # register local intents
        self.register_self_intent(down_intent, self.handle_down_intent)
        self.register_self_intent(left_intent, self.handle_left_intent)
        self.register_self_intent(right_intent, self.handle_right_intent)
        self.register_self_intent(b_intent, self.handle_b_intent)
        self.register_self_intent(a_intent, self.handle_a_intent)
        # disable local intents until needed
        self.disable_intent('KonamiDownIntent')
        self.disable_intent('KonamiLeftIntent')
        self.disable_intent('KonamiRightIntent')
        self.disable_intent('KonamiBIntent')
        self.disable_intent('KonamiAIntent')

        # register global intents
        self.register_intent(up_intent, self.handle_up_intent)


    def handle_up_intent(self, message):
        self.speak_dialog("up")
        self.counter += 1
        if self.counter == 2:
            # disable up
            self.disable_intent('KonamiUpIntent')
            # enable down
            self.enable_self_intent("KonamiDownIntent")
            self.counter = 0

    def handle_down_intent(self, message):
        self.speak_dialog("down")
        self.counter += 1
        if self.counter == 2:
            self.disable_intent('KonamiDownIntent')
            self.enable_self_intent("KonamiLeftIntent")
            self.counter = 0

    def handle_left_intent(self, message):
        self.speak_dialog("left")
        self.disable_intent('KonamiLeftIntent')
        self.enable_self_intent("KonamiRightIntent")

    def handle_right_intent(self, message):
        self.speak_dialog("right")
        self.counter += 1
        self.disable_intent('KonamiRightIntent')
        self.enable_self_intent("KonamiLeftIntent")
        if self.counter == 2:
            self.disable_intent('KonamiLeftIntent')
            self.enable_self_intent("KonamiBIntent")
            self.counter = 0

    def handle_b_intent(self, message):
        self.speak_dialog("b")
        self.disable_intent('KonamiBIntent')
        self.enable_self_intent('KonamiAIntent')


    def handle_a_intent(self, message):
        if not self.cheat_code_script:
            self.speak_dialog("no.script")
            return

        if not exists(self.cheat_code_script):
            data = {
                "script": self.cheat_code_script
            }
            self.speak_dialog("missing.script", data)
            return

        self.speak_dialog("cheat_code")
        # TODO change this lazy mechanism, use subprocess ?
        import mycroft.skills.konami_code.cheat_code
        self.counter = 0
        self.disable_intent('KonamiAIntent')
        self.enable_intent('KonamiUpIntent')


    # reset code input on invalid utterance
    def converse(self, transcript, lang="en-us"):
        determined, intent = self.intents.determine_intent(transcript)
        handled = False

        if determined:
            handled = self.intents.execute_intent()

        if not handled and self.counter == 0:
            self.enable_intent('KonamiUpIntent')
            self.disable_intent('KonamiDownIntent')
            self.disable_intent('KonamiLeftIntent')
            self.disable_intent('KonamiRightIntent')
            self.disable_intent('KonamiBIntent')
            self.disable_intent('KonamiAIntent')
            self.counter = 0
        return handled

    def stop(self):
        pass


def create_skill():
    return KonamiCodeSkill()
