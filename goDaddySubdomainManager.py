import pkgutil
import sys
import json
import os
import requests
import threading
from configparser import ConfigParser

def actionMenu():
     global actions

     for index,currentAction in enumerate(actions):
          print(str(index+1) + ". " + currentAction)

     print("99. Exit")

def getARecords(overrideDomain="",overrideAPIKey=""):
     global APIKey
     global currentSubDomains
     global domain
     
     if overrideDomain != "":
          domain=overrideDomain
     
     if overrideAPIKey != "":
          APIKey=overrideAPIKey
      
     if domain == "" or APIKey == "":
          return ["ERROR","Domain or API key is not set"]
     
     headers={'Authorization': 'sso-key ' + APIKey,'Content-Type' : 'application/json','accept' : 'application/json'}

     try:
          url=f"https://api.godaddy.com/v1/domains/{domain}/records/A/"
          
          resp = requests.get(url,headers=headers)          
                   
          if resp.status_code != 200: 
               return ["ERROR","An error occcurred. Please check your domain & API key"]
               
          currentSubDomains = resp.json()

          return ["OK"]
     except:
          return ["ERROR","An error occcurred. Please check your domain & API key"]

def getPublicIPAddress():
     global publicIPAddress

     try:
          resp = requests.get("https://api.ipify.org")

          publicIPAddress=resp.content.decode()
     except:
          print("An error occurred")
          sys.exit()

def getUserInput():
     global actions
     global currentSubDomains
     global headers
     global publicIPAddress
     global url

     while True:
          actionMenu()

          action=input("Please select an action: ")
          action=int(action)

          if action == 1: # Add Record
               newSubDomain=input("Please enter the name of the new sub domain or empty to cancel: ")

               if newSubDomain == "":
                    continue

               # Make sure it doesn't exist already
               newSubDomainExists = False

               for index,currentDomain in enumerate(currentSubDomains):
                    if currentDomain['name'] == newSubDomain:
                         print(f"Error! The sub domain {newSubDomain} exists already")
                         newSubDomainExists = True
                         break

               if newSubDomainExists == False:
                    currentSubDomains.append({'data' : publicIPAddress,'name': newSubDomain,'ttl': 600,'type': 'A'})
                    #print(currentSubDomains)
          if action == 2: # Rename record (delete and create)
               subDomainMenu()

               subdomain=input("Please select the sub domain to rename: ")
               subdomain=int(subdomain)

               if subdomain == 99:
                    continue

               newSubDomain=input("Please enter the new name for this sub domain or empty to cancel: ")

               if newSubDomain == "":
                    continue

               # Make sure it doesn't exist already
               newSubDomainExists = False

               for index,currentDomain in enumerate(currentSubDomains):
                    if currentDomain['name'] == newSubDomain:
                         print(f"Error! The sub domain {newSubDomain} already exists")
                         newSubDomainExists = True
                         break

               if newSubDomainExists == False:
                    currentSubDomains.pop(subdomain-1) # Remove old item
                    currentSubDomains.append({'data' : publicIPAddress,'name': newSubDomain,'ttl': 600,'type': 'A'})
          if action == 3: # Delete record
               subDomainMenu()

               subdomain=input("Please select the sub domain to delete: ")
               subdomain=int(subdomain)

               currentSubDomains.pop(subdomain-1)
          if action == 4: # View all records
               for currentDomain in currentSubDomains:
                    print(currentDomain['name'])
          if action == 5: # Save changes
               try:
                    url=f"https://api.godaddy.com/v1/domains/{domain}/records/A/"
                    headers={'Authorization': 'sso-key ' + APIKey,'Content-Type' : 'application/json','accept' : 'application/json'}
                    
                    resp = requests.put(url,headers=headers,data=json.dumps(currentSubDomains))
                    print("The A records have been saved to GoDaddy")
               except:
                    print("An error occurred")
          if action == 99:
               sys.exit()

          if action < 0 or action > len(actions):
               print("Invalid action")

