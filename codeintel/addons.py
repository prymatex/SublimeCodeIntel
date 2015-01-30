#!/usr/bin/env python

import socket
try:
    import queue
except ImportError:
    import Queue as queue

from prymatex.core.settings import ConfigurableItem
from prymatex.qt import  QtCore
from prymatex.gui.codeeditor import CodeEditorAddon
from prymatex.gui.codeeditor.modes import CodeEditorComplitionMode

from sublime import View

from codeintel.models import CodeIntelCompletionModel
from codeintel.SublimeCodeIntel import PythonCodeIntel

class CodeIntelAddon(CodeEditorAddon):
    # --------------- Default settings
    
    # Sets the mode in which CodeIntel runs:
    #    true - Enabled (the default).
    #    false - Disabled.
    codeintel = ConfigurableItem(default = True)
    
    # Disable Sublime Text autocomplete:
    sublime_auto_complete = ConfigurableItem(default = True)
    
    # Tooltips method: 
    #    "popup" - Uses Autocomplete popup for tooltips.
    #    "panel" - Uses the output panel for tooltips.
    #    "status" - Uses the status bar for tooltips (was the default).
    codeintel_tooltips = ConfigurableItem(default = "popup")
    
    # Insert functions snippets.
    codeintel_snippets = ConfigurableItem(default = True)
    
    # An array of language names which are enabled.
    codeintel_enabled_languages = ConfigurableItem(default = [
        "JavaScript", "SCSS", "Python", "HTML",
        "Ruby", "Python3", "XML", "Sass", "HTML5", "Perl", "CSS",
        "Twig", "Less", "Node.js", "TemplateToolkit", "PHP"
    ])

    # Maps syntax names to languages. This allows variations on a syntax
    # (for example "Python (Django)") to be used. The key is
    # the base filename of the .tmLanguage syntax files, and the value
    # is the syntax it maps to.
    codeintel_syntax_map = ConfigurableItem(default = {
        "Python Django": "Python"
    })

    # Sets the mode in which SublimeCodeIntel's live autocomplete runs:
    #    true - Autocomplete popups as you type (the default).
    #    false - Autocomplete popups only when you request it.
    codeintel_live = ConfigurableItem(default=True)

    # Tooltips method:
    # "popup" - Uses Autocomplete popup for tooltips.
    # "panel" - Uses the output panel for tooltips.
    # "status" - Uses the status bar for tooltips (was the default).
    codeintel_tooltips = ConfigurableItem(default="popup")

    # "buffer" - add word completions from current view
    # "all" - add word completions from all views from active window
    # "none" - do not add word completions
    codeintel_word_completions = ConfigurableItem(default="buffer")

    # Insert functions snippets.
    codeintel_snippets = ConfigurableItem(default=True)

    # Define filters per language to exclude paths from scanning.
    # ex: "JavaScript":["/build/", "/min/"]
    codeintel_scan_exclude_dir = ConfigurableItem(default=[])

    # ----- Code Scanning: Controls how the Code Intelligence system scans your source code files.
    # Maximum directory depth:
    codeintel_max_recursive_dir_depth = ConfigurableItem(default=10)

    # Include all files and directories from the project base directory:
    codeintel_scan_files_in_project = ConfigurableItem(default=True)

    # API Catalogs: SublimeCodeIntel uses API catalogs to provide autocomplete and calltips for 3rd-party libraies.
    # Add te libraries that you use in your code. Note: Adding all API catalogs for a particular language can lead to confusing results.
    
    #    Avaliable catalogs:
        # PyWin32 (Python3) (for Python3: Python Extensions for Windows)
        # PyWin32 (for Python: Python Extensions for Windows)
        # Rails (for Ruby: Rails version 1.1.6)
        # jQuery (for JavaScript: jQuery JavaScript library - version 1.9.1)
        # Prototype (for JavaScript: JavaScript framework for web development)
        # dojo (for JavaScript: Dojo Toolkit API - version 1.5.0)
        # Ext_30 (for JavaScript: Ext JavaScript framework - version 3.0)
        # HTML5 (for JavaScript: HTML5 (Canvas, Web Messaging, Microdata))
        # MochiKit (for JavaScript: A lightweight JavaScript library - v1.4.2)
        # Mozilla Toolkit (for JavaScript: Mozilla Toolkit API - version 1.8)
        # XBL (for JavaScript: XBL JavaScript support - version 1.0)
        # YUI (for JavaScript: Yahoo! User Interface Library - v2.8.1)
        # Drupal (for PHP: A full-featured PHP content management/discussion engine -- v5.1)
        # PECL (for PHP: A collection of PHP Extensions)
    codeintel_selected_catalogs = ConfigurableItem(default = [])
    
    # When editing within a defined scope, no live completion will trigger. ex: ["comment"]
    codeintel_exclude_scopes_from_complete_triggers = ConfigurableItem(default = ["comment"])

    # Defines a configuration for each language.
    codeintel_config = ConfigurableItem(default = {
        "Python3": {
            "python3": "/usr/local/bin/python3.3",
            "codeintel_scan_extra_dir": [
                "/Applications/Sublime Text.app/Contents/MacOS",
                "~/Library/Application Support/Sublime Text 3/Packages/SublimeCodeIntel/arch",
                "~/Library/Application Support/Sublime Text 3/Packages/SublimeCodeIntel/libs"
            ],
            "codeintel_scan_files_in_project": True,
            "codeintel_selected_catalogs": []
        },
        "JavaScript": {
            "codeintel_scan_extra_dir": [],
            "codeintel_scan_exclude_dir":["/build/", "/min/"],
            "codeintel_scan_files_in_project": False,
            "codeintel_max_recursive_dir_depth": 2,
            "codeintel_selected_catalogs": ["jQuery"]
        },
        "PHP": {
            "php": "/Applications/MAMP/bin/php/php5.5.3/bin/php",
            "codeintel_scan_extra_dir": [],
            "codeintel_scan_files_in_project": True,
            "codeintel_max_recursive_dir_depth": 15,
            "codeintel_scan_exclude_dir":["/Applications/MAMP/bin/php/php5.5.3/"]
        }
    })

    def initialize(self, **kwargs):
        super(CodeIntelAddon, self).initialize(**kwargs)
        self.setObjectName("CodeIntelAddon")
        
        # Build Sublime abstraction
        self.view = View(self.editor)
        self.view.add_event_listener(PythonCodeIntel())

        self.complition_model = CodeIntelCompletionModel(parent=self)
        complition = self.editor.findAddon(CodeEditorComplitionMode)
        complition.registerModel(self.complition_model)

    # ---------------- Shortcuts
    def contributeToShortcuts(self):
        return [{
            "sequence": ("CodeIntel", "GoToPythonDefinition", "Meta+Alt+Ctrl+Up"),
            "activated": lambda : self.goToPythonDefinition()
        }, {
            "sequence": ("CodeIntel", "BackToPythonDefinition", "Meta+Alt+Ctrl+Left"),
            "activated": lambda : self.backToPythonDefinition()
        }]
