import os
import sys
import fontTools.svgLib.path as svg_path
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen
import image_converter
import PIL.Image


def __main__():
    if len(sys.argv) < 2:
        print("Please pass the file directory path containing the svgs you want to create a font with as an argument!")
        return

    path = sys.argv[1]
    for filename in os.listdir(path):
        if filename.split(".")[-1] == "jpeg":
            input_path = path + filename
            output_path = path + filename.split(".")[0] + ".svg"
            img = PIL.Image.open(input_path)
            print(f"Loaded '{input_path}'")
            svg = image_converter.convert_to_svg(img)

            with open(output_path, "w") as file:
                file.write(svg)
            print(f"Saved to '{output_path}'")

    generate_from_svgs(path)


def generate_from_svgs(path):
    default_char = default_charstr()
    char_strings = {
        ".notdef": default_char,
        "space": default_char,
        ".null": default_char,
    }

    glyph_order = [".notdef", ".null", "space"]
    char_map = {32: "space"}
    advance_widths = {".notdef": 600, "space": 500, ".null": 250}
    advance_heights = {".notdef": 600, "space": 500, ".null": 250}

    for filename in os.listdir(path):
        if filename.split(".")[-1] == "svg":
            char_string = draw_charstr(path + filename)
            char = filename.split('.')[0]
            char_strings[char] = char_string
            glyph_order.append(char)
            char_map[ord(char)] = char
            advance_widths[char] = 250
            advance_heights[char] = 250

    fb = FontBuilder(1024, isTTF=False)
    fb.setupGlyphOrder(glyph_order)
    fb.setupCharacterMap(char_map)

    family_name = "GeneratedFont"
    style_name = "Test"
    version = "0.1"

    name_strings = dict(
        uniqueFontIdentifier="fontBuilder: " + family_name + "." + style_name,
        fullName=family_name + "-" + style_name,
        psName=family_name + "-" + style_name,
        version="Version " + version,
    )

    fb.setupCFF(name_strings["psName"], {"FullName": name_strings["psName"]}, char_strings, {})
    lsb = {gn: cs.calcBounds(None)[0] for gn, cs in char_strings.items()}
    metrics = {}
    for gn, advanceWidth in advance_widths.items():
        metrics[gn] = (advanceWidth, lsb[gn])
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=824, descent=200)
    fb.setupNameTable(name_strings)
    fb.setupOS2(sTypoAscender=824, usWinAscent=824, usWinDescent=200)
    fb.setupPost()
    fb.save("test.otf")


# create char string to use in otf file from svg
def draw_charstr(filename):
    pen = T2CharStringPen(200, None)
    svg = svg_path.SVGPath(filename)
    svg.draw(pen)

    return pen.getCharString()


# default char string; currently a placeholder
def default_charstr():
    pen = T2CharStringPen(600, None)
    pen.moveTo((100, 100))
    pen.lineTo((100, 1000))
    pen.curveTo((200, 900), (400, 900), (500, 1000))
    pen.lineTo((500, 100))
    pen.closePath()
    return pen.getCharString()


if __name__ == "__main__":
    __main__()
