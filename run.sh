<<<<<<< HEAD
# nohup rasa run actions >logs/log/logs_actions.txt 2>&1 & echo $! > logs/pid/actions.pid
# nohup rasa run --enable-api >logs/log/logs_rasa_api.txt 2>&1 & echo $! > logs/pid/rasa_api.pid
nohup python app.py >logs/log/logs.txt 2>&1 & echo $! > logs/pid/run.pid
=======
nohup rasa run actions >logs/log/logs_actions.txt 2>&1 & echo $! > logs/pid/actions.pid
nohup rasa run --enable-api >logs/log/logs_rasa_api.txt 2>&1 & echo $! > logs/pid/rasa_api.pid
# nohup python app.py >logs/log/logs.txt 2>&1 & echo $! > logs/pid/run.pid
>>>>>>> fc8d1f2c2afe319a6100fca45c0bcc08d1bc2dec
