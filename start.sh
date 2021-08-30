if [ ! -d venv ]; then
  python3.9 -m venv venv
fi
if [ ! -d log ]; then
  mkdir log
fi
source venv/bin/activate
pip install -r requirements.txt
python main.py 2>&1 | tee log/$(date +"%m-%d-%Y").log
