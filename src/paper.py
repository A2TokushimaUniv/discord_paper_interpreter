import os
import urllib.request
from logzero import logger
import fitz
import mimetypes
import uuid
import time


def _is_pdf(tmp_file_name, http_response_obj):
    mimetype = str(mimetypes.guess_type(tmp_file_name)[0])
    logger.info(f"MimeType of {tmp_file_name} is {mimetype}.")
    content_type = http_response_obj.getheader("Content-Type")
    logger.info(f"Content-Type of {tmp_file_name} is {content_type}.")
    return "application/pdf" in content_type or "application/pdf" in mimetype


def download_pdf(url, is_upload, save_path, max_retries=5, retry_delay=3):
    headers = (
        {"User-Agent": "Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)"}
        if is_upload
        else {}
    )
    req = urllib.request.Request(url, None, headers)
    logger.info(f"Downloading pdf from {url}...")

    retries = 0
    while retries < max_retries:
        try:
            with urllib.request.urlopen(req) as web_file:
                with open(save_path, "wb") as local_file:
                    local_file.write(web_file.read())

                if not _is_pdf(save_path, web_file):
                    logger.warn(f"Content-type of {url} is not application/pdf.")
                    os.remove(save_path)
                    return False
        except Exception as e:
            retries += 1
            logger.warning(
                f"Failed to download pdf from {url}. Retrying ({retries}/{max_retries})..."
            )
            logger.warning(f"Exception: {str(e)}")
            time.sleep(retry_delay)
            continue

        return True

    logger.error(f"Failed to download pdf from {url} after {max_retries} retries.")
    return False


# See: https://github.com/pymupdf/PyMuPDF-Utilities/blob/master/examples/extract-images/extract-from-pages.py
def _recoverpix(doc, item):
    xref = item[0]  # xref of PDF image
    smask = item[1]  # xref of its /SMask

    # special case: /SMask or /Mask exists
    if smask > 0:
        pix0 = fitz.Pixmap(doc.extract_image(xref)["image"])
        if pix0.alpha:  # catch irregular situation
            pix0 = fitz.Pixmap(pix0, 0)  # remove alpha channel
        mask = fitz.Pixmap(doc.extract_image(smask)["image"])

        try:
            pix = fitz.Pixmap(pix0, mask)
        except Exception as e:  # fallback to original base image in case of problems
            logger.warning(f"Exception: {e}")
            pix = fitz.Pixmap(doc.extract_image(xref)["image"])

        if pix0.n > 3:
            ext = "pam"
        else:
            ext = "png"

        return {  # create dictionary expected by caller
            "ext": ext,
            "colorspace": pix.colorspace.n,
            "image": pix.tobytes(ext),
        }

    # special case: /ColorSpace definition exists
    # to be sure, we convert these cases to RGB PNG images
    if "/ColorSpace" in doc.xref_object(xref, compressed=True):
        pix = fitz.Pixmap(doc, xref)
        pix = fitz.Pixmap(fitz.csRGB, pix)
        return {  # create dictionary expected by caller
            "ext": "png",
            "colorspace": 3,
            "image": pix.tobytes("png"),
        }
    return doc.extract_image(xref)


def _extract_images(
    tmp_folder_name,
    doc,
    min_width=600,
    min_height=600,
    abssize=2048,
    max_ratio=8,
    max_num=5,
):
    page_count = doc.page_count

    xreflist = []
    imglist = []
    images = []
    logger.info("Extracting images...")
    is_max_num = False
    for pno in range(page_count):
        if is_max_num:
            break
        il = doc.get_page_images(pno)
        imglist.extend([x[0] for x in il])
        for img in il:
            if len(images) >= max_num:
                is_max_num = True
                break
            xref = img[0]
            if xref in xreflist:
                continue
            width = img[2]
            height = img[3]
            if width < min_width and height < min_height:
                continue
            image = _recoverpix(doc, img)
            imgdata = image["image"]

            if len(imgdata) <= abssize:
                continue

            if width / height > max_ratio or height / width > max_ratio:
                continue
            imgname = f'image{pno + 1}_{str(uuid.uuid4())}.{image["ext"]}'
            image_save_path = os.path.join(tmp_folder_name, imgname)
            with open(image_save_path, "wb") as fout:
                fout.write(imgdata)
            images.append(image_save_path)
            xreflist.append(xref)

    logger.info(f"Successfully extract {len(xreflist)} images.")
    return images


def read(tmp_folder_name, tmp_file_name):
    logger.info(f"Reading pdf text from {tmp_file_name}...")
    paper_text = ""
    paper_images = []
    with fitz.open(tmp_file_name) as doc:
        paper_text = "".join([page.get_text() for page in doc]).strip()
        paper_images = _extract_images(tmp_folder_name, doc)

    # delete after refenrences
    reference_pos = max(
        paper_text.find("References"),
        paper_text.find("REFERENCES"),
        paper_text.find("参考文献"),
    )
    if reference_pos > -1:
        paper_text = paper_text[:reference_pos]
    return paper_text, paper_images
