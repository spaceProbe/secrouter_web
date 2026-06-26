# SecRouter documentation — Sphinx config.
project = "SecRouter"
author = "SecRouter"
copyright = "2026, SecRouter"
release = "1.0"

extensions = ["myst_parser"]
myst_enable_extensions = ["colon_fence", "deflist"]
myst_heading_anchors = 3

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
source_suffix = {".md": "markdown"}

html_theme = "furo"
html_title = "SecRouter Docs"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_show_sphinx = False
html_copy_source = False
html_show_sourcelink = False
pygments_style = "friendly"
pygments_dark_style = "monokai"

html_theme_options = {
    "light_logo": "logo-mark.svg",
    "dark_logo": "logo-mark-dark.svg",
    "sidebar_hide_name": False,
    "light_css_variables": {
        "color-brand-primary": "#54672f",
        "color-brand-content": "#54672f",
    },
    "dark_css_variables": {
        "color-brand-primary": "#aebb78",
        "color-brand-content": "#aebb78",
    },
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://git.secrouter.io/spaceProbe/secrouter",
            "html": '<svg stroke="currentColor" fill="currentColor" viewBox="0 0 16 16" width="20" height="20"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8z"/></svg>',
            "class": "",
        },
    ],
}
