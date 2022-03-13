import subprocess
import datetime
import random
import _thread
import pygame
import ELM327
import Visual
import Button
import Gadgit
import Config
import Select
import Confirm
DISPLAY_PERIOD = 100
TIMER_PERIOD = 500
# Start value for pygame user events.
EVENT_TIMER = pygame.USEREVENT + 1
#Acquiring data
def AquisitionLoop(ThisDisplay):
	try:
		while (ThisDisplay.Meters["GO_STOP"].GetDown() == True or ThisDisplay.Plots["GO_STOP"].GetDown() == True):
			# Update the gadgit data from the ECU.
			if ThisDisplay.CurrentTab == ThisDisplay.Meters and ThisDisplay.Meters["LOCK"].GetDown() == True and ThisDisplay.Meters["GO_STOP"].GetDown() == True:
				if LockELM327.acquire(0):
					_thread.start_new_thread(MeterData, (ThisDisplay, ))
			# Update the plot data from the ECU.
			if ThisDisplay.CurrentTab == ThisDisplay.Plots and ThisDisplay.Plots["GO_STOP"].GetDown() == True:
				if LockELM327.acquire(0):
					_thread.start_new_thread(PlotData, (ThisDisplay, ))
	except Exception as Catch:
		print(str(Catch))
	# Allow this function to be called again if required.
	LockAquisition.release()
# Set the configuration before start.
ApplyConfig()
# Create a timer for updating the displayed time/date and updating gadgit data from the ECU.
pygame.time.set_timer(EVENT_TIMER, TIMER_PERIOD)
# Aquire a lock for use when communicating with the ELM327 device.
if LockELM327.acquire(0):
	_thread.start_new_thread(ConnectELM327, (ThisDisplay, ))