def readPreference(preferenceName,type = 'string'):
     global config
     global configFile
     
     config.read(configFile)

     try:
          if type == 'string':
               return config['DEFAULT'][preferenceName]
          elif type == 'boolean':
               val=config['DEFAULT'][preferenceName]
               
               if val == "True" or val == True:
                    return True
               else:
                    return False
     except:
          return ""

def savePreferences(overrideDomain="",overrideAPIKey="", overrideTheme=""):
     global APIKey
     global config
     global configFile
     global domain
     global theme
     
     if overrideDomain != "":
          currentDomain=overrideDomain
     else:
          currentDomain=domain
     
     if overrideAPIKey != "":
          currentAPIKey=overrideAPIKey
     else:
          currentAPIKey=APIKey
     
     if overrideTheme != "":
          currentTheme=overrideTheme
     else:
          currentTheme=theme

     config['DEFAULT']={ 'Domain' : currentDomain, 'APIKey': currentAPIKey, 'Theme' : currentTheme }
     
     with open(configFile, 'w') as configfile:
          config.write(configfile)

def subDomainMenu():
     global currentSubDomains

     for index,currentDomain in enumerate(currentSubDomains):
          print(str(index+1) + ". " + currentDomain['name'])

     print("99. Cancel")

# Check if these packages are installed before trying to import them
if pkgutil.find_loader("json") is None:
     print("json package is missing. Please run pip install json to install it")
     sys.exit(0)
     
if pkgutil.find_loader("requests") is None:
     print("requests package is missing. Please run pip install requests to install it")
     sys.exit(0)

# These vars will be read from the ini
domain=""
APIKey=""
theme=""
useGUI=False

actions=["Add record","Rename record","Delete record","View all records","Save changes"]
headers={'Authorization': 'sso-key ' + APIKey,'Content-Type' : 'application/json','accept' : 'application/json'}
url=f"https://api.godaddy.com/v1/domains/{domain}/records/A/"

aRecordsResponse=""
currentSubDomains=[]
publicIPAddress=""
demoMode = False
width=1150
configFile='config.ini'

# Load preferences from ini
config = ConfigParser()

domain=readPreference('Domain')
APIKey=readPreference('APIKey')
theme=readPreference('theme')
useGUI=readPreference('useGUI','boolean')

# You can force useGUI=True with a setting in config.ini or a command line parameter
if len(sys.argv) == 2 and sys.argv[1] == "--gui" and useGUI == False:
     useGUI=True

