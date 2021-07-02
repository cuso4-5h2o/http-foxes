from jinja2 import Environment, FileSystemLoader
from PIL import Image, ImageFont, ImageDraw
import os
import yaml
import shutil
import configparser


def copy_dir(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


def load_config():
    with open(os.path.join(os.getcwd(), "config.yaml"), "r") as config_file:
        return yaml.safe_load(config_file)


def generate_picture(env, text, description, picture, author, source, link_prefix, font_path, site_name, dist_prefix):
    img = Image.open(picture)
    if img.size[0] > img.size[1]:
        new_height = int(img.size[1]/(img.size[0]/800))
        img = img.resize((800, new_height))
    if img.size[0] > 800:
        new_width = int(img.size[0]/(img.size[1]/800))
        img = img.resize((new_width, 800))
    img.save(dist_prefix+".jpg")
    img_with_1_border = Image.new(
        'RGB', (img.size[0]+6, img.size[1]+6), (0, 0, 0))
    img_with_1_border.paste(img, (3, 3))
    img_with_2_border = Image.new(
        'RGB', (img_with_1_border.size[0]+6, img_with_1_border.size[1]+6), (255, 255, 255))
    img_with_2_border.paste(img_with_1_border, (3, 3))
    img_with_text = Image.new(
        'RGB', (img_with_2_border.size[0] + 140, img_with_2_border.size[1] + 220), (0, 0, 0))
    img_with_text.paste(img_with_2_border, (70, 50))
    title = text.split(" ")[0]
    subtitle = " ".join(text.split(" ")[1:])
    font_title = ImageFont.truetype(font_path, 64)
    font_subtitle = ImageFont.truetype(font_path, 48)
    title_size = font_title.getsize(title)
    subtitle_size = font_subtitle.getsize(subtitle)
    draw = ImageDraw.Draw(img_with_text)
    draw_position = int(
        (img_with_text.size[0]-title_size[0])/2), int(img_with_text.size[1]-(title_size[1]/2)-140)
    draw.text(draw_position, title, (255, 255, 255), font=font_title)
    draw_position = int((img_with_text.size[0]-subtitle_size[0])/2), int(
        img_with_text.size[1]-(subtitle_size[1]/2)-80)
    draw.text(draw_position, subtitle, (255, 255, 255), font=font_subtitle)
    img_with_text.save(dist_prefix+".png")
    ini = configparser.ConfigParser()
    ini.add_section("picture")
    ini.set("picture", "code", title)
    ini.set("picture", "name", subtitle)
    ini.set("picture", "description", description)
    ini.set("picture", "author", author)
    ini.set("picture", "source", source)
    ini.set("picture", "picture", "{}/{}.png".format(link_prefix, title))
    ini.set("picture", "picture_without_text",
            "{}/{}.jpg".format(link_prefix, title))
    with open(dist_prefix+".ini", "w") as config_file:
        ini.write(config_file)
    template = env.get_template("view.html")
    os.makedirs(dist_prefix)
    with open(os.path.join(dist_prefix, "index.html"), "w", encoding="utf-8") as html_file:
        html_file.write(template.render(page_title="{} - {}".format(text, site_name),
                        code=title, name=subtitle, description=description, source=source, author=author, site_name=site_name, link_prefix=link_prefix))


def generate_index(env, site_name, pictures_raw, dist):
    template = env.get_template("index.html")
    pictures = []
    for picture_raw in pictures_raw:
        pictures.append({"code": picture_raw["s"].split(" ")[0], "name": " ".join(picture_raw["s"].split(" ")[1:])})
    with open(dist, "w", encoding="utf-8") as html_file:
        html_file.write(template.render(page_title=site_name, pictures=pictures))


def copy_static_files():
    copy_dir("static", "publish")


env = Environment(loader=FileSystemLoader("./templates"))
config = load_config()
publish_dir = os.path.join(os.getcwd(), config["publish_dir"])
picture_dir = os.path.join(os.getcwd(), config["picture_dir"])
font_file = os.path.join(os.getcwd(), config["font_file"])
if os.path.exists(publish_dir):
    print("Clearing publish directory ...")
    shutil.rmtree(publish_dir)
os.makedirs(publish_dir)
print("Copying static files ...")
copy_static_files()
print("Generating index page ...")
generate_index(env, config["site_name"], config["pictures"], 
               os.path.join(publish_dir, "index.html"))
for pic in config["pictures"]:
    print("Generating picture {} ...".format(pic["s"]))
    status_code = pic["s"].split(" ")[0]
    generate_picture(env, pic["s"], pic["d"], os.path.join(
        picture_dir, status_code+".jpg"), pic["a"], pic["u"], config["link_prefix"], font_file, config["site_name"], os.path.join(publish_dir, status_code))
