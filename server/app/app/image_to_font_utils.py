# For now, this will consist of many different methods so we can easily change/exchange them
# Before submission, we might want to compress them into only the methods we need

from flask import flash

template_symbols_dict = {
  "english_lower_case_letters": ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]
}

def process_image(image):
    return image

def cut_image(processed_image, template_type):
    if template_type == "english_lower_case_letters":
        cut_images = []
        for symbol in template_symbols_dict["english_lower_case_letters"]:
            cut_images.append(processed_image)
        return cut_images

    else:
        flash('Template type not recognized', 'danger')
        return None