if useGUI == True:
     if pkgutil.find_loader("PySide6") is None:
          print("PySide6 package is missing. Please run pip install PySide6 to install it")
          sys.exit(0)

     if pkgutil.find_loader("qtmodern") is None:
          print("qtmodern package is missing. Please run pip install qtmodern to install it")
          sys.exit(0)

      # Only needed when using GUI
     from PySide6.QtCore import QEvent, QSize, Qt, Slot
     from PySide6.QtGui import QIcon, QPixmap
     from qtpy.QtWidgets import QApplication, QComboBox, QLabel, QLineEdit, QListWidget, QMainWindow, QMessageBox, QPushButton, QWidget
     import qtmodern.styles
     import qtmodern.windows
     
     class GoDaddyDNSManager(QWidget):
          isModified = False
          
          def __init__(self):
               YCoord = {
                    'row1': 40,
                    'row2': 120
               }
               
               sizes = { # fixed size and coordinates for all elements so I can easily adjust the position for all elements from one place
                    'MainWindowWidth' : 1150,
                    'MainWindowHeight' : 725,
                    'ThemeDropdownX' : 1075,
                    'ThemeDropdownY' : 4,
                    'AddLabelMinimumWidth' : 120,
                    'AddLabelX' : 5,
                    'AddLabelY' : YCoord['row1'],
                    'AddFieldMinimumWidth' : 90,
                    'AddFieldX' : 140,
                    'AddFieldY' : YCoord['row1'],
                    'AddButtonX' : 355,
                    'AddButtonY' : YCoord['row1']-2,
                    'SaveButtonX' : 620,
                    'SaveButtonY' : YCoord['row1']-2,
                    'SubDomainsListX' : 5,
                    'SubDomainsListY' : YCoord['row2'],
                    'SubDomainsMinimumWidth' : 250,
                    'SubDomainsMaximumWidth' : 330,
                    'NewNameLabelMinimumWidth' : 250,
                    'NewNameLabelX' : 280,
                    'NewNameLabelY' : YCoord['row2'],
                    'NewNameFieldX' : 450,
                    'NewNameFieldY' : YCoord['row2']-2,
                    'RenameButtonX' : 600,
                    'RenameButtonY' : YCoord['row2'],
                    'DeleteButtonX' : 600,
                    'DeleteButtonY' : YCoord['row2'] + 50,
               }

               super().__init__()

               self.setFixedSize(sizes['MainWindowWidth'], sizes['MainWindowHeight'])
               
               self.window().setWindowTitle("Go Daddy Subdomain Manager")
               
               self.themeList = QComboBox(self)
               self.themeList.addItem('light')
               self.themeList.addItem('dark')
               
               if theme == "light" or theme == "dark":
                    self.themeList.setCurrentText(theme)

               self.themeList.currentIndexChanged.connect(self.themeComboxBoxChanged)
               self.themeList.move(sizes['ThemeDropdownX'],sizes['ThemeDropdownY'])

               self.addLabel = QLabel(self)
               self.addLabel.setText("Add sub domain")
               self.addLabel.setMinimumWidth(sizes['AddLabelMinimumWidth'])
               self.addLabel.move(sizes['AddLabelX'],sizes['AddLabelY'])

               self.addField = QLineEdit(self)
               self.addField.setMinimumWidth(sizes['AddFieldMinimumWidth'])
               self.addField.move(sizes['AddFieldX'],sizes['AddFieldY'])
               
               self.addButton = QPushButton(self)
               self.addButton.setText("Add")
               self.addButton.move(sizes['AddButtonX'],sizes['AddButtonY'])
               self.addButton.clicked.connect(self.addButtonClicked)

               self.saveButton = QPushButton(self)
               self.saveButton.setText("Save")
               self.saveButton.move(sizes['SaveButtonX'],sizes['SaveButtonY'])
               self.saveButton.clicked.connect(self.saveButtonClicked)

               self.subDomainsList = QListWidget(self)
               self.subDomainsList.setSortingEnabled(True)
               self.subDomainsList.itemClicked.connect(self.listItemClicked)
               self.subDomainsList.move(sizes['SubDomainsListX'],sizes['SubDomainsListY'])
               self.subDomainsList.setMinimumWidth(sizes['SubDomainsMinimumWidth'])
               self.subDomainsList.setMaximumHeight(sizes['SubDomainsMaximumWidth'])

               self.newNameLabel = QLabel(self)
               self.newNameLabel.setText("New sub domain name")
               self.newNameLabel.setMinimumWidth(sizes['NewNameLabelMinimumWidth'])
               self.newNameLabel.move(sizes['NewNameLabelX'],sizes['NewNameLabelY'])
               
               self.newNameField = QLineEdit(self)
               self.newNameField.move(sizes['NewNameFieldX'],sizes['NewNameFieldY'])

               self.renameButton = QPushButton(self)
               self.renameButton.setText("Rename")
               self.renameButton.move(sizes['RenameButtonX'],sizes['RenameButtonY'])
               self.renameButton.clicked.connect(self.renameButtonClicked)

               self.deleteButton = QPushButton(self)
               self.deleteButton.setText("Delete")
               self.deleteButton.move(sizes['DeleteButtonX'],sizes['DeleteButtonY'])
               self.deleteButton.clicked.connect(self.deleteButtonClicked)
               
               self.hideRenameDeleteFields()
               self.loadSubDomains()
            
          def addButtonClicked(self):
               if self.addField.text() == "":
                    self.messageBox("Add new sub domain","Please enter the name of the subdomain to add")
             
               for index,currentDomain in enumerate(currentSubDomains):
                    if currentDomain['name']== self.addField.text():
                         self.messageBox("Add new sub domain",f"Error! The sub domain {self.addField.text()} exists already")
                         return
                         
               currentSubDomains.append({'data' : publicIPAddress,'name': self.addField.text(),'ttl': 600,'type': 'A'})
        
               self.subDomainsList.addItem(self.addField.text())
               
               self.isModified = True
               
               self.subDomainsList.clearSelection()
               
               self.addField.setText("")
               
               self.adjustSubDomainListHeight()
               
               self.newNameLabel.hide()
               self.newNameField.hide()
               self.renameButton.hide()
               self.deleteButton.hide()

          def adjustSubDomainListHeight(self):
               newHeight=self.subDomainsList.count()*17.1 if self.subDomainsList.count()*17.1 <  615 else 550
               
               self.subDomainsList.setMinimumHeight(newHeight)
            
          def closeEvent(self, event):
               if self.isModified == True:
                    result = self.messageBox_YesNo("Unsaved Changed", "You have unsaved changes. Are you sure you want to exit without saving these changes ?")
                    
                    if result == "NO":
                         event.ignore()
          
          def deleteButtonClicked(self):
               result = self.messageBox_YesNo("Delete Subdomains from Go Daddy", "Are you sure you want to delete this sub domain ?")

               if result == "NO":
                    return

               selectedItems=self.subDomainsList.currentItem().text()
               
               self.subDomainsList.takeItem(self.subDomainsList.currentRow())
               
               # Find and delete item
               for index,currentDomain in enumerate(currentSubDomains):
                    if currentDomain['name'] == selectedItems:
                         currentSubDomains.pop(index)
               
               self.isModified = True               
               self.hideRenameDeleteFields()
               self.adjustSubDomainListHeight()

          def hideRenameDeleteFields(self):
               self.newNameLabel.hide()
               self.newNameField.hide()
               self.renameButton.hide()
               self.deleteButton.hide()

          def listItemClicked(self):
               if len(self.subDomainsList.selectedItems()) != 0:
                    self.newNameLabel.show()
                    self.newNameField.show()
                    self.newNameField.setText(self.subDomainsList.currentItem().text())
                    
                    self.renameButton.show()
                    self.deleteButton.show()
               else:
                    self.newNameLabel.hide()
                    self.newNameField.hide()
                    self.renameButton.hide()
                    self.deleteButton.hide()
               
          def loadSubDomains(self):
               global domain
               global APIKey
               
               self.subDomainsList.clear()
               
               getPublicIPAddress()

               if demoMode == False:
                    if domain == "":
                         self.messageBox("Domain","Please enter the domain")
                         return
                    
                    if APIKey == "":
                         self.messageBox("API key","Please enter the API key")
                         return

                    resp=getARecords(domain,APIKey)
                    
                    if resp[0] != "OK":
                         self.messageBox("An error occurred getting the records",resp[1])
                         return

                    for index,currentDomain in enumerate(currentSubDomains):
                         self.subDomainsList.addItem(currentDomain['name'])
                         
                    self.adjustSubDomainListHeight()
                    
                    self.addLabel.show()
                    self.addField.show()
                    self.addButton.show()
                    self.subDomainsList.show()
                    self.saveButton.show()                   
               else:
                    self.subDomainsList.addItem('subdomain1')
                    self.subDomainsList.addItem('subdomain2')
                    self.subDomainsList.addItem('subdomain3')

          def messageBox(self, title, message): # Display MessageBox with Ok button
               QMessageBox.question(self, title, message, QMessageBox.Ok)

               return True
        
          def messageBox_YesNo(self, title, message):
               reply = QMessageBox.question(self, title, message, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

               if reply == QMessageBox.Yes:
                    return "YES"
               else:
                    return "NO"
              
          def renameButtonClicked(self):
               selectedItems=self.subDomainsList.currentItem().text()
         
               if len(selectedItems) == 0:
                    self.messageBox("Rename","Please select the sub domain to rename")
                    return

               if self.newNameField.text() != "":
                    newSubDomain = self.newNameField.text()

                    # Make sure it doesn't exist already
                    for index,currentDomain in enumerate(currentSubDomains):
                         if currentDomain['name'] == newSubDomain:
                              self.messageBox("Error!",f"The new sub domain name {newSubDomain} already exists")
                    
                              return
                        
                    self.subDomainsList.takeItem(self.subDomainsList.currentRow())
              
                    # Find and delete item
                    for index,currentDomain in enumerate(currentSubDomains):
                         if currentDomain['name'] == selectedItems:
                              currentSubDomains.pop(index)

                    currentSubDomains.append({'data' : publicIPAddress,'name': newSubDomain,'ttl': 600,'type': 'A'})
                    
                    self.subDomainsList.addItem(newSubDomain)
                    
                    self.isModified = True
                    
                    self.newNameField.setText("")
                    self.hideRenameDeleteFields()
               else:
                    self.messageBox("Rename","Please enter the new name for the sub domain")
              
          def saveButtonClicked(self):
               result = self.messageBox_YesNo("Save Subdomains to Go Daddy", "Are you sure you want to save these sub domains ?")

               if result == "NO":
                    return

               try:
                    resp = requests.put(url,headers=headers,data=json.dumps(currentSubDomains))
                    
                    self.messageBox("Save sub domains","The sub domains have been saved")
                    
                    self.isModified = False
               except:
                    self.messageBox("Save sub domains","An error occurred saving the sub domains")

          def themeComboxBoxChanged(self): 
               global theme
               
               currentTheme = self.themeList.currentText()

               if currentTheme == "light":                    
                    qtmodern.styles.light(QApplication.instance())
                    theme="light"
                    savePreferences()
               elif currentTheme == "dark":
                    qtmodern.styles.dark(QApplication.instance())
                    theme="dark"
                    savePreferences()

if demoMode == True:
     domain = "example.com"
     APIKey="0123456789012345678901234567890123456789012345678901234567"
     aRecordsResponse=["OK","Demo Mode"];
elif domain != "" and APIKey != "":
     aRecordsResponse=getARecords()
     
     getPublicIPAddress()
else:
     aRecordsResponse=["ERROR","Domain or API key is not set. Please edit config.ini"];

if __name__ == "__main__" and useGUI == True:
     
     app = QApplication(sys.argv)
     
     if theme == "light":
          qtmodern.styles.light(app)
     elif theme == "dark":
          qtmodern.styles.dark(app)

     gdWindow=GoDaddyDNSManager()    
     mw = qtmodern.windows.ModernWindow(gdWindow)
     mw.btnMaximize.hide()
     
     if aRecordsResponse[0] != "OK":
          print(aRecordsResponse[1])
          sys.exit()

     try: # Write icon. If this doesn't succeed its no big deal
          # Write temporary output file icon.py
          from pathlib import Path
          hex_content = Path('icon.png').read_bytes()
          Path('icon.py').write_text(f'icon = {hex_content}')
          from icon import icon

          pixmap = QPixmap()
          pixmap.loadFromData(icon)
          appIcon = QIcon(pixmap)
          mw.setWindowIcon(appIcon)

          os.remove('icon.py') # Remove temporary generated file
     except:
          ""

     mw.show()
     
     sys.exit(app.exec_())   
else:
     if aRecordsResponse[0] == "OK":
          getUserInput()
     else:
          print(aRecordsResponse[1])
          sys.exit()