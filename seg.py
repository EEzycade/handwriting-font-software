import numpy as np
import pandas as pd

import datetime as dt
from tqdm import tqdm
from uuid import uuid4
import re
import os

from matplotlib import pyplot as plt
from matplotlib.widgets import Button

import cv2
from ocr.src.ocr import page, words, characters
from ocr.src.ocr.normalization import word_normalization, letter_normalization
from ocr.src.ocr.tfhelpers import Model
from ocr.src.ocr.datahelpers import idx2char
from ocr.src.ocr.helpers import implt, resize, img_extend

import tensorflow as tf2

char_classifier = Model('ocr/models/char-clas/en/CharClassifier', 'add_2')

def segment_image(img_file):
    img = cv2.cvtColor(cv2.imread(img_file), cv2.COLOR_BGR2RGB)
    crop = page.detection(img)
    boxes = words.detection(crop)
    boxes = [box for line in words.sort_words(boxes) for box in line]

    result = []
    for x1, y1, x2, y2 in tqdm(boxes):
        word_img = img[y1:y2, x1:x2]
        word_img = word_normalization(
            word_img,
            60,
            border=False,
            tilt=True,
            hyst_norm=True
        )
        word_img = cv2.copyMakeBorder(
            word_img,
            0, 0, 30, 30,
            cv2.BORDER_CONSTANT,
            value=[0, 0, 0]
        )
        gaps = characters.segment(word_img, RNN=True)
        for i, j in zip(gaps[:-1], gaps[1:]):
            char_img = word_img[:, i:j]
            char_img, dim = letter_normalization(char_img, is_thresh=True, dim=True)
            if dim[0] > 4 and dim[1] > 4:
                prob ,= tf2.nn.softmax(char_classifier.run(char_img.flatten()[None,:])).numpy()
                result.append((prob, char_img, (x1, y1, x2, y2, i, j)))
    return result

PROMPTS = {
    'LND': """Our London business is good, but Vienna and Berlin are quiet. Mr. D. Lloyd has gone to Switzerland and I hope for good news. He will be there for a week at 1496 Zermott Street and then goes to Turin and Rome and will join Colonel Parry and arrive at Athens, Greece, November 27 or December 2. Letters there should be addressed King James Blvd. 3580. We expect Charles E. Fuller Tuesday. Dr. L. McQuaid and Robert Unger, Esq., left on the ’Y. X.’ Express tonight.""",
    'WOZ': """Within a short time she was walking briskly toward the Emerald City, her silver shoes tinkling merrily on the hard, yellow roadbed. The sun shone bright and the birds sang sweet and Dorothy did not feel nearly as bad as you might think a little girl would who had been suddenly whisked away from her own country and set down in the midst of a strange land.""",
    'PHR': """The early bird may get the worm, but the second mouse gets the cheese.""",
}

def viewer(probs, full_img, char_img, box, prompt="", prompt_index=0):
    x1, y1, x2, y2, i, j = box
    ax1 = plt.subplot(1, 2, 1)
    ax2 = plt.subplot(1, 2, 2)
    ax1.imshow(char_img, cmap='gray')

    a = int((i - 30) * (y2 - y1) / 60)
    b = int((j - 30) * (y2 - y1) / 60)

    img_with_box = full_img[y1-30:y2+30, x1+a-30:x1+b+30].copy()
    img_with_box = cv2.rectangle(img_with_box, (30, 30), (b-a+30, y2-y1+30), color=(255, 0, 0), thickness=2)
    ax2.imshow(img_with_box)

    ranking = (-probs).argsort()
    #for i in range(10):
    #    print(f"{idx2char(ranking[i])}: {100*probs[ranking[i]]:05.2f}%")

    buttons = []
    result = [None]
    for i, c in zip(range(5), ["magenta", "blue", "green", "goldenrod", "orange"]):
        ch = idx2char(ranking[i])
        button = Button(
            plt.axes([i/6, 0.0, 1/6, 0.2]),
            f"'{ch}'\n{100*probs[ranking[i]]:04.1f}%\n({'Upper' if ch.isupper() else 'Lower'}case)",
            color='dark'+c,
            hovercolor=c
        )
        def callback(_):
            plt.close()
            result[0] = idx2char(ranking[i])
        button.on_clicked(callback)
        buttons.append(button)
    button = Button(
        plt.axes([5/6, 0.0, 1/6, 0.2]),
        "Invalid",
        color='darkred',
        hovercolor='red',
    )
    def callback(_):
        plt.close()
        result[0] = ""
    button.on_clicked(callback)

    if prompt:
        old_char = prompt[prompt_index]
        if prompt_index - 20 > 0:
            prompt = "..." + prompt[prompt_index-20:]
            prompt_index = 23
            assert old_char == prompt[prompt_index]
        if prompt_index + 30 < len(prompt):
            prompt = prompt[:prompt_index+30] + "..."
            assert old_char == prompt[prompt_index]
        #plt.text(0.9, 0.0, prompt, size=36)
        plt.suptitle(prompt)
    #plt.suptitle(f"Character")
    fullscreen(plt)
    plt.show()
    return result[0]

def process(imgs, csv=None, working_dir="."):
    os.makedirs(working_dir, exist_ok=True)
    if csv is not None and os.path.exists(csv):
        df = pd.read_csv(csv)
    else:
        df = pd.DataFrame()
    for img_file in imgs:
        match = re.search(r"w(\d{4})_s(\d{2})_p(\w{3})_r(\d{2})\.png$", img_file)
        writer_id = int(match[1])
        session_id = int(match[2])
        prompt_id = match[3]
        round_id = int(match[4])
        prompt = PROMPTS[prompt_id]
        print(writer_id, session_id, prompt_id, round_id)
        print("Prompt:", prompt, sep="\n")
        full_img = cv2.cvtColor(cv2.imread(img_file), cv2.COLOR_BGR2RGB)
        characters = segment_image(img_file)
        total = 0
        for i, (probs, char_img, box) in enumerate(tqdm(characters)):
            char = viewer(probs, full_img, char_img, box, prompt, prompt_index=i * len(prompt) // len(characters))
            if char is None: raise Exception("Viewer Closed")
            if char:
                total += 1
                filename = str(uuid4()) + ".png"
                cv2.imwrite(f"{working_dir}/{filename}", char_img)
                df = df.append({
                    'date': str(dt.datetime.now().date()),
                    'char': char,
                    #'box': box,
                    'location': filename,
                    'original_img': img_file,
                    'writer_id': writer_id,
                    'session_id': session_id,
                    'prompt_id': prompt_id,
                    'round_id': round_id,
                }, ignore_index=True)
    print(f"Captured {total} new images.")
    return df

def fullscreen(plt):
    if plt.get_backend() == "TkAgg":
        mgr = plt.get_current_fig_manager()
        mgr.resize(*mgr.window.maxsize())

if __name__=="__main__":
    import sys
    args = sys.argv[1:]
    if not args:
        args = ["data/session1/w0002_s01_pLND_r01.png"]
    df = process(args, csv="processed-data/manifest.csv", working_dir="processed-data/")
    df.to_csv("processed-data/manifest.csv", index=False)
    print(df)

