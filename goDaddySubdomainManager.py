# when changes are made prompt user if exiting without saving
# set height accd to # of tems

useGUI=True

domain=""
APIKey=""

style="original"; # Valid values are "original", "light" or "dark"

# Do not edit anything below this line
if style != "original" and style != "light" and style != "dark":
     print("Invalid style. Valid values are original, light or dark")
     sys.exit(0)

demoMode = False

if useGUI == True and demoMode == True:
     domain = "example.com"
     APIKey="0123456789012345678901234567890123456789012345678901234567";
     
# Package imports
import pkgutil
import sys

# Before trying to import these packages, validate if they are installed first
if pkgutil.find_loader("json") is None:
     print("json package is missing. Please run pip install json to install it")
     sys.exit(0)
     
if pkgutil.find_loader("requests") is None:
     print("requests package is missing. Please run pip install requests to install it")
     sys.exit(0)

# Only required if useGUI=true
if useGUI == True and pkgutil.find_loader("PySide6") is None:
     print("PySide6 package is missing. Please run pip install PySide6 to install it")
     sys.exit(0)

import json;
import requests;

if useGUI == True:
     from PySide6.QtCore import Qt, Slot
     from qtpy.QtWidgets import QApplication, QMainWindow,QLabel,QLineEdit,QListWidget,QMessageBox,QPushButton,QWidget
     #from PySide6.QtWidgets import (QApplication,QLabel,QLineEdit,QListWidget,QMessageBox,QPushButton,QWidget)
     import qtmodern.styles
     import qtmodern.windows
     
if useGUI == False and domain == "":
     print("Please enter the domain");
     sys.exit();

if useGUI == False and APIKey == "":
     print("Please enter your API Key");
     sys.exit();

url=f"https://api.godaddy.com/v1/domains/{domain}/records/A/";

headers={'Authorization': 'sso-key ' + APIKey,'Content-Type' : 'application/json','accept' : 'application/json'};

currentSubDomains=[];
publicIPAddress="";

actions=["Add record","Rename record","Delete record","View all record","Save changes"]

def actionMenu():
     global actions;

     for index,currentAction in enumerate(actions):
          print(str(index+1) + ". " + currentAction);

     print("99. Exit");

def getARecords(overrideDomain="",overrideAPIKey=""):
     global APIKey;
     global currentSubDomains;
     global domain;
     global headers;
     global URL;
     
     if overrideDomain != "":
          domain=overrideDomain
     
     if overrideAPIKey != "":
          APIKey=overrideAPIKey
    
     if useGUI == False and domain == "":
          return
     
     if useGUI == True:
          if domain == "":
               return "Domain is not set"
          
          if APIKey == "":
               return "API Key is not set"

     try:
          url=f"https://api.godaddy.com/v1/domains/{domain}/records/A/";
          
          resp = requests.get(url,headers=headers);

          currentSubDomains = resp.json();

          return ""
     except:
          print("An error occurred");
          return "an error occcurred"

def getPublicIPAddress():
     global publicIPAddress;

     try:
          resp = requests.get("https://api.ipify.org");

          publicIPAddress=resp.content.decode();
     except:
          print("An error occurred");
          sys.exit()

def getUserInput():
     global actions;
     global currentSubDomains;
     global headers;
     global publicIPAddress;
     global url;

     while True:
          actionMenu();

          action=input("Please select an action: ");
          action=int(action);

          if action == 1: # Add Record
               newSubDomain=input("Please enter the name of the new sub domain or empty to cancel: ");

               if newSubDomain == "":
                    continue;

               # Make sure it doesn't exist already
               newSubDomainExists = False;

               for index,currentDomain in enumerate(currentSubDomains):
                    if currentDomain['name'] == newSubDomain:
                         print(f"Error! The sub domain {newSubDomain} exists already")
                         newSubDomainExists = True;
                         break;

               if newSubDomainExists == False:
                    currentSubDomains.append({'data' : publicIPAddress,'name': newSubDomain,'ttl': 600,'type': 'A'});
                    print(currentSubDomains);
          if action == 2: # Rename record (delete and create)
               subDomainMenu();

               subdomain=input("Please select the sub domain to rename: ");
               subdomain=int(subdomain);

               if subdomain == 99:
                    continue;

               newSubDomain=input("Please enter the new name for this sub domain or empty to cancel: ");

               if newSubDomain == "":
                    continue;

               # Make sure it doesn't exist already
               newSubDomainExists = False;

               for index,currentDomain in enumerate(currentSubDomains):
                    if currentDomain['name'] == newSubDomain:
                         print(f"Error! The sub domain {newSubDomain} already exists")
                         newSubDomainExists = True;
                         break;

               if newSubDomainExists == False:
                    currentSubDomains.pop(subdomain-1); # Remove old item
                    currentSubDomains.append({'data' : publicIPAddress,'name': newSubDomain,'ttl': 600,'type': 'A'});
          if action == 3: # Delete record
               subDomainMenu();

               subdomain=input("Please select the sub domain to delete: ");
               subdomain=int(subdomain);

               currentSubDomains.pop(subdomain-1);
          if action == 4: # View all records
               for currentDomain in currentSubDomains:
                    print(currentDomain['name']);
          if action == 5: # Save changes
               try:
                    resp = requests.put(url,headers=headers,data=json.dumps(currentSubDomains));
                    print("The A records have been saved to Go Daddy")
               except:
                    print("An error occurred");
          if action == 99:
               sys.exit();

          if action < 0 or action > len(actions):
               print("Invalid action")

