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
#apply config
def ApplyConfig():
	Config.LoadConfig()
	ELM327.DEBUG = Config.ConfigValues["Debug"]
	ELM327.SERIAL_PORT_NAME = Config.ConfigValues["SerialPort"]
	ThisDisplay.DEBUG = Config.ConfigValues["Debug"]
	ThisELM327.LoadVehicle(Config.ConfigValues["Vehicle"])
	Visual.VisualZOrder[0].SetFont(Config.ConfigValues["FontName"])
#Info on vali PIDs
def FrameData(ThisDisplay):
	try:
		# Get a list of all valid PIDs the connected ECU supports.
		ValidPIDs = ThisELM327.GetValidPIDs()
		# Get the information available for each of the supported PIDs.
		ThisDisplay.SetVisualText(ThisDisplay.FrameData, "INFO", "", False)
		for PID in sorted(ValidPIDs):
			if ValidPIDs[PID][ELM327.FIELD_PID_DESCRIPTION] != '!':
				# Display the information returned for the current PID.
				if PID[1] == '1':
					PidData = ThisELM327.DoPID(PID)
					ThisDisplay.SetVisualText(ThisDisplay.FrameData, "INFO", "[" + PID + "] " + ValidPIDs[PID] + "\n", True, PidData)
	except Exception as Catch:
		print(str(Catch))
	# Allow another ELM327 communication now this one is complete.
	LockELM327.release()
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

				# Unhighlight pressed buttons which are not latch or toggle.
				for ThisVisual in Visual.VisualZOrder:
					if ThisVisual.GetName() not in FlashVisuals and ThisVisual.GetPressType() == Visual.PRESS_DOWN:
						ThisVisual.SetDown(False)

				# Flash visual instances flagged to be flashed.
				for ThisVisual in FlashVisuals:
					if FlashVisuals[ThisVisual].GetDown() == False:
						FlashVisuals[ThisVisual].SetDown(True)
					else:
						FlashVisuals[ThisVisual].SetDown(False)
			except Exception as Catch:
				print(str(Catch))
		# Only process the following events if the ELM327 device is currently communicating.
		elif LockELM327.locked() == True:
			if ThisEvent.type == pygame.MOUSEBUTTONDOWN:
				# Allow GO/STOP button to be toggled while ELM327 communications are occuring.
				if ThisDisplay.CurrentTab == ThisDisplay.Meters:
					ThisDisplay.Meters["GO_STOP"].IsEvent(Visual.EVENT_MOUSE_DOWN, ThisEvent.pos[0], ThisEvent.pos[1], ThisEvent.button)
				elif ThisDisplay.CurrentTab == ThisDisplay.Plots:
					ThisDisplay.Plots["GO_STOP"].IsEvent(Visual.EVENT_MOUSE_DOWN, ThisEvent.pos[0], ThisEvent.pos[1], ThisEvent.button)

		# Only process the following events if the ELM327 device is not currently communicating.
		elif LockELM327.locked() == False:
			if ThisEvent.type == pygame.MOUSEBUTTONDOWN:
				# Pass button down events to all buttons and gadgits.
				ButtonGadgit = ThisDisplay.IsEvent(Visual.EVENT_MOUSE_DOWN, ThisEvent.pos[0], ThisEvent.pos[1], ThisEvent.button)
				if Config.ConfigValues["Debug"] == "ON":
					print(str(ButtonGadgit))
				if ButtonGadgit != False:
					# If exit button is pressed, finish the application.
					if ButtonGadgit["BUTTON"] == "EXIT":
						# Display a confirmation to exit the application.
						ThisDisplay.CurrentTab["CONFIRM"] = Confirm.Confirm(ThisDisplay.ThisSurface, "CONFIRM_EXIT", "Exit the application?")
					# If confirm dialog button yes is pressed, close the dialog.
					elif ButtonGadgit["BUTTON"] == "YES":
						ThisDisplay.CurrentTab.pop("CONFIRM", None)
						if ButtonGadgit["GADGIT"] == "CONFIRM_EXIT":
							ExitFlag = True
						elif ButtonGadgit["GADGIT"] == "CONFIRM_CLEAR_ECU":
							if LockELM327.acquire(0):
								_thread.start_new_thread(ClearTroubleInfo, (ThisDisplay, ))
					# If confirm dialog button no is pressed, close the dialog.
					elif ButtonGadgit["BUTTON"] == "NO":
						ThisDisplay.CurrentTab.pop("CONFIRM", None)
					# If select dialog selection is made, close the dialog.
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
						# Remember which gadgit the select is for.
						SelectGadgit = ButtonGadgit["GADGIT"]
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
					# If vehicle button is pressed, get the vehicle data from the ECU.
					elif ButtonGadgit["BUTTON"] == "VEHICLE":
						if LockELM327.acquire(0):
							_thread.start_new_thread(VehicleData, (ThisDisplay, ))
					# If clear button is pressed, clear the trouble and related data on the ECU.
					elif ButtonGadgit["BUTTON"] == "CLEAR":
						# Display a confirmation to clear ECU trouble codes.
						ThisDisplay.CurrentTab["CONFIRM"] = Confirm.Confirm(ThisDisplay.ThisSurface, "CONFIRM_CLEAR_ECU", "Clear all trouble codes\nand related data\non the ECU?")
					# If GO/STOP button is pressed, start data aquisition.
					elif ButtonGadgit["BUTTON"] == "GO_STOP":
						if ThisDisplay.CurrentTab == ThisDisplay.Meters or ThisDisplay.CurrentTab == ThisDisplay.Plots:
							if LockAquisition.acquire(0):
								_thread.start_new_thread(AquisitionLoop, (ThisDisplay, ))
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
			elif ThisEvent.type == pygame.MOUSEBUTTONUP:
				# Pass button up events to all buttons and gadgits.
				ButtonGadgit = ThisDisplay.IsEvent(Visual.EVENT_MOUSE_UP, ThisEvent.pos[0], ThisEvent.pos[1], ThisEvent.button)
			elif ThisEvent.type == pygame.MOUSEMOTION:
				# When a button is down, pass movement events to all buttons and gadgits.
				if ThisEvent.buttons[0] > 0:
					ButtonGadgit = ThisDisplay.IsEvent(Visual.EVENT_MOUSE_MOVE, ThisEvent.pos[0], ThisEvent.pos[1], ThisEvent.buttons[0])
				else:
					ButtonGadgit = ThisDisplay.IsEvent(Visual.EVENT_MOUSE_HOVER, ThisEvent.pos[0], ThisEvent.pos[1], ThisEvent.buttons[0])
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

