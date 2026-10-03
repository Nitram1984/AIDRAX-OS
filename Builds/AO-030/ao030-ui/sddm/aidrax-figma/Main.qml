import QtQuick 2.15
import QtQuick.Controls 2.15
import QtMultimedia 5.15
import SddmComponents 2.0
import "."

Rectangle {
    id: root
    width: 1440
    height: 900
    color: AidraxTokens.canvas

    property int userIndex: (userModel && userModel.lastIndex >= 0) ? userModel.lastIndex : 0
    property int sessionIndex: (sessionModel && sessionModel.lastIndex >= 0) ? sessionModel.lastIndex : 0
    property string selectedUser: ""
    property bool loginBusy: false

    function resolveUserName() {
        if (userModel && userModel.count > 0) {
            var name = userModel.data(
                userModel.index(root.userIndex, 0),
                Qt.UserRole + 1
            )
            if (name)
                return name
        }

        if (userModel && userModel.lastUser)
            return userModel.lastUser

        return ""
    }

    MediaPlayer {
        id: backgroundPlayer
        source: "bg.mp4"
        autoPlay: true
        loops: MediaPlayer.Infinite
        muted: true
    }

    VideoOutput {
        anchors.fill: parent
        source: backgroundPlayer
        fillMode: VideoOutput.PreserveAspectCrop
        opacity: 0.50
    }

    Rectangle {
        anchors.fill: parent
        color: "#660B0712"
    }

    Column {
        anchors.left: parent.left
        anchors.leftMargin: 72
        anchors.verticalCenter: parent.verticalCenter
        spacing: 18

        Rectangle {
            width: 216; height: 32; radius: 16
            color: AidraxTokens.surface
            border.width: 1
            border.color: AidraxTokens.accentBorder

            Text {
                anchors.centerIn: parent
                text: "AIDRAX DESIGN SYSTEM • V1"
                color: AidraxTokens.accentText
                font.family: "Inter"
                font.pixelSize: 13
                font.weight: Font.DemiBold
            }
        }

        Text {
            text: "AIDRAX OS"
            color: AidraxTokens.textPrimary
            font.family: "Inter"
            font.pixelSize: 64
            font.weight: Font.DemiBold
        }

        Text {
            text: "Adaptive intelligence.\nClearly structured."
            color: AidraxTokens.textSecondary
            font.family: "Inter"
            font.pixelSize: 18
        }

        Rectangle {
            width: 260; height: 4; radius: 2
            color: AidraxTokens.accent
        }
    }

    Column {
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.margins: 48

        Text {
            id: clock
            anchors.right: parent.right
            color: AidraxTokens.textPrimary
            font.family: "Inter"
            font.pixelSize: 28
            font.weight: Font.DemiBold

            function updateClock() {
                text = Qt.formatTime(new Date(), "HH:mm")
            }

            Component.onCompleted: updateClock()

            Timer {
                interval: 1000
                running: true
                repeat: true
                onTriggered: clock.updateClock()
            }
        }
    }

    Rectangle {
        width: 390
        height: 330
        radius: AidraxTokens.radiusXL
        anchors.right: parent.right
        anchors.rightMargin: 72
        anchors.verticalCenter: parent.verticalCenter
        color: "#CC17121F"
        border.width: 1
        border.color: AidraxTokens.accentBorder

        Column {
            anchors.fill: parent
            anchors.margins: 32
            spacing: 18

            Text {
                text: "WELCOME BACK"
                color: AidraxTokens.accentText
                font.family: "Inter"
                font.pixelSize: 13
                font.weight: Font.DemiBold
            }

            Text {
                text: selectedUser !== "" ? selectedUser : "AIDRAX USER"
                color: AidraxTokens.textPrimary
                font.family: "Inter"
                font.pixelSize: 24
                font.weight: Font.DemiBold
            }

            TextField {
                id: password
                width: parent.width
                height: 52
                placeholderText: "Password"
                echoMode: TextInput.Password
                color: AidraxTokens.textPrimary

                background: Rectangle {
                    radius: AidraxTokens.radiusMD
                    color: "#AA0B0712"
                    border.width: password.activeFocus ? 2 : 1
                    border.color: password.activeFocus
                                  ? AidraxTokens.accent
                                  : AidraxTokens.accentBorder
                }

                onAccepted: loginButton.clicked()
            }

            Button {
                id: loginButton
                width: parent.width
                height: 52
                text: loginBusy ? "AUTHENTICATING…" : "ENTER AIDRAX"

                background: Rectangle {
                    radius: AidraxTokens.radiusMD
                    color: loginButton.down
                           ? AidraxTokens.accentBorder
                           : AidraxTokens.accent
                }

                onClicked: {
                    var uname = root.resolveUserName()

                    if (uname !== "" && password.text !== "") {
                        root.selectedUser = uname
                        loginBusy = true
                        sddm.login(uname, password.text,
                                   root.sessionIndex)
                    }
                }
            }

            Text {
                id: statusText
                text: loginBusy
                      ? "Authenticating with AIDRAX OS…"
                      : "SYSTEM READY"
                color: loginBusy
                       ? AidraxTokens.statusInfo
                       : AidraxTokens.statusGreen
                font.pixelSize: 13
            }
        }
    }

    Connections {
        target: sddm
        function onLoginFailed() {
            loginBusy = false
            password.text = ""
            password.forceActiveFocus()
            statusText.text = "AUTHENTICATION FAILED"
            statusText.color = AidraxTokens.statusRed
        }
    }

    Component.onCompleted: {
        selectedUser = resolveUserName()
        password.forceActiveFocus()
    }
}
