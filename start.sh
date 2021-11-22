if [ ! -d venv ]; then
  python3.9 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt
python main.py
