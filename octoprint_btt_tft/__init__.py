# coding=utf-8
from __future__ import absolute_import

### (Don't forget to remove me)
# This is a basic skeleton for your plugin's __init__.py. You probably want to adjust the class name of your plugin
# as well as the plugin mixins it's subclassing from. This is really just a basic skeleton to get you started.

import octoprint.plugin
from octoprint.events import Events
from octoprint.printer import PrinterCallback

class btt_tft(
	octoprint.plugin.TemplatePlugin,
	octoprint.plugin.ProgressPlugin,
	octoprint.plugin.EventHandlerPlugin,
	octoprint.plugin.RestartNeedingPlugin,
	octoprint.plugin.StartupPlugin):

	def on_after_startup(self):
		self._logger.info("BTT_TFT_Plugin loaded")

	def on_event(self, event, payload):
		if event == Events.PRINT_STARTED:
			self._logger.info("PrintStarted. Sending to TFT")
			self._printer.commands("M118 P0 A1 action:print_start")
		if event == Events.PRINT_DONE:
			self._logger.info("PrintDone. Sending to TFT")
			self._printer.commands("M118 P0 A1 action:print_end")
		if event == Events.PRINT_CANCELLED:
			self._logger.info("PrintCancelled. Sending to TFT")
			self._printer.commands("M118 P0 A1 action:cancel")
		if event == Events.PRINT_PAUSED:
			self._logger.info("PrintPaused. Sending to TFT")
			self._printer.commands("M118 P0 A1 action:pause")
		if event == Events.PRINT_RESUMED:
			self._logger.info("PrintResumed. Sending to TFT")
			self._printer.commands("M118 P0 A1 action:resume")
		if event == Events.Z_CHANGE:
			self._logger.info("ZChange occured. ToDo: update TFT Progress")

	def onHostActionCommand(self, comm, line, action, *args, **kwargs):
		if action == "notification remote pause":
			self._logger.info("Pause command received. Pausing Print")
			self._printer.pause_print()
		if action == "notification remote resume":
			self._logger.info("Resume command received. Resuming Print")
			self._printer.resume_print()
		if action == "notification remote cancel":
			self._logger.info("cancle command received. Cancleling Print")
			self._printer.cancel_print()
		if action == "octoprint shtdown":
			self._logger.info("Received shtdown command. ToDo: Shutdown host")

	def on_print_progress(self, storage, path, progress):
		self._logger.info("Progress was made. Updating progress")
		data = self._printer.get_current_data()
		progressData = data['progress']
		timeLeft = int(progressData['printTimeLeft'])
		timeLeftHours = timeLeft//3600
		timeLeftMinutes = (timeLeft//60)%60
		timeLeftSeconds = timeLeft%60
		message = "M118 P0 A1 action:notification Time Left {h}h{m}m{s}s".format(h = timeLeftHours, m = timeLeftMinutes, s = timeLeftSeconds)
		self._printer.commands(message)
		fileSize = data['job']['file']['size']
		filePos = progressData['filepos']
		message = "M118 P0 A1 action:notification Data Left {pos}/{size}".format(size=fileSize, pos=filePos)
		self._printer.commands(message)

# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.

__plugin_name__ = "BigTreeTech TFT Display Communicator"
__plugin_pythoncompat__ = ">=2.7,<4"

def __plugin_load__():
	plugin = btt_tft()

	global __plugin_implementation__
	__plugin_implementation__ = plugin

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.comm.protocol.action": plugin.onHostActionCommand
	}