#!/bin/sh

rm inventory.json
buildozer android debug
scp bin/office_arbi* jeff@192.168.2.2:~/apk/office_arbitrage.apk
