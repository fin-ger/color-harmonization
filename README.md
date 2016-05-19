# Color Harmonization

This is an implementation of the color harmonization method described in [this paper](http://leyvand.com/harmonization/harmonization.pdf).

This software is written in python using gtk3 via the gi repository and pyopengl.

> IMPORTANT: Not finished yet!

## How to build

In order to build this project just type `make run` in the projects root directory.
The build will then install all requirements for your local user via pip.
After installation of the dependencies the program should start automatically.

This project was tested with python 3.4 and pip 8.1.1 on gentoo linux.

## Troubleshooting

#### `python3 is not installed on this system`

Make sure that python 3 is available over a `python3` executable in your `PATH`.

#### `pip3 is not installed on this system`

Make sure that the `pip3` executable is available in your `PATH`.

#### `command not found: mypy`

Make sure that your local binary installation folder for pip3 is in your `PATH`.
Usually this is `~/.local/bin/`. To fix this issue add this line to your `.bashrc`/`.zshrc`/...

```
PATH="${PATH}:~/.local/bin"
```
