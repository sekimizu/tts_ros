#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import rospy
from gtts import gTTS
from tts.msg import TTS
from sound_play.libsoundplay import SoundClient

class GoogleTTS:
    def __init__(self, caller_id):
        rospy.init_node('google_tts_node', anonymous = True, log_level=rospy.DEBUG)
        rospy.loginfo('{0} Create Google TTS node complete...'.format(caller_id))

        params = rospy.get_param("~", {})
        tts_params = params.pop("tts", {})
        self._topic_from = tts_params.pop('TOPIC_FROM', 'tts_speak')
        self._subscriber = rospy.Subscriber(self._topic_from, TTS, self._callback)
        self._soundhandle = SoundClient()
        self._caller_id = caller_id
        self._tmp_file_location = tts_params.pop('TMP_FILE_LOCATION', '/tmp/voice.wav')
        self._volume = tts_params.pop('VOLUME', '1.0')
        rospy.sleep(1)

    def _callback(self, msg):
        try:
            text, lang, sink = (msg.text, msg.lang, msg.sink)
        except Exception:
            raise ROSInterruptException('Error occur while parsing argument')
        if not text or not lang or not sink:
            raise ROSInterruptException('Argument can not be empty')

        rospy.loginfo('{0} Text = {1}, Lang = {2}, Sink = {3}'.format(
            self._caller_id, text, lang, sink
        ))

        if sink == 'google':
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(self._tmp_file_location)
            self._soundhandle.playWave(self._tmp_file_location, self._volume)
        elif sink == 'festival':
            voice = 'voice_cmu_us_ahw_cg'
            self._soundhandle.say(text, voice, self._volume)      
        else:
            raise ROSInterruptException('Unknown sink {0}'.format(sink))

    def on_shutdown(self):
        rospy.loginfo('{0} Shutdown Google TTS node complete...'.format(self._caller_id))
        self._subscriber.unsubscribe(self._topic_from)

if __name__ == '__main__':
    try:
        GoogleTTS(caller_id = rospy.get_caller_id())
    except rospy.ROSInterruptException:
        pass
    else:
        rospy.spin()
