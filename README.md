# NaggyPy

**A Python linter that MAKES SURE you write good code, in a not-so-passive-aggressive way.**

NaggyPy is a comedic linter for Python that provides sarcastic, snarky, and mildly irritating comments on your code style. Rather than politely suggesting improvements, NaggyPy will fuss at you for daring to have docstring typos, single-letter variables, or multiple imports on one line.

## Features

- **Syntax Error Detection**  
  If your code doesn’t parse, NaggyPy will let you know—rudely.

- **Naming Conventions**  
  - Complains if functions aren’t snake_case.
  - Complains if classes aren’t CapWords.
  - Shames you for single-letter variables.

- **Docstrings**  
  - Warns if you have no docstring.
  - Warns if the docstring is too short.
  - Warns if it doesn’t start with a capital letter or end with punctuation.  
  Essentially, it will warn you about everything.

- **Comment Ridicule**  
  - If you write comments, NaggyPy implies you don’t trust your own genius.
  - If your comment line is longer than 72 characters, expect a lecture about readability.

- **Import & Line-Length Checks**  
  - Multiple imports on a single line? How dare you.
  - Lines longer than 79 characters? The linter calls you out.

- **Nested Loops**  
  - Finds loops within loops, wonders why you’ve chosen to confuse future maintainers.

…and more comedic jabs at your coding style.

## Installation

1. **Download and Install**  
   - Install from the VS Code Marketplace, or  
   - Download the `.vsix` file and install via:
     ```bash
     code --install-extension naggypy-0.0.1.vsix
     ```
   - Alternatively, open VS Code, press `F1` → “Extensions: Install from VSIX…” and select the `.vsix`.

2. **Activate**  
   - The extension activates on Python files.  
   - You can also manually run the “Run NaggyPy Linter” command from the Command Palette.

## Usage

1. **On Save**  
   - By default, NaggyPy may lint automatically when you save a Python file (depending on your extension settings).

2. **Manual Command**  
   - Press `F1` (or `Ctrl+Shift+P`) and search for **"Run NaggyPy Linter"**.  
   - This command spawns our Python-based linter behind the scenes, collects comedic “issues,” and displays them in the Problems panel.

## Requirements

- A working **Python** environment accessible via the command `python`.  

## Known Issues

- Large files or complex AST structures might slow down the linter slightly.  
- Our comedic messages can be mildly infuriating if you’re used to constructive feedback.

## Release Notes

### 0.0.1
- Initial release of NaggyPy. 
- Shames your code thoroughly!

## Contributing

Feel free to submit pull requests if you want to add more comedic rules or support other editors. Also open issues if you find bugs or have ideas for spicier snark.

## License

MIT License