"""Python mirror of motion/src/theme.ts colours (used by Manim scenes + UI hints)."""

THEMES: dict[str, dict[str, str]] = {
    "cosmos": {"bg": "#08090D", "text": "#ECE8DF", "muted": "#8D8A84", "accent": "#E8A33D", "accent2": "#8FB3FF", "good": "#7FD6A4", "bad": "#F07167"},
    "midnight": {"bg": "#06070C", "text": "#EEF0F6", "muted": "#8A8FA3", "accent": "#7C9CFF", "accent2": "#F5B971", "good": "#6EE7B7", "bad": "#FB7185"},
    "chalk": {"bg": "#18201D", "text": "#F2EFE6", "muted": "#9AA59F", "accent": "#F2C14E", "accent2": "#7FD1B9", "good": "#9BE38A", "bad": "#F28B82"},
    "paper": {"bg": "#F1ECE2", "text": "#1B1A17", "muted": "#6E685E", "accent": "#D2491E", "accent2": "#2B59C3", "good": "#2E7D4F", "bad": "#B3261E"},
    "neon": {"bg": "#040406", "text": "#F5F5F7", "muted": "#85859A", "accent": "#00E5C7", "accent2": "#FF4D8D", "good": "#00E5C7", "bad": "#FF4D8D"},
    "solar": {"bg": "#110B07", "text": "#FFF4E6", "muted": "#A8978A", "accent": "#FF8A3D", "accent2": "#FFD166", "good": "#B8E986", "bad": "#FF6B6B"},
}

THEME_NOTES = {
    "cosmos": "Pragyan house style — lunar dark with saffron accent. Versatile default.",
    "midnight": "Deep navy, periwinkle accent. Tech, product, CS.",
    "chalk": "Blackboard green with chalk yellow. Maths and physics derivations.",
    "paper": "Warm editorial light mode. Humanities, documents, summaries.",
    "neon": "Black with cyan/magenta. Code, algorithms, futuristic topics.",
    "solar": "Warm ember dark. History, stories, biology.",
}