# Application message loop.
ExitFlag = False
while ExitFlag == False:
	pygame.time.wait(DISPLAY_PERIOD)

	# Process pygame events.
	for ThisEvent in pygame.event.get():
		# If pygame says quit, finish the application.
		if ThisEvent.type == pygame.QUIT:
			ExitFlag = True
		elif ThisEvent.type == pygame.KEYDOWN:
			KeysPressed = pygame.key.get_pressed()
			# If the ESC key is pressed, finish the application.
			if KeysPressed[pygame.K_ESCAPE]:
				ExitFlag = True
		elif ThisEvent.type == EVENT_TIMER:
			try:
				# Update the displayed date and time.
				Now = datetime.datetime.now()
				NowTime = Now.strftime("%H:%M")
				NowDate = Now.strftime("%Y-%m-%d")
				ThisDisplay.SetVisualText(ThisDisplay.CurrentTab, "TIME", NowTime)
				ThisDisplay.SetVisualText(ThisDisplay.CurrentTab, "DATE", NowDate)
		# Only process the following events if the ELM327 device is currently communicating.
		elif LockELM327.locked() == True:
			if ThisEvent.type == pygame.MOUSEBUTTONDOWN:
				# Allow GO/STOP button to be toggled while ELM327 communications are occuring.
					elif "SELECTED" in ButtonGadgit:
						ThisDisplay.CurrentTab.pop("SELECT", None)
						if ButtonGadgit["SELECTED"] != False:
							SelectLines = SelectText.split('\n')
							SelectedLine = SelectLines[ButtonGadgit["SELECTED"] - 1]
							if ButtonGadgit["GADGIT"] == "SELECT_PID":
								ThisPID = SelectedLine[SelectedLine.find("[") + 1:SelectedLine.find("]")]
								# Get a list of all valid PIDs the connected ECU supports.
								ValidPIDs = ThisELM327.GetValidPIDs()
								if ThisPID in ValidPIDs:
									if SelectGadgit[:5] != "PLOT_":
										ThisDisplay.Meters[SelectGadgit].SetPID(ThisPID, ValidPIDs[ThisPID])
									else:
										ThisDisplay.Plots["PLOT"].SetPID(int(SelectGadgit[5]) - 1, ThisPID, ValidPIDs[ThisPID])
								else:
									if SelectGadgit[:5] != "PLOT_":
										ThisDisplay.Meters[SelectGadgit].SetPID("", "")
									else:
										ThisDisplay.Plots["PLOT"].SetPID(int(SelectGadgit[5]) - 1, "", "")
							elif ButtonGadgit["GADGIT"] == "SELECT_FONT_NAME":
								Config.ConfigValues["FontName"] = SelectedLine
							elif ButtonGadgit["GADGIT"] == "SELECT_SERIAL_PORT_NAME":
								Config.ConfigValues["SerialPort"] = SelectedLine
							elif ButtonGadgit["GADGIT"] == "SELECT_VEHICLE_NAME":
								Config.ConfigValues["Vehicle"] = SelectedLine
					elif ButtonGadgit["BUTTON"] == "RESET":
						ThisDisplay.Plots["PLOT"].ClearData()
					# If configure button is pressed.
					elif ButtonGadgit["BUTTON"] == "CONFIG":
						# Display configuration dialog.
						ThisDisplay.CurrentTab["CONFIGURE"] = Config.Config(ThisDisplay.ThisSurface, "CONFIGURE", "CONFIGURE")
					# If save config button is pressed.
					elif ButtonGadgit["BUTTON"] == "SAVE_CONFIG":
						ThisDisplay.CurrentTab.pop("CONFIGURE", None)
						ApplyConfig()
					elif ButtonGadgit["BUTTON"] == "SELECT_FONT":
						# Get a list of mono space font names.
						SelectText = ThisDisplay.CurrentTab["CONFIGURE"].GetFontNameList()
					elif ButtonGadgit["BUTTON"] == "SELECT_VEHICLE":
						# Remember which gadgit the select is for.
						SelectGadgit = ButtonGadgit["GADGIT"]
						# Get a list of vehicle trouble code file names.
						SelectText = ThisDisplay.CurrentTab["CONFIGURE"].GetVehicleNameList()
						# Display a font name selection dialog.
						ThisDisplay.CurrentTab["SELECT"] = Select.Select(ThisDisplay.ThisSurface, "SELECT_SERIAL_PORT_NAME", SelectText)
					# If connect button is pressed, connect to the CAN BUS.
					elif ButtonGadgit["BUTTON"] == "CONNECT":
						if LockELM327.acquire(0):
							_thread.start_new_thread(ConnectELM327, (ThisDisplay, ))
					# If select button is pressed, select a PID for the specific gadgit.
					elif ButtonGadgit["BUTTON"] == "SELECT" or ButtonGadgit["BUTTON"][:5] == "PLOT_":
						# Remember which gadgit the select is for.
						if ButtonGadgit["BUTTON"] == "SELECT":
							SelectGadgit = ButtonGadgit["GADGIT"]
						else:
							SelectGadgit = ButtonGadgit["BUTTON"]
						# Get a list of all valid PIDs the connected ECU supports.
						ValidPIDs = ThisELM327.GetValidPIDs()
						# Get the information available for each of the supported PIDs.
						SelectText = "NONE\n"
						for PID in sorted(ValidPIDs):
							if ValidPIDs[PID][ELM327.FIELD_PID_DESCRIPTION] != '!':
								PidDescription = ValidPIDs[PID].split("|")
								SelectText += "[" + PID + "] " + PidDescription[0] + "\n"
						# Display a PID selection dialog.
						ThisDisplay.CurrentTab["SELECT"] = Select.Select(ThisDisplay.ThisSurface, "SELECT_PID", SelectText)
					# If close button is pressed, close the relavent dialog.
					elif ButtonGadgit["BUTTON"] == "CLOSE":
						if ButtonGadgit["BUTTON"] == "SELECT":
							ThisDisplay.CurrentTab.pop("SELECT", None)
						elif ButtonGadgit["BUTTON"] == "CONFIGURE":
							ThisDisplay.CurrentTab.pop("CONFIGURE", None)
					# If add button is pressed, add a new gadgit to the meters tab.
					elif ButtonGadgit["BUTTON"] == "LOCK":
						if ThisDisplay.Meters["LOCK"].GetDown() == False:
							ThisDisplay.Meters["ADD"].SetVisible(True)
						else:
							ThisDisplay.Meters["ADD"].SetVisible(False)
						for ThisGadget in ThisDisplay.Meters:
							if type(ThisDisplay.Meters[ThisGadget]) is not str and type(ThisDisplay.Meters[ThisGadget]) is not Button.Button:
								for ThisButton in ThisDisplay.Meters[ThisGadget].Buttons:
									if ThisDisplay.Meters["LOCK"].GetDown() == False:
										ThisDisplay.Meters[ThisGadget].Buttons[ThisButton].SetVisible(True)
									else:
										ThisDisplay.Meters[ThisGadget].Buttons[ThisButton].SetVisible(False)
# Update the display.
ThisDisplay.Display()
# Save the current state of the meters tab to resume when next run.
ThisDisplay.SaveMetersTab()
# Save the config for the plot series.
ThisDisplay.Plots["PLOT"].SaveSeriesConfig()
# Terminate application.
pygame.time.set_timer(EVENT_TIMER, 0)
ThisDisplay.Close()
quit()

