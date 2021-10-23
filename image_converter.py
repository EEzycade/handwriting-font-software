import potrace
import PIL.Image
import PIL.ImageFilter
import sys
import numpy as np

def __main__():
    if len(sys.argv) != 2:
        print(f"Pass the path to the image as an argument:\npython image_converter.py test.jpeg")
        return

    img_input_path = sys.argv[1]
    img_output_path = ".".join(img_input_path.split(".")[:-1]) + ".svg"
    
    img = PIL.Image.open(img_input_path)
    print(f"Loaded '{img_input_path}'")
    svg = convert_to_svg(img, preprocess_steps=[lambda path: remove_zigzags(path, angle=75)])

    with open(img_output_path, "w") as file:
        file.write(svg)
    print(f"Saved to '{img_output_path}'")

def convert_to_svg(img: PIL.Image, preprocess_steps=[], turdsize=50, opttolerance=0.2, blacklevel=0.5, blur_radius=3, **kwargs) -> str:
    """Convert a PIL Image to an SVG string
    
    img: PIL.Image
        The image to convert.
    turdsize: int
        Discard any regions with an area smaller than `turdsize` pixels.
    opttolerance: float
        Parameter controling when optimizations are acceptable.
    alphamax: float
        Parameter to control when to make a corner round vs sharp.
    blacklevel: float
        Cuttoff point to determine when a pixel should be black.
    turnpolicy: int
        Policy for deciding which way to turn when the image is ambiguous. 
        Choices are
            - POTRACE_TURNPOLICY_BLACK = 0
            - POTRACE_TURNPOLICY_WHITE = 1
            - POTRACE_TURNPOLICY_LEFT = 2
            - POTRACE_TURNPOLICY_RIGHT = 3
            - POTRACE_TURNPOLICY_MINORITY = 4
            - POTRACE_TURNPOLICY_MAJORITY = 5
            - POTRACE_TURNPOLICY_RANDOM = 6
    blur_radius: int
        Before converting to SVG, the image is blurred to remove any sharp edges.
        This parameter controls how strongly to blur. Larger values tend to make
        the characters smaller. Radius is measured in pixels and may need to
        change for different image sizes.

    returns:
        A string representation of the image as an SVG
    
    For more information on the different parameters, see http://potrace.sourceforge.net/potrace.pdf
    """
    img = img.filter(PIL.ImageFilter.GaussianBlur(radius=blur_radius))

    bitmap = potrace.Bitmap(img, blacklevel=blacklevel)
    path = bitmap.trace(turdsize=turdsize, opttolerance=opttolerance, **kwargs)

    for preprocess_step in preprocess_steps:
        preprocess_step(path)

    data = []
    for curve in path:
        data.append(f"M{curve.start_point.x},{curve.start_point.y}")
        for segment in curve.segments:
            if segment.is_corner:
                # Corner
                data.append(f"L{segment.c.x},{segment.c.y}")
                data.append(f"L{segment.end_point.x},{segment.end_point.y}")
            else:
                # Bezier curve
                data.append(f"C{segment.c1.x},{segment.c1.y}")
                data.append(f" {segment.c2.x},{segment.c2.y}")
                data.append(f" {segment.end_point.x},{segment.end_point.y}")
        data.append("z")
    data = "".join(data)

    width, height = kwargs.get("width", img.width), kwargs.get("height", img.height)
    return f"""
    <svg version="1.1"
         xmlns="http://www.w3.org/2000/svg"
         xmlns:xlink="http://www.w3.org/1999/xlink"
         width="{width}"
         height="{height}"
         viewBox="0 0 {width} {height}">

        <path stroke="none"
              fill="black"
              fill-rule="evenodd"
              d="{data}"/>

    </svg>
    """

def remove_zigzags(path: potrace.Path, angle=90):
    """Remove points if they form two angles larger than `angle` degrees
    
    path: Curve
        The path to edit.
    angle: int
        The minimum angle measured in degrees.
    """
    min_cos = np.cos(np.pi * angle / 180)
    for curve in path:
        i = 0
        while i+3 < len(curve):
            # Get the 4 points
            p1 = curve[i].end_point
            p2 = curve[i+1].end_point
            p3 = curve[i+2].end_point
            p4 = curve[i+3].end_point

            # Create 3 vectors from them
            v1 = np.array([p2.x - p1.x, p2.y - p1.y])
            v2 = np.array([p3.x - p2.x, p3.y - p2.y])
            v3 = np.array([p4.x - p3.x, p4.y - p3.y])

            # Find the angle between each of them
            cos12 = v1.dot(v2) / np.sqrt(v1.dot(v1) * v2.dot(v2))
            cos23 = v2.dot(v3) / np.sqrt(v2.dot(v2) * v3.dot(v3))
            cos13 = v1.dot(v3) / np.sqrt(v1.dot(v1) * v3.dot(v3))

            if cos12 < min_cos and cos23 < min_cos and cos13 >= 0:
                # If we have two angles in a row that are too large, then we remove them
                curve.pop(i+1)
                curve.pop(i+1)
                curve[i]._segment.c[2] = p3
            i += 1

def rescale(path: potrace.Path, height=1000, width=None):
    """Rescale a path

    path: Path
        The path to rescale (inplace)
    height: int
        Rescale y coordinates to go from 0 to height
    width: int or None
        Rescale x coordinates to go from 0 to width, or if width is None
        keep the image proportional
    """
    maxx, minx = -np.inf, np.inf
    maxy, miny = -np.inf, np.inf
    for curve in path:
        for segment in curve.segments:
            for pt in (segment.c, segment.end_point) if segment.is_corner else (segment.c1, segment.c2, segment.end_point):
                maxx = max(maxx, pt.x)
                maxy = max(maxy, pt.y)
                minx = min(minx, pt.x)
                miny = min(miny, pt.y)
    delta_x = maxx - minx
    delta_y = maxy - miny

    if width is None:
        width = height * delta_x / delta_y

    for curve in path:
        for segment in curve.segments:
            for pt in (segment.c, segment.end_point) if segment.is_corner else (segment.c1, segment.c2, segment.end_point):
                pt.x = (pt.x - minx) * width / delta_x
                pt.y = (pt.y - miny) * height / delta_y

def stretch_char(path: potrace.Path, lower: int, upper: int, original_height=1000):
    """Stretch a character so that the canvas goes from y=lower to y=upper

    path: potrace.Path
        The path to stretch (inplace).
    lower: int
        The new minimum y coordinate.
    upper: int
        The new maximum y coordinate.
    original_height: int (default 1000)
        The original height (ie, all y coordinates are assumed to be between 0
        and `original_height`).
    """
    for curve in path:
        for segment in curve.segments:
            for pt in (segment.c, segment.end_point) if segment.is_corner else (segment.c1, segment.c2, segment.end_point):
                pt.x *= (upper - lower) / original_height
                pt.y *= (upper - lower) / original_height
                pt.y += lower

def get_char_sizing(char: str, char_settings: dict):
    """Extract lower and upper y coordinate of char according to char_settings"""
    return char_settings["sizing"][char_settings["character-setting"][char]]

if __name__ == "__main__":
    __main__()

