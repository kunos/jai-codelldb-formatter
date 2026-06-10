# jai-codelldb-formatter
Jai code formatter for lldb debugger.
Adds support for:
- Strings
- Arrays

To activate the formatter you have to add a cmd line parameter to lldb:
"command script import jai_formatters.py"

To use it from Zed add it to your launch profile. Ex:
```
// Project-local debug tasks
//
// For more documentation on how to configure debug tasks,
// see: https://zed.dev/docs/debugger
[
	{
		// The label for the debug configuration and used to identify the debug session inside the debug panel & new process modal
		"label": "Launch SpaceGame",
		// The debug adapter that Zed should use to debug the program
		"adapter": "CodeLLDB",
		// Request:
		//  - launch: Zed will launch the program if specified, or show a debug terminal with the right configuration
		//  - attach: Zed will attach to a running program to debug it, or when the process_id is not specified, will show a process picker (only supported for node currently)
		"request": "launch",
		// The program to debug. This field supports path resolution with ~ or . symbols.
		"program": "space_game/space_game.exe",
		"initCommands": [
			"command script import $ZED_WORKTREE_ROOT/jai_formatters.py",
		],
]
```
