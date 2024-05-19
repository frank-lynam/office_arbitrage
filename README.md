# Super Simple Kivy Buildozer Example

This just works. Easy peasy. [Kivy](https://kivy.org/) and [Buildozer](https://github.com/kivy/buildozer) are pretty neat!

# To run

You might need to do the install steps in [the buildozer docs](https://buildozer.readthedocs.io/en/latest/) to make sure you've got all the dependencies, but they "just work" in Ubuntu under WSL pretty nicely. Then:

```bash
git clone {this repo}
cd super_simple_kivy_buildozer_example
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
export PATH=$PATH:~/.local/bin/
buildozer android debug
```

And the the apk will be in `bin/`. Copy it to your phone however you like and install =]

# Make your app do this

Just do these things:

- Run `buildozer init` in your project and edit `buildozer.spec` as desired
- Have a main.py that starts a kivy app
- Run `buildozer android debug` to build an apk

# Where'd you get that great png?

Oh man, check out [OMG-IMG](https://icons8.com/license). They got tons of great stuff!
