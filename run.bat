@echo off
REM Starte Docker Compose
start cmd /k  "docker-compose up"
REM Warte 5 Sekunden bis docker eingeeschaltet 
ping -n 6 127.0.0.1 > nul
REM  Tabellen Bauen (einmalig)
start cmd /k "python -m pipenv run apply_migrations"
Rem empty data base 
start cmd /k "python -m pipenv run emptydb.py"
REM Start Main
start cmd /k "python -m pipenv run .\OPCUA\Main.py"

REM Start Kafka Producer Client
start cmd /k "python -m pipenv run .\OPCUA\KafkaProducer_Client.py"

REM Move to  kafka  ordner
cd C:\Users\yassine\Neuer Ordner (2)\daten-streaming-infrastruktur\Kafka_Test
REM Start CONSUMER  IMG + TIMESSERIES
start cmd /k "py -m pipenv run kafka_consumer_timeseries.py"
start cmd /k "py -m pipenv run kafka_consumer_image.py"


REM Move to  Faust ordner
cd C:\Users\yassine\Neuer Ordner (2)\daten-streaming-infrastruktur\Faust
REM Start Faust IMG + TIMESSERIES + Port Definition
start cmd /k "py -m pipenv run faust -A faust_test_image worker -l info --web-port 6066"
REM Start CONSUMER  IMG + TIMESSERIES
start cmd /k "py -m pipenv run kafka_consumer_test_image.py"



REM Move to  FaustAI ordner
cd C:\Users\yassine\Neuer Ordner (2)\daten-streaming-infrastruktur\FaustAI

REM Start FaustAI IMG + TIMESSERIES + Port Definition
start cmd /k "py -m pipenv run faust -A faust_test_timeseriesAI worker -l info --web-port 6067"
start cmd /k "py -m pipenv run faust -A faust_test_imageAI worker -l info --web-port 6068"

REM Start CONSUMER  IMG + TIMESSERIES
start cmd /k "py -m pipenv run kafka_consumer_test_timeseriesAI.py"
start cmd /k "py -m pipenv run kafka_consumer_test_imageAI.py"


cd C:\Users\yassine\Neuer Ordner (2)\daten-streaming-infrastruktur 
start cmd /k "py -m pipenv run  ui_plotly.py"
REM  start cmd /k "py -m pipenv run  ui_plotly_demo.py"
REM start cmd /k "py -m pipenv run  plotdb.py"


REM Prompt the user to press any key to stop the running programs
echo.
echo Press any key to stop the running programs...
pause >nul

REM Terminate the running Python processes
taskkill /f /im python.exe
taskkill /f /im py.exe
taskkill /f /im faust.exe

REM Stop Docker Compose
docker-compose down

exit
