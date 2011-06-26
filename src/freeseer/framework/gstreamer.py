import gobject
gobject.threads_init()
import pygst
pygst.require("0.10")
import gst


class Gstreamer:
    def __init__(self):
        self.window_id = None
        
        # Initialize Player
        self.player = gst.Pipeline('player')
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect('message', self.on_message)
        bus.connect('sync-message::element', self.on_sync_message)
        
        # Initialize Entry Points
        self.audio_tee = gst.element_factory_make('tee', 'audio_tee')
        self.video_tee = gst.element_factory_make('tee', 'video_tee')
        self.player.add(self.audio_tee, self.video_tee)

    ##
    ## GST Player Functions
    ##
    def on_message(self, bus, message):
        t = message.type
      
        if t == gst.MESSAGE_EOS:
            #self.player.set_state(gst.STATE_NULL)
            #self.stop()
            pass
        elif t == gst.MESSAGE_ERROR:
            err, debug = message.parse_error()
            self.core.logger.log.debug('Error: ' + str(err) + str(debug))
            #self.player.set_state(gst.STATE_NULL)
            #self.stop()

        elif message.structure is not None:
            s = message.structure.get_name()

            
    def on_sync_message(self, bus, message):
        if message.structure is None:
            return
        message_name = message.structure.get_name()
        if message_name == 'prepare-xwindow-id':
            imagesink = message.src
            imagesink.set_property('force-aspect-ratio', True)
            imagesink.set_xwindow_id(int(self.window_id))
            
    ##
    ## Recording functions
    ##
    def record(self):
        pass
    
    def stop(self):
        for plugin in self.output_plugins:
            gst.element_unlink_many(self.video_tee, plugin)
            self.player.remove(plugin)
    
    def load_output_plugins(self, plugins):
        self.output_plugins = []
        for plugin in plugins:
            type = plugin.get_type()
            bin = plugin.get_output_bin('test-filename')
            self.output_plugins.append(bin)
            
            if type == "video":
                self.player.add(bin)
                gst.element_link_many(self.video_tee, bin)
    
    def load_videomixer(self, mixer):
        videomixer = mixer.get_videomixer_bin()
        self.player.add(videomixer)
        gst.element_link_many(videomixer, self.video_tee)
