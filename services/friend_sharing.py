import uuid
from utils.config import *
import qrcode
import os
from PIL import Image
from context import *

def generate_link_and_qr_code_for_friend_sharing(username, profile_name,extra_description):
    link = _generate_link_for_friend_sharing()
    profile = profile_repo.get_profile_by_name(profile_name)
    if profile is None:
        return None,None
    avatar_url = os.path.join('./static',profile.avatar)
    _generate_qr_code_url_for_friend_sharing(link,avatar_url)
    sharing_link_repo.remove_existing_link(username,profile_name)
    sharing_link_repo.add(username,profile_name,extra_description,link)
    return link

def _generate_link_for_friend_sharing():
    return f"sl-{uuid.uuid4()}"

def _generate_qr_code_url_for_friend_sharing(link, avatar_url='./static/images/default.png'):
    
    logo = Image.open(avatar_url)
    # taking base width
    basewidth = 120
 
    # adjust image size
    wpercent = (basewidth/float(logo.size[0]))
    hsize = int((float(logo.size[1])*float(wpercent)))
    logo = logo.resize((basewidth, hsize), Image.LANCZOS)
    path = os.path.join(qr_code_url_base, f'{link}.png')

    QRcode = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H
    )
    url = f'https://linkyun.co/friend/chat/{link}'
 
    # adding URL or text to QRcode
    QRcode.add_data(url)
    # generating QR code
    QRcode.make()
    
    # taking color name from user
    QRcolor = 'Purple'
    
    # adding color to QR code
    QRimg = QRcode.make_image(
        fill_color=QRcolor, back_color="white").convert('RGB')
    
    # set size of QR code
    pos = ((QRimg.size[0] - logo.size[0]) // 2,
        (QRimg.size[1] - logo.size[1]) // 2)
    QRimg.paste(logo, pos)
    
    # save the QR code generated
    QRimg.save(path)

    return path