import json
from xml.dom.minidom import parse

from glyph import Glyph

def parseFont(path_to_font: str) -> list[Glyph]:
    """
    Parsuje font w formacie svg na listę obiektów Glyph

    Args:
        path_to_font (str): ścieżka do pliku svg
    
    Returns:
        list[Glyph]: lista obiektów Glyph
    """
    glyphs = []
    document = parse(path_to_font)

    for g in document.getElementsByTagName("glyph"):
        if g.hasAttribute("d") and g.getAttribute("unicode"):
            glyphUnicode = g.getAttribute("unicode")
            glyphSvgPath = g.getAttribute("d")
            glyph_horiz_adv_x = g.getAttribute("horiz-adv-x")
            glyphs.append(Glyph(glyphUnicode, glyphSvgPath, float(glyph_horiz_adv_x)))
            
    return glyphs

def parseFontsToJson(fonts: list[tuple[str, list[Glyph]]])  -> str:
    """
    Parsuje listę fontów na JSON

    Args:
        fonts (list[tuple[str, list[Glyph]]]): lista fontów do parsowania
    Returns:
        str: JSON
    """
    jsonOutput = {}
    jsonOutput["fonts"] = []
    for font in fonts:
        glyphs = [] 
        for glyph in font[1]:
            g = {}
            g["unicode"] = glyph.unicode
            g["svg"] = glyph.svg_code()
            glyphs.append(g)
        jsonOutput["fonts"].append({"name": font[0], "glyphs": glyphs})
    return json.dumps(jsonOutput)

def parseJsonFontMat(jsonFont) -> list[tuple[Glyph, list]]:
    """
    Parsuje JSON na listę obiektów Glyph i listę okręgów

    Args:
        jsonFont: JSON z fontem

    Returns:
        List[tuple[Glyph, list]]: lista obiektów Glyph z okręgami
    """
    glyphs = []
    for glyph in jsonFont['glyphs']:
        glyphs.append((Glyph(glyph['unicode'], glyph['mat']['svg']), glyph['mat']['circles']))

    return glyphs