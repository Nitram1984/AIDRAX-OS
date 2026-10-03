import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    color: "#0B0712"

    Rectangle {
        anchors.centerIn: parent
        width: 420
        height: 260
        radius: 28
        color: "#E617121F"
        border.width: 1
        border.color: "#8B5CF6"

        Column {
            anchors.fill: parent
            anchors.margins: 32
            spacing: 18

            Text {
                text: "AIDRAX OS"
                color: "#F8F5FF"
                font.family: "Inter"
                font.pixelSize: 32
                font.weight: Font.DemiBold
            }

            Text {
                text: "SESSION LOCKED"
                color: "#B69CFF"
                font.pixelSize: 13
            }

            Text {
                text: Qt.formatTime(new Date(), "HH:mm")
                color: "#F8F5FF"
                font.pixelSize: 48
            }

            Text {
                text: "AIDRAX • SYSTEM SECURED"
                color: "#37F29A"
                font.pixelSize: 13
            }
        }
    }
}
