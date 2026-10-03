import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtMultimedia 5.15
import org.kde.plasma.core 2.0 as PlasmaCore
import org.kde.plasma.components 3.0 as PlasmaComponents3

Item {
    id: root

    // KScreenLocker injects these in the lock-screen context.
    // We intentionally use them without replacing KDE's authentication backend.
    property var authenticator
    property string notification
    property bool capsLockOn: false

    focus: true

    MediaPlayer {
        id: bgPlayer
        source: "file://" + StandardPaths.writableLocation(StandardPaths.HomeLocation) + "/.local/share/aidrax/lockscreen/bg.mp4"
        autoPlay: true
        loops: MediaPlayer.Infinite
        muted: true
    }

    VideoOutput {
        anchors.fill: parent
        source: bgPlayer
        fillMode: VideoOutput.PreserveAspectCrop
    }

    Rectangle {
        anchors.fill: parent
        color: "#24030A18"
    }

    // User badge
    Rectangle {
        x: 48; y: 42
        width: 310; height: 74
        radius: 28
        color: "#88070B17"
        border.width: 1
        border.color: "#A0E8C85A"

        Row {
            anchors.fill: parent
            anchors.margins: 12
            spacing: 12

            Rectangle {
                width: 48; height: 48; radius: 24
                color: "#332A2A2A"
                border.width: 2
                border.color: "#E8C85A"
                Text {
                    anchors.centerIn: parent
                    text: "✦"
                    color: "#F0D46A"
                    font.pixelSize: 20
                }
            }

            Column {
                anchors.verticalCenter: parent.verticalCenter
                spacing: 2
                Text {
                    text: (typeof userName !== "undefined" && userName) ? userName.toUpperCase() : "MADDIN"
                    color: "white"
                    font.bold: true
                    font.pixelSize: 17
                }
                Text {
                    text: "AIDRAX • ASTRAL EXPRESS"
                    color: "#E8C85A"
                    font.pixelSize: 10
                    font.bold: true
                }
            }
        }
    }

    // Clock
    Column {
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.topMargin: 34
        anchors.rightMargin: 44
        horizontalAlignment: Text.AlignRight
        Text {
            id: clockText
            color: "white"
            font.pixelSize: 28
            font.bold: true
            text: Qt.formatTime(new Date(), "HH:mm")
        }
        Text {
            color: "#E8C85A"
            font.pixelSize: 12
            text: Qt.formatDate(new Date(), "dddd, dd.MM.yyyy")
        }
        Timer {
            interval: 1000
            running: true
            repeat: true
            onTriggered: clockText.text = Qt.formatTime(new Date(), "HH:mm")
        }
    }

    // Password panel
    Rectangle {
        id: loginPanel
        width: Math.min(520, parent.width - 80)
        height: 126
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 92
        radius: 24
        color: "#99070B17"
        border.width: 1
        border.color: "#88E8C85A"

        Column {
            anchors.fill: parent
            anchors.margins: 18
            spacing: 10

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: "ENTER PASSWORD"
                color: "#F0D46A"
                font.bold: true
                font.pixelSize: 12
                letterSpacing: 2
            }

            TextField {
                id: passwordField
                width: parent.width
                height: 44
                echoMode: TextInput.Password
                placeholderText: "Password"
                horizontalAlignment: TextInput.AlignHCenter
                focus: true
                onAccepted: {
                    if (typeof authenticator !== "undefined" && authenticator) {
                        authenticator.tryUnlock(passwordField.text)
                    }
                }
            }

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: (typeof notification !== "undefined" && notification) ? notification : "Click to Start"
                color: "#EAEAEA"
                font.pixelSize: 11
            }
        }
    }

    Keys.onPressed: {
        if (event.key === Qt.Key_Escape) {
            passwordField.text = ""
        } else if (event.text && event.text.length > 0 && !event.modifiers) {
            passwordField.forceActiveFocus()
        }
    }
}
