import argparse
from fontTools import ttLib
from fontTools import subset
from fontTools import merge
from subprocess import run
from uuid import uuid4

def fill_font(main_file, base_file, output_file=None):
    tmp1 = "tmp-" + str(uuid4())
    tmp2 = "tmp-" + str(uuid4())
    tmp3 = "tmp-" + str(uuid4())
    if base_file.endswith("otf"):
        run(["python", "otf2ttf.py", "-o=" + tmp1, base_file])
    elif base_file.endswith("ttf"):
        run(["cp", base_file, tmp1])
    else: assert False
    if main_file.endswith("otf"):
        run(["python", "otf2ttf.py", "-o=" + tmp2, main_file])
    elif main_file.endswith("ttf"):
        run(["cp", main_file, tmp2])
    else: assert False

    if output_file is None:
        output_file = main_file

    base_font = ttLib.TTFont(tmp1)
    main_font = ttLib.TTFont(tmp2)
    missing_chars = set(base_font.getGlyphOrder()) - set(main_font.getGlyphOrder())

    subset.main([tmp1, "--glyphs=" + ",".join(missing_chars), "--output-file=" + tmp3])
    #run(["python", "otf2ttf.py", "-o=" + tmp2, tmp2])
    run(["python", "scale-font.py", tmp2, str(base_font["head"].unitsPerEm), "--output=" + tmp2])
    merge.main([tmp3, tmp2, "--output-file=" + output_file])
    run(["rm", tmp1, tmp2, tmp3])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--main-font", type=str, help="Main font")
    parser.add_argument("--base-font", type=str, help="Font to use for missing characters.")
    parser.add_argument("--output-file", type=str, default=None, help="File to output as")
    args = parser.parse_args()
    fill_font(args.main_font, args.base_font, args.output_file)

