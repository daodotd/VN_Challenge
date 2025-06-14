def color_font(text, color):
    """Wrap text with Kivy markup color tags for colored text rendering"""
    return f"[color={color}]{text}[/color]"