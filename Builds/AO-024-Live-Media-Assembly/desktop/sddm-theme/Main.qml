import QtQuick 2.15
import QtQuick.Controls 2.15
import SddmComponents 2.0

Rectangle {
    width: 1920
    height: 1080
    color: "#070a18"
    Image {
        anchors.fill: parent
        source: "aidrax-spectral-dragon-001.png"
        fillMode: Image.PreserveAspectCrop
    }
    Rectangle { anchors.fill: parent; color: "#08091d"; opacity: 0.42 }
    Text {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        anchors.topMargin: 110
        text: "AIDRAX OS"
        color: "#d5dcff"
        font.pixelSize: 46
        font.letterSpacing: 8
    }
    Column {
        anchors.centerIn: parent
        width: 420
        spacing: 14
        TextField {
            id: userName
            width: parent.width
            placeholderText: "Benutzer"
        }
        TextField {
            id: password
            width: parent.width
            echoMode: TextInput.Password
            placeholderText: "Passwort"
            onAccepted: sddm.login(userName.text, password.text, sessionModel.lastIndex)
        }
        Button {
            text: "ANMELDEN"
            width: parent.width
            onClicked: sddm.login(userName.text, password.text, sessionModel.lastIndex)
        }
    }
}
