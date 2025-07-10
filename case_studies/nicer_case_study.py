import threading
import time

import coolNewLanguage.src as hilt
from NICER.autobright import normalize_brightness
from NICER.neural_models import CAN
from NICER.nicer import NICER
from NICER import config
import numpy as np
from PIL import Image
import torch
from torchvision.transforms import transforms

tool = hilt.Tool('nicer')

tool.state['saturation'] = 0
tool.state['contrast'] = 0
tool.state['brightness'] = 0
tool.state['shadows'] = 0
tool.state['highlights'] = 0
tool.state['exposure'] = 0
tool.state['locallaplacian'] = 0
tool.state['nonlocaldehazing'] = 0
tool.state['gamma'] = 0.1

tool.state['enhanced_img_path'] = None
tool.state['original_img_path'] = None

nicer = NICER(checkpoint_can=config.can_checkpoint_path, checkpoint_nima=config.nima_checkpoint_path,
                           can_arch=config.can_filter_count)

# upload image
def image_upload():
    """
    Stage to upload an image for enhancement
    """
    uploaded_image = hilt.FileUploadComponent(
        '.jpg', label="Upload an image to enhance:"
    )

    if tool.user_input_received():
        content = hilt.UserContent(
                content_name="original_image",
                content_file_path=uploaded_image.value,
                content_type=hilt.ContentTypes.JPG
        )
        tool.save_content(content)
        tool.state['original_img_path'] = uploaded_image.value
        hilt.results.show_results(content, results_title="Image uploaded successfully!")
tool.add_stage('image_upload', image_upload)

device = 'cuda' if torch.cuda.is_available() else 'cpu'
can = CAN(no_of_filters=8) if config.can_filter_count == 8 else CAN(no_of_filters=7)
can.load_state_dict(torch.load(config.can_checkpoint_path, map_location=device)['state_dict'])
can.eval()
can.to(device)

def alternate_can(image, filterList):
    # alternate CAN for previewing the images, as NICER's CAN is used for gradient computation
    # filterList is passable since while optimizing, we cannot use nicer.filters, as these hold the gradients

    # gets called from periodiccall queue handler
    bright_norm_img = normalize_brightness(image, input_is_PIL=True)
    image = Image.fromarray(bright_norm_img)
    image_tensor = transforms.ToTensor()(image)

    filter_tensor = torch.zeros((8, image_tensor.shape[1], image_tensor.shape[2]),
                                dtype=torch.float32).to(device)  # tensorshape [c,w,h]
    for l in range(8):
        filter_tensor[l, :, :] = filterList[l]  # construct uniform filtermap
    mapped_img = torch.cat((image_tensor.cpu(), filter_tensor.cpu()), dim=0).unsqueeze(dim=0).to(device)

    enhanced_img = can(mapped_img)  # enhance img with CAN
    enhanced_img = enhanced_img.cpu()
    enhanced_img = enhanced_img.detach().permute(2, 3, 1, 0).squeeze().numpy()

    enhanced_clipped = np.clip(enhanced_img, 0.0, 1.0) * 255.0
    enhanced_clipped = enhanced_clipped.astype('uint8')

    # returns a np.array of type np.uint8
    return enhanced_clipped

def resize_image(img_path=None):
    pil_img = Image.open(img_path)

    img_width = pil_img.size[0]
    img_height = pil_img.size[1]

    # dirty hack to avoid errors when image is a square:
    if img_width == img_height:
        pil_img = pil_img.resize((img_width, img_height - 1))
        img_width = pil_img.size[0]
        img_height = pil_img.size[1]

    # resize images so that they can fit next to each other:
    # margins of the display canvas: 0.6*windowwidth, 0.9*windowheight
    if img_width > img_height:
        max_width = int(0.6 * 1920)  # images wider than high: place above each other
        max_height = int(0.5 * 0.9 * 1080)  # max height is half the display canvas
    elif img_height > img_width:
        max_width = int(0.5 * 0.6 * 1920)  # images higher than wide: place next to each other
        max_height = int(0.9 * 1920)
    max_size = int(0.9 * 1080) if img_height > img_width else int(0.6 * 1920)
    # just to that there are no errors if image is not resized:
    new_img_width = img_width
    new_img_height = img_height
    # img too large: either exceeds max size, or it is too broad / high to be displayed next to each other
    if max(pil_img.size) > max_size or pil_img.size[1] > max_height or pil_img.size[0] > max_width:
        longer_side = max(pil_img.size)
        factor = max_size / longer_side
        new_img_width = int(img_width * factor)
        new_img_height = int(img_height * factor)
        if img_width > img_height and new_img_height > max_height:  # landscape format
            while new_img_height > max_height:
                factor *= 0.99
                new_img_width = int(img_width * factor)
                new_img_height = int(img_height * factor)
        elif img_height > img_width and new_img_width > max_width:  # portrait format
            while new_img_width > max_width:
                factor *= 0.99
                new_img_width = int(img_width * factor)
                new_img_height = int(img_height * factor)
        # img is now resized in a way for 2 images to fit next to each other
        pil_img = pil_img.resize((new_img_width, new_img_height))

    return pil_img

