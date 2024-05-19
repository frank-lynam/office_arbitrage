# Office Arbitrage

A silly arbitrage phone game using AI-generated images and flavor text.

# Build

```bash
git clone {this repo}
cd office_arbitrage
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
export PATH=$PATH:~/.local/bin/
buildozer android debug
```

And the the apk will be in `bin/`. Copy it to your phone however you like and install =]