def subDomainMenu():
     global currentSubDomains;

     for index,currentDomain in enumerate(currentSubDomains):
          print(str(index+1) + ". " + currentDomain['name']);

     print("99. Cancel");

getARecords();
getPublicIPAddress();

if useGUI == True:
     class GoDaddyDNSManager(QMainWindow):
          def __init__(self):
               QWidget.__init__(self)
        
               self.resize(1150, 750)
        
               self.gdDomainLabel = QLabel(self)
               self.gdDomainLabel.setText("Go Daddy Domain: ")
               self.gdDomainLabel.setMinimumWidth(150)
               self.gdDomainLabel.move(5,25)
               
               self.gdDomainField = QLineEdit(self)
               self.gdDomainField.setMinimumWidth(200)
               self.gdDomainField.setText(domain)
               self.gdDomainField.move(140,23)
               
               self.gdAPIKeyLabel = QLabel(self)
               self.gdAPIKeyLabel.setText("API Key: ")
               self.gdAPIKeyLabel.move(355,25)
               
               self.gdAPIKeyField = QLineEdit(self)
               self.gdAPIKeyField.setMinimumWidth(550)
               self.gdAPIKeyField.setText(APIKey)
               self.gdAPIKeyField.move(420,23)
               
               self.loadSubDomainsButton = QPushButton(self)
               self.loadSubDomainsButton.setText("Load Sub Domains")
               self.loadSubDomainsButton.setMinimumWidth(150)
               self.loadSubDomainsButton.move(975,23)
               self.loadSubDomainsButton.clicked.connect(self.loadSubDomains)
                        
               self.addLabel = QLabel(self)
               self.addLabel.setText("Add sub domain")
               self.addLabel.setMinimumWidth(120)
               self.addLabel.move(5,65)
        
               self.addField = QLineEdit(self)
               self.addField.setMinimumWidth(550)
               self.addField.move(150,63)
        
               self.addButton = QPushButton(self)
               self.addButton.setText("Add")
               self.addButton.move(720,63)
               self.addButton.clicked.connect(self.addButtonClicked)
        
               self.saveButton = QPushButton(self)
               self.saveButton.setText("Save")
               self.saveButton.move(1000,62)
               self.saveButton.clicked.connect(self.saveButtonClicked)
        
               self.subDomainsList = QListWidget(self)
               self.subDomainsList.setSortingEnabled(True)
               self.subDomainsList.itemClicked.connect(self.listItemClicked)               
               self.subDomainsList.move(5,120)
               self.subDomainsList.setMinimumWidth(250)
               #self.subDomainsList.setMinimumHeight(530)

               self.loadSubDomains(True)
               
               self.newNameLabel = QLabel(self)
               self.newNameLabel.setText("New sub domain name")
               self.newNameLabel.setMinimumWidth(250)
               self.newNameLabel.move(280,180)
               self.newNameLabel.hide()
               
               self.newNameField = QLineEdit(self)
               self.newNameField.move(450,178)
               self.newNameField.hide()
               
               self.renameButton = QPushButton(self)
               self.renameButton.setText("Rename")
               self.renameButton.move(600,178)
               self.renameButton.clicked.connect(self.renameButtonClicked)
               self.renameButton.hide()
               
               self.deleteButton = QPushButton(self)
               self.deleteButton.setText("Delete")
               self.deleteButton.move(600,250)
               self.deleteButton.clicked.connect(self.deleteButtonClicked)
               self.deleteButton.hide()

          def addButtonClicked(self):
               if self.addField.text() == "":
                    self.messageBox("Add new sub domain","Please enter the name of the subdomain to add")
             
               for index,currentDomain in enumerate(currentSubDomains):
                    if (currentDomain['name']== self.addField.text()):
                         self.messageBox("Add new sub domain",f"Error! The sub domain {self.addField.text()} exists already")
                         return
               currentSubDomains.append({'data' : publicIPAddress,'name': self.addField.text(),'ttl': 600,'type': 'A'});
        
               self.subDomainsList.addItem(self.addField.text())
               
               self.adjustSubDomainListHeight()
        
               self.addField.setText("")

          def adjustSubDomainListHeight(self):
               newHeight=self.subDomainsList.count()*17.1 if self.subDomainsList.count()*17.1 <  615 else 615;
               
               self.subDomainsList.setMinimumHeight(newHeight)
               
          def deleteButtonClicked(self):
               result = self.messageBox_YesNo("Delete Subdomains from Go Daddy", "Are you sure you want to delete this sub domain ?")

               if result == "NO":
                    return

               selectedItems=self.subDomainsList.currentItem().text()
               
               self.subDomainsList.takeItem(self.subDomainsList.currentRow())
               
               # Find and delete item
               for index,currentDomain in enumerate(currentSubDomains):
                    if currentDomain['name'] == selectedItems:
                         currentSubDomains.pop(index);
                
               self.adjustSubDomainListHeight()
                
          def listItemClicked(self):
               if len(self.subDomainsList.selectedItems()) != 0:
                    self.newNameLabel.show()
                    self.newNameField.show()
                    self.renameButton.show()
                    self.deleteButton.show()
               else:
                    self.newNameLabel.hide()
                    self.newNameField.hide()
                    self.renameButton.hide()
                    self.deleteButton.hide()
               
          def loadSubDomains(self,initialLoading):
               self.subDomainsList.clear()
               
               
               if demoMode == False:     
                    resp=getARecords(self.gdDomainField.text(),self.gdAPIKeyField.text())
         
                    if initialLoading != True and resp != "":
                         self.messageBox("An error occurred getting the records",resp)
                         return

                    for index,currentDomain in enumerate(currentSubDomains):
                         self.subDomainsList.addItem(currentDomain['name'])
                         
                    self.adjustSubDomainListHeight()
               else:
                    self.subDomainsList.addItem('subdomain1')
                    self.subDomainsList.addItem('subdomain2')
                    self.subDomainsList.addItem('subdomain3')
                    
          # Display MessageBox with Ok button
          def messageBox(self, title, message):
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
                              self.newNameField.setText("")
                    
                              return
                        
                    self.subDomainsList.takeItem(self.subDomainsList.currentRow())
              
                    # Find and delete item
                    for index,currentDomain in enumerate(currentSubDomains):
                         if currentDomain['name'] == selectedItems:
                              currentSubDomains.pop(index);

                    currentSubDomains.append({'data' : publicIPAddress,'name': newSubDomain,'ttl': 600,'type': 'A'});
                    
                    self.subDomainsList.addItem(newSubDomain)
               else:
                    self.messageBox("Rename","Please enter the new name for the sub domain")
              
          def saveButtonClicked(self):
               result = self.messageBox_YesNo("Save Subdomains to Go Daddy", "Are you sure you want to save these sub domains ?")

               if result == "NO":
                    return

               try:
                    resp = requests.put(url,headers=headers,data=json.dumps(currentSubDomains));
                    self.messageBox("Save sub domains","The sub domains have been saved")
               except:
                    self.messageBox("Save sub domains","An error occurred saving the sub domains")

if __name__ == "__main__" and useGUI == True:
     app = QApplication(sys.argv)
     
     if style == "light":
          qtmodern.styles.light(app)
          
     if style == "dark":
          qtmodern.styles.dark(app)
    
     if style == "light" or style == "dark":
          mw = qtmodern.windows.ModernWindow(GoDaddyDNSManager())
          mw.show()
     else:
          widget = GoDaddyDNSManager()
          widget.show()
     
     sys.exit(app.exec_())   
else:
     getARecords()
     getPublicIPAddress()
     getUserInput()
