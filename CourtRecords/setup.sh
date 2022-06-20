export PYTHONUNBUFFERED=1
ps -W | awk '$0~a,NF=1' a=python.exe | xargs kill -f
sleep 2
../../../python/Scripts/python setup.py develop