# enhance image: show slider values, with input components to update
# on submit, enhance one epoch and show in result
# enhanced_img_pil = Image.fromarray(msg)
def enhance_image():
    """
    Stage to enhance the uploaded image
    """
    hilt.TextComponent(f"Current saturation value: {tool.state['saturation']}")
    saturation = hilt.UserInputComponent(
        float, label="Set saturation"
    )
    hilt.TextComponent(f"Current contrast value: {tool.state['contrast']}")
    contrast = hilt.UserInputComponent(
        float, label="Set contrast"
    )
    hilt.TextComponent(f"Current brightness value: {tool.state['brightness']}")
    brightness = hilt.UserInputComponent(
        float, label="Set brightness"
    )
    hilt.TextComponent(f"Current shadows value: {tool.state['shadows']}")
    shadows = hilt.UserInputComponent(
        float, label="Set shadows"
    )
    hilt.TextComponent(f"Current highlights value: {tool.state['highlights']}")
    highlights = hilt.UserInputComponent(
        float, label="Set highlights"
    )
    hilt.TextComponent(f"Current exposure value: {tool.state['exposure']}")
    exposure = hilt.UserInputComponent(
        float, label="Set exposure"
    )
    hilt.TextComponent(f"Current local laplacian value: {tool.state['locallaplacian']}")
    locallaplacian = hilt.UserInputComponent(
        float, label="Set local laplacian"
    )
    hilt.TextComponent(f"Current non-local dehazing value: {tool.state['nonlocaldehazing']}")
    nonlocaldehazing = hilt.UserInputComponent(
        float, label="Set non-local dehazing"
    )
    hilt.TextComponent(f"Current gamma value: {tool.state['gamma']}")
    gamma = hilt.UserInputComponent(
        float, label="Set gamma"
    )

    if tool.user_input_received():
        nicer.set_filters([saturation.value, contrast.value, brightness.value, shadows.value, highlights.value, exposure.value, locallaplacian.value, nonlocaldehazing.value])
        nicer.set_gamma(gamma.value)

        if tool.state['enhanced_img_path'] is None:
            img = tool.state['original_img_path']
        else:
            img = tool.state['enhanced_img_path']

        t = threading.Thread(target=nicer.enhance_image, args=(img, False, None, 1))
        t.start()
        while True:
            time.sleep(1)
            if nicer.queue.empty():
                continue
            msg = nicer.queue.get(0)
            if isinstance(msg, list):
                msg = [x * 100 for x in msg]
                tool.state['saturation'] = msg[0]
                tool.state['contrast'] = msg[1]
                tool.state['brightness'] = msg[2]
                tool.state['shadows'] = msg[3]
                tool.state['highlights'] = msg[4]
                tool.state['locallaplacian'] = msg[5]
                tool.state['nonlocaldehazing'] = msg[6]
                tool.state['exposure'] = msg[7]
                break

        enhanced = alternate_can(resize_image(img), msg)

        enhanced_img_pil = Image.fromarray(enhanced)
        enhanced_img_pil.save('enhanced_image.jpg')
        tool.state['enhanced_img_path'] = 'enhanced_image.jpg'
        content = hilt.UserContent(
            content_name="enhanced_image",
            content_file_path='enhanced_image.jpg',
            content_type=hilt.ContentTypes.JPG
        )
        tool.save_content(content)
        hilt.results.show_results(content, results_title="Enhanced image after one epoch:")

tool.add_stage('enhance_image', enhance_image)

if __name__ == "__main__":
    # Run the tool
    tool.run()