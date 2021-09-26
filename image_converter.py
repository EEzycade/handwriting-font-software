import potrace
import PIL.Image
import sys

def __main__():
    if len(sys.argv) != 2:
        print(f"Pass the path to the image as an argument:\npython image_converter.py test.jpeg")
        return

    img_input_path = sys.argv[1]
    img_output_path = ".".join(img_input_path.split(".")[:-1]) + ".svg"
    
    img = PIL.Image.open(img_input_path)
    print(f"Loaded '{img_input_path}'")
    svg = convert_to_svg(img)

    with open(img_output_path, "w") as file:
        file.write(svg)
    print(f"Saved to '{img_output_path}'")

def convert_to_svg(img: PIL.Image, turdsize=50, opttolerance=0.2, blacklevel=0.5, **kwargs) -> str:
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

    returns:
        A string representation of the image as an SVG
    
    For more information on the different parameters, see http://potrace.sourceforge.net/potrace.pdf
    """
    bitmap = potrace.Bitmap(img, blacklevel=blacklevel)
    path = bitmap.trace(turdsize=turdsize, opttolerance=opttolerance, **kwargs)

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

    return f"""
    <svg version="1.1"
         xmlns="http://www.w3.org/2000/svg"
         xmlns:xlink="http://www.w3.org/1999/xlink"
         width="{img.width}"
         height="{img.height}"
         viewBox="0 0 {img.width} {img.height}">

        <path stroke="none"
              fill="black"
              fill-rule="evenodd"
              d="{data}"/>

    </svg>
    """


if __name__ == "__main__":
    __main__()

