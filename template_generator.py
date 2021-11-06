from PIL import Image, ImageDraw
import math

# At 96 PPI
INCH = 96
LETTER_SIZE = (816, 1056)
A4_SIZE = (793, 1122)


# count = amount of chars for template
# box_w, line_w = widths of the boxes and outlines
# img_sz = size of the final image
# margin = margin width on all sides of the final image
def create_template(count, box_w, line_w, img_sz=LETTER_SIZE, margin=INCH):
    max_dimms = (math.floor((img_sz[0] - (2 * margin)) / box_w), math.floor((img_sz[1] - (2 * margin)) / box_w))
    count = count if max_dimms[0] * max_dimms[1] > count else max_dimms[0] * max_dimms[1]
    template = Image.new("RGBA", img_sz, (0, 0, 0, 0))
    off = math.floor(line_w / 2)  # offset
    draw = ImageDraw.Draw(template)

    drawn = 0
    for y in range(math.ceil(count / max_dimms[0])):
        for x in range(max_dimms[0] if count - drawn > max_dimms[0] else count - drawn):
            draw.rectangle([(margin + (x * box_w) - off, margin + (y * box_w) - off),
                            (margin + ((x + 1) * box_w), margin + ((y + 1) * box_w))],
                           None, "black", line_w)
            drawn = drawn + 1
    template.show()
