import sys, os, re, shutil, datetime



def get_resource_path(file_name:str):
    try:
        meipass = sys._MEIPASS
    except AttributeError:
        return os.path.join('crawl/myreplica', file_name)
    else:
        return os.path.join(meipass, file_name)



def extract_size(description:str):
    # description = description.lower()
    # description = re.sub(r'\s', '', description)

    size_patterns = [
        re.compile(r'(?P<size>\d+\.?\d*\s*[x\*]\s*\d+\.?\d*\s*[x\*]\s*\d+\.?\d*\s*cm)', re.IGNORECASE),
        re.compile(r'(?P<size>\d+\.?\d*\s*[x\*]\s*\d+\.?\d*\s*[x\*]\s*\d+\.?\d*)', re.IGNORECASE),
        re.compile(r'(?P<size>W?\s*\d+\.?\d*\s*cm\s*[x\*]\s*H?\d+\.?\d*\s*cm\s*[x\*]\s*D?\d+\.?\d*\s*cm)', re.IGNORECASE),
        re.compile(r'(?P<size>W?\d+\.?\d*\s*mm\s*[x\*]\s*H?\d+\.?\d*\s*mm\s*[x\*]\s*D?\d+\.?\d*\s*mm)', re.IGNORECASE),
        re.compile(r'(?P<size>\d+\.?\d*\s*cm\s*[x\*]\s*\d+\.?\d*\s*cm\s*[x\*]\s*\d+\.?\d*\s*cm)', re.IGNORECASE),
        re.compile(r'(?P<size>\d+\.?\d*″\s*W?\s*x\s*\d+\.?\d*″H?\s*x\s\d+\.?\d*″D?)', re.IGNORECASE),
        re.compile(r'(?P<size>W?\d.\.?\d*\s*cm\s*[x\*]\.?\s*L?\d+\.?\d*cm\s*[x\*]\s*D?\d+\.?\d*cm)', re.IGNORECASE),
        re.compile(r'(?P<size>\d+\.?\d*″\s*W?\s*[x\*]\s*\d.\.?\d*″\s*H?\s*[x\*]\s*\d+\.?\d*″D?)', re.IGNORECASE),
        re.compile(r'(?P<size>\d+\.?\d*\s*cm\s*\(width\)\s*[x\*]\s*\d+\.?\d*\s*cm\s*\(height\)\s*[x\*]\s*\d+\.?\d*\s*cm\s*\(depth\))', re.IGNORECASE),
        re.compile(r'(?P<size>Length\s*\d+\.?\d*\s*cm\s*[xX\*]\s*Height\s*\d+\.?\d*cm\s*[xX\s*]\s*Width\s*\d+\.?\d*cm)', re.IGNORECASE),
        re.compile(r'(?P<size>\d+\.?\d\s*cmW\s*[x\*]\s*\d+\.?\d*\s*cmH\s*[x\*]\s*\d+\.?\d*\s*cmD)', re.IGNORECASE),
        re.compile(r'(?P<size>\d+\.?\d*\s*[x\*]\s*\d+\.?\d*cm)', re.IGNORECASE),
        re.compile(r'(?P<size>\d+\.?\d*\s*\?\?\s*\d+\.?\d*\s*\?\?\s*\d+\.?\d*\s*cm)', re.IGNORECASE),
        re.compile(r'(?P<size>\d+\.?\d*\s*×\s*\d+\.?\d*\s*×\s*\d+\.?\d*\s*cm)', re.IGNORECASE),
        re.compile(r'(?P<size>L\s*\d+\.?\d*\s*[x\*]\s*H\s*\d+\.?\d*\s*[x\*]\s*D\s*\d+\.?\d*\s*cm)', re.IGNORECASE),
        re.compile(r'(?P<size>\d+\.?\d*”\s*W?\s*[x\*]\s*\d+\.?\d*”H?\s*[x\*]\s*\d+\.?\d*”D?)', re.IGNORECASE), # 10.8”W x 7.5”H x 1.6”D
        re.compile(r'(?P<size>\d+\.?\d*\s*cm\s*\(width\)\s*[x\*]\s\d+\.?\d*\s*cm\s*\(length\)\s*[x\*]\s*\d+\.?\d*\s*cm\s*\(depth\))', re.IGNORECASE), # 22 cm (width) x 29 cm (length) x 15 cm (depth)
        re.compile(r'(?P<size>W\d+\.?\d*\s*x\s*H\d+\.?\d*\s*x\s*D\d+\.?\d*cm)', re.IGNORECASE), # W25.5 x H11 x D4cm
        re.compile(r'(?P<size>\d+\.?\d*[x\*]\d+\.?\d*\.?\d*cm)', re.IGNORECASE), # 11.5*10.5.5cm
        re.compile(r'(?P<size>\d+\.?\d*”W\s*x\s*\d+\.?\d”L\s*x\s*\d+\.?\d*”D)', re.IGNORECASE), # 12”W x 10.5”L x 5.5”D
    ]

    for pattern in size_patterns:
        for line in description.split('\n'):
            if match := pattern.search(line):
                return match.group('size')
    return ''


def synk_images_by_records(records, src_dir, dest_dir, fmt_dir_name):
    current_time = datetime.datetime.now()

    for i, row in enumerate(records):
        product_id = row['product_id']
        product_name = row['product_name']
        subpath = fmt_dir_name.format(product_id=product_id, product_name=product_name)
        src = os.path.join(src_dir, subpath)
        dest = os.path.join(dest_dir, subpath)

        if not os.path.exists(dest):
            shutil.copytree(src, dest, dirs_exist_ok=True)

        min_ago = current_time - datetime.timedelta(minutes=i)
        mtime = min_ago.timestamp()
        os.utime(dest, (mtime, mtime